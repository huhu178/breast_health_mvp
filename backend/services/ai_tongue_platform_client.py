import time
from typing import Any, Dict, Optional, Tuple

import requests

from config import Config


class AITonguePlatformClient:
    """
    ISDoc
    @description AI舌诊开放平台客户端（企业应用），负责获取/缓存 access_token 并发起鉴权请求
    """

    def __init__(self) -> None:
        self._session = requests.Session()
        self._cached_token: Optional[str] = None
        self._cached_expire_at: float = 0.0

    def _token_endpoint(self) -> str:
        base = (getattr(Config, "AI_TONGUE_BASE_URL", "") or "").rstrip("/")
        return f"{base}/backend/auth/invoker/pwd/signin"

    def _ensure_configured(self) -> Tuple[bool, str]:
        devid = (getattr(Config, "AI_TONGUE_DEVID", "") or "").strip()
        devsecret = (getattr(Config, "AI_TONGUE_DEVSECRET", "") or "").strip()
        if not devid or not devsecret:
            return False, "AI_TONGUE_DEVID / AI_TONGUE_DEVSECRET 未配置（请在 .env 中设置）"
        return True, ""

    def get_access_token(self, force_refresh: bool = False) -> Tuple[Optional[str], Optional[int], Optional[str]]:
        """
        ISDoc
        @description 获取 access_token（带内存缓存）；返回 (token, expires_in, error_message)
        """
        ok, err = self._ensure_configured()
        if not ok:
            return None, None, err

        now = time.time()
        # 预留 60s 安全窗口，避免刚拿到就过期
        if (not force_refresh) and self._cached_token and now < (self._cached_expire_at - 60):
            expires_in = max(0, int(self._cached_expire_at - now))
            return self._cached_token, expires_in, None

        devid = (getattr(Config, "AI_TONGUE_DEVID", "") or "").strip()
        devsecret = (getattr(Config, "AI_TONGUE_DEVSECRET", "") or "").strip()

        try:
            resp = self._session.post(
                self._token_endpoint(),
                data={"devid": devid, "devsecret": devsecret},
                timeout=15,
            )
        except Exception as e:
            return None, None, f"获取access_token请求失败: {str(e)}"

        try:
            payload = resp.json()
        except Exception:
            return None, None, f"获取access_token响应非JSON（HTTP {resp.status_code}）"

        if resp.status_code != 200:
            return None, None, f"获取access_token失败（HTTP {resp.status_code}）: {payload}"

        if payload.get("code") != 0:
            return None, None, f"获取access_token失败: {payload.get('msg') or payload}"

        data = payload.get("data") or {}
        token = (data.get("access_token") or "").strip()
        expires_in = int(data.get("expires_in") or 0)
        if not token:
            return None, None, f"获取access_token失败: access_token为空: {payload}"

        self._cached_token = token
        self._cached_expire_at = now + (expires_in if expires_in > 0 else 0)
        return token, expires_in, None

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json: Any = None,
        data: Any = None,
        timeout: int = 30,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[int], Optional[str]]:
        """
        ISDoc
        @description 以 Bearer access_token 调用开放平台接口；返回 (json, status_code, error_message)
        """
        token, _, err = self.get_access_token()
        if err:
            return None, None, err

        merged_headers = dict(headers or {})
        merged_headers["Authorization"] = f"Bearer {token}"

        try:
            resp = self._session.request(
                method=method.upper(),
                url=url,
                headers=merged_headers,
                params=params,
                json=json,
                data=data,
                timeout=timeout,
            )
        except Exception as e:
            return None, None, f"调用开放平台接口失败: {str(e)}"

        try:
            payload = resp.json()
        except Exception:
            payload = {"raw_text": resp.text}

        if resp.status_code >= 400:
            return payload, resp.status_code, f"开放平台接口HTTP错误: {resp.status_code}"

        return payload, resp.status_code, None


ai_tongue_platform_client = AITonguePlatformClient()

