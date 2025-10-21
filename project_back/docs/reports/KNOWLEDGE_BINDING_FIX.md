# 知识点绑定权限漏洞修复

## 🐛 发现的问题

### 严重安全漏洞: 用户可以绑定其他人的知识点

**问题描述**:
- 用户在编辑题目时,可以选择其他用户创建的知识点进行绑定
- 这导致用户可以"盗用"其他人的知识点权重数据
- 练习模式可能会基于错误的知识点权重推荐题目

**影响范围**:
- `PUT /api/v1/questions/{qid}/knowledge` - 绑定题目与知识点
- 智能推荐算法 - 可能使用错误的权重计算

## ✅ 修复内容

### 1. Service层修复

**文件**: `app/services/knowledge_service.py`

**函数**: `bind_question_knowledge()`

**修改前**:
```python
def bind_question_knowledge(db: Session, question_id: int, items: Iterable[dict]):
    # 只检查知识点是否存在
    if not db.query(KnowledgePoint.id).filter(KnowledgePoint.id == kid).first():
        raise AppException(f"知识点不存在: {kid}", 400)
```

**修改后**:
```python
def bind_question_knowledge(db: Session, question_id: int, items: Iterable[dict], user: Optional[User] = None):
    # 🔒 验证知识点创建者权限
    for it in items:
        kid = int(it["knowledge_id"])
        kp = db.query(KnowledgePoint).filter(KnowledgePoint.id == kid).first()
        
        if not kp:
            raise AppException(f"知识点不存在: {kid}", 400)
        
        # 🔒 非管理员只能绑定自己创建的知识点
        if not is_admin and kp.created_by and kp.created_by != user_id:
            raise AppException(f"无权限使用知识点: {kp.name}(ID:{kid})", 403)
```

### 2. API层修复

**文件**: `app/api/v1/endpoints/knowledge.py`

**接口**: `PUT /questions/{qid}/knowledge`

**修改前**:
```python
knowledge_service.bind_question_knowledge(db, qid, [i.dict() for i in items])
```

**修改后**:
```python
# 🔒 传递用户信息以验证知识点权限
knowledge_service.bind_question_knowledge(db, qid, [i.dict() for i in items], user=me)
```

## 🔐 权限验证逻辑

### 绑定知识点权限规则

| 用户角色 | 可以绑定的知识点 |
|---------|----------------|
| 普通用户 | ✅ 只能绑定自己创建的知识点 |
| 管理员 | ✅ 可以绑定任何知识点 |

### 验证流程

```
用户选择知识点 → 验证题目权限 → 验证知识点权限 → 保存绑定关系
                   ↓                    ↓
            是否是自己的题目？      是否是自己的知识点？
                   ↓                    ↓
              NO → 403             NO → 403
              YES → ✓              YES → ✓
```

## 🧪 练习模式安全性

### 已验证的安全点

1. **题目隔离** ✅
   - 所有抽题函数都过滤 `QuestionVersion.created_by == user_id`
   - 用户只能看到自己的题目

2. **知识点绑定隔离** ✅ (本次修复)
   - 只能绑定自己创建的知识点
   - 防止使用他人的知识点权重

3. **错题本隔离** ✅
   - `ErrorBook.user_id` 过滤
   - 每个用户只能访问自己的错题

### 权重计算安全性

智能推荐算法中的权重计算:

```python
# 1. 获取用户错题关联的知识点
error_kps = db.query(QuestionKnowledge.knowledge_id).join(
    ErrorBook, ErrorBook.question_id == QuestionKnowledge.question_id
).filter(
    ErrorBook.user_id == user_id,  # ✅ 只查用户自己的错题
    ErrorBook.mastered == False
)

# 2. 计算权重
weight = calculate_inherited_weight(db, user_id, kp_id)  # ✅ 基于用户自己的数据
```

**结论**: 
- 虽然 `calculate_inherited_weight` 函数没有直接过滤 `created_by`
- 但因为输入的知识点ID来自用户自己的错题
- 而错题只关联用户自己创建的题目
- 题目只能绑定用户自己的知识点
- 所以整个链路是安全的 ✅

## 📋 测试验证

### 测试场景1: 普通用户尝试绑定他人知识点

**步骤**:
1. 用户A创建知识点 "数学" (ID=1)
2. 用户B创建题目
3. 用户B尝试为题目绑定知识点ID=1

**预期结果**:
```
HTTP 403 Forbidden
{
  "detail": "无权限使用知识点: 数学(ID:1)"
}
```

### 测试场景2: 管理员绑定任意知识点

**步骤**:
1. 用户A创建知识点 "数学" (ID=1)
2. 管理员创建题目
3. 管理员为题目绑定知识点ID=1

**预期结果**:
```
HTTP 200 OK
{ "ok": true }
```

### 测试场景3: 用户绑定自己的知识点

**步骤**:
1. 用户A创建知识点 "数学" (ID=1)
2. 用户A创建题目
3. 用户A为题目绑定知识点ID=1

**预期结果**:
```
HTTP 200 OK
{ "ok": true }
```

## 🔄 数据完整性

### 检查现有数据

```sql
-- 查找可能存在的跨用户绑定
SELECT 
    qk.question_id,
    qk.knowledge_id,
    qv.created_by AS question_creator,
    kp.created_by AS knowledge_creator,
    CASE 
        WHEN qv.created_by != kp.created_by THEN '⚠️ 跨用户绑定'
        ELSE '✅ 正常'
    END AS status
FROM QUESTION_KNOWLEDGE qk
JOIN QUESTION q ON q.id = qk.question_id
JOIN QUESTION_VERSION qv ON qv.id = q.current_version_id
JOIN KNOWLEDGE_POINT kp ON kp.id = qk.knowledge_id
WHERE qv.created_by IS NOT NULL 
  AND kp.created_by IS NOT NULL
  AND qv.created_by != kp.created_by;
```

### 清理异常数据(可选)

如果发现跨用户绑定的数据:

```sql
-- 删除跨用户的知识点绑定
DELETE qk FROM QUESTION_KNOWLEDGE qk
JOIN QUESTION q ON q.id = qk.question_id
JOIN QUESTION_VERSION qv ON qv.id = q.current_version_id
JOIN KNOWLEDGE_POINT kp ON kp.id = qk.knowledge_id
WHERE qv.created_by IS NOT NULL 
  AND kp.created_by IS NOT NULL
  AND qv.created_by != kp.created_by;
```

## 🚀 部署步骤

### 1. 重启后端服务

```powershell
cd C:\Users\yjq\Desktop\myproject\project_back
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 2. 验证修复

- 使用普通用户登录
- 尝试绑定其他用户的知识点
- 应该收到 403 错误

### 3. 清理异常数据(可选)

如果数据库中已有跨用户绑定,执行清理SQL

## 📝 修改记录

- 2025-10-21: 修复知识点绑定权限漏洞
  - 添加知识点创建者验证
  - 防止用户绑定他人知识点
  - 保护知识点权重数据安全
