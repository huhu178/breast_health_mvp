"""
数据规范化工具
用于B端和小程序的数据处理，确保字段处理逻辑一致
"""
from datetime import datetime, date


def clean_empty_string(value):
    """将空字符串转换为None，避免数据库类型转换错误"""
    if value == '' or value == ' ' or (isinstance(value, str) and value.strip() == ''):
        return None
    return value


def clean_numeric_value(value, value_type='float'):
    """清理数值类型字段：空字符串转为None，字符串数字转为数值"""
    if value is None or value == '' or value == ' ':
        return None
    if value_type == 'float':
        try:
            return float(value) if value else None
        except (ValueError, TypeError):
            return None
    elif value_type == 'int':
        try:
            return int(value) if value else None
        except (ValueError, TypeError):
            return None
    return value


def list_to_string(value):
    """处理列表类型字段（多选框）：将列表转换为逗号分隔的字符串"""
    if isinstance(value, list):
        return ','.join(value) if value else None
    return clean_empty_string(value)


def pick_first(data, *keys):
    """
    从多个候选字段名中按顺序取第一个非空值
    
    Args:
        data: 数据字典
        *keys: 字段名列表
    
    Returns:
        第一个非空（非空字符串）的值，否则返回 None
    """
    for k in keys:
        v = data.get(k) if isinstance(data, dict) else None
        if v is None:
            continue
        if isinstance(v, str) and v.strip() == '':
            continue
        return v
    return None


def parse_date(date_str):
    """
    ISDoc
    @description 解析日期为 date 对象
    
    - 支持 YYYY-MM-DD 字符串
    - 支持 datetime
    - 支持 date（原样返回）
    """
    if not date_str:
        return None
    try:
        if isinstance(date_str, str):
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        elif isinstance(date_str, datetime):
            return date_str.date()
        elif isinstance(date_str, date):
            return date_str
    except (ValueError, TypeError, AttributeError):
        return None
    return None

