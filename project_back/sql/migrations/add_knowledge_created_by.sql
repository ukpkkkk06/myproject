-- 为知识点表添加 created_by 字段
-- 用于实现知识点的权限隔离

USE `myexam_db`;

-- 1. 添加 created_by 字段
ALTER TABLE `KNOWLEDGE_POINT` 
ADD COLUMN `created_by` BIGINT UNSIGNED NULL COMMENT '创建者用户ID' AFTER `description`,
ADD INDEX `idx_kp_created_by` (`created_by`);

-- 2. 添加外键约束(可选,如果需要严格的引用完整性)
-- ALTER TABLE `KNOWLEDGE_POINT`
-- ADD CONSTRAINT `fk_kp_creator` 
-- FOREIGN KEY (`created_by`) REFERENCES `USER`(`id`) 
-- ON DELETE SET NULL ON UPDATE CASCADE;

-- 3. 为现有知识点设置默认创建者(可选)
-- 如果数据库中已有知识点,可以将它们分配给第一个用户或管理员
-- UPDATE `KNOWLEDGE_POINT` SET `created_by` = 1 WHERE `created_by` IS NULL;

-- 4. 查看修改结果
DESC `KNOWLEDGE_POINT`;

-- 5. 查看当前知识点数据
SELECT id, name, parent_id, created_by FROM `KNOWLEDGE_POINT` LIMIT 10;