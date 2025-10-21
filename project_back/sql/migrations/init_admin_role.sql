-- 初始化管理员角色
-- 注意: 从代码层面,第一个注册的用户会自动成为管理员
-- 此脚本仅用于为已存在的用户追加管理员权限
-- 执行: mysql -u root -p myexam_db < .\sql\init_admin_role.sql

USE `myexam_db`;

-- 1. 插入 ADMIN 角色(如果不存在)
INSERT INTO `ROLE` (`code`, `name`, `description`, `created_at`, `updated_at`)
VALUES ('ADMIN', '管理员', '拥有全部权限,可以访问和管理所有用户的数据', NOW(), NOW())
ON DUPLICATE KEY UPDATE 
    `name` = '管理员',
    `description` = '拥有全部权限,可以访问和管理所有用户的数据',
    `updated_at` = NOW();

-- 2. 插入 USER 角色(如果不存在)
INSERT INTO `ROLE` (`code`, `name`, `description`, `created_at`, `updated_at`)
VALUES ('USER', '普通用户', '基础权限,仅能查看和管理自己创建的数据', NOW(), NOW())
ON DUPLICATE KEY UPDATE 
    `name` = '普通用户',
    `description` = '基础权限,仅能查看和管理自己创建的数据',
    `updated_at` = NOW();

-- 3. 为指定用户分配管理员角色
-- 方式1: 为用户ID=1分配管理员权限(如果该用户存在)
INSERT IGNORE INTO `USER_ROLE` (`user_id`, `role_id`, `created_at`)
SELECT 1, r.id, NOW()
FROM `ROLE` r
WHERE r.code = 'ADMIN'
AND EXISTS (SELECT 1 FROM `USER` WHERE id = 1);

-- 方式2: 为指定账号分配管理员权限(替换 'admin' 为实际账号)
-- INSERT IGNORE INTO `USER_ROLE` (`user_id`, `role_id`, `created_at`)
-- SELECT u.id, r.id, NOW()
-- FROM `USER` u
-- CROSS JOIN `ROLE` r
-- WHERE u.account = 'admin' AND r.code = 'ADMIN';

-- 显示当前用户角色分配情况
SELECT 
    u.id AS user_id,
    u.account,
    u.nickname,
    GROUP_CONCAT(r.code) AS role_codes,
    GROUP_CONCAT(r.name) AS role_names,
    CASE WHEN GROUP_CONCAT(r.code) LIKE '%ADMIN%' THEN '是' ELSE '否' END AS is_admin
FROM `USER` u
LEFT JOIN `USER_ROLE` ur ON ur.user_id = u.id
LEFT JOIN `ROLE` r ON r.id = ur.role_id
GROUP BY u.id, u.account, u.nickname
ORDER BY u.id;
