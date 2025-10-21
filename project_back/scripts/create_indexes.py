"""执行智能推荐索引创建"""
from sqlalchemy import create_engine, text

# 连接数据库
engine = create_engine('mysql+pymysql://root:123456@localhost:3306/myexam_db')

# 读取SQL文件
with open('sql/add_smart_recommendation_indexes.sql', 'r', encoding='utf-8') as f:
    sql_content = f.read()

# 分割SQL语句
statements = []
in_select_block = False
for line in sql_content.split('\n'):
    line = line.strip()
    # 跳过注释和空行
    if not line or line.startswith('--') or line.startswith('/*'):
        continue
    # 检测SELECT语句块的开始
    if line.startswith('SELECT'):
        in_select_block = True
        continue
    # 在SELECT语句块中,跳过直到遇到分号
    if in_select_block:
        if ';' in line:
            in_select_block = False
        continue
    # 跳过USE语句
    if 'USE ' in line:
        continue
    if line:
        statements.append(line)

# 合并语句
full_statements = []
current = ''
for stmt in statements:
    current += ' ' + stmt
    if ';' in current:
        full_statements.append(current.replace(';', '').strip())
        current = ''

# 执行索引创建
with engine.connect() as conn:
    for statement in full_statements:
        if statement and 'INDEX' in statement:
            try:
                conn.execute(text(statement))
                index_name = statement.split('INDEX')[1].split('ON')[0].strip()
                print(f'✅ 创建索引: {index_name}')
            except Exception as e:
                if 'Duplicate' in str(e):
                    index_name = statement.split('INDEX')[1].split('ON')[0].strip()
                    print(f'⚠️  索引已存在: {index_name}')
                else:
                    print(f'❌ 创建失败: {e}')
    conn.commit()

print('\n✅ 索引创建完成！')

# 验证索引
print('\n📊 验证索引列表：')
with engine.connect() as conn2:
    result = conn2.execute(text("""
        SELECT 
            TABLE_NAME,
            INDEX_NAME,
            GROUP_CONCAT(COLUMN_NAME ORDER BY SEQ_IN_INDEX) as COLUMNS
        FROM INFORMATION_SCHEMA.STATISTICS
        WHERE TABLE_SCHEMA = 'myexam_db'
          AND TABLE_NAME IN ('ERROR_BOOK', 'QUESTION_KNOWLEDGE', 'QUESTION', 'KNOWLEDGE_POINT', 'QUESTION_TAG')
          AND INDEX_NAME LIKE 'idx_%'
        GROUP BY TABLE_NAME, INDEX_NAME
        ORDER BY TABLE_NAME, INDEX_NAME
    """))

    for row in result:
        print(f'  {row[0]}.{row[1]} ({row[2]})')
