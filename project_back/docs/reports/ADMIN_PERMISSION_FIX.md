# 管理员权限修复说明

## 修复内容

### 1. 修复了 `app/api/deps.py`

**问题:** 原代码中 User 对象没有 `is_admin` 属性,导致所有权限检查失效

**修复:** 在 `get_current_user()` 函数中查询用户角色,动态设置 `is_admin` 属性

```python
# 查询用户的所有角色代码
role_codes = (
    db.query(Role.code)
    .join(UserRole, UserRole.role_id == Role.id)
    .filter(UserRole.user_id == user.id)
    .all()
)
# 如果角色列表中包含 ADMIN,则是管理员
user.is_admin = any(r.code == "ADMIN" for r in role_codes)
```

### 2. 修复了 `app/services/user_service.py`

**新增功能:** 第一个注册的用户自动成为管理员

```python
# 检查是否是第一个用户(系统初始化)
is_first_user = db.query(User).count() == 0

if is_first_user:
    # 自动创建 ADMIN 角色并分配给第一个用户
    admin_role = db.query(Role).filter(Role.code == "ADMIN").first()
    if not admin_role:
        admin_role = Role(code="ADMIN", name="管理员", description="...")
        db.add(admin_role)
    db.add(UserRole(user_id=user.id, role_id=admin_role.id))
```

### 3. 创建了 `sql/init_admin_role.sql`

用于为已存在的用户追加管理员权限

## 管理员初始化机制

### 🎯 自动初始化(推荐)

**第一个注册的用户会自动成为管理员!**

1. 确保数据库中没有任何用户
2. 注册第一个账号
3. 该账号自动获得 ADMIN + USER 双重角色

**示例流程:**

```bash
# 1. 清空用户表(仅用于测试/初始化)
DELETE FROM USER_ROLE;
DELETE FROM USER;

# 2. 在前端注册第一个账号
# 账号: admin
# 密码: Admin123!
# 邮箱: admin@example.com

# 3. 该账号自动成为管理员
```

### 🔧 手动分配(用于已有用户)

如果数据库中已有用户,可以使用SQL为现有用户分配管理员权限:

**方式1: 使用数据库管理工具执行 `sql/init_admin_role.sql`**

**方式2: 直接执行SQL**

```sql
-- 为用户ID=1分配管理员权限
INSERT IGNORE INTO USER_ROLE (user_id, role_id, created_at)
SELECT 1, id, NOW() FROM ROLE WHERE code = 'ADMIN';

-- 或者为指定账号分配管理员权限
INSERT IGNORE INTO USER_ROLE (user_id, role_id, created_at)
SELECT u.id, r.id, NOW()
FROM USER u
CROSS JOIN ROLE r
WHERE u.account = 'admin' AND r.code = 'ADMIN';
```

### 验证权限

### 验证权限

查看所有用户的角色分配:

```sql
SELECT 
    u.id, 
    u.account,
    GROUP_CONCAT(r.code) AS roles,
    CASE WHEN GROUP_CONCAT(r.code) LIKE '%ADMIN%' THEN '是' ELSE '否' END AS is_admin
FROM USER u
LEFT JOIN USER_ROLE ur ON ur.user_id = u.id
LEFT JOIN ROLE r ON r.id = ur.role_id
GROUP BY u.id, u.account;
```

### 重启后端服务

修改代码后需要重启:

```powershell
cd C:\Users\yjq\Desktop\myproject\project_back
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**重要:** 旧Token不包含角色信息,已登录用户需要重新登录!

## 权限说明

### 管理员权限 (is_admin=True)

拥有管理员权限的用户可以:
- ✅ 查看和编辑**所有用户**的题目
- ✅ 删除任何题目
- ✅ 访问所有知识点
- ✅ 管理所有用户的数据

### 普通用户权限 (is_admin=False)

普通用户只能:
- ✅ 查看和编辑**自己创建**的题目
- ✅ 访问自己的知识点
- ❌ 无法访问其他用户的数据

## 角色体系

| 角色代码 | 角色名称 | 说明 |
|---------|---------|------|
| ADMIN   | 管理员   | 全部权限 |
| USER    | 普通用户 | 基础权限 |

## 检查管理员权限是否生效

### 方法1: 查看日志

登录后,在后端日志中可以看到用户的 `is_admin` 状态

### 方法2: 测试访问权限

- 管理员登录后,应该能看到所有用户的题目
- 普通用户登录后,只能看到自己的题目

### 方法3: API 测试

```bash
# 获取当前用户信息(应返回 is_admin 字段)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/users/me
```

## 故障排查

### 问题: 设置了管理员角色但仍无权限

**排查步骤:**
1. 检查 `USER_ROLE` 表是否有对应记录
2. 确认 `ROLE` 表中 ADMIN 角色的 `code` 字段是 "ADMIN"(大写)
3. 重启后端服务
4. 重新登录获取新的 Token

### 问题: 所有用户都是管理员

**原因:** 可能在代码中错误地为所有用户分配了 ADMIN 角色

**解决:**
```sql
-- 删除错误的管理员分配
DELETE ur FROM USER_ROLE ur
INNER JOIN ROLE r ON r.id = ur.role_id
WHERE r.code = 'ADMIN' AND ur.user_id != 1;  -- 保留 ID=1 的管理员
```

## 修改记录

- 2025-10-21: 修复管理员权限检查失效问题
- 2025-10-21: 添加角色初始化脚本
