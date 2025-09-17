-- 00_init.sql
-- 职责：在目标数据库(已由 create_database.sql 创建)中初始化全部表结构与外键。
-- 执行前需已存在数据库，并在命令中指定：
--   mysql -u root -p myexam_db < .\sql\00_init.sql
-- 若数据库名不同，请替换 myexam_db。
-- 不负责创建 DATABASE，也不进行权限授予。

-- 可选：如脚本未通过命令行指定数据库，可手动取消注释：
-- USE `myexam_db`;

-- 通用设置
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 1. 角色
CREATE TABLE `ROLE` (
    `id`            BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    `code`          VARCHAR(64) NOT NULL,
    `name`          VARCHAR(100) NOT NULL,
    `description`   TEXT NULL,
    `created_at`    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_role_code (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. 用户
CREATE TABLE `USER` (
    `id`            BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    `nickname`      VARCHAR(100) NULL,
    `account`       VARCHAR(64) NOT NULL,
    `email`         VARCHAR(255) NULL,
    `status`        VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
    `created_at`    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_account (`account`),
    UNIQUE KEY uk_user_email (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. 试卷
CREATE TABLE `PAPER` (
    `id`            BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    `title`         VARCHAR(255) NOT NULL,
    `exam_type`     VARCHAR(64) NULL,
    `year`          VARCHAR(8) NULL,
    `difficulty`    TINYINT NULL,
    `created_by`    BIGINT UNSIGNED NULL,
    `is_public`     TINYINT(1) NOT NULL DEFAULT 0,
    `status`        VARCHAR(32) NOT NULL DEFAULT 'DRAFT',
    `created_at`    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_paper_created_by (`created_by`),
    CONSTRAINT fk_paper_creator FOREIGN KEY (`created_by`) REFERENCES `USER`(`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. 题目（current_version_id 之后再加外键）
CREATE TABLE `QUESTION` (
    `id`                BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    `current_version_id` BIGINT UNSIGNED NULL,
    `type`              VARCHAR(32) NOT NULL,
    `difficulty`        TINYINT NULL,
    `language_code`     VARCHAR(16) NULL,
    `source_type`       VARCHAR(32) NULL,
    `audit_status`      VARCHAR(32) NOT NULL DEFAULT 'PENDING',
    `is_active`         TINYINT(1) NOT NULL DEFAULT 1,
    `created_at`        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_question_type (`type`),
    KEY idx_question_active (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. 题目版本
CREATE TABLE `QUESTION_VERSION` (
    `id`            BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    `question_id`   BIGINT UNSIGNED NOT NULL,
    `version_no`    INT NOT NULL,
    `stem`          TEXT NOT NULL,
    `options`       JSON NULL,
    `correct_answer` VARCHAR(255) NULL,
    `explanation`   TEXT NULL,
    `change_note`   VARCHAR(255) NULL,
    `created_by`    BIGINT UNSIGNED NULL,
    `is_active`     TINYINT(1) NOT NULL DEFAULT 1,
    `created_at`    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_question_version (`question_id`,`version_no`),
    KEY idx_qv_question (`question_id`),
    KEY idx_qv_created_by (`created_by`),
    CONSTRAINT fk_qv_question FOREIGN KEY (`question_id`) REFERENCES `QUESTION`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_qv_creator FOREIGN KEY (`created_by`) REFERENCES `USER`(`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4b. 为 QUESTION.current_version_id 添加外键
ALTER TABLE `QUESTION`
    ADD CONSTRAINT fk_question_current_version
    FOREIGN KEY (`current_version_id`) REFERENCES `QUESTION_VERSION`(`id`)
    ON DELETE SET NULL ON UPDATE CASCADE;

-- 6. 用户角色关联
CREATE TABLE `USER_ROLE` (
    `id`        BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    `user_id`   BIGINT UNSIGNED NOT NULL,
    `role_id`   BIGINT UNSIGNED NOT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_role (`user_id`,`role_id`),
    KEY idx_user_role_role (`role_id`),
    CONSTRAINT fk_user_role_user FOREIGN KEY (`user_id`) REFERENCES `USER`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_user_role_role FOREIGN KEY (`role_id`) REFERENCES `ROLE`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. 试卷题目
CREATE TABLE `PAPER_QUESTION` (
    `id`            BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    `paper_id`      BIGINT UNSIGNED NOT NULL,
    `question_id`   BIGINT UNSIGNED NOT NULL,
    `seq`           INT NOT NULL,
    `section`       VARCHAR(64) NULL,
    `score`         DECIMAL(10,2) NOT NULL DEFAULT 0,
    UNIQUE KEY uk_paper_question (`paper_id`,`question_id`),
    UNIQUE KEY uk_paper_seq (`paper_id`,`seq`),
    KEY idx_pq_question (`question_id`),
    CONSTRAINT fk_pq_paper FOREIGN KEY (`paper_id`) REFERENCES `PAPER`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_pq_question FOREIGN KEY (`question_id`) REFERENCES `QUESTION`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 8. 考试尝试
CREATE TABLE `EXAM_ATTEMPT` (
    `id`                 BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    `user_id`            BIGINT UNSIGNED NOT NULL,
    `paper_id`           BIGINT UNSIGNED NOT NULL,
    `attempt_index`      INT NOT NULL DEFAULT 1,
    `start_time`         DATETIME NOT NULL,
    `submit_time`        DATETIME NULL,
    `total_score`        DECIMAL(10,2) NULL,
    `calculated_accuracy` DECIMAL(6,4) NULL,
    `status`             VARCHAR(32) NOT NULL DEFAULT 'IN_PROGRESS',
    `duration_seconds`   INT NULL,
    `created_at`         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_attempt_user_paper_idx (`user_id`,`paper_id`,`attempt_index`),
    KEY idx_attempt_paper (`paper_id`),
    CONSTRAINT fk_attempt_user FOREIGN KEY (`user_id`) REFERENCES `USER`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_attempt_paper FOREIGN KEY (`paper_id`) REFERENCES `PAPER`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 9. 用户作答
CREATE TABLE `USER_ANSWER` (
    `id`             BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    `attempt_id`     BIGINT UNSIGNED NOT NULL,
    `user_id`        BIGINT UNSIGNED NOT NULL,
    `question_id`    BIGINT UNSIGNED NOT NULL,
    `paper_id`       BIGINT UNSIGNED NULL,
    `user_answer`    VARCHAR(1024) NULL,
    `is_correct`     TINYINT(1) NULL,
    `score_obtained` DECIMAL(10,2) NULL,
    `time_spent_ms`  INT NULL,
    `answer_time`    DATETIME NULL,
    `first_flag`     TINYINT(1) NOT NULL DEFAULT 0,
    UNIQUE KEY uk_answer_attempt_question (`attempt_id`,`question_id`),
    KEY idx_answer_user (`user_id`),
    KEY idx_answer_question (`question_id`),
    KEY idx_answer_paper (`paper_id`),
    CONSTRAINT fk_answer_attempt FOREIGN KEY (`attempt_id`) REFERENCES `EXAM_ATTEMPT`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_answer_user FOREIGN KEY (`user_id`) REFERENCES `USER`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_answer_question FOREIGN KEY (`question_id`) REFERENCES `QUESTION`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_answer_paper FOREIGN KEY (`paper_id`) REFERENCES `PAPER`(`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 10. 知识点
CREATE TABLE `KNOWLEDGE_POINT` (
    `id`            BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    `name`          VARCHAR(255) NOT NULL,
    `parent_id`     BIGINT UNSIGNED NULL,
    `description`   TEXT NULL,
    `level`         INT NULL,
    `created_at`    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    KEY idx_kp_parent (`parent_id`),
    CONSTRAINT fk_kp_parent FOREIGN KEY (`parent_id`) REFERENCES `KNOWLEDGE_POINT`(`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    UNIQUE KEY uk_kp_name_parent (`name`,`parent_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 11. 题目-知识点
CREATE TABLE `QUESTION_KNOWLEDGE` (
    `id`            BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    `question_id`   BIGINT UNSIGNED NOT NULL,
    `knowledge_id`  BIGINT UNSIGNED NOT NULL,
    `weight`        TINYINT NULL,
    UNIQUE KEY uk_question_knowledge (`question_id`,`knowledge_id`),
    KEY idx_qk_knowledge (`knowledge_id`),
    CONSTRAINT fk_qk_question FOREIGN KEY (`question_id`) REFERENCES `QUESTION`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_qk_kp FOREIGN KEY (`knowledge_id`) REFERENCES `KNOWLEDGE_POINT`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 12. 标签
CREATE TABLE `TAG` (
    `id`         BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    `name`       VARCHAR(128) NOT NULL,
    `type`       VARCHAR(64) NULL,
    `parent_id`  BIGINT UNSIGNED NULL,
    `is_active`  TINYINT(1) NOT NULL DEFAULT 1,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    KEY idx_tag_parent (`parent_id`),
    CONSTRAINT fk_tag_parent FOREIGN KEY (`parent_id`) REFERENCES `TAG`(`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    UNIQUE KEY uk_tag_name_parent (`name`,`parent_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 13. 题目-标签
CREATE TABLE `QUESTION_TAG` (
    `id`          BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    `question_id` BIGINT UNSIGNED NOT NULL,
    `tag_id`      BIGINT UNSIGNED NOT NULL,
    UNIQUE KEY uk_question_tag (`question_id`,`tag_id`),
    KEY idx_qt_tag (`tag_id`),
    CONSTRAINT fk_qt_question FOREIGN KEY (`question_id`) REFERENCES `QUESTION`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_qt_tag FOREIGN KEY (`tag_id`) REFERENCES `TAG`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 14. 错题本
CREATE TABLE `ERROR_BOOK` (
    `id`               BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    `user_id`          BIGINT UNSIGNED NOT NULL,
    `question_id`      BIGINT UNSIGNED NOT NULL,
    `first_wrong_time` DATETIME NULL,
    `last_wrong_time`  DATETIME NULL,
    `wrong_count`      INT NOT NULL DEFAULT 0,
    `next_review_time` DATETIME NULL,
    `mastered`         TINYINT(1) NOT NULL DEFAULT 0,
    `updated_at`       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_error_user_question (`user_id`,`question_id`),
    KEY idx_error_question (`question_id`),
    CONSTRAINT fk_error_user FOREIGN KEY (`user_id`) REFERENCES `USER`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_error_question FOREIGN KEY (`question_id`) REFERENCES `QUESTION`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SET FOREIGN_KEY_CHECKS = 1;