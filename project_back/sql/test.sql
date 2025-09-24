START TRANSACTION;

-- 1. 为现有版本补 created_by（把 2 换成你的实际用户 ID）
UPDATE QUESTION_VERSION SET created_by = 2 WHERE created_by IS NULL;

-- 2. 新增题目 & 版本
-- 方案：先插入 QUESTION 占位（current_version_id 先为 NULL），再插入版本，最后回填 current_version_id

-- 题 A：简单加法
INSERT INTO QUESTION (current_version_id, `type`, difficulty, language_code, source_type, audit_status, is_active, created_at, updated_at)
VALUES (NULL, 'SC', 1, NULL, NULL, 'APPROVED', 1, NOW(), NOW());
SET @qid_a = LAST_INSERT_ID();

INSERT INTO QUESTION_VERSION (question_id, version_no, stem, options, correct_answer, explanation, change_note, created_by, is_active, created_at)
VALUES
(@qid_a, 1,
 '7 + 5 = ?',
 '["10","11","12","13"]',
 'C',
 '解析: 7+5=12，选 C',
 '初始版本',
 2, 1, NOW());
SET @qv_a = LAST_INSERT_ID();
UPDATE QUESTION SET current_version_id = @qv_a WHERE id = @qid_a;

-- 题 B：判断题
INSERT INTO QUESTION (current_version_id, `type`, difficulty, language_code, source_type, audit_status, is_active, created_at, updated_at)
VALUES (NULL, 'SC', 2, NULL, NULL, 'APPROVED', 1, NOW(), NOW());
SET @qid_b = LAST_INSERT_ID();

INSERT INTO QUESTION_VERSION (question_id, version_no, stem, options, correct_answer, explanation, change_note, created_by, is_active, created_at)
VALUES
(@qid_b, 1,
 '下列哪项是质数？',
 '["21","23","25","27"]',
 'B',
 '解析: 23 是质数',
 '初始版本',
 2, 1, NOW());
SET @qv_b = LAST_INSERT_ID();
UPDATE QUESTION SET current_version_id = @qv_b WHERE id = @qid_b;

-- 题 C：再来一道
INSERT INTO QUESTION (current_version_id, `type`, difficulty, language_code, source_type, audit_status, is_active, created_at, updated_at)
VALUES (NULL, 'SC', 3, NULL, NULL, 'APPROVED', 1, NOW(), NOW());
SET @qid_c = LAST_INSERT_ID();

INSERT INTO QUESTION_VERSION (question_id, version_no, stem, options, correct_answer, explanation, change_note, created_by, is_active, created_at)
VALUES
(@qid_c, 1,
 '2 的 5 次方等于多少？',
 '["16","24","32","64"]',
 'C',
 '解析: 2^5 = 32',
 '初始版本',
 2, 1, NOW());
SET @qv_c = LAST_INSERT_ID();
UPDATE QUESTION SET current_version_id = @qv_c WHERE id = @qid_c;

COMMIT;

-- 验证：
-- SELECT Q.id, Q.type, Q.difficulty, Q.audit_status, Q.current_version_id, V.stem, V.created_by
-- FROM QUESTION Q JOIN QUESTION_VERSION V ON Q.current_version_id = V.id
-- ORDER BY Q.id DESC LIMIT 10;