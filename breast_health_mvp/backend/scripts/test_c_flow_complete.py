"""
完整C端流程测试：从对话到报告生成
"""
import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_complete_flow():
    print("=" * 60)
    print("🧪 C端完整流程测试")
    print("=" * 60)
    
    # 1. 开始对话
    print("\n📍 步骤 1: 开始对话")
    response = requests.post(f"{BASE_URL}/api/c/chat/start", json={})
    print(f"   状态码: {response.status_code}")
    data = response.json()
    print(f"   响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    if data['code'] != 0:  # code: 0 表示成功
        print("❌ 开始对话失败")
        return
    
    session_id = data['data']['session_id']
    print(f"✅ 会话ID: {session_id}")
    
    # 2. 模拟用户回答问题
    print("\n📍 步骤 2: 模拟用户回答")
    
    collected_data = {
        "age": 46,
        "birads_level": "2",
        "nodule_size": "<=5mm",
        "symptoms": ["疼痛", "乳头溢液"],
        "pain_type": "周期性疼痛",
        "family_history": "二级亲属",
        "rhythm_type": "规律月经",
        "cycle_phase": "排卵期",
        "exam_history_type": ["超声检查"],
        "sleep_quality": "一般",
        "main_concern": "担心是恶性的"
    }
    
    # 发送每个回答
    for key, value in collected_data.items():
        print(f"\n   问题: {key}")
        print(f"   回答: {value}")
        
        response = requests.post(f"{BASE_URL}/api/c/chat/message", json={
            "session_id": session_id,
            "message": str(value),
            "intent": key
        })
        
        if response.status_code == 200:
            print(f"   ✅ 消息发送成功")
        else:
            print(f"   ❌ 消息发送失败: {response.text}")
        
        time.sleep(0.5)
    
    # 3. 完成对话并生成报告
    print("\n📍 步骤 3: 完成对话并生成报告")
    response = requests.post(f"{BASE_URL}/api/c/chat/complete", json={
        "session_id": session_id,
        "collected_data": collected_data
    })
    
    print(f"   状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
        
        if data['code'] == 0:  # code: 0 表示成功
            report_info = data['data']
            print(f"\n✅ 报告生成成功！")
            print(f"   报告编号: {report_info.get('report_code')}")
            print(f"   下载令牌: {report_info.get('download_token')}")
            print(f"   风险等级: {report_info.get('risk_level')}")
        else:
            print(f"❌ 报告生成失败: {data['message']}")
    else:
        print(f"❌ 请求失败: {response.text}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == '__main__':
    try:
        test_complete_flow()
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()

