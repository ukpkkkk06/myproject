# 📁 SQL 脚本目录

数据库脚本和迁移文件管理

---

## 🏗️ 目录结构

```
sql/
├── README.md                    # 📖 本文档
├── 00_init.sql                 # 🎯 数据库表结构初始化
├── create_database.sql         # 🎯 创建数据库
├── migrations/                 # 🔄 数据库迁移脚本
│   ├── add_knowledge_created_by.sql
│   ├── add_smart_recommendation_indexes.sql
│   ├── fix_null_created_by.sql
│   ├── init_admin_role.sql
│   └── remove_duplicate_indexes.sql
└── seeds/                      # 🌱 测试数据脚本
    ├── seed_practice.sql
    └── seed_question_knowledge.sql
```

---

## 🎯 核心脚本

### 1. create_database.sql
**用途**: 创建数据库  
**执行时机**: 首次部署时  
**命令**:
```bash
mysql -u root -p < sql/create_database.sql
```

### 2. 00_init.sql
**用途**: 初始化所有表结构  
**执行时机**: 数据库创建后  
**命令**:
```bash
mysql -u root -p myexam_db < sql/00_init.sql
```

**包含的表**:
- `ROLE` - 角色表
- `USER` - 用户表
- `PAPER` - 试卷表
- `QUESTION` - 题目表
- `QUESTION_VERSION` - 题目版本表
- `QUESTION_KNOWLEDGE` - 题目知识点关联表
- `KNOWLEDGE_POINT` - 知识点表
- `TAG` - 标签表
- `QUESTION_TAG` - 题目标签关联表
- `USER_ROLE` - 用户角色关联表
- `ERROR_BOOK` - 错题本表
- `USER_ANSWER` - 用户答题记录表
- `EXAM_ATTEMPT` - 考试记录表
- `PAPER_QUESTION` - 试卷题目关联表

---

## 🔄 迁移脚本 (migrations/)

这些脚本用于对现有数据库进行结构或数据修改，**大部分已执行**。

### 📋 迁移历史

| 文件名 | 日期 | 用途 | 状态 |
|--------|------|------|------|
| `add_knowledge_created_by.sql` | 2025-10-21 | 为知识点表添加 created_by 字段 | ✅ 已执行 |
| `add_smart_recommendation_indexes.sql` | 2025-10-21 | 添加智能推荐功能索引 | ✅ 已执行 |
| `fix_null_created_by.sql` | 2025-10-21 | 修复历史数据中的 NULL 创建者 | ✅ 已执行 |
| `init_admin_role.sql` | 2025-10-21 | 初始化角色和管理员权限 | ✅ 已执行 |
| `remove_duplicate_indexes.sql` | 2025-10-21 | 删除重复的数据库索引 | ✅ 已执行 |

### 🚨 注意事项

- ⚠️ **已执行的迁移脚本不要重复执行**
- 📝 这些文件保留用于：
  - 记录数据库变更历史
  - 新环境初始化时参考
  - 问题排查时回溯
- 🔍 执行前请先查看脚本内容和注释

### 执行示例

```bash
# 查看脚本内容
cat sql/migrations/add_knowledge_created_by.sql

# 执行特定迁移（确认未执行过）
mysql -u root -p myexam_db < sql/migrations/add_knowledge_created_by.sql
```

---

## 🌱 测试数据 (seeds/)

用于开发和测试环境的示例数据。

### 1. seed_practice.sql
**用途**: 插入 5 道简单的练习题  
**内容**:
- 题1: 1+1=?
- 题2: 2+2=?
- 题3: 3+1=?
- 题4: 5-2=?
- 题5: 6-2=?

**执行**:
```bash
mysql -u root -p myexam_db < sql/seeds/seed_practice.sql
```

### 2. seed_question_knowledge.sql
**用途**: 为题目关联知识点，支持智能推荐  
**内容**:
- 为题目关联"数学"、"四则运算"等知识点
- 设置权重（100=主要考点，60=宽泛相关）

