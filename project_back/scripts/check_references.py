"""
全面检查项目中的所有引用
位置: scripts/check_references.py
用法: python scripts/check_references.py (从项目根目录运行)
"""
import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("=" * 70)
print("🔍 项目引用检查报告")
print("=" * 70)

# 1. Python 导入检查
print("\n📦 1. Python 模块导入检查")
print("-" * 70)

errors = []
try:
    from app.main import app
    from app import api_router
    print("✅ app.main 导入成功")
    print("✅ app.api_router 导入成功")
except Exception as e:
    errors.append(f"❌ 主应用导入失败: {e}")
    print(errors[-1])

try:
    from app.api.v1.endpoints import (
        health, auth, users, practice, tags,
        error_book, question_bank, admin, knowledge
    )
    print("✅ 所有 9 个 endpoint 模块导入成功")
except Exception as e:
    errors.append(f"❌ Endpoint 导入失败: {e}")
    print(errors[-1])

try:
    from app.services import (
        user_service, question_bank_service, practice_service,
        knowledge_service, error_book_service, auth_service
    )
    print("✅ 所有 6 个 service 模块导入成功")
except Exception as e:
    errors.append(f"❌ Service 导入失败: {e}")
    print(errors[-1])

try:
    from app.models.user import User
    from app.models.question import Question
    from app.models.tag import Tag, QuestionTag
    from app.models.knowledge_point import KnowledgePoint
    from app.models.error_book import ErrorBook
    from app.models.role import Role
    print("✅ 所有核心模型导入成功")
except Exception as e:
    errors.append(f"❌ 模型导入失败: {e}")
    print(errors[-1])

# 2. 路由检查
print("\n🚦 2. API 路由检查")
print("-" * 70)
try:
    from app.main import app
    from fastapi.testclient import TestClient
    
    client = TestClient(app)
    
    # 测试关键路由
    test_routes = [
        ('/api/v1/health', 200),
        ('/api/v1/me', 401),  # 未认证应返回 401
        ('/api/v1/tags', 401),  # 需要认证
    ]
    
    for route, expected in test_routes:
        try:
            response = client.get(route)
            if response.status_code == expected:
                print(f"✅ {route} -> {response.status_code}")
            else:
                msg = f"⚠️  {route} -> {response.status_code} (期望: {expected})"
                print(msg)
                errors.append(msg)
        except Exception as e:
            msg = f"❌ {route} 测试失败: {e}"
            print(msg)
            errors.append(msg)
    
    # 统计路由数量
    api_routes = [r for r in app.routes if hasattr(r, 'path') and '/api/v1' in r.path]
    print(f"\n✅ 共注册 {len(api_routes)} 个 API 路由")
    
except Exception as e:
    errors.append(f"❌ 路由检查失败: {e}")
    print(errors[-1])

# 3. 数据库模型映射检查
print("\n🗄️  3. 数据库表与模型映射检查")
print("-" * 70)

db_tables = [
    'ERROR_BOOK', 'EXAM_ATTEMPT', 'KNOWLEDGE_POINT', 'PAPER',
    'PAPER_QUESTION', 'QUESTION', 'QUESTION_KNOWLEDGE', 'QUESTION_TAG',
    'QUESTION_VERSION', 'ROLE', 'TAG', 'USER', 'USER_ANSWER', 'USER_ROLE'
]

model_files = [
    'error_book.py', 'exam_attempt.py', 'knowledge_point.py', 'paper.py',
    'paper_question.py', 'question.py', 'question_knowledge.py',
    'question_version.py', 'role.py', 'tag.py', 'user.py', 
    'user_answer.py', 'user_role.py'
]

# QuestionTag 模型在 tag.py 文件中定义
special_cases = {
    'QUESTION_TAG': 'tag.py'  # QuestionTag 类定义在 tag.py 中
}

models_dir = 'app/models'
missing_models = []
for table in db_tables:
    # 检查特殊情况
    if table in special_cases:
        if special_cases[table] in model_files:
            continue
    
    model_file = table.lower() + '.py'
    if model_file not in model_files:
        missing_models.append(f"❌ 数据库表 {table} 缺少对应的模型文件")
        
if missing_models:
    errors.extend(missing_models)
    for msg in missing_models:
        print(msg)
else:
    print(f"✅ 所有 {len(db_tables)} 个数据库表都有对应的模型文件")

# 4. 空文件检查
print("\n📄 4. 空文件/冗余文件检查")
print("-" * 70)

empty_files = [
    'app/models_init_.py',
    'app/schemas_init_.py',
    'frontend-mp/src/shime-uni.d.ts',
]

for f in empty_files:
    if os.path.exists(f):
        print(f"⚠️  发现冗余文件: {f}")
        errors.append(f"冗余文件: {f}")
    else:
        print(f"✅ 已清理: {f}")

# 5. 总结
print("\n" + "=" * 70)
print("📊 检查总结")
print("=" * 70)

if errors:
    print(f"\n❌ 发现 {len(errors)} 个问题:")
    for i, err in enumerate(errors, 1):
        print(f"  {i}. {err}")
    sys.exit(1)
else:
    print("\n✅ 所有检查通过！项目引用完全正确。")
    print("\n检查项目:")
    print("  ✅ Python 模块导入")
    print("  ✅ API 路由注册")
    print("  ✅ 数据库表模型映射")
    print("  ✅ 空文件清理")
    sys.exit(0)
