-- ========================================
-- 智能推荐功能性能优化索引
-- ========================================
-- 用途：提升智能推荐算法的查询性能
-- 创建时间：2025-10-21
-- ========================================

USE myexam_db;

-- 1. ERROR_BOOK 表索引
-- 用于快速查询用户的错题记录
CREATE INDEX idx_error_book_user_mastered 
ON ERROR_BOOK(user_id, mastered);

-- 用于时间衰减计算（按最后错误时间排序）
CREATE INDEX idx_error_book_last_wrong 
ON ERROR_BOOK(user_id, last_wrong_time);

-- 2. QUESTION_KNOWLEDGE 表索引  
-- 用于快速查询知识点关联的题目
CREATE INDEX idx_question_knowledge_knowledge 
ON QUESTION_KNOWLEDGE(knowledge_id);

-- 用于反向查询题目关联的知识点
CREATE INDEX idx_question_knowledge_question 
ON QUESTION_KNOWLEDGE(question_id);

-- 3. QUESTION 表索引
-- 用于难题筛选（基于difficulty字段）
CREATE INDEX idx_question_active_difficulty 
ON QUESTION(is_active, difficulty);

-- 用于题型筛选
CREATE INDEX idx_question_active_type 
ON QUESTION(is_active, type);

-- 4. KNOWLEDGE_POINT 表索引
-- 用于快速查找父子关系
CREATE INDEX idx_knowledge_point_parent 
ON KNOWLEDGE_POINT(parent_id);

-- 用于层级查询
CREATE INDEX idx_knowledge_point_level 
ON KNOWLEDGE_POINT(level);

-- 5. QUESTION_TAG 表索引
-- 用于学科筛选
CREATE INDEX idx_question_tag_tag 
ON QUESTION_TAG(tag_id);

-- ========================================
-- 验证索引创建
-- ========================================
SELECT 
    TABLE_NAME,
    INDEX_NAME,
    COLUMN_NAME,
    SEQ_IN_INDEX
FROM INFORMATION_SCHEMA.STATISTICS
WHERE TABLE_SCHEMA = 'myexam_db'
  AND TABLE_NAME IN ('ERROR_BOOK', 'QUESTION_KNOWLEDGE', 'QUESTION', 'KNOWLEDGE_POINT', 'QUESTION_TAG')
  AND INDEX_NAME LIKE 'idx_%'
ORDER BY TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX;