**执行**:
```bash
mysql -u root -p myexam_db < sql/seeds/seed_question_knowledge.sql
```

### 🚨 注意事项

- ⚠️ **仅用于开发/测试环境**
- 🚫 **生产环境禁止执行**
- 🔄 某些脚本包含 `TRUNCATE` 操作，会清空现有数据

---

## 🚀 快速开始指南

### 全新环境初始化

```bash
# 1. 创建数据库
mysql -u root -p < sql/create_database.sql

# 2. 初始化表结构
mysql -u root -p myexam_db < sql/00_init.sql

# 3. 初始化角色（可选）
mysql -u root -p myexam_db < sql/migrations/init_admin_role.sql

# 4. 添加测试数据（开发环境）
mysql -u root -p myexam_db < sql/seeds/seed_practice.sql
mysql -u root -p myexam_db < sql/seeds/seed_question_knowledge.sql
```

### 使用 Alembic 迁移（推荐）

```bash
# 使用 Alembic 管理数据库版本
alembic upgrade head
```

---

## 📊 数据库结构概览

### 核心实体关系

```
USER (用户)
  ├─ USER_ROLE → ROLE (角色)
  ├─ QUESTION (创建的题目)
  ├─ KNOWLEDGE_POINT (创建的知识点)
  ├─ ERROR_BOOK (错题记录)
  └─ USER_ANSWER (答题记录)

QUESTION (题目)
  ├─ QUESTION_VERSION (版本历史)
  ├─ QUESTION_KNOWLEDGE → KNOWLEDGE_POINT
  ├─ QUESTION_TAG → TAG
  └─ PAPER_QUESTION → PAPER

KNOWLEDGE_POINT (知识点)
  ├─ parent_id → KNOWLEDGE_POINT (自关联)
  └─ QUESTION_KNOWLEDGE → QUESTION
```

---

## 🔍 常用查询

### 查看数据库表
```sql
SHOW TABLES;
```

### 查看表结构
```sql
DESC QUESTION;
DESC USER;
```

### 查看索引
```sql
SHOW INDEX FROM QUESTION_KNOWLEDGE;
```

### 查看用户角色
```sql
SELECT u.account, u.nickname, GROUP_CONCAT(r.code) AS roles
FROM USER u
LEFT JOIN USER_ROLE ur ON ur.user_id = u.id
LEFT JOIN ROLE r ON r.id = ur.role_id
GROUP BY u.id;
```

### 查看题目知识点关联
```sql
SELECT q.id, qv.stem, kp.name AS knowledge, qk.weight
FROM QUESTION q
JOIN QUESTION_VERSION qv ON q.current_version_id = qv.id
JOIN QUESTION_KNOWLEDGE qk ON qk.question_id = q.id
JOIN KNOWLEDGE_POINT kp ON kp.id = qk.knowledge_id
LIMIT 10;
```

---

## 🛠️ 维护建议

### 新增迁移脚本规范

当需要修改数据库结构时：

1. **优先使用 Alembic**:
   ```bash
   alembic revision --autogenerate -m "描述"
   ```

2. **手动 SQL 脚本命名规范**:
   ```
   YYYYMMDD_description.sql
   
   示例:
   - 20251021_add_user_avatar.sql
   - 20251022_create_comment_table.sql
   ```

3. **脚本内容要求**:
   - 包含日期和用途注释
   - 使用 `USE myexam_db;`
   - 执行前检查（`IF NOT EXISTS`）
   - 包含回滚说明（可选）

4. **执行后记录**:
   - 更新 `migrations/README.md` 中的迁移历史表
   - 标注执行状态和日期

### 测试数据管理

- 定期更新 seeds/ 中的测试数据
- 保持与实际业务场景一致
- 避免硬编码用户 ID

---

## 📝 相关文档

- [数据库设计文档](../docs/guides/)
- [Alembic 迁移记录](../alembic/versions/)
- [项目主 README](../README.md)

---

**最后更新**: 2025-10-21
