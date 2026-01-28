"""
ID生成工具
统一管理患者编号、档案编号、报告编号的生成
"""
import random
import string
from datetime import datetime


def generate_patient_code():
    """
    生成患者编号：PT20251126150102ABCD

    格式：PT + 时间戳(14位) + 随机字符(4位)
    示例：PT20251126150102A3F9
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f'PT{timestamp}{random_str}'


def generate_record_code():
    """
    生成档案编号：RC20251126150102ABCD

    格式：RC + 时间戳(14位) + 随机字符(4位)
    示例：RC20251126150102B7K2
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f'RC{timestamp}{random_str}'


def generate_report_code():
    """
    生成报告编号：RP20251126150102ABCD

    格式：RP + 时间戳(14位) + 随机字符(4位)
    示例：RP20251126150102C9M5
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f'RP{timestamp}{random_str}'


def generate_conversation_code():
    """
    生成对话编号：CV20251126150102ABCD

    格式：CV + 时间戳(14位) + 随机字符(4位)
    示例：CV20251126150102D2N8
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f'CV{timestamp}{random_str}'


# 测试代码
if __name__ == '__main__':
    print("ID生成工具测试")
    print("="*60)
    print(f"患者编号: {generate_patient_code()}")
    print(f"档案编号: {generate_record_code()}")
    print(f"报告编号: {generate_report_code()}")
    print(f"对话编号: {generate_conversation_code()}")
    print("="*60)
