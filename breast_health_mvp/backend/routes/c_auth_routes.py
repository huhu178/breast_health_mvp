"""
C端认证路由（线索入口 + 登录/注册）
支持：微信登录、手机号登录、来源追踪
"""
from flask import Blueprint, request, jsonify
from models import db, CPatient
from utils.response import Response
from datetime import datetime
import uuid
import re
from utils.id_generator import generate_patient_code

# 创建蓝图
c_auth_bp = Blueprint('c_auth', __name__, url_prefix='/api/c/auth')

# ============================================
# 辅助函数
# ============================================

def verify_phone(phone):
    """验证手机号格式（中国大陆）"""
    if not phone:
        return False, "手机号不能为空"

    if not re.match(r'^1[3-9]\d{9}$', phone):
        return False, "手机号格式错误（请输入11位中国大陆手机号）"

    return True, "验证通过"


def create_or_update_lead(
    phone=None, 
    wechat_openid=None, 
    wechat_unionid=None,
    name=None,
    source_channel='unknown',
    campaign_code=None,
    entry_url=None
):
    """
    创建或更新线索/客户记录
    
    参数:
        phone: 手机号
        wechat_openid: 微信 OpenID
        wechat_unionid: 微信 UnionID
        name: 姓名
        source_channel: 来源渠道（web/wechat/h5/app）
        campaign_code: 活动代码
        entry_url: 入口 URL
    
    返回:
        (patient, is_new) - 患者对象和是否新建标识
    """
    now = datetime.utcnow()
    patient = None
    is_new = False
    
    # 1. 尝试通过手机号查找
    if phone:
        patient = CPatient.query.filter_by(phone=phone).first()
    
    # 2. 尝试通过微信 UnionID 查找（跨公众号/小程序统一身份）
    if not patient and wechat_unionid:
        patient = CPatient.query.filter_by(wechat_unionid=wechat_unionid).first()
    
    # 3. 尝试通过微信 OpenID 查找
    if not patient and wechat_openid:
        patient = CPatient.query.filter_by(wechat_openid=wechat_openid).first()
    
    # 4. 如果找不到，创建新线索
    if not patient:
        patient = CPatient(
            patient_code=generate_patient_code(),
            name=name or '访客',
            phone=phone,
            wechat_openid=wechat_openid,
            wechat_unionid=wechat_unionid,
            source_channel=source_channel,
            campaign_code=campaign_code,
            entry_url=entry_url,
            lead_status='new',
            status='active',
            is_contacted=False,
            first_visit_at=now,
            last_activity_at=now
        )
        db.session.add(patient)
        is_new = True
    else:
        # 5. 更新现有记录
        if name:
            patient.name = name
        if phone and not patient.phone:
            patient.phone = phone
        if wechat_unionid and not patient.wechat_unionid:
            patient.wechat_unionid = wechat_unionid
        if wechat_openid and not patient.wechat_openid:
            patient.wechat_openid = wechat_openid
        
        # 更新来源信息（保留首次来源，更新最新来源）
        if source_channel and source_channel != 'unknown':
            patient.source_channel = source_channel
        if campaign_code:
            patient.campaign_code = campaign_code
        if entry_url:
            patient.entry_url = entry_url
        
        patient.last_activity_at = now
        
        # 确保有首次访问时间
        if not patient.first_visit_at:
            patient.first_visit_at = now
    
    db.session.flush()
    return patient, is_new


# ============================================
# 1. 手机号登录/注册（线索入口）
# ============================================

