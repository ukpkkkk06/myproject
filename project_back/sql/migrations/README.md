# 🔄 数据库迁移脚本

历史数据库变更记录

---

## 📋 迁移历史

### 2025-10-21

#### 0. 20251021_sync_with_production_schema.sql
- **日期**: 2025-10-21
- **用途**: 同步生产环境数据库结构到 `00_init.sql`
- **来源**: 从 DBeaver 导出的实际生产环境 DDL
- **状态**: ✅ 已完成（文档记录）
- **主要变更**:
  - USER 表: `status` 字段长度调整, 新增 `last_login_at` 和 `password_hash`
  - KNOWLEDGE_POINT 表: 新增 `created_by` 字段
  - 多个表的索引规范化和性能优化
  - 新增 `alembic_version` 表
- **注意**: 本文件用于记录变更历史，实际变更已通过其他迁移脚本完成

#### 1. add_knowledge_created_by.sql
- **日期**: 2025-10-21
- **用途**: 为 `KNOWLEDGE_POINT` 表添加 `created_by` 字段
- **原因**: 实现知识点的权限隔离，支持多用户数据隔离
- **状态**: ✅ 已执行
- **影响**:
  - 添加 `created_by` 字段（BIGINT UNSIGNED NULL）
  - 添加索引 `idx_kp_created_by`
  - 支持外键约束（可选）

#### 2. add_smart_recommendation_indexes.sql
- **日期**: 2025-10-21
- **用途**: 添加智能推荐功能的性能优化索引
- **状态**: ✅ 已执行
- **影响的表**:
  - `ERROR_BOOK`: 
    - `idx_error_book_user_mastered` (user_id, mastered)
    - `idx_error_book_last_wrong` (user_id, last_wrong_time)
  - `QUESTION_KNOWLEDGE`:
    - `idx_question_knowledge_knowledge` (knowledge_id)
    - `idx_question_knowledge_question` (question_id)
  - `QUESTION`:
    - `idx_question_active_difficulty` (is_active, difficulty)
    - `idx_question_active_type` (is_active, type)
  - `KNOWLEDGE_POINT`:
    - `idx_knowledge_point_parent` (parent_id)
    - `idx_knowledge_point_level` (level)
  - `QUESTION_TAG`:
    - `idx_question_tag_tag` (tag_id)

#### 3. fix_null_created_by.sql
- **日期**: 2025-10-21
- **用途**: 修复 `QUESTION_VERSION` 表中 `created_by` 为 NULL 的历史数据
- **原因**: 导入题目时未设置创建者，导致权限检查失败
- **状态**: ✅ 已执行
- **操作**:
  - 将所有 `created_by IS NULL` 的记录设置为管理员（user_id=1）
  - 修复了题目 69 和 76 无法访问的问题

#### 4. init_admin_role.sql
- **日期**: 2025-10-21
- **用途**: 初始化角色表和管理员权限
- **状态**: ✅ 已执行
- **内容**:
  - 插入 `ADMIN` 角色（管理员）
  - 插入 `USER` 角色（普通用户）
  - 为用户 ID=1 分配管理员权限
  - 显示当前用户角色分配情况

#### 5. remove_duplicate_indexes.sql
- **日期**: 2025-10-21
- **用途**: 删除重复的数据库索引，优化性能
- **状态**: ✅ 已执行
- **优化内容**:
  - `KNOWLEDGE_POINT` 表:
    - 删除 `idx_kp_parent`（保留 `idx_knowledge_point_parent`）
  - `QUESTION_KNOWLEDGE` 表:
    - 删除 `idx_qk_knowledge`（保留 `idx_question_knowledge_knowledge`）
- **效果**: 减少索引维护开销，提升写入性能

---

## 🚨 重要说明

### ⚠️ 执行注意事项

1. **已执行的脚本不要重复执行**
   - 这些脚本都已在生产/开发数据库中执行
   - 重复执行可能导致错误或数据不一致

2. **新环境初始化**
   - 使用 `../00_init.sql` 进行全新安装
   - 或使用 Alembic 迁移: `alembic upgrade head`

3. **执行前备份**
   ```bash
   # 备份数据库
   mysqldump -u root -p myexam_db > backup_$(date +%Y%m%d).sql
   ```

4. **测试环境先行**
   - 新迁移脚本先在测试环境验证
   - 确认无误后再应用到生产环境

### 📝 保留原因

这些已执行的脚本保留用于：
- 📖 记录数据库变更历史
- 🔍 问题排查和回溯
- 🆕 新环境初始化时参考
- 📚 团队知识共享

---

## 🛠️ 创建新迁移

### 使用 Alembic（推荐）

```bash
# 自动检测模型变化
alembic revision --autogenerate -m "添加用户头像字段"

# 手动创建迁移
alembic revision -m "创建评论表"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

### 手动 SQL 脚本

如果必须使用手动 SQL：

1. **命名规范**:
   ```
   YYYYMMDD_description.sql
   ```

2. **脚本模板**:
   ```sql
   -- ====================================================================
   -- 迁移说明
   -- 日期: YYYY-MM-DD
   -- 用途: 描述这个迁移的目的
   -- 影响: 说明会影响哪些表
   -- ====================================================================
   
   USE myexam_db;
   
   -- 执行前检查
   -- （确保幂等性，可重复执行不会出错）
   
   -- 主要变更
   ALTER TABLE xxx ADD COLUMN yyy ...;
   
   -- 验证结果
   DESC xxx;
   
   -- 回滚方案（可选）
   -- ALTER TABLE xxx DROP COLUMN yyy;
   ```

3. **执行**:
   ```bash
   mysql -u root -p myexam_db < sql/migrations/20251021_new_migration.sql
   ```

4. **记录**:
   - 更新本 README 的迁移历史表
   - 标注执行状态和日期

---

## 🔄 迁移最佳实践

### 1. 向后兼容
- 避免直接删除字段，先标记为废弃
- 新增字段使用默认值或允许 NULL
- 重命名时保留旧字段一段时间

### 2. 数据迁移
- 大数据量使用批量处理
- 考虑执行时间和锁表影响
- 准备回滚方案

### 3. 索引管理
- 大表添加索引在低峰时段执行
- 先删除后添加，避免临时索引冗余
- 监控索引使用情况

### 4. 测试验证
```sql
-- 验证表结构
DESC table_name;

-- 验证索引
SHOW INDEX FROM table_name;

-- 验证数据
SELECT * FROM table_name LIMIT 5;

-- 验证外键
SELECT * FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
WHERE TABLE_SCHEMA = 'myexam_db' AND TABLE_NAME = 'table_name';
```

---

## 📊 迁移状态查询

### 查看 Alembic 版本
```bash
alembic current
alembic history
```

### 查看表结构变更
```sql
-- 查看最近修改的表
SELECT TABLE_NAME, UPDATE_TIME 
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'myexam_db' 
ORDER BY UPDATE_TIME DESC 
LIMIT 10;

-- 查看表的创建语句
SHOW CREATE TABLE table_name;
```

---

## 📚 相关文档

- [SQL 脚本主文档](../README.md)
- [Alembic 迁移版本](../../alembic/versions/)
- [数据库设计文档](../../docs/guides/)

---

**最后更新**: 2025-10-21
