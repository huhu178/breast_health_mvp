"""
统一响应格式工具类
"""
from flask import jsonify

class Response:
    """统一的响应格式"""
    
    @staticmethod
    def success(data=None, message='操作成功', status_code=200):
        """成功响应"""
        response = {
            'success': True,
            'code': 0,
            'message': message,
            'data': data
        }
        return jsonify(response), status_code
    
    @staticmethod
    def error(message='操作失败', code=1, status_code=400):
        """
        错误响应

        兼容历史调用方式：
        - 旧代码里大量使用 Response.error(msg, 404/500) 期望第二个参数是 HTTP 状态码，
          但本函数原签名里第二个参数是 code，导致实际 HTTP 状态码仍为默认 400。
        - 这里做兼容：当第二个参数是 >=100 的整数且未显式传 status_code 时，
          认为它是 HTTP 状态码，并同步写入响应体 code 字段。
        """
        # 兼容旧调用：Response.error("xxx", 404) -> HTTP 404
        if isinstance(code, int) and code >= 100 and status_code == 400:
            status_code = code
        response = {
            'success': False,
            # 约定：code 优先反映 HTTP 状态码，方便前端直接展示/判断
            'code': status_code if isinstance(status_code, int) else code,
            'message': message,
            'data': None
        }
        return jsonify(response), status_code
    
    @staticmethod
    def paginate(items, total, page, per_page):
        """分页响应"""
        return Response.success({
            'items': items,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        })
