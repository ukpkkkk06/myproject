-- create_database.sql
-- 仅负责创建数据库及可选权限，不包含任何表结构。
-- 如需多环境，可复制本文件为 create_database.dev.sql / create_database.prod.sql 等，或用模板变量。
-- 执行方式（PowerShell 示例）：
--   mysql -u root -p < .\sql\create_database.sql
-- 然后再执行：
--   mysql -u root -p myexam_db < .\sql\00_init.sql

-- 根据需要修改数据库名/字符集/排序规则
CREATE DATABASE IF NOT EXISTS `myexam_db`
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- 可选：授予业务账号（如无权限或已存在跳过）
-- GRANT ALL ON `myexam_db`.* TO 'app_user'@'%' IDENTIFIED BY 'StrongPassword!';
-- FLUSH PRIVILEGES;
