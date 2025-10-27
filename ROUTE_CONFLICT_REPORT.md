# 路由路径冲突检查报告

## 📋 当前路由配置（app/__init__.py）

```python
api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health.router, tags=["health"])                    # NO PREFIX
api_router.include_router(auth.router, tags=["auth"])                        # NO PREFIX
api_router.include_router(users.router, tags=["users"])                      # NO PREFIX
api_router.include_router(practice.router, tags=["practice"])                # NO PREFIX
api_router.include_router(tags.router, tags=["tags"])                        # NO PREFIX
api_router.include_router(error_book.router, prefix="/error-book", tags=["error-book"])  # ✅ HAS PREFIX
api_router.include_router(question_bank.router, tags=["question-bank"])      # NO PREFIX ❌
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])     # ✅ HAS PREFIX
api_router.include_router(knowledge.router, tags=["knowledge"])              # NO PREFIX
```

---

## ⚠️ 发现的问题

### 1. ❌ question_bank.py - 路径重复问题

**问题描述**: 
- router注册时**没有prefix**
- 但路由定义中**自己加了** `/question-bank/` 前缀
- 导致部分路由有重复定义

**具体路由**:
```python
# 有 /question-bank/ 前缀的（会变成 /api/v1/question-bank/xxx）
@router.get("/question-bank/import-template")
@router.get("/question-bank/my-questions")
@router.get("/question-bank/questions/brief")
@router.get("/question-bank/questions/{qid:int}")
@router.put("/question-bank/questions/{qid:int}")
@router.get("/question-bank/questions/{qid:int}/tags")
@router.put("/question-bank/questions/{qid:int}/tags")
@router.post("/question-bank/import-excel")

# 没有前缀的（会变成 /api/v1/xxx）❌ 不一致
@router.get("/my-questions")
@router.get("/questions/brief")
@router.get("/questions/{qid:int}")
@router.put("/questions/{qid:int}")
@router.get("/questions")
@router.get("/tags")  # ❌ 与 tags.py 的 /tags 冲突！
```

**影响**:
- 路径不统一，部分API路径是 `/api/v1/question-bank/xxx`
- 部分API路径是 `/api/v1/xxx`
- `/api/v1/tags` 与 tags.py 的路由冲突

**建议修复**:
1. 在 `app/__init__.py` 中添加 `prefix="/question-bank"`
2. 删除所有路由定义中的 `/question-bank/` 前缀
3. 删除 `question_bank.py` 中的 `@router.get("/tags")`，避免与 tags.py 冲突

---

### 2. ✅ error_book.py - 正确配置

**配置**:
```python
# app/__init__.py
api_router.include_router(error_book.router, prefix="/error-book", tags=["error-book"])

# error_book.py
@router.get("")                     # → /api/v1/error-book
@router.post("/{question_id}/record")  # → /api/v1/error-book/{question_id}/record
@router.patch("/{question_id}/master") # → /api/v1/error-book/{question_id}/master
@router.delete("/{question_id}")      # → /api/v1/error-book/{question_id}
```

**状态**: ✅ 正确，路由清晰统一

---

### 3. ✅ admin.py - 已修复

**配置**:
```python
# app/__init__.py
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])

# admin.py
@router.get("/users/{uid:int}")         # → /api/v1/admin/users/{uid}
@router.put("/users/{uid:int}")         # → /api/v1/admin/users/{uid}
@router.put("/users/{uid:int}/password") # → /api/v1/admin/users/{uid}/password
@router.get("/stats")                   # → /api/v1/admin/stats
@router.get("/mem/stats")               # → /api/v1/admin/mem/stats
@router.get("/mem/top")                 # → /api/v1/admin/mem/top
@router.post("/mem/reset-peak")         # → /api/v1/admin/mem/reset-peak
```

**状态**: ✅ 已修复，路由清晰统一

---

### 4. ⚠️ users.py - 需要确认

让我检查 users.py 是否有类似问题...

---

### 5. ⚠️ practice.py - 需要确认

让我检查 practice.py 是否有类似问题...

---

### 6. ⚠️ knowledge.py - 需要确认

让我检查 knowledge.py 是否有类似问题...

---

## 🔧 修复建议

### 优先级 P0 - 立即修复

**question_bank.py 路径冲突**:

1. 修改 `app/__init__.py`:
```python
api_router.include_router(question_bank.router, prefix="/question-bank", tags=["question-bank"])
```

2. 修改 `question_bank.py`，删除所有路由中的 `/question-bank/` 前缀:
```python
# 修改前
@router.get("/question-bank/import-template")
@router.get("/question-bank/my-questions")
# ... 等等

# 修改后
@router.get("/import-template")
@router.get("/my-questions")
# ... 等等
```

3. 删除 `question_bank.py` 中的重复 tags 路由:
```python
# 删除这个，因为已经有 tags.py
@router.get("/tags", response_model=List[TagOut])
```

---

## 📊 检查清单

- [x] admin.py - 已修复 ✅
- [x] error_book.py - 配置正确 ✅
- [ ] question_bank.py - **需要修复** ❌
- [ ] users.py - 待检查
- [ ] practice.py - 待检查
- [ ] knowledge.py - 待检查
- [x] tags.py - 配置正确 ✅
- [x] auth.py - 配置正确 ✅
- [x] health.router - 配置正确 ✅

---

## 🎯 下一步行动

1. 立即修复 question_bank.py 的路径冲突
2. 检查其余端点文件是否有类似问题
3. 建立路由命名规范文档
