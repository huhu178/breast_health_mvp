from flask import Blueprint, request

from config import Config
from services.ai_tongue_platform_client import ai_tongue_platform_client
from utils.response import Response


ai_tongue_platform_bp = Blueprint(
    "ai_tongue_platform",
    __name__,
    url_prefix="/api/miniprogram/ai-tongue",
)


def _require_miniprogram_token() -> bool:
    """
    ISDoc
    @description 如果配置了 MINIPROGRAM_API_TOKEN，则要求请求携带 X-Miniprogram-Token
    """
    expected = (getattr(Config, "MINIPROGRAM_API_TOKEN", "") or "").strip()
    if not expected:
        return True
    got = (request.headers.get("X-Miniprogram-Token") or "").strip()
    return got == expected


@ai_tongue_platform_bp.route("/token/status", methods=["GET"])
def token_status():
    """
    ISDoc
    @description 获取开放平台 access_token 状态（不返回 token 本体）
    @response 200 { enabled: boolean, expires_in: number }
    """
    if not _require_miniprogram_token():
        return Response.error("未授权", 401)

    devid = (getattr(Config, "AI_TONGUE_DEVID", "") or "").strip()
    devsecret = (getattr(Config, "AI_TONGUE_DEVSECRET", "") or "").strip()
    enabled = bool(devid and devsecret)
    if not enabled:
        return Response.success({"enabled": False, "expires_in": None}, "未配置AI舌诊开放平台鉴权信息")

    _, expires_in, err = ai_tongue_platform_client.get_access_token()
    if err:
        return Response.error(err, 500)
    return Response.success({"enabled": True, "expires_in": expires_in}, "OK")


@ai_tongue_platform_bp.route("/proxy", methods=["POST"])
def proxy_call():
    """
    ISDoc
    @description 后端代调用 AI舌诊开放平台接口（小程序不直接暴露 devsecret）
    @bodyParam method {string} 必填，GET/POST/PUT/DELETE
    @bodyParam path {string} 必填，以 /backend 开头的路径，如 /backend/xxx/yyy
    @bodyParam params {object} 可选，query 参数
    @bodyParam json {object} 可选，JSON 请求体
    @bodyParam form {object} 可选，表单请求体（application/x-www-form-urlencoded）
    """
    if not _require_miniprogram_token():
        return Response.error("未授权", 401)

    data = request.get_json(silent=True) or {}
    method = (data.get("method") or "").strip().upper()
    path = (data.get("path") or "").strip()
    params = data.get("params") if isinstance(data.get("params"), dict) else None
    json_body = data.get("json") if isinstance(data.get("json"), (dict, list)) else None
    form_body = data.get("form") if isinstance(data.get("form"), dict) else None

    if method not in ("GET", "POST", "PUT", "DELETE", "PATCH"):
        return Response.error("method不支持", 400)
    if not path.startswith("/backend/"):
        return Response.error("path必须以 /backend/ 开头", 400)

    base = (getattr(Config, "AI_TONGUE_BASE_URL", "") or "https://www.ai-tongue.com").rstrip("/")
    url = f"{base}{path}"

    payload, status_code, err = ai_tongue_platform_client.request(
        method=method,
        url=url,
        params=params,
        json=json_body,
        data=form_body,
        timeout=30,
    )
    if err:
        # 保留第三方错误 payload，方便你调试对接
        return Response.error({"message": err, "status_code": status_code, "payload": payload}, 502)
    return Response.success({"status_code": status_code, "payload": payload}, "OK")

