# 🌱 测试数据脚本

用于开发和测试环境的示例数据

---

## 📋 脚本列表

### 1. seed_practice.sql
**用途**: 插入基础练习题，用于测试练习功能

**包含内容**:
- 5 道简单的数学题（单选题）
- 题目难度: 1（简单）
- 题目类型: SC（单选）
- 状态: 已审核通过，已激活

**题目列表**:
| 题号 | 题干 | 选项 | 答案 |
|------|------|------|------|
| 1 | 1+1=？ | A.1, B.2, C.3, D.4 | B |
| 2 | 2+2=？ | A.2, B.3, C.4, D.5 | C |
| 3 | 3+1=？ | A.3, B.4, C.5, D.6 | B |
| 4 | 5-2=？ | A.2, B.3, C.4, D.5 | B |
| 5 | 6-2=？ | A.3, B.4, C.5, D.6 | B |

**执行**:
```bash
mysql -u root -p myexam_db < sql/seeds/seed_practice.sql
```

**特点**:
- 使用事务确保数据一致性
- 自动生成解析内容
- 回填 `QUESTION.current_version_id`

---

### 2. seed_question_knowledge.sql
**用途**: 为题目关联知识点，支持智能推荐功能测试

**包含内容**:
- 题目与知识点的关联关系
- 关联权重设置（100=主要考点，60=宽泛相关）
- 支持层级知识点关联

**权重设计**:
```
weight 字段表示"题目与知识点的关联强度" (0-100):
  100 = 该知识点是题目的主要考点（直接关联）
  60  = 该知识点是宽泛相关的父节点（继承关联）
```

**层级优先原则**:
- 层级越深的知识点，权重越高
- 子节点（更具体）→ weight=100（优先推荐）
- 父节点（更宽泛）→ weight=60（次要推荐）

**示例数据**:
```
题目关联示例:
- 单选题 → "数学"（level=0, weight=100）
- 简单单选题 → "四则运算"（level=1, weight=100）
            → "数学"（level=0, weight=60）
```

**执行**:
```bash
mysql -u root -p myexam_db < sql/seeds/seed_question_knowledge.sql
```

**注意**:
- ⚠️ 包含 `TRUNCATE TABLE QUESTION_KNOWLEDGE`
- 执行前会清空现有的题目知识点关联

---

## 🚀 快速开始

### 初始化开发环境

```bash
# 1. 创建数据库和表结构（如果还没有）
mysql -u root -p < sql/create_database.sql
mysql -u root -p myexam_db < sql/00_init.sql

# 2. 添加练习题
mysql -u root -p myexam_db < sql/seeds/seed_practice.sql

# 3. 关联知识点
mysql -u root -p myexam_db < sql/seeds/seed_question_knowledge.sql

# 4. 初始化角色（可选）
mysql -u root -p myexam_db < sql/migrations/init_admin_role.sql
```

### 验证数据

```bash
# 登录 MySQL
mysql -u root -p myexam_db

# 查看题目
SELECT q.id, qv.stem, q.type, q.difficulty
FROM QUESTION q
JOIN QUESTION_VERSION qv ON q.current_version_id = qv.id
WHERE q.is_active = 1;

# 查看题目知识点关联
SELECT 
    q.id,
    qv.stem,
    kp.name AS knowledge,
    qk.weight
FROM QUESTION q
JOIN QUESTION_VERSION qv ON q.current_version_id = qv.id
JOIN QUESTION_KNOWLEDGE qk ON qk.question_id = q.id
JOIN KNOWLEDGE_POINT kp ON kp.id = qk.knowledge_id
ORDER BY q.id, qk.weight DESC;
```

---

## 🚨 注意事项

### ⚠️ 仅用于开发/测试

- 🚫 **严禁在生产环境执行**
- 📊 这些是示例数据，不代表真实业务
- 🔄 某些脚本包含 `TRUNCATE` 操作

### 🛡️ 安全建议

1. **环境隔离**
   ```bash
   # 检查当前数据库
   SELECT DATABASE();
   
   # 确认不是生产环境
   SELECT @@hostname, @@version;
   ```

2. **数据备份**
   ```bash
   # 执行前备份
   mysqldump -u root -p myexam_db > backup_before_seed.sql
   ```

3. **清理数据**
   ```sql
   -- 清理测试数据
   DELETE FROM QUESTION_KNOWLEDGE WHERE question_id <= 5;
   DELETE FROM QUESTION_VERSION WHERE question_id <= 5;
   DELETE FROM QUESTION WHERE id <= 5;
   ```

---

## 🆕 添加新的测试数据

### 脚本命名规范

```
seed_<category>.sql

示例:
- seed_users.sql          # 测试用户
- seed_tags.sql           # 标签数据
- seed_knowledge.sql      # 知识点树
- seed_comprehensive.sql  # 综合测试题
```

### 脚本模板

