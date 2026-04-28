"""
测试 C 端 AI 对话 API
"""
import requests
import json
import time

BASE_URL = 'http://localhost:5000'

def test_chat_flow():
    """测试完整的对话流程"""
    print("\n" + "=" * 60)
    print("🤖 测试 C 端 AI 对话流程")
    print("=" * 60)
    
    # 1. 先登录获取患者信息
    print("\n📱 步骤1：用户登录")
    login_url = f"{BASE_URL}/api/c/auth/phone"
    login_data = {
        "phone": "13800138888",
        "name": "对话测试用户",
        "source_channel": "web"
    }
    
    response = requests.post(login_url, json=login_data)
    if response.status_code != 200:
        print(f"❌ 登录失败: {response.text}")
        return
    
    login_result = response.json()
    if not login_result.get('success'):
        print(f"❌ 登录失败: {login_result.get('message')}")
        return
    
    patient_code = login_result['data']['patient']['patient_code']
    print(f"✅ 登录成功，患者编码: {patient_code}")
    
    # 2. 开始对话
    print("\n💬 步骤2：开始AI对话")
    start_chat_url = f"{BASE_URL}/api/c/chat/start"
    start_chat_data = {
        "phone": "13800138888",
        "channel": "web"
    }
    
    response = requests.post(start_chat_url, json=start_chat_data)
    print(f"请求 URL: {start_chat_url}")
    print(f"响应状态: {response.status_code}")
    result = response.json()
    print(f"响应数据: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    if response.status_code != 200 or not result.get('success'):
        print(f"❌ 开始对话失败")
        return
    
    session_id = result['data']['session_id']
    print(f"✅ 对话开始成功，会话ID: {session_id}")
    
    # 3. 发送消息
    print("\n📝 步骤3：发送用户消息")
    send_message_url = f"{BASE_URL}/api/c/chat/message"
    
    messages = [
        "您好，我想咨询一下乳腺结节的问题",
        "我今年35岁，最近检查发现有结节",
        "超声显示结节大小约8mm，BI-RADS 3级"
    ]
    
    for i, msg in enumerate(messages, 1):
        print(f"\n  消息{i}: {msg}")
        send_data = {
            "session_id": session_id,
            "message": msg,
            "channel": "web"
        }
        
        response = requests.post(send_message_url, json=send_data)
        result = response.json()
        
        if response.status_code == 200 and result.get('success'):
            ai_response = result['data']['message']
            print(f"  AI回复: {ai_response}")
        else:
            print(f"  ❌ 发送失败: {result.get('message')}")
        
        time.sleep(0.5)  # 模拟真实对话间隔
    
    # 4. 获取对话历史
    print("\n📜 步骤4：获取对话历史")
    history_url = f"{BASE_URL}/api/c/chat/history/{session_id}"
    
    response = requests.get(history_url)
    print(f"请求 URL: {history_url}")
    print(f"响应状态: {response.status_code}")
    result = response.json()
    
    if response.status_code == 200 and result.get('success'):
        messages = result['data']['messages']
        print(f"✅ 获取成功，共 {len(messages)} 条消息:")
        for msg in messages[:3]:  # 只显示前3条
            print(f"  - [{msg['role']}] {msg['content'][:50]}...")
    else:
        print(f"❌ 获取失败: {result.get('message')}")
    
    # 5. 完成对话
    print("\n✅ 步骤5：完成对话")
    complete_url = f"{BASE_URL}/api/c/chat/complete"
    complete_data = {
        "session_id": session_id,
        "collected_data": {
            "age": 35,
            "nodule_size": "8mm",
            "birads_level": "3"
        }
    }
    
    response = requests.post(complete_url, json=complete_data)
    print(f"请求 URL: {complete_url}")
    print(f"响应状态: {response.status_code}")
    result = response.json()
    print(f"响应数据: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    if response.status_code == 200 and result.get('success'):
        print(f"✅ 对话完成")
        if 'report' in result['data']:
            print(f"  - 报告编码: {result['data']['report'].get('report_code')}")
    else:
        print(f"❌ 完成失败: {result.get('message')}")
    
    print("\n" + "=" * 60)
    print("✅ AI 对话流程测试完成")
    print("=" * 60)


if __name__ == '__main__':
    try:
        test_chat_flow()
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

