#!/usr/bin/env python3
"""
健康检查和心跳报告脚本
用途：
1. Docker HEALTHCHECK 检查服务是否存活
2. 定期向外部监控系统报告状态（可选）
"""
import sys
import time
import json
import os
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

# 配置
HEALTH_URL = os.getenv("HEALTH_CHECK_URL", "http://localhost:8000/api/v1/health")
EXTERNAL_WEBHOOK = os.getenv("HEALTH_WEBHOOK_URL", "")  # 可选：外部监控webhook
TIMEOUT = 5  # 超时时间（秒）

def check_health():
    """
    检查本地健康状态
    返回: (bool, dict) - (是否健康, 响应数据)
    """
    try:
        req = Request(HEALTH_URL, headers={"User-Agent": "HealthCheck/1.0"})
        with urlopen(req, timeout=TIMEOUT) as response:
            data = json.loads(response.read().decode('utf-8'))
            # 新格式：检查status字段是否为healthy
            is_healthy = (response.status == 200 and 
                         data.get("status") == "healthy")
            return is_healthy, data
    except HTTPError as e:
        # 503表示服务运行但不健康
        if e.code == 503:
            try:
                data = json.loads(e.read().decode('utf-8'))
                return False, data
            except:
                return False, {"error": f"HTTP 503", "status": "unhealthy"}
        return False, {"error": f"HTTP {e.code}"}
    except URLError as e:
        return False, {"error": f"URLError: {e.reason}"}
    except Exception as e:
        return False, {"error": f"Exception: {str(e)}"}

def report_to_external(health_data):
    """
    向外部监控系统报告健康状态（可选）
    """
    if not EXTERNAL_WEBHOOK:
        return
    
    try:
        payload = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": "myexam-api",
            "health": health_data
        }
        data = json.dumps(payload).encode('utf-8')
        req = Request(
            EXTERNAL_WEBHOOK, 
            data=data, 
            headers={
                "Content-Type": "application/json",
                "User-Agent": "HealthCheck/1.0"
            },
            method="POST"
        )
        with urlopen(req, timeout=TIMEOUT) as response:
            print(f"✅ 报告已发送到外部监控系统: {response.status}")
    except Exception as e:
        print(f"⚠️ 发送外部报告失败: {e}")

def main():
    """
    主函数：单次健康检查
    用于 Docker HEALTHCHECK
    """
    is_healthy, data = check_health()
    
    if is_healthy:
        print(f"✅ 健康检查通过: {json.dumps(data, ensure_ascii=False)}")
        sys.exit(0)
    else:
        print(f"❌ 健康检查失败: {json.dumps(data, ensure_ascii=False)}")
        sys.exit(1)

def monitor_loop(interval=300):
    """
    监控循环：定期检查并报告
    interval: 间隔时间（秒），默认300秒=5分钟
    """
    print(f"🚀 启动健康监控，检查间隔: {interval}秒")
    print(f"📍 健康检查URL: {HEALTH_URL}")
    if EXTERNAL_WEBHOOK:
        print(f"📡 外部报告URL: {EXTERNAL_WEBHOOK}")
    
    while True:
        try:
            is_healthy, data = check_health()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if is_healthy:
                # 提取检查结果
                checks = data.get('checks', {})
                db_msg = checks.get('database', {}).get('message', '未知')
                sys_msg = checks.get('system', {}).get('message', '未知')
                
                # 提取系统详情（如果有）
                sys_details = checks.get('system', {}).get('details', {})
                cpu = sys_details.get('cpu_percent', '?')
                mem = sys_details.get('memory_percent', '?')
                
                print(f"[{timestamp}] ✅ 服务健康")
                print(f"  └─ {db_msg}")
                print(f"  └─ {sys_msg} (CPU:{cpu}%, 内存:{mem}%)")
                
                # 向外部系统报告
                report_to_external(data)
            else:
                # 提取错误信息
                checks = data.get('checks', {})
                error_msgs = []
                
                for check_name, check_data in checks.items():
                    if check_data.get('status') != 'healthy':
                        error_msgs.append(f"{check_name}: {check_data.get('message', '未知错误')}")
                
                if not error_msgs:
                    error_msgs = [data.get('error', '未知错误')]
                
                print(f"[{timestamp}] ❌ 服务异常")
                for msg in error_msgs:
                    print(f"  └─ {msg}")
                
                # 失败时也报告
                report_to_external(data)
            
            time.sleep(interval)
            
        except KeyboardInterrupt:
            print("\n👋 监控已停止")
            break
        except Exception as e:
            print(f"⚠️ 监控循环错误: {e}")
            time.sleep(interval)

if __name__ == "__main__":
    # 判断运行模式
    if len(sys.argv) > 1 and sys.argv[1] == "monitor":
        # 监控模式：持续运行
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 300
        monitor_loop(interval)
    else:
        # 单次检查模式（用于Docker HEALTHCHECK）
        main()
