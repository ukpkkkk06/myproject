-- 修改为你的库名
USE myexam_db;

START TRANSACTION;

-- 题1
INSERT INTO QUESTION(`type`,`difficulty`,`audit_status`,`is_active`)
VALUES ('SC',1,'APPROVED',1);
SET @qid := LAST_INSERT_ID();
INSERT INTO QUESTION_VERSION (question_id,version_no,stem,`options`,correct_answer,is_active)
VALUES (@qid,1,'1+1=？','["A.1","B.2","C.3","D.4"]','B',1);

-- 题2
INSERT INTO QUESTION(`type`,`difficulty`,`audit_status`,`is_active`)
VALUES ('SC',1,'APPROVED',1);
SET @qid := LAST_INSERT_ID();
INSERT INTO QUESTION_VERSION (question_id,version_no,stem,`options`,correct_answer,is_active)
VALUES (@qid,1,'2+2=？','["A.2","B.3","C.4","D.5"]','C',1);

-- 题3
INSERT INTO QUESTION(`type`,`difficulty`,`audit_status`,`is_active`)
VALUES ('SC',1,'APPROVED',1);
SET @qid := LAST_INSERT_ID();
INSERT INTO QUESTION_VERSION (question_id,version_no,stem,`options`,correct_answer,is_active)
VALUES (@qid,1,'3+1=？','["A.3","B.4","C.5","D.6"]','B',1);

-- 题4
INSERT INTO QUESTION(`type`,`difficulty`,`audit_status`,`is_active`)
VALUES ('SC',1,'APPROVED',1);
SET @qid := LAST_INSERT_ID();
INSERT INTO QUESTION_VERSION (question_id,version_no,stem,`options`,correct_answer,is_active)
VALUES (@qid,1,'5-2=？','["A.2","B.3","C.4","D.5"]','B',1);

-- 题5
INSERT INTO QUESTION(`type`,`difficulty`,`audit_status`,`is_active`)
VALUES ('SC',1,'APPROVED',1);
SET @qid := LAST_INSERT_ID();
INSERT INTO QUESTION_VERSION (question_id,version_no,stem,`options`,correct_answer,is_active)
VALUES (@qid,1,'6-2=？','["A.3","B.4","C.5","D.6"]','B',1);

-- 回填 QUESTION.current_version_id
UPDATE QUESTION q
JOIN QUESTION_VERSION v ON v.question_id = q.id AND v.version_no = 1
SET q.current_version_id = v.id
WHERE q.current_version_id IS NULL;

UPDATE QUESTION_VERSION
SET explanation = CONCAT('解析：正确答案是 ', correct_answer)
WHERE explanation IS NULL;

COMMIT;
