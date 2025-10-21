# 用户管理API权限修复说明

**修复日期**: 2025-10-21  
**文件**: `app/api/v1/endpoints/users.py`  
**问题**: 所有用户管理接口完全缺乏身份验证和权限控制  

---

## 🔧 修复内容

### 1. 添加权限依赖函数

```python
def require_admin(me: User = Depends(get_current_user)):
    """要求管理员权限"""
    if not getattr(me, "is_admin", False):
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return me
```

这个函数可以被任何需要管理员权限的接口使用。

---

### 2. 修复各个接口

#### ✅ POST /users - 创建用户
- **之前**: ❌ 任何人都可以创建用户
- **现在**: ✅ 仅管理员可创建用户
- **权限**: `Depends(require_admin)`

```python
@router.post("/users", response_model=UserRead)
def create_user(
    payload: UserCreate, 
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)  # 仅管理员
):
    """创建用户 - 仅管理员可用"""
    return user_service.create_user(db, payload)
```

---

#### ✅ GET /users/simple - 查看用户列表
- **之前**: ❌ 任何人都可以查看所有用户
- **现在**: ✅ 仅管理员可查看用户列表
- **权限**: `Depends(require_admin)`

```python
@router.get("/users/simple", response_model=UsersSimplePage)
def list_users_simple(
    skip: int = 0,
    limit: int = 20,
    account: str | None = None,
    email: str | None = None,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)  # 仅管理员
):
    """查看用户列表 - 仅管理员可用"""
    return user_service.list_users_simple(db, skip=skip, limit=limit, account=account, email=email)
```

---

#### ✅ GET /users/{user_id} - 查看用户详情
- **之前**: ❌ 任何人都可以查看任何用户
- **现在**: ✅ 管理员可查看所有用户,普通用户只能查看自己
- **权限**: `Depends(get_current_user)` + 自定义权限检查

```python
@router.get("/users/{user_id:int}", response_model=UserOut)
def get_user(
    user_id: int, 
    db: Session = Depends(get_db),
    me: User = Depends(get_current_user)  # 需要登录
):
    """查看用户详情 - 管理员可查看所有用户,普通用户只能查看自己"""
    # 检查权限:管理员可以查看任何用户,普通用户只能查看自己
    is_admin = getattr(me, "is_admin", False)
    if not is_admin and me.id != user_id:
        raise HTTPException(status_code=403, detail="无权限访问该用户信息")
    
    return user_service.get_user(db, user_id)
```

**权限逻辑**:
- 管理员: 可查看任何用户
- 普通用户: 只能查看自己 (`me.id == user_id`)

---

#### ✅ PUT /users/{user_id} - 修改用户信息
- **之前**: ❌ 任何人都可以修改任何用户
- **现在**: ✅ 管理员可修改所有用户,普通用户只能修改自己
- **权限**: `Depends(get_current_user)` + 自定义权限检查

```python
@router.put("/users/{user_id:int}", response_model=UserOut)
def update_user(
    user_id: int, 
    body: dict, 
    db: Session = Depends(get_db),
    me: User = Depends(get_current_user)  # 需要登录
):
    """修改用户信息 - 管理员可修改所有用户,普通用户只能修改自己"""
    # 检查权限:管理员可以修改任何用户,普通用户只能修改自己
    is_admin = getattr(me, "is_admin", False)
    if not is_admin and me.id != user_id:
        raise HTTPException(status_code=403, detail="无权限修改该用户信息")
    
    return user_service.update_user(db, user_id, body)
```

**权限逻辑**:
- 管理员: 可修改任何用户
- 普通用户: 只能修改自己 (`me.id == user_id`)

---

#### ✅ DELETE /users/{user_id} - 删除用户
- **之前**: ❌ 任何人都可以删除任何用户
- **现在**: ✅ 仅管理员可删除用户,且不能删除自己
- **权限**: `Depends(require_admin)` + 额外的自我保护检查

```python
@router.delete("/users/{user_id:int}")
def delete_user(
    user_id: int, 
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)  # 仅管理员
):
    """删除用户 - 仅管理员可用"""
    # 防止删除自己
    if admin.id == user_id:
        raise HTTPException(status_code=400, detail="不能删除自己的账号")
    
    user_service.delete_user(db, user_id)
    return {"code": 0, "message": "ok"}
```

**权限逻辑**:
- 必须是管理员
- 不能删除自己的账号

---

## 📊 权限矩阵

| 接口 | 管理员 | 普通用户 | 未登录 |
|-----|-------|---------|--------|
| POST /users | ✅ 可创建 | ❌ 禁止 | ❌ 禁止 |
| GET /users/simple | ✅ 可查看全部 | ❌ 禁止 | ❌ 禁止 |
| GET /users/{id} | ✅ 可查看任何用户 | ✅ 仅可查看自己 | ❌ 禁止 |
| PUT /users/{id} | ✅ 可修改任何用户 | ✅ 仅可修改自己 | ❌ 禁止 |
| DELETE /users/{id} | ✅ 可删除(非自己) | ❌ 禁止 | ❌ 禁止 |

---

## 🔒 安全改进

1. **身份验证**: 所有接口都需要JWT token
2. **权限隔离**: 管理员和普通用户有明确的权限边界
3. **资源访问控制**: 普通用户只能访问自己的资源
4. **自我保护**: 管理员不能删除自己
5. **错误提示**: 清晰的403/400错误信息

---

## ⚠️ 注意事项

### 1. 用户注册
用户注册应该通过 `/api/v1/auth/register` 接口,而不是 `/api/v1/users` 接口。

### 2. 首次管理员
根据之前的修复,第一个注册的用户会自动成为管理员。

### 3. 管理员后台
如果需要管理员专用的用户管理功能,建议使用 `/api/v1/admin/users` 接口。

---

## 🧪 测试建议

### 测试1: 未登录访问
```bash
curl -X GET http://localhost:8000/api/v1/users/simple
# 期望: 401 Unauthorized
```

### 测试2: 普通用户访问他人信息
```bash
curl -X GET http://localhost:8000/api/v1/users/999 \
  -H "Authorization: Bearer {normal_user_token}"
# 期望: 403 Forbidden (假设用户ID不是999)
```

### 测试3: 普通用户访问自己信息
```bash
curl -X GET http://localhost:8000/api/v1/users/1 \
  -H "Authorization: Bearer {user1_token}"
# 期望: 200 OK
```

### 测试4: 管理员创建用户
```bash
curl -X POST http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer {admin_token}" \
  -H "Content-Type: application/json" \
  -d '{"account":"test","password":"123456","email":"test@example.com"}'
# 期望: 200 OK
```

### 测试5: 管理员删除自己
```bash
curl -X DELETE http://localhost:8000/api/v1/users/1 \
  -H "Authorization: Bearer {admin_token}"
# 期望: 400 Bad Request (不能删除自己)
```

---

## ✅ 修复状态

- [x] 添加 `require_admin` 权限依赖函数
- [x] POST /users - 添加管理员权限
- [x] GET /users/simple - 添加管理员权限
- [x] GET /users/{id} - 添加身份验证和权限检查
- [x] PUT /users/{id} - 添加身份验证和权限检查
- [x] DELETE /users/{id} - 添加管理员权限和自我保护

---

## 🚀 下一步

1. ✅ 用户管理API权限修复完成
2. ⏭️ 下一步: 实现错题本Service缺失函数
3. ⏭️ 下一步: 为标签API添加身份验证

