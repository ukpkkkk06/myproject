"""临时脚本:更新知识点的 level 字段"""
from sqlalchemy import create_engine, text

# 连接数据库
engine = create_engine('mysql+pymysql://root:123456@localhost:3306/myexam_db')
conn = engine.connect()

# 更新根节点的 level = 0
result1 = conn.execute(text('UPDATE KNOWLEDGE_POINT SET level = 0 WHERE parent_id IS NULL'))
conn.commit()
print(f'✅ 更新了 {result1.rowcount} 个根节点的 level = 0')

# 更新子节点的 level = parent.level + 1
result2 = conn.execute(text('''
    UPDATE KNOWLEDGE_POINT kp1 
    JOIN KNOWLEDGE_POINT kp2 ON kp1.parent_id = kp2.id 
    SET kp1.level = kp2.level + 1
'''))
conn.commit()
print(f'✅ 更新了 {result2.rowcount} 个子节点的 level')

# 查询并显示结果
result3 = conn.execute(text('SELECT id, name, parent_id, level FROM KNOWLEDGE_POINT ORDER BY id'))
rows = result3.fetchall()

print('\n📊 当前知识点列表:')
print('-' * 60)
for row in rows:
    parent_str = str(row[2]) if row[2] else 'NULL'
    print(f'ID: {row[0]:2d} | 名称: {row[1]:8s} | 父ID: {parent_str:4s} | Level: {row[3]}')
print('-' * 60)

conn.close()
print('\n✅ 数据库更新完成!')
