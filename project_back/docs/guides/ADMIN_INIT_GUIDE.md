# 管理员初始化测试指南

## 方案一: 全新系统(推荐)

### 适用场景
- 新部署的系统
- 数据库刚初始化
- 没有注册任何用户

### 测试步骤

1. **确保数据库为空**(可选,用于测试)
   ```sql
   DELETE FROM USER_ROLE;
   DELETE FROM USER;
   DELETE FROM ROLE;
   ```

2. **启动后端服务**
   ```powershell
   cd C:\Users\yjq\Desktop\myproject\project_back
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

3. **注册第一个账号**
   - 打开前端注册页面
   - 账号: `admin`
   - 密码: `Admin123!`
   - 邮箱: `admin@example.com`
   - 昵称: `系统管理员`

4. **验证管理员权限**
   ```sql
   -- 查看用户角色
   SELECT 
       u.id, 
       u.account,
       GROUP_CONCAT(r.code) AS roles,
       CASE WHEN GROUP_CONCAT(r.code) LIKE '%ADMIN%' THEN '✅管理员' ELSE '普通用户' END AS 权限
   FROM USER u
   LEFT JOIN USER_ROLE ur ON ur.user_id = u.id
   LEFT JOIN ROLE r ON r.id = ur.role_id
   GROUP BY u.id, u.account;
   ```

   **预期结果:**
   ```
   id | account | roles       | 权限
   1  | admin   | ADMIN,USER  | ✅管理员
   ```

5. **登录测试**
   - 使用 `admin` / `Admin123!` 登录
   - 调用 `/api/v1/me` 查看用户信息
   - 应该看到 `"is_admin": true`

6. **权限测试**
   - 注册第二个普通账号 `user1`
   - 用 `user1` 创建一些题目
   - 用 `admin` 登录,应该能看到 `user1` 的题目 ✅
   - 用 `user1` 登录,只能看到自己的题目 ✅

## 方案二: 已有用户系统

### 适用场景
- 系统已运行,有现有用户
- 需要为某个用户升级为管理员

### 方法1: 通过SQL指定用户ID

```sql
-- 1. 确保ADMIN角色存在
INSERT INTO ROLE (code, name, description, created_at, updated_at)
VALUES ('ADMIN', '管理员', '拥有全部权限', NOW(), NOW())
ON DUPLICATE KEY UPDATE name='管理员';

-- 2. 为用户ID=1分配管理员角色
INSERT IGNORE INTO USER_ROLE (user_id, role_id, created_at)
SELECT 1, id, NOW() FROM ROLE WHERE code = 'ADMIN';
```

### 方法2: 通过账号名指定

```sql
-- 为账号名为 'admin' 的用户分配管理员权限
INSERT IGNORE INTO USER_ROLE (user_id, role_id, created_at)
SELECT u.id, r.id, NOW()
FROM USER u
CROSS JOIN ROLE r
WHERE u.account = 'admin' AND r.code = 'ADMIN';
```

### 方法3: 使用初始化脚本

```powershell
# 在数据库管理工具中执行 sql/init_admin_role.sql
# 脚本会自动为用户ID=1分配管理员权限
```

## 验证清单

- [ ] 第一个注册的用户自动成为管理员
- [ ] 管理员可以看到所有用户的题目
- [ ] 普通用户只能看到自己的题目
- [ ] `/api/v1/me` 返回 `is_admin: true` (管理员)
- [ ] `/api/v1/me` 返回 `is_admin: false` (普通用户)
- [ ] 管理员可以编辑其他用户的题目
- [ ] 普通用户无法访问其他用户的题目

## 常见问题

### Q: 如何撤销管理员权限?

```sql
DELETE ur FROM USER_ROLE ur
INNER JOIN ROLE r ON r.id = ur.role_id
WHERE ur.user_id = 1 AND r.code = 'ADMIN';
```

### Q: 如何查看所有管理员?

```sql
SELECT 
    u.id,
    u.account,
    u.nickname,
    u.email
FROM USER u
INNER JOIN USER_ROLE ur ON ur.user_id = u.id
INNER JOIN ROLE r ON r.id = ur.role_id
WHERE r.code = 'ADMIN';
```

### Q: 第一个用户已注册但不是管理员怎么办?

可能是在代码修复前注册的,执行SQL补救:

```sql
INSERT IGNORE INTO USER_ROLE (user_id, role_id, created_at)
SELECT 1, id, NOW() FROM ROLE WHERE code = 'ADMIN';
```

然后用户需要重新登录获取新Token。

### Q: 是否可以有多个管理员?

可以! 为多个用户分配 ADMIN 角色即可:

```sql
-- 为用户2也设为管理员
INSERT IGNORE INTO USER_ROLE (user_id, role_id, created_at)
SELECT 2, id, NOW() FROM ROLE WHERE code = 'ADMIN';
```

## 安全建议

1. ✅ 管理员账号使用强密码
2. ✅ 限制管理员数量(建议1-3个)
3. ✅ 定期检查管理员列表
4. ✅ 生产环境禁用默认管理员账号
5. ✅ 考虑添加管理员操作日志
