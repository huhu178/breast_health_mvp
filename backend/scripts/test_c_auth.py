"""
测试 C 端认证 API
"""
import requests
import json

BASE_URL = 'http://localhost:5000'

def test_phone_auth():
    """测试手机号登录/注册"""
    print("\n" + "=" * 60)
    print("📱 测试手机号登录/注册")
    print("=" * 60)
    
    url = f"{BASE_URL}/api/c/auth/phone"
    data = {
        "phone": "13800138000",
        "name": "测试用户",
        "source_channel": "web",
        "campaign_code": "test_2024",
        "entry_url": "https://example.com/health-check"
    }
    
    response = requests.post(url, json=data)
    print(f"\n请求 URL: {url}")
    print(f"请求数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
    print(f"\n响应状态: {response.status_code}")
    print(f"响应数据: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print("\n✅ 手机号登录/注册成功")
            return result['data']
        else:
            print(f"\n❌ 登录失败: {result.get('message')}")
            return None
    else:
        print(f"\n❌ 请求失败: HTTP {response.status_code}")
        return None


def test_wechat_auth():
    """测试微信登录/注册"""
    print("\n" + "=" * 60)
    print("💬 测试微信登录/注册")
    print("=" * 60)
    
    url = f"{BASE_URL}/api/c/auth/wechat"
    data = {
        "wechat_openid": "oABC123TEST456",
        "wechat_unionid": "uXYZ789TEST012",
        "nickname": "微信测试用户",
        "source_channel": "wechat",
        "campaign_code": "wechat_2024"
    }
    
    response = requests.post(url, json=data)
    print(f"\n请求 URL: {url}")
    print(f"请求数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
    print(f"\n响应状态: {response.status_code}")
    print(f"响应数据: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print("\n✅ 微信登录/注册成功")
            return result['data']
        else:
            print(f"\n❌ 登录失败: {result.get('message')}")
            return None
    else:
        print(f"\n❌ 请求失败: HTTP {response.status_code}")
        return None


def test_bind_phone(patient_code):
    """测试绑定手机号"""
    print("\n" + "=" * 60)
    print("🔗 测试绑定手机号")
    print("=" * 60)
    
    url = f"{BASE_URL}/api/c/auth/bind-phone"
    data = {
        "patient_code": patient_code,
        "phone": "13900139000"
    }
    
    response = requests.post(url, json=data)
    print(f"\n请求 URL: {url}")
    print(f"请求数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
    print(f"\n响应状态: {response.status_code}")
    print(f"响应数据: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print("\n✅ 绑定手机号成功")
            return result['data']
        else:
            print(f"\n❌ 绑定失败: {result.get('message')}")
            return None
    else:
        print(f"\n❌ 请求失败: HTTP {response.status_code}")
        return None


def test_get_profile(patient_code):
    """测试获取用户信息"""
    print("\n" + "=" * 60)
    print("👤 测试获取用户信息")
    print("=" * 60)
    
    url = f"{BASE_URL}/api/c/auth/profile/{patient_code}"
    
    response = requests.get(url)
    print(f"\n请求 URL: {url}")
    print(f"\n响应状态: {response.status_code}")
    print(f"响应数据: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print("\n✅ 获取用户信息成功")
            return result['data']
        else:
            print(f"\n❌ 获取失败: {result.get('message')}")
            return None
    else:
        print(f"\n❌ 请求失败: HTTP {response.status_code}")
        return None


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("🚀 开始测试 C 端认证 API")
    print("=" * 60)
    
    # 1. 测试手机号登录
    phone_result = test_phone_auth()
    
    # 2. 测试微信登录
    wechat_result = test_wechat_auth()
    
    # 3. 测试绑定手机号（使用微信登录的账号）
    if wechat_result and wechat_result.get('patient'):
        patient_code = wechat_result['patient']['patient_code']
        bind_result = test_bind_phone(patient_code)
        
        # 4. 测试获取用户信息
        if bind_result:
            test_get_profile(patient_code)
    
    # 5. 测试获取手机号登录的用户信息
    if phone_result and phone_result.get('patient'):
        patient_code = phone_result['patient']['patient_code']
        test_get_profile(patient_code)
    
    print("\n" + "=" * 60)
    print("✅ 所有测试完成")
    print("=" * 60)


if __name__ == '__main__':
    import time
    print("⏳ 等待 Flask 服务启动...")
    time.sleep(5)
    
    try:
        main()
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

