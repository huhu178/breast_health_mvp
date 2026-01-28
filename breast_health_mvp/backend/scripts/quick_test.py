"""
快速测试 API 是否正常运行
"""
import requests
import time
import json

print("⏳ 等待 Flask 服务启动...")
time.sleep(5)

BASE_URL = 'http://localhost:5000'

# 1. 健康检查
print("\n" + "=" * 60)
print("🏥 健康检查")
print("=" * 60)
try:
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"响应状态: {response.status_code}")
    print(f"响应数据: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    if response.status_code == 200:
        print("✅ Flask 服务运行正常")
    else:
        print("❌ 服务异常")
        exit(1)
except Exception as e:
    print(f"❌ 无法连接到服务: {e}")
    exit(1)

# 2. 测试手机号登录
print("\n" + "=" * 60)
print("📱 测试手机号登录/注册")
print("=" * 60)
url = f"{BASE_URL}/api/c/auth/phone"
data = {
    "phone": "13800138001",
    "name": "测试用户A",
    "source_channel": "web",
    "campaign_code": "test_2024",
    "entry_url": "https://example.com/health"
}

try:
    response = requests.post(url, json=data)
    print(f"请求 URL: {url}")
    print(f"响应状态: {response.status_code}")
    result = response.json()
    print(f"响应数据: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    if response.status_code == 200 and result.get('success'):
        print("✅ 手机号登录成功")
        patient_data = result['data']['patient']
        print(f"\n用户信息:")
        print(f"  - 用户编码: {patient_data['patient_code']}")
        print(f"  - 姓名: {patient_data['name']}")
        print(f"  - 手机: {patient_data['phone']}")
        print(f"  - 来源: {patient_data['source_channel']}")
        print(f"  - 线索状态: {patient_data['lead_status']}")
    else:
        print(f"❌ 登录失败: {result.get('message')}")
except Exception as e:
    print(f"❌ 请求失败: {e}")
    import traceback
    traceback.print_exc()

# 3. 测试微信登录
print("\n" + "=" * 60)
print("💬 测试微信登录/注册")
print("=" * 60)
url = f"{BASE_URL}/api/c/auth/wechat"
data = {
    "wechat_openid": "oTEST_" + str(int(time.time())),
    "wechat_unionid": "uTEST_" + str(int(time.time())),
    "nickname": "微信测试用户B",
    "source_channel": "wechat"
}

try:
    response = requests.post(url, json=data)
    print(f"请求 URL: {url}")
    print(f"响应状态: {response.status_code}")
    result = response.json()
    print(f"响应数据: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    if response.status_code == 200 and result.get('success'):
        print("✅ 微信登录成功")
        patient_data = result['data']['patient']
        print(f"\n用户信息:")
        print(f"  - 用户编码: {patient_data['patient_code']}")
        print(f"  - 姓名: {patient_data['name']}")
        print(f"  - 来源: {patient_data['source_channel']}")
        print(f"  - 需要补充手机号: {result['data']['need_phone']}")
    else:
        print(f"❌ 登录失败: {result.get('message')}")
except Exception as e:
    print(f"❌ 请求失败: {e}")

print("\n" + "=" * 60)
print("✅ 测试完成")
print("=" * 60)

