-- ========================================
-- 删除重复索引优化
-- 执行日期: 2025-10-21
-- 目的: 删除功能重复的索引，提升数据库性能
-- ========================================

USE myexam_db;

-- 1. KNOWLEDGE_POINT 表
-- 删除旧索引 idx_kp_parent（保留更规范的 idx_knowledge_point_parent）
-- DROP INDEX idx_kp_parent ON KNOWLEDGE_POINT;  -- ✅ 已执行

-- 2. QUESTION_KNOWLEDGE 表  
-- 删除旧索引 idx_qk_knowledge（保留更规范的 idx_question_knowledge_knowledge）
-- DROP INDEX idx_qk_knowledge ON QUESTION_KNOWLEDGE;  -- ✅ 已执行

-- ========================================
-- 验证优化结果
-- ========================================

-- 查看 KNOWLEDGE_POINT 当前索引
SELECT 
    'KNOWLEDGE_POINT' as table_name,
    INDEX_NAME,
    COLUMN_NAME,
    NON_UNIQUE,
    INDEX_TYPE
FROM INFORMATION_SCHEMA.STATISTICS
WHERE TABLE_SCHEMA = 'myexam_db'
  AND TABLE_NAME = 'KNOWLEDGE_POINT'
  AND INDEX_NAME LIKE 'idx_%'
ORDER BY INDEX_NAME, SEQ_IN_INDEX;

-- 查看 QUESTION_KNOWLEDGE 当前索引
SELECT 
    'QUESTION_KNOWLEDGE' as table_name,
    INDEX_NAME,
    COLUMN_NAME,
    NON_UNIQUE,
    INDEX_TYPE
FROM INFORMATION_SCHEMA.STATISTICS
WHERE TABLE_SCHEMA = 'myexam_db'
  AND TABLE_NAME = 'QUESTION_KNOWLEDGE'
  AND INDEX_NAME LIKE 'idx_%'
ORDER BY INDEX_NAME, SEQ_IN_INDEX;

-- ========================================
-- 优化效果
-- ========================================
-- KNOWLEDGE_POINT: 从 4 个索引减少到 3 个（删除重复）
-- QUESTION_KNOWLEDGE: 从 3 个索引减少到 2 个（删除重复）
-- 预期效果: 
-- - 减少索引维护开销
-- - 降低写操作延迟
-- - 减少磁盘空间占用
