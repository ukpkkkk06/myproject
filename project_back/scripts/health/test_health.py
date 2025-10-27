#!/usr/bin/env python3
"""
健康检查功能测试脚本
用于本地测试健康检查端点和监控功能
"""
import requests
import json
import time
from datetime import datetime

API_BASE = "http://localhost:8000"

def test_ping():
    """测试快速心跳端点"""
    print("\n🔍 测试 /api/v1/ping ...")
    try:
        response = requests.get(f"{API_BASE}/api/v1/ping", timeout=5)
        print(f"✅ 状态码: {response.status_code}")
        print(f"📦 响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False

def test_health():
    """测试完整健康检查端点"""
    print("\n🔍 测试 /api/v1/health ...")
    try:
        response = requests.get(f"{API_BASE}/api/v1/health", timeout=5)
        print(f"✅ HTTP状态码: {response.status_code}")
        data = response.json()
        
        print(f"\n📦 响应数据:")
        print(f"   总体状态: {data.get('status')}")
        print(f"   时间戳: {data.get('timestamp')}")
        print(f"   服务名称: {data.get('service')}")
        
        # 显示各项检查结果
        checks = data.get('checks', {})
        print(f"\n   检查项目:")
        
        for check_name, check_data in checks.items():
            status = check_data.get('status')
            message = check_data.get('message')
            status_icon = "✅" if status == "healthy" else "❌" if status == "unhealthy" else "⚠️"
            print(f"   {status_icon} {check_name}: {message}")
            
            # 显示详细信息（如果有）
            if 'details' in check_data:
                details = check_data['details']
                print(f"      └─ CPU: {details.get('cpu_percent')}%")
                print(f"      └─ 内存: {details.get('memory_percent')}% ({details.get('memory_used_mb')} MB)")
        
        # 判断是否成功
        is_healthy = data.get('status') == 'healthy'
        return response.status_code == 200 and is_healthy
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False

def test_monitor_mode():
    """模拟监控模式（连续检查3次）"""
    print("\n🔍 测试监控模式（每10秒检查一次，共3次）...")
    
    for i in range(3):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[{timestamp}] 第 {i+1}/3 次检查")
        
        try:
            response = requests.get(f"{API_BASE}/api/v1/health", timeout=5)
            data = response.json()
            
            if response.status_code == 200 and data.get('status') == 'healthy':
                checks = data.get('checks', {})
                db_msg = checks.get('database', {}).get('message', '未知')
                sys_data = checks.get('system', {})
                sys_msg = sys_data.get('message', '未知')
                details = sys_data.get('details', {})
                cpu = details.get('cpu_percent', '?')
                mem = details.get('memory_percent', '?')
                
                print(f"✅ 服务健康")
                print(f"  └─ {db_msg}")
                print(f"  └─ {sys_msg} (CPU:{cpu}%, 内存:{mem}%)")
            else:
                print(f"❌ 服务异常 | 状态: {data.get('status')}")
                checks = data.get('checks', {})
                for name, check in checks.items():
                    if check.get('status') != 'healthy':
                        print(f"  └─ {name}: {check.get('message')}")
        except Exception as e:
            print(f"❌ 异常 | {e}")
        
        if i < 2:  # 不是最后一次才等待
            print("⏳ 等待10秒...")
            time.sleep(10)

def main():
    print("🚀 ===== 健康检查功能测试 =====")
    print(f"📍 API地址: {API_BASE}")
    
    # 检查服务是否运行
    print("\n🔌 检查服务是否运行...")
    try:
        requests.get(API_BASE, timeout=2)
        print("✅ 服务正在运行")
    except:
        print("❌ 服务未运行，请先启动服务")
        print("   docker-compose up -d")
        print("   或")
        print("   uvicorn app.main:app --reload")
        return
    
    # 运行测试
    results = []
    results.append(("Ping端点", test_ping()))
    results.append(("健康检查端点", test_health()))
    
    # 询问是否测试监控模式
    print("\n" + "="*50)
    user_input = input("是否测试监控模式？(需要30秒) [y/N]: ").strip().lower()
    if user_input == 'y':
        test_monitor_mode()
    
    # 总结
    print("\n" + "="*50)
    print("📊 测试总结:")
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"   {name}: {status}")
    
    all_passed = all(r[1] for r in results)
    if all_passed:
        print("\n🎉 所有测试通过！健康检查功能正常")
    else:
        print("\n⚠️ 部分测试失败，请检查日志")

if __name__ == "__main__":
    main()
