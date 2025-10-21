-- ====================================================================
-- 同步生产环境数据库结构
-- 日期: 2025-10-21
-- 用途: 将 00_init.sql 更新为与生产环境一致的最新结构
-- 来源: 从 DBeaver 导出的实际数据库 DDL
-- ====================================================================

-- 本文件记录了从旧版本到新版本的所有变更
-- 注意: 这些变更已经在生产环境中存在，此文件仅用于记录

USE myexam_db;

-- ========================================
-- 变更记录
-- ========================================

-- 1. USER 表变更
-- - status 字段长度从 VARCHAR(32) 改为 VARCHAR(20)
-- - 新增 last_login_at 字段（已通过 Alembic 迁移添加）
-- - 新增 password_hash 字段（已通过 Alembic 迁移添加）
-- ALTER TABLE `USER` 
-- MODIFY `status` VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
-- ADD COLUMN `last_login_at` DATETIME NULL AFTER `updated_at`,
-- ADD COLUMN `password_hash` VARCHAR(255) NULL AFTER `last_login_at`;

-- 2. KNOWLEDGE_POINT 表变更
-- - 新增 created_by 字段和索引（已通过 add_knowledge_created_by.sql 添加）
-- ALTER TABLE `KNOWLEDGE_POINT`
-- ADD COLUMN `created_by` BIGINT UNSIGNED NULL COMMENT '创建者用户ID' AFTER `description`,
-- ADD INDEX `idx_kp_created_by` (`created_by`);

-- 3. QUESTION 表新增索引
-- - 新增智能推荐相关的复合索引（已通过 add_smart_recommendation_indexes.sql 添加）
-- ALTER TABLE `QUESTION`
-- ADD INDEX `idx_question_active_difficulty` (`is_active`, `difficulty`),
-- ADD INDEX `idx_question_active_type` (`is_active`, `type`);

-- 4. QUESTION_KNOWLEDGE 表索引规范化
-- - 将 idx_qk_knowledge 重命名为 idx_question_knowledge_knowledge
-- - 新增 idx_question_knowledge_question 索引
-- 注意: 旧索引 idx_qk_knowledge 已通过 remove_duplicate_indexes.sql 删除
-- ALTER TABLE `QUESTION_KNOWLEDGE`
-- ADD INDEX `idx_question_knowledge_knowledge` (`knowledge_id`),
-- ADD INDEX `idx_question_knowledge_question` (`question_id`);

-- 5. QUESTION_TAG 表新增索引
-- - 新增 idx_question_tag_tag 索引（与 idx_qt_tag 功能相同，保留两者）
-- ALTER TABLE `QUESTION_TAG`
-- ADD INDEX `idx_question_tag_tag` (`tag_id`);

-- 6. KNOWLEDGE_POINT 表索引规范化
-- - 将 idx_kp_parent 重命名为 idx_knowledge_point_parent
-- - 新增 idx_knowledge_point_level 索引
-- 注意: 旧索引 idx_kp_parent 已通过 remove_duplicate_indexes.sql 删除
-- ALTER TABLE `KNOWLEDGE_POINT`
-- ADD INDEX `idx_knowledge_point_parent` (`parent_id`),
-- ADD INDEX `idx_knowledge_point_level` (`level`);

-- 7. ERROR_BOOK 表变更
-- - 新增 created_at 字段
-- - 新增智能推荐相关索引
-- ALTER TABLE `ERROR_BOOK`
-- ADD COLUMN `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP AFTER `updated_at`,
-- ADD INDEX `idx_error_book_user_mastered` (`user_id`, `mastered`),
-- ADD INDEX `idx_error_book_last_wrong` (`user_id`, `last_wrong_time`);

-- 8. alembic_version 表
-- - Alembic 迁移管理表（由 Alembic 自动创建）
-- CREATE TABLE `alembic_version` (
--     `version_num` VARCHAR(32) NOT NULL,
--     PRIMARY KEY (`version_num`)
-- ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ========================================
-- 验证变更
-- ========================================

-- 验证 USER 表结构
SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'myexam_db' AND TABLE_NAME = 'USER'
ORDER BY ORDINAL_POSITION;

-- 验证 KNOWLEDGE_POINT 索引
SHOW INDEX FROM KNOWLEDGE_POINT 
WHERE INDEX_NAME LIKE 'idx_%';

-- 验证 QUESTION 索引
SHOW INDEX FROM QUESTION 
WHERE INDEX_NAME LIKE 'idx_%';

-- 验证 ERROR_BOOK 结构
DESC ERROR_BOOK;

-- ========================================
-- 总结
-- ========================================
-- 本次更新主要包括:
-- 1. 用户认证字段完善（password_hash, last_login_at）
-- 2. 知识点权限隔离支持（created_by）
-- 3. 智能推荐性能优化（多个复合索引）
-- 4. 索引命名规范化（统一命名风格）
-- 5. 错题本功能增强（created_at）
-- 6. Alembic 版本管理支持
-- 
-- 所有变更已在生产环境实施，00_init.sql 已同步更新
-- ========================================
