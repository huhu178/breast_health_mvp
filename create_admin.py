"""
创建管理员账号脚本
"""
import requests
import time

# 等待服务启动
print("等待服务启动...")
time.sleep(3)

# 注册管理员账号
url = "http://localhost:5000/api/auth/register"
data = {
    "username": "admin",
    "password": "123456",
    "real_name": "管理员"
}

try:
    response = requests.post(url, json=data)
    result = response.json()
    
    if result.get('success'):
        print("✅ 管理员账号创建成功！")
        print(f"   用户名: {data['username']}")
        print(f"   密码: {data['password']}")
        print(f"   姓名: {data['real_name']}")
        print("\n🌐 现在可以访问：http://localhost:5000/login")
    else:
        print(f"⚠️ {result.get('message')}")
        if "已存在" in result.get('message', ''):
            print("   账号已存在，可以直接使用")
            print(f"   用户名: {data['username']}")
            print(f"   密码: {data['password']}")
except Exception as e:
    print(f"❌ 错误：{e}")
    print("   请确认服务是否正常运行")

