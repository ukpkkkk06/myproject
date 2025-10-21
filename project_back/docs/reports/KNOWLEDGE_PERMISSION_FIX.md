# 知识点权限隔离修复说明

## 🐛 问题描述

**严重安全漏洞**: 用户可以访问、查看其他用户创建的知识点

**原因**: 
- `KNOWLEDGE_POINT` 表缺少 `created_by` 字段
- API没有权限过滤,返回所有用户的知识点

## ✅ 修复内容

### 1. 数据库变更

**文件**: `sql/add_knowledge_created_by.sql`

添加 `created_by` 字段到 `KNOWLEDGE_POINT` 表:

```sql
ALTER TABLE `KNOWLEDGE_POINT` 
ADD COLUMN `created_by` BIGINT UNSIGNED NULL COMMENT '创建者用户ID',
ADD INDEX `idx_kp_created_by` (`created_by`);
```

### 2. 模型更新

**文件**: `app/models/knowledge_point.py`

添加 `created_by` 字段映射:

```python
created_by = Column(BigInteger, ForeignKey("USER.id"), nullable=True, index=True)
```

### 3. Service层更新

**文件**: `app/services/knowledge_service.py`

**修改的函数**:

- `list_tree()` - 添加权限过滤
  ```python
  # 管理员: 看到所有知识点
  # 普通用户: 只看到自己创建的知识点
  if not is_admin:
      query = query.filter(KnowledgePoint.created_by == user_id)
  ```

- `create()` - 记录创建者
  ```python
  node = KnowledgePoint(
      ...,
      created_by=user_id  # 记录创建者
  )
  ```

- `update()` - 权限检查
  ```python
  # 只能修改自己创建的知识点
  if not is_admin and node.created_by != user_id:
      raise AppException("无权限修改此知识点", 403)
  ```

- `delete()` - 权限检查
  ```python
  # 只能删除自己创建的知识点
  if not is_admin and node.created_by != user_id:
      raise AppException("无权限删除此知识点", 403)
  ```

### 4. API层更新

**文件**: `app/api/v1/endpoints/knowledge.py`

所有知识点相关接口添加用户认证和权限控制:

- `GET /knowledge/tree` - 添加用户参数,实现权限过滤
- `POST /knowledge` - 传递用户信息记录创建者
- `PUT /knowledge/{kid}` - 传递用户信息验证权限
- `DELETE /knowledge/{kid}` - 传递用户信息验证权限

## 🚀 部署步骤

### 步骤1: 执行数据库迁移

**使用Docker exec方式**:

```powershell
# 执行SQL迁移脚本
docker exec -i mysql-server mysql -u root -p123456 myexam_db < C:\Users\yjq\Desktop\myproject\project_back\sql\add_knowledge_created_by.sql
```

**或使用数据库管理工具**:
- 打开 Navicat/DBeaver
- 连接到 `localhost:3306/myexam_db`
- 执行 `sql/add_knowledge_created_by.sql`

### 步骤2: 处理现有数据(可选)

如果数据库中已有知识点,需要为它们分配创建者:

```sql
-- 方案A: 将所有知识点分配给管理员(用户ID=1)
UPDATE KNOWLEDGE_POINT SET created_by = 1 WHERE created_by IS NULL;

-- 方案B: 删除所有现有知识点(仅适用于测试环境)
DELETE FROM QUESTION_KNOWLEDGE;  -- 先删除关联
DELETE FROM KNOWLEDGE_POINT;     -- 再删除知识点
```

### 步骤3: 重启后端服务

```powershell
# Terminal: uvicorn
cd C:\Users\yjq\Desktop\myproject\project_back
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 步骤4: 测试验证

1. **创建测试账号**
   - 用户A: 创建知识点 "数学"
   - 用户B: 创建知识点 "英语"

2. **验证隔离**
   - 用户A登录 → 只能看到 "数学"
   - 用户B登录 → 只能看到 "英语"
   - 管理员登录 → 能看到所有知识点

3. **验证权限**
   - 用户A无法修改/删除用户B的知识点
   - 管理员可以修改/删除任何知识点

## 📊 权限矩阵

| 操作 | 创建者 | 其他用户 | 管理员 |
|-----|-------|---------|--------|
| 查看知识点 | ✅ | ❌ | ✅ 全部 |
| 创建子知识点 | ✅ | ❌ | ✅ |
| 修改知识点 | ✅ | ❌ | ✅ |
| 删除知识点 | ✅ | ❌ | ✅ |

## ⚠️ 注意事项

### 1. 现有知识点处理

**问题**: 现有知识点的 `created_by` 为 NULL

**影响**: 
- NULL 的知识点所有用户都看不到(包括管理员)
- 需要决定如何分配这些知识点

**解决方案**:
```sql
-- 将现有知识点分配给第一个用户
UPDATE KNOWLEDGE_POINT 
SET created_by = (SELECT MIN(id) FROM USER) 
WHERE created_by IS NULL;
```

### 2. 知识点共享

目前知识点是**完全隔离**的,不支持共享。

如果未来需要支持知识点共享,可以:
- 添加 `is_public` 字段(公开/私有)
- 添加 `KNOWLEDGE_SHARE` 表(分享给特定用户)

### 3. 父子节点权限

**规则**: 只能在自己创建的父节点下创建子节点

**例如**:
- 用户A创建了 "数学" 
- 用户B**不能**在 "数学" 下创建 "代数"
- 用户A**可以**在 "数学" 下创建 "代数"

## 🧪 测试SQL

### 测试1: 验证字段是否添加

```sql
DESC KNOWLEDGE_POINT;
-- 应该看到 created_by 字段
```

### 测试2: 查看知识点创建者

```sql
SELECT 
    kp.id,
    kp.name,
    kp.created_by,
    u.account AS creator_account
FROM KNOWLEDGE_POINT kp
LEFT JOIN USER u ON u.id = kp.created_by
ORDER BY kp.id;
```

### 测试3: 验证权限隔离

```sql
-- 查看每个用户的知识点数量
SELECT 
    u.id,
    u.account,
    COUNT(kp.id) AS knowledge_count
FROM USER u
LEFT JOIN KNOWLEDGE_POINT kp ON kp.created_by = u.id
GROUP BY u.id, u.account;
```

## 🔄 回滚方案

如果需要回滚修改:

```sql
-- 删除 created_by 字段
ALTER TABLE KNOWLEDGE_POINT DROP COLUMN created_by;
```

然后还原代码文件。

## 📝 修改记录

- 2025-10-21: 修复知识点权限隔离漏洞
  - 添加 created_by 字段
  - 实现权限过滤和检查
  - 更新API、Service、Model三层
