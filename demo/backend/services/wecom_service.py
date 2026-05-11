"""
企业微信服务封装

职责：
- 管理应用 access_token
- 发送企业微信应用消息
- 在配置缺失或患者未绑定接收人时返回 dry_run，保留完整消息记录

患者侧真实触达需要先完成企微客户联系绑定，拿到 external_userid 或可投递的 userid。
当前项目只有 patient.wechat_id 字段，不能等同于企业微信 external_userid。
"""
from __future__ import annotations

import os
import time
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

import requests
from flask import current_app


class WeComService:
    API_BASE = 'https://qyapi.weixin.qq.com/cgi-bin'

    def __init__(self):
        self._access_token: Optional[str] = None
        self._access_token_expire_at = 0.0
        self.session = requests.Session()

    def _config(self) -> Dict[str, Any]:
        return {
            'corp_id': current_app.config.get('WECOM_CORP_ID', ''),
            'agent_id': current_app.config.get('WECOM_AGENT_ID', ''),
            'agent_secret': current_app.config.get('WECOM_AGENT_SECRET', ''),
            'dry_run': bool(current_app.config.get('WECOM_DRY_RUN', True)),
        }

    def is_configured(self) -> bool:
        cfg = self._config()
        return bool(cfg['corp_id'] and cfg['agent_id'] and cfg['agent_secret'])

    def get_access_token(self) -> str:
        cfg = self._config()
        if not self.is_configured():
            raise RuntimeError('企业微信配置不完整：请配置 WECOM_CORP_ID/WECOM_AGENT_ID/WECOM_AGENT_SECRET')

        now = time.time()
        if self._access_token and now < self._access_token_expire_at - 120:
            return self._access_token

        resp = self.session.get(
            f'{self.API_BASE}/gettoken',
            params={'corpid': cfg['corp_id'], 'corpsecret': cfg['agent_secret']},
            timeout=10,
        )
        data = resp.json()
        if data.get('errcode') != 0:
            raise RuntimeError(f"获取企业微信 access_token 失败：{data}")
        self._access_token = data['access_token']
        self._access_token_expire_at = now + int(data.get('expires_in', 7200))
        return self._access_token

    def send_text(self, recipient: str, content: str, *, safe: int = 0) -> Dict[str, Any]:
        """
        发送企业微信应用文本消息。

        recipient 在真实环境中应为成员 userid。若要触达外部联系人，需要在客户联系场景
        使用 external_userid 对应接口扩展，这里先把投递边界显式隔离。
        """
        cfg = self._config()
        if not recipient:
            return {
                'ok': False,
                'dry_run': True,
                'status': 'dry_run',
                'reason': 'missing_recipient',
                'message': '患者尚未绑定企业微信接收人，已仅保存随访消息记录'
            }
        if cfg['dry_run'] or not self.is_configured():
            return {
                'ok': True,
                'dry_run': True,
                'status': 'dry_run',
                'recipient': recipient,
                'payload': {'touser': recipient, 'msgtype': 'text', 'text': {'content': content}}
            }

        token = self.get_access_token()
        payload = {
            'touser': recipient,
            'msgtype': 'text',
            'agentid': int(cfg['agent_id']),
            'text': {'content': content},
            'safe': safe,
            'enable_duplicate_check': 1,
            'duplicate_check_interval': 1800,
        }
        resp = self.session.post(
            f'{self.API_BASE}/message/send',
            params={'access_token': token},
            json=payload,
            timeout=10,
        )
        data = resp.json()
        ok = data.get('errcode') == 0
        return {
            'ok': ok,
            'dry_run': False,
            'status': 'sent' if ok else 'failed',
            'payload': payload,
            'response': data,
            'provider_message_id': data.get('msgid') or data.get('invaliduser')
        }

    def download_media(self, media_id: str, *, subdir: str = 'uploads/followup/wecom') -> Dict[str, Any]:
        """
        下载企业微信临时素材到本地。

        dry_run 或配置不完整时不会请求企微，只返回可追踪的待下载状态。
        """
        media_id = (media_id or '').strip()
        if not media_id:
            return {'ok': False, 'status': 'missing_media_id', 'reason': 'media_id 为空'}

        cfg = self._config()
        if cfg['dry_run'] or not self.is_configured():
            return {
                'ok': False,
                'dry_run': True,
                'status': 'pending_download',
                'reason': '企业微信配置未启用，已记录 media_id，暂不下载素材',
                'media_id': media_id,
            }

        token = self.get_access_token()
        resp = self.session.get(
            f'{self.API_BASE}/media/get',
            params={'access_token': token, 'media_id': media_id},
            timeout=20,
            stream=True,
        )
        content_type = (resp.headers.get('Content-Type') or '').lower()
        if 'application/json' in content_type or 'text/plain' in content_type:
            data = resp.json()
            return {
                'ok': False,
                'dry_run': False,
                'status': 'failed',
                'media_id': media_id,
                'response': data,
                'reason': data.get('errmsg') or str(data),
            }
        resp.raise_for_status()

        ext = 'jpg'
        if 'png' in content_type:
            ext = 'png'
        elif 'gif' in content_type:
            ext = 'gif'
        elif 'webp' in content_type:
            ext = 'webp'
        elif 'pdf' in content_type:
            ext = 'pdf'

        date_path = datetime.now().strftime('%Y/%m/%d')
        folder = os.path.join(subdir, date_path)
        os.makedirs(folder, exist_ok=True)
        filename = f'{uuid.uuid4().hex}.{ext}'
        file_path = os.path.join(folder, filename)
        with open(file_path, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return {
            'ok': True,
            'dry_run': False,
            'status': 'downloaded',
            'media_id': media_id,
            'file_path': file_path,
            'url': '/' + file_path.replace(os.sep, '/'),
            'content_type': content_type,
            'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else None,
        }


wecom_service = WeComService()
