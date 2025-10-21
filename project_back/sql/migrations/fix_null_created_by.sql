-- ====================================================================
-- 修复题目版本表中 created_by 为 NULL 的历史数据
-- 日期: 2025-10-21
-- 问题: 题目版本的 created_by 字段为 NULL 导致用户无法访问这些题目
-- 解决方案: 将所有 created_by 为 NULL 的记录设置为管理员(user_id=1)
-- ====================================================================

-- 查看影响的记录数
SELECT COUNT(*) as null_count 
FROM QUESTION_VERSION 
WHERE created_by IS NULL;

-- 查看具体的记录
SELECT id, question_id, created_by 
FROM QUESTION_VERSION 
WHERE created_by IS NULL 
ORDER BY id;

-- 更新所有 created_by 为 NULL 的记录
UPDATE QUESTION_VERSION 
SET created_by = 1  -- 设置为第一个用户(管理员 alice)
WHERE created_by IS NULL;

-- 验证更新结果
SELECT COUNT(*) as null_count 
FROM QUESTION_VERSION 
WHERE created_by IS NULL;

-- 验证具体的题目(69和76)
SELECT q.id, q.current_version_id, qv.created_by 
FROM QUESTION q 
LEFT JOIN QUESTION_VERSION qv ON q.current_version_id = qv.id 
WHERE q.id IN (69, 76);
