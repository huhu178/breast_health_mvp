"""
Third-party AI tongue diagnosis integration.

Current production path is H5 member SSO. The older direct interface methods are
kept behind an explicit TONGUE_DIRECT_API_ENABLED switch for compatibility only.
"""
import base64
import json
import os
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7


class TongueDiagnosisService:
    def __init__(self):
        self.base_url = os.getenv('TONGUE_API_BASE_URL', 'https://www.ai-tongue.com').rstrip('/')
        self.auth_url = os.getenv(
            'TONGUE_AUTH_URL',
            f'{self.base_url}/backend/auth/invoker/pwd/signin'
        )
        self.pre_url = os.getenv(
            'TONGUE_PRE_URL',
            f'{self.base_url}/backend/interfacesvc/i/tongue/task/pre'
        )
        self.confirm_url = os.getenv(
            'TONGUE_CONFIRM_URL',
            f'{self.base_url}/backend/interfacesvc/i/tongue/task/do'
        )
        self.h5_sso_url = os.getenv('TONGUE_H5_SSO_URL', f'{self.base_url}/h5/sso')
        self.third_user_init_url = os.getenv(
            'TONGUE_THIRD_USER_INIT_URL',
            f'{self.base_url}/backend/check/i/secret/thirdUser/init'
        )
        self.report_query_url = os.getenv(
            'TONGUE_REPORT_QUERY_URL',
            f'{self.base_url}/backend/check/i/report/query'
        )
        self.enabled = os.getenv('TONGUE_API_ENABLED', 'false').lower() == 'true'
        self.dry_run = os.getenv('TONGUE_API_DRY_RUN', 'true').lower() != 'false'
        self.timeout = int(os.getenv('TONGUE_API_TIMEOUT', '20'))
        self.token_cache: Dict[str, Any] = {}

    def is_real_call_enabled(self) -> bool:
        return self.enabled and not self.dry_run

    def _require_config(self):
        missing = [
            key for key in ('TONGUE_DEV_ID', 'TONGUE_DEV_SECRET', 'TONGUE_DEV_RSA_PRIVATE_KEY', 'TONGUE_AES_KEY', 'TONGUE_CALLBACK_BASE_URL')
            if not os.getenv(key)
        ]
        if missing:
            raise RuntimeError(f'舌诊接口缺少环境变量: {", ".join(missing)}')

    def _require_auth_config(self):
        missing = [
            key for key in ('TONGUE_DEV_ID', 'TONGUE_DEV_SECRET')
            if not os.getenv(key)
        ]
        if missing:
            raise RuntimeError(f'舌诊授权缺少环境变量: {", ".join(missing)}')

    def _require_h5_config(self):
        missing = [
            key for key in ('TONGUE_DEV_ID', 'TONGUE_DEV_SECRET', 'TONGUE_DEV_RSA_PRIVATE_KEY', 'TONGUE_PLATFORM_RSA_PUBLIC_KEY')
            if not os.getenv(key)
        ]
        if missing:
            raise RuntimeError(f'H5舌诊接入缺少环境变量: {", ".join(missing)}')

    def get_access_token(self) -> str:
        if not self.is_real_call_enabled():
            return 'dry-run-token'
        self._require_config()
        return self._fetch_access_token()

    def get_real_access_token_for_h5(self) -> str:
        self._require_auth_config()
        return self._fetch_access_token()

    def _fetch_access_token(self) -> str:
        now = time.time()
        token = self.token_cache.get('access_token')
        if token and self.token_cache.get('expires_at', 0) - 60 > now:
            return token

        resp = requests.post(
            self.auth_url,
            files={},
            data={
                'devid': os.getenv('TONGUE_DEV_ID'),
                'devsecret': os.getenv('TONGUE_DEV_SECRET')
            },
            timeout=self.timeout
        )
        payload = resp.json()
        if resp.status_code >= 400 or payload.get('code') not in (0, '0'):
            raise RuntimeError(payload.get('msg') or payload.get('message') or '获取舌诊access_token失败')
        data = payload.get('data') or {}
        access_token = data.get('access_token')
        if not access_token:
            raise RuntimeError('舌诊授权接口未返回access_token')
        self.token_cache = {
            'access_token': access_token,
            'expires_at': now + int(data.get('expires_in') or 1200)
        }
        return access_token

    def sign_out_id(self, out_id: str) -> str:
        """MD5withRSA signature using PKCS1_v1_5 padding."""
        private_key_text = os.getenv('TONGUE_DEV_RSA_PRIVATE_KEY', '').strip()
        if not private_key_text:
            if not self.is_real_call_enabled():
                return 'dry-run-signature'
            raise RuntimeError('缺少TONGUE_DEV_RSA_PRIVATE_KEY')
        private_key = serialization.load_pem_private_key(
            self._normalize_private_key(private_key_text).encode('utf-8'),
            password=None
        )
        signature = private_key.sign(
            out_id.encode('utf-8'),
            padding.PKCS1v15(),
            hashes.MD5()
        )
        return base64.b64encode(signature).decode('utf-8')

    def sign_value(self, value: str) -> str:
        return self.sign_out_id(value)

    def verify_signature(self, out_id: str, signature: str) -> bool:
        """Verify MD5withRSA signature using the platform public key."""
        return self.verify_value_signature(out_id, signature)

    def verify_value_signature(self, value: str, signature: str) -> bool:
        """Verify MD5withRSA signature for an arbitrary source string."""
        public_key_text = os.getenv('TONGUE_PLATFORM_RSA_PUBLIC_KEY', '').strip()
        if not public_key_text:
            return not self.is_real_call_enabled()
        public_key = serialization.load_pem_public_key(
            self._normalize_public_key(public_key_text).encode('utf-8')
        )
        try:
            public_key.verify(
                base64.b64decode(signature),
                value.encode('utf-8'),
                padding.PKCS1v15(),
                hashes.MD5()
            )
            return True
        except Exception:
            return False

    def encrypt_payload(self, payload: Dict[str, Any]) -> str:
        key = self._aes_key()
        raw = json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
        padder = PKCS7(128).padder()
        padded = padder.update(raw) + padder.finalize()
        encryptor = Cipher(algorithms.AES(key), modes.ECB()).encryptor()
        encrypted = encryptor.update(padded) + encryptor.finalize()
        return base64.b64encode(encrypted).decode('utf-8')

    def decrypt_payload(self, encrypt_data: str) -> Dict[str, Any]:
        key = self._aes_key()
        decryptor = Cipher(algorithms.AES(key), modes.ECB()).decryptor()
        decrypted = decryptor.update(base64.b64decode(encrypt_data)) + decryptor.finalize()
        unpadder = PKCS7(128).unpadder()
        raw = unpadder.update(decrypted) + unpadder.finalize()
        return json.loads(raw.decode('utf-8'))

    def rsa_encrypt_with_platform_public_key(self, value: str) -> str:
        public_key_text = os.getenv('TONGUE_PLATFORM_RSA_PUBLIC_KEY', '').strip()
        if not public_key_text:
            raise RuntimeError('缺少TONGUE_PLATFORM_RSA_PUBLIC_KEY')
        public_key = serialization.load_pem_public_key(
            self._normalize_public_key(public_key_text).encode('utf-8')
        )
        encrypted = public_key.encrypt(
            value.encode('utf-8'),
            padding.PKCS1v15()
        )
        return base64.b64encode(encrypted).decode('utf-8')

    def rsa_decrypt_with_private_key(self, value: str) -> str:
        private_key_text = os.getenv('TONGUE_DEV_RSA_PRIVATE_KEY', '').strip()
        if not private_key_text:
            raise RuntimeError('缺少TONGUE_DEV_RSA_PRIVATE_KEY')
        private_key = serialization.load_pem_private_key(
            self._normalize_private_key(private_key_text).encode('utf-8'),
            password=None
        )
        decrypted = private_key.decrypt(
            base64.b64decode(value),
            padding.PKCS1v15()
        )
        return decrypted.decode('utf-8')

    def build_h5_sso(self, *, third_id: str, patient: Any = None) -> Dict[str, Any]:
        self._require_h5_config()
        access_token = self.get_real_access_token_for_h5()
        encrypted_third_id = self.rsa_encrypt_with_platform_public_key(third_id)
        sign_encrypted_third_id = self.sign_value(encrypted_third_id)
        init_payload = {
            'devId': os.getenv('TONGUE_DEV_ID'),
            'thirdId': third_id,
            'encryptedThirdId': encrypted_third_id,
            'signEncryptedThirdId': sign_encrypted_third_id
        }
        if patient:
            init_payload.update({
                'name': getattr(patient, 'name', '') or '',
                'userName': getattr(patient, 'name', '') or '',
                'age': getattr(patient, 'age', None),
                'sex': self._sex_value(getattr(patient, 'gender', '')),
                'phone': getattr(patient, 'phone', '') or ''
            })
        init_response = self.try_init_third_user(access_token=access_token, payload=init_payload)
        query = {
            'access_token': access_token,
            'encryptedThirdId': encrypted_third_id,
            'signEncryptedThirdId': sign_encrypted_third_id,
            'capture': os.getenv('TONGUE_H5_CAPTURE', 'all'),
            'diseaseCode': os.getenv('TONGUE_H5_DISEASE_CODE', 'C00.D00'),
            'excludePages': os.getenv(
                'TONGUE_H5_EXCLUDE_PAGES',
                'allFaceImage,sideFaceImage,bottomTab,edition,instruction,share'
            )
        }
        if patient:
            if getattr(patient, 'name', None):
                query['userName'] = patient.name
            if getattr(patient, 'phone', None):
                query['phone'] = patient.phone
            if getattr(patient, 'gender', None):
                query['sex'] = self._sex_value(patient.gender)
        return {
            'third_id': third_id,
            'encrypted_third_id': encrypted_third_id,
            'sign_encrypted_third_id': sign_encrypted_third_id,
            'h5_url': f'{self.h5_sso_url}?{urlencode(query)}',
            'third_user_init_response': init_response
        }

    def try_init_third_user(self, *, access_token: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            resp = requests.post(
                self.third_user_init_url,
                headers={'Authorization': f'Bearer {access_token}'},
                json=payload,
                timeout=self.timeout
            )
            try:
                data = resp.json()
            except Exception:
                data = {'raw_text': resp.text}
            data['_http_status'] = resp.status_code
            return data
        except Exception as e:
            return {
                'supported': False,
                'error': str(e)
            }

    def query_h5_reports(self, *, third_id: str = None, start: str = None, end: str = None, next_page_key: str = None) -> Dict[str, Any]:
        token = self.get_real_access_token_for_h5()
        payload = {
            'apiVersion': 20240815
        }
        if third_id:
            payload['thirdId'] = third_id
        if start:
            payload['start'] = start
        if end:
            payload['end'] = end
        if next_page_key:
            payload['nextPageKey'] = next_page_key

        resp = requests.post(
            self.report_query_url,
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            },
            json=payload,
            timeout=self.timeout
        )
        try:
            data = resp.json()
        except Exception:
            data = {'raw_text': resp.text}
        data['_http_status'] = resp.status_code
        data['_request'] = payload
        return data

    def find_report_row(self, response: Dict[str, Any], third_id: str) -> Optional[Dict[str, Any]]:
        data = response.get('data') or {}
        rows = data.get('rows') or []
        matches = [row for row in rows if row.get('thirdId') == third_id]
        if not matches:
            return None
        return sorted(matches, key=lambda row: str(row.get('time') or ''), reverse=True)[0]

    def submit_precheck(self, *, out_id: str, return_url: str, tongue_img_path: str, tongue_back_img_path: str) -> Dict[str, Any]:
        encrypt_payload = {
            'returnUrl': return_url,
            'imageType': os.getenv('TONGUE_IMAGE_TYPE', '1'),
            'strictLevel': int(os.getenv('TONGUE_STRICT_LEVEL', '5')),
        }
        if not self.is_real_call_enabled():
            return {
                'dry_run': True,
                'code': 0,
                'msg': 'dry-run: 舌诊预判未真实调用',
                'request': {'outId': out_id, 'encryptData': encrypt_payload}
            }
        token = self.get_access_token()
        data = {
            'outId': out_id,
            'signature': self.sign_out_id(out_id),
            'encryptData': self.encrypt_payload(encrypt_payload)
        }
        with open(tongue_img_path, 'rb') as tongue_file, open(tongue_back_img_path, 'rb') as back_file:
            resp = requests.post(
                self.pre_url,
                headers={'Authorization': f'Bearer {token}'},
                data=data,
                files={
                    'tongueImg': tongue_file,
                    'tongueBackImg': back_file
                },
                timeout=self.timeout
            )
        return resp.json()

    def submit_confirm(self, *, out_id: str, patient: Any, record: Any) -> Dict[str, Any]:
        payload = {
            'userName': getattr(patient, 'name', '') or '',
            'age': getattr(patient, 'age', None) or getattr(record, 'age', None),
            'sex': self._sex_value(getattr(patient, 'gender', '')),
            'height': getattr(record, 'height', None),
            'weight': getattr(record, 'weight', None),
            'diseaseCode': os.getenv('TONGUE_DISEASE_CODE', 'tongue'),
            'requireInquiry': False,
            'language': os.getenv('TONGUE_LANGUAGE', 'zh_CN')
        }
        if not self.is_real_call_enabled():
            return {
                'dry_run': True,
                'code': 0,
                'msg': 'dry-run: 舌诊确认提交未真实调用',
                'request': {'outId': out_id, 'encryptData': payload}
            }
        token = self.get_access_token()
        resp = requests.post(
            self.confirm_url,
            headers={'Authorization': f'Bearer {token}'},
            data={
                'outId': out_id,
                'signature': self.sign_out_id(out_id),
                'encryptData': self.encrypt_payload(payload)
            },
            timeout=self.timeout
        )
        return resp.json()

    def extract_tongue_feature(self, payload: Dict[str, Any]) -> Optional[str]:
        result = payload.get('result') or {}
        return (
            (((result.get('characterMap') or {}).get('tongue') or {}).get('feature'))
            or payload.get('tongueFeature')
            or payload.get('tongue_feature')
        )

    def _aes_key(self) -> bytes:
        value = os.getenv('TONGUE_AES_KEY', '').strip()
        if not value:
            if not self.is_real_call_enabled():
                return b'0' * 16
            raise RuntimeError('缺少TONGUE_AES_KEY')
        try:
            raw = base64.b64decode(value, validate=True)
        except Exception as e:
            raise RuntimeError('TONGUE_AES_KEY必须是Base64编码') from e
        if len(raw) not in (16, 24, 32):
            raise RuntimeError('TONGUE_AES_KEY Base64解码后长度必须为16/24/32字节')
        return raw

    def _normalize_private_key(self, value: str) -> str:
        if 'BEGIN' in value:
            return value.replace('\\n', '\n')
        return '-----BEGIN PRIVATE KEY-----\n' + '\n'.join([value[i:i + 64] for i in range(0, len(value), 64)]) + '\n-----END PRIVATE KEY-----'

    def _normalize_public_key(self, value: str) -> str:
        if 'BEGIN' in value:
            return value.replace('\\n', '\n')
        return '-----BEGIN PUBLIC KEY-----\n' + '\n'.join([value[i:i + 64] for i in range(0, len(value), 64)]) + '\n-----END PUBLIC KEY-----'

    def _sex_value(self, gender: str) -> str:
        if str(gender).strip() in ('男', 'M', 'm', '1'):
            return os.getenv('TONGUE_SEX_MALE', '1')
        return os.getenv('TONGUE_SEX_FEMALE', '2')


tongue_diagnosis_service = TongueDiagnosisService()