```sql
-- ========================================
-- [测试数据名称]
-- ========================================
-- 用途: 描述这个测试数据的用途
-- 创建时间: YYYY-MM-DD
-- ========================================

USE myexam_db;

-- 清理旧数据（可选）
-- TRUNCATE TABLE xxx;

-- 开启事务
START TRANSACTION;

-- 插入数据
INSERT INTO xxx VALUES (...);

-- 验证数据
SELECT COUNT(*) FROM xxx;

-- 提交事务
COMMIT;
```

### 最佳实践

1. **使用事务**
   ```sql
   START TRANSACTION;
   -- 插入操作
   COMMIT;
   ```

2. **幂等性**
   ```sql
   -- 使用 INSERT IGNORE 或 ON DUPLICATE KEY UPDATE
   INSERT IGNORE INTO TAG (name, type) VALUES ('数学', 'SUBJECT');
   ```

3. **关联完整性**
   ```sql
   -- 确保外键引用存在
   INSERT INTO QUESTION_KNOWLEDGE (question_id, knowledge_id, weight)
   SELECT q.id, 1, 100
   FROM QUESTION q
   WHERE q.is_active = 1;
   ```

4. **可读性**
   - 添加注释说明数据来源
   - 使用有意义的测试数据
   - 保持数据的真实性

---

## 📊 测试场景

### 1. 基础功能测试
```bash
# seed_practice.sql
# 测试: 题目显示、答题、评分
```

### 2. 智能推荐测试
```bash
# seed_question_knowledge.sql
# 测试: 错题推荐、知识点推荐、难度自适应
```

### 3. 权限测试
```bash
# 需要配合 init_admin_role.sql
# 测试: 多用户隔离、管理员权限
```

### 4. 性能测试
```bash
# 需要大量数据
# 可以使用循环生成
```

**批量生成示例**:
```sql
-- 生成 1000 道题
DELIMITER $$
CREATE PROCEDURE generate_questions(IN num INT)
BEGIN
    DECLARE i INT DEFAULT 1;
    WHILE i <= num DO
        INSERT INTO QUESTION (type, difficulty, audit_status, is_active)
        VALUES ('SC', FLOOR(1 + RAND() * 5), 'APPROVED', 1);
        
        SET @qid = LAST_INSERT_ID();
        
        INSERT INTO QUESTION_VERSION (
            question_id, version_no, stem, 
            options, correct_answer, is_active
        )
        VALUES (
            @qid, 1, CONCAT('题目 ', i, ' 的题干'), 
            '["A","B","C","D"]', 'A', 1
        );
        
        SET i = i + 1;
    END WHILE;
END$$
DELIMITER ;

-- 调用存储过程
CALL generate_questions(1000);

-- 删除存储过程
DROP PROCEDURE IF EXISTS generate_questions;
```

---

## 🔄 数据重置

### 清理所有测试数据

```sql
-- 禁用外键检查
SET FOREIGN_KEY_CHECKS = 0;

-- 清空相关表
TRUNCATE TABLE QUESTION_KNOWLEDGE;
TRUNCATE TABLE QUESTION_TAG;
TRUNCATE TABLE QUESTION_VERSION;
TRUNCATE TABLE QUESTION;
TRUNCATE TABLE ERROR_BOOK;
TRUNCATE TABLE USER_ANSWER;
TRUNCATE TABLE EXAM_ATTEMPT;
TRUNCATE TABLE PAPER_QUESTION;

-- 启用外键检查
SET FOREIGN_KEY_CHECKS = 1;
```

### 重新导入

```bash
# 重新执行种子数据
mysql -u root -p myexam_db < sql/seeds/seed_practice.sql
mysql -u root -p myexam_db < sql/seeds/seed_question_knowledge.sql
```

---

## 📚 相关文档

- [SQL 脚本主文档](../README.md)
- [数据库迁移记录](../migrations/README.md)
- [智能推荐功能文档](../../docs/guides/智能推荐功能文档.md)

---

## 💡 提示

### 快速查看数据

```bash
# 查看所有题目
mysql -u root -p myexam_db -e "
SELECT q.id, qv.stem, q.type, q.difficulty
FROM QUESTION q
JOIN QUESTION_VERSION qv ON q.current_version_id = qv.id
LIMIT 10;
"

# 查看知识点关联统计
mysql -u root -p myexam_db -e "
SELECT 
    kp.name,
    COUNT(qk.question_id) AS question_count
FROM KNOWLEDGE_POINT kp
LEFT JOIN QUESTION_KNOWLEDGE qk ON qk.knowledge_id = kp.id
GROUP BY kp.id
ORDER BY question_count DESC;
"
```

### 导出测试数据

```bash
# 导出题目数据
mysqldump -u root -p myexam_db QUESTION QUESTION_VERSION \
    --no-create-info --skip-add-locks > backup_questions.sql

# 导出知识点关联
mysqldump -u root -p myexam_db QUESTION_KNOWLEDGE \
    --no-create-info --skip-add-locks > backup_knowledge.sql
```

---

**最后更新**: 2025-10-21
