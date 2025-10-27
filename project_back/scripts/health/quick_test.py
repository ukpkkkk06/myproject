#!/usr/bin/env python3
"""
快速健康检查演示
直接调用健康检查接口，展示返回的状态信息
"""
import sys
from urllib.request import urlopen, Request
import json

API_URL = "http://localhost:8000/api/v1/health"

def main():
    print("🔍 调用健康检查接口...")
    print(f"📍 URL: {API_URL}\n")
    
    try:
        req = Request(API_URL, headers={"User-Agent": "QuickTest/1.0"})
        with urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            # 打印格式化的JSON
            print("📦 响应数据:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            print()
            
            # 解析并显示状态
            print("="*50)
            print("📊 健康状态摘要:")
            print("="*50)
            
            overall_status = data.get('status')
            status_icon = "✅" if overall_status == "healthy" else "❌"
            print(f"\n{status_icon} 总体状态: {overall_status.upper()}\n")
            
            checks = data.get('checks', {})
            for check_name, check_data in checks.items():
                status = check_data.get('status')
                message = check_data.get('message')
                icon = "✅" if status == "healthy" else "❌" if status == "unhealthy" else "⚠️"
                
                print(f"{icon} {check_name.upper()}:")
                print(f"   状态: {status}")
                print(f"   消息: {message}")
                
                if 'details' in check_data:
                    print(f"   详情: {check_data['details']}")
                print()
            
            print("="*50)
            
            if overall_status == "healthy":
                print("\n✅ 服务运行正常，可以接受流量")
                sys.exit(0)
            else:
                print("\n❌ 服务异常，请检查日志")
                sys.exit(1)
                
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        print("\n提示：")
        print("1. 确保后端服务正在运行")
        print("2. 检查URL是否正确")
        print("3. 如果使用Docker，确保端口映射正确")
        sys.exit(1)

if __name__ == "__main__":
    main()