@c_auth_bp.route('/phone', methods=['POST'])
def phone_auth():
    """
    手机号登录/注册
    
    请求体:
    {
        "phone": "13800138000",
        "name": "张三",  // 可选
        "source_channel": "web",  // 可选：web/wechat/h5/app
        "campaign_code": "2024_spring_promo",  // 可选：活动代码
        "entry_url": "https://example.com/health-check"  // 可选：入口URL
    }
    
    响应:
    {
        "success": true,
        "data": {
            "patient": { ... },
            "is_new": true,  // 是否新用户
            "session_token": "xxx"  // 可用于后续会话验证
        }
    }
    """
    data = request.json or {}
    
    phone = data.get('phone')
    name = data.get('name', '')
    source_channel = data.get('source_channel', 'web')
    campaign_code = data.get('campaign_code')
    entry_url = data.get('entry_url')
    
    # 1. 验证手机号
    is_valid, message = verify_phone(phone)
    if not is_valid:
        return Response.error(message, 400)
    
    try:
        # 2. 创建或更新线索
        patient, is_new = create_or_update_lead(
            phone=phone,
            name=name,
            source_channel=source_channel,
            campaign_code=campaign_code,
            entry_url=entry_url
        )
        
        db.session.commit()
        
        # 3. 生成会话 Token（简单实现，实际应使用 JWT）
        session_token = f"ST_{patient.patient_code}_{uuid.uuid4().hex[:16]}"
        
        # 4. 返回结果
        return Response.success({
            'patient': {
                'id': patient.id,
                'patient_code': patient.patient_code,
                'name': patient.name,
                'phone': patient.phone,
                'source_channel': patient.source_channel,
                'lead_status': patient.lead_status,
                'is_new': is_new
            },
            'is_new': is_new,
            'session_token': session_token,
            'message': '欢迎使用乳腺结节健康管理平台' if is_new else '欢迎回来'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ 手机号登录失败: {e}")
        import traceback
        traceback.print_exc()
        return Response.error(f'登录失败: {str(e)}', 500)


# ============================================
# 2. 微信登录/注册（线索入口）
# ============================================

@c_auth_bp.route('/wechat', methods=['POST'])
def wechat_auth():
    """
    微信登录/注册
    
    请求体:
    {
        "code": "wx_auth_code",  // 微信授权 code（由前端获取）
        "wechat_openid": "oABC123...",  // 可选：直接提供 OpenID
        "wechat_unionid": "uXYZ456...",  // 可选：直接提供 UnionID
        "nickname": "微信用户",  // 可选：微信昵称
        "source_channel": "wechat",  // 可选：wechat/wechat_mini
        "campaign_code": "wechat_2024",  // 可选
        "entry_url": "https://mp.weixin.qq.com/..."  // 可选
    }
    
    响应:
    {
        "success": true,
        "data": {
            "patient": { ... },
            "is_new": true,
            "session_token": "xxx",
            "need_phone": true  // 是否需要补充手机号
        }
    }
    """
    data = request.json or {}
    
    # 1. 获取微信信息
    code = data.get('code')
    wechat_openid = data.get('wechat_openid')
    wechat_unionid = data.get('wechat_unionid')
    nickname = data.get('nickname', '')
    source_channel = data.get('source_channel', 'wechat')
    campaign_code = data.get('campaign_code')
    entry_url = data.get('entry_url')
    
    # 2. 验证必要参数
    if not code and not wechat_openid:
        return Response.error('缺少微信授权码或 OpenID', 400)
    
    try:
        # TODO: 如果提供了 code，需要调用微信 API 获取 openid/unionid
        # 示例代码（需要配置微信 AppID/AppSecret）:
        # if code:
        #     wx_result = get_wechat_userinfo(code)
        #     wechat_openid = wx_result['openid']
        #     wechat_unionid = wx_result.get('unionid')
        #     nickname = wx_result.get('nickname', '')
        
        # 3. 创建或更新线索
        patient, is_new = create_or_update_lead(
            wechat_openid=wechat_openid,
            wechat_unionid=wechat_unionid,
            name=nickname,
            source_channel=source_channel,
            campaign_code=campaign_code,
            entry_url=entry_url
        )
        
        db.session.commit()
        
        # 4. 生成会话 Token
        session_token = f"ST_{patient.patient_code}_{uuid.uuid4().hex[:16]}"
        
        # 5. 判断是否需要补充手机号
        need_phone = not patient.phone
        
        # 6. 返回结果
        return Response.success({
            'patient': {
                'id': patient.id,
                'patient_code': patient.patient_code,
                'name': patient.name,
                'phone': patient.phone,
                'wechat_openid': patient.wechat_openid[:10] + '...' if patient.wechat_openid else None,  # 部分隐藏
                'source_channel': patient.source_channel,
                'lead_status': patient.lead_status,
                'is_new': is_new
            },
            'is_new': is_new,
            'session_token': session_token,
            'need_phone': need_phone,
            'message': '欢迎使用乳腺结节健康管理平台' if is_new else '欢迎回来'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ 微信登录失败: {e}")
        import traceback
        traceback.print_exc()
        return Response.error(f'登录失败: {str(e)}', 500)


# ============================================
# 3. 补充手机号（微信用户绑定手机）
# ============================================

@c_auth_bp.route('/bind-phone', methods=['POST'])
def bind_phone():
    """
    为微信用户绑定手机号
    
    请求体:
    {
        "patient_code": "CP20241106...",  // 或使用 session_token
        "phone": "13800138000"
    }
    """
    data = request.json or {}
    
    patient_code = data.get('patient_code')
    phone = data.get('phone')
    
    # 1. 验证参数
    if not patient_code:
        return Response.error('缺少患者编码', 400)
    
    is_valid, message = verify_phone(phone)
    if not is_valid:
        return Response.error(message, 400)
    
    try:
        # 2. 查找患者
        patient = CPatient.query.filter_by(patient_code=patient_code).first()
        if not patient:
            return Response.error('患者不存在', 404)
        
        # 3. 检查手机号是否已被其他用户使用
        existing = CPatient.query.filter_by(phone=phone).first()
        if existing and existing.id != patient.id:
            # 如果手机号已存在且属于另一个用户，可以考虑合并账号
            return Response.error('该手机号已被其他账号使用', 409)
        
        # 4. 绑定手机号
        patient.phone = phone
        patient.last_activity_at = datetime.utcnow()
        
        db.session.commit()
        
        return Response.success({
            'patient': {
                'id': patient.id,
                'patient_code': patient.patient_code,
                'name': patient.name,
                'phone': patient.phone
            },
            'message': '手机号绑定成功'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ 绑定手机号失败: {e}")
        import traceback
        traceback.print_exc()
        return Response.error(f'绑定失败: {str(e)}', 500)


# ============================================
# 4. 获取线索信息（用于前端显示）
# ============================================

@c_auth_bp.route('/profile/<patient_code>', methods=['GET'])
def get_profile(patient_code):
    """
    获取线索/客户基本信息
    
    URL: GET /api/c/auth/profile/CP20241106...
    """
    try:
        patient = CPatient.query.filter_by(patient_code=patient_code).first()
        if not patient:
            return Response.error('用户不存在', 404)
        
        return Response.success({
            'patient': {
                'id': patient.id,
                'patient_code': patient.patient_code,
                'name': patient.name,
                'phone': patient.phone,
                'source_channel': patient.source_channel,
                'campaign_code': patient.campaign_code,
                'lead_status': patient.lead_status,
                'first_visit_at': patient.first_visit_at.isoformat() if patient.first_visit_at else None,
                'last_activity_at': patient.last_activity_at.isoformat() if patient.last_activity_at else None
            }
        })
        
    except Exception as e:
        print(f"❌ 获取用户信息失败: {e}")
        return Response.error(f'查询失败: {str(e)}', 500)

