"""
B端舌诊 H5 接入路由。

当前业务入口只生成手机 H5 单点登录地址；电脑 B 端不作为拍照采集终端。
"""
import os
import json
import uuid
from datetime import datetime
from html import escape

from flask import Blueprint, request, Response as FlaskResponse, redirect
from werkzeug.utils import secure_filename

from models import db, BPatient, BHealthRecord, BReport, BTongueDiagnosis
from services.tongue_diagnosis_service import tongue_diagnosis_service
from utils.decorators import login_required
from utils.response import Response


b_tongue_bp = Blueprint('b_tongue', __name__, url_prefix='/api/b/tongue-diagnosis')


def _save_tongue_file(file, out_id, kind):
    if not file or not file.filename:
        return None
    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
    if ext not in ('jpg', 'jpeg', 'png'):
        raise ValueError('舌诊图片仅支持jpg/jpeg/png')
    date_path = datetime.utcnow().strftime('%Y/%m')
    folder = os.path.join('uploads', 'tongue', date_path, out_id)
    os.makedirs(folder, exist_ok=True)
    filename = f'{kind}_{uuid.uuid4().hex}.{ext}'
    path = os.path.join(folder, secure_filename(filename))
    file.save(path)
    return path


def _callback_url():
    base = os.getenv('TONGUE_CALLBACK_BASE_URL', '').rstrip('/')
    if not base:
        return ''
    return f'{base}/api/b/tongue-diagnosis/callback'


def _mobile_open_url(task_id):
    base = os.getenv('TONGUE_PUBLIC_BASE_URL', '').rstrip('/') or request.url_root.rstrip('/')
    return f'{base}/api/b/tongue-diagnosis/open/{task_id}'


def _build_third_id(patient_id, record_id=None):
    suffix = uuid.uuid4().hex[:8]
    record_part = record_id if record_id else 'latest'
    return f'BH-B-{patient_id}-{record_part}-{datetime.utcnow().strftime("%Y%m%d%H%M%S")}-{suffix}'


def _get_int_value(data, key):
    try:
        if hasattr(data, 'get') and hasattr(data, 'getlist'):
            return data.get(key, type=int)
        value = data.get(key) if hasattr(data, 'get') else None
        return int(value) if value not in (None, '') else None
    except Exception:
        return None


def _write_tongue_result_to_record_and_report(task, payload):
    if not task.record_id or not task.tongue_feature:
        return

    record = BHealthRecord.query.get(task.record_id)
    if record:
        record.tongue_check_result_id = task.out_id
        record.tongue_result_raw = json.dumps(payload, ensure_ascii=False)
        record.tongue_result_summary = task.tongue_feature
        record.tongue_checked_at = datetime.utcnow()

    report = None
    if task.report_id:
        report = BReport.query.get(task.report_id)
    if not report:
        report = BReport.query.filter_by(record_id=task.record_id).order_by(BReport.created_at.desc()).first()
    if not report:
        return

    tongue_block_text = f'舌象特征分析：{task.tongue_feature}'
    if report.report_summary:
        if '舌象特征分析：' not in report.report_summary:
            report.report_summary = f'{report.report_summary}\n{tongue_block_text}'
    else:
        report.report_summary = tongue_block_text

    if report.report_html:
        summary_html = (
            '<section class="tongue-diagnosis-section" style="margin-top:16px;line-height:1.7;">'
            '<h3 style="font-size:16px;margin:0 0 8px;">舌象特征分析</h3>'
            f'<div style="white-space:pre-line;">{escape(task.tongue_feature)}</div>'
            '</section>'
        )
        if 'tongue-diagnosis-section' not in report.report_html:
            if '</body>' in report.report_html:
                report.report_html = report.report_html.replace('</body>', f'{summary_html}</body>')
            else:
                report.report_html = report.report_html + summary_html


@b_tongue_bp.route('/tasks', methods=['POST'])
@login_required
def create_tongue_task(current_user):
    """兼容旧直连接口；默认停用。"""
    if os.getenv('TONGUE_DIRECT_API_ENABLED', 'false').lower() != 'true':
        return Response.error('当前舌诊已切换为H5单点登录接入，请使用 /api/b/tongue-diagnosis/h5-sso', 400)
    patient_id = request.form.get('patient_id', type=int)
    record_id = request.form.get('record_id', type=int)
    if not patient_id:
        return Response.error('patient_id不能为空', 400)

    patient = BPatient.query.get(patient_id)
    if not patient:
        return Response.error('患者不存在', 404)
    record = BHealthRecord.query.get(record_id) if record_id else BHealthRecord.query.filter_by(patient_id=patient_id).order_by(BHealthRecord.created_at.desc()).first()
    report = BReport.query.filter_by(record_id=record.id).order_by(BReport.created_at.desc()).first() if record else None

    tongue_img = request.files.get('tongue_img')
    tongue_back_img = request.files.get('tongue_back_img')
    if not tongue_img or not tongue_back_img:
        return Response.error('请同时上传舌面图和舌下图', 400)

    out_id = request.form.get('out_id') or f'TONGUE-{patient_id}-{datetime.utcnow().strftime("%Y%m%d%H%M%S")}-{uuid.uuid4().hex[:8]}'
    try:
        tongue_path = _save_tongue_file(tongue_img, out_id, 'tongue')
        back_path = _save_tongue_file(tongue_back_img, out_id, 'tongue_back')

        task = BTongueDiagnosis(
            out_id=out_id,
            patient_id=patient_id,
            record_id=record.id if record else None,
            report_id=report.id if report else None,
            status='created',
            tongue_img_path=tongue_path,
            tongue_back_img_path=back_path,
            submitted_by=current_user.id,
            request_payload={
                'callback_url': _callback_url(),
                'dry_run': not tongue_diagnosis_service.is_real_call_enabled()
            }
        )
        db.session.add(task)
        db.session.flush()

        pre_response = tongue_diagnosis_service.submit_precheck(
            out_id=out_id,
            return_url=_callback_url(),
            tongue_img_path=tongue_path,
            tongue_back_img_path=back_path
        )
        task.pre_response = pre_response
        task.status = 'pre_submitted'
        task.pre_status = 'dry_run' if pre_response.get('dry_run') else 'submitted'
        db.session.commit()
        return Response.success({'task': task.to_dict()}, '舌诊预判已提交', 201)
    except Exception as e:
        db.session.rollback()
        return Response.error(f'舌诊预判提交失败: {str(e)}', 500)


@b_tongue_bp.route('/h5-sso', methods=['POST'])
@login_required
def create_h5_sso(current_user):
    """生成第三方 H5 会员单点登录地址。"""
    data = request.get_json(silent=True) or request.form
    patient_id = _get_int_value(data, 'patient_id')
    record_id = _get_int_value(data, 'record_id')
    if not patient_id:
        return Response.error('patient_id不能为空', 400)

    patient = BPatient.query.get(patient_id)
    if not patient:
        return Response.error('患者不存在', 404)
    record = BHealthRecord.query.get(record_id) if record_id else BHealthRecord.query.filter_by(patient_id=patient_id).order_by(BHealthRecord.created_at.desc()).first()
    report = BReport.query.filter_by(record_id=record.id).order_by(BReport.created_at.desc()).first() if record else None
    third_id = data.get('third_id') or _build_third_id(patient_id, record.id if record else None)

    try:
        sso = tongue_diagnosis_service.build_h5_sso(third_id=third_id, patient=patient)
        task = BTongueDiagnosis(
            out_id=third_id,
            patient_id=patient_id,
            record_id=record.id if record else None,
            report_id=report.id if report else None,
            status='h5_sso_created',
            submitted_by=current_user.id,
            request_payload={
                'mode': 'h5_sso',
                'third_id': third_id,
                'encryptedThirdId': sso.get('encrypted_third_id'),
                'signEncryptedThirdId': sso.get('sign_encrypted_third_id'),
                'h5_url': sso.get('h5_url'),
                'third_user_init_response': sso.get('third_user_init_response')
            }
        )
        db.session.add(task)
        db.session.flush()
        mobile_open_url = _mobile_open_url(task.id)
        task.request_payload = {
            **(task.request_payload or {}),
            'mobile_open_url': mobile_open_url
        }
        db.session.commit()
        return Response.success({
            'task': task.to_dict(),
            'third_id': third_id,
            'h5_url': sso.get('h5_url'),
            'mobile_open_url': mobile_open_url,
            'third_user_init_response': sso.get('third_user_init_response')
        }, 'H5舌诊登录地址已生成')
    except Exception as e:
        db.session.rollback()
        return Response.error(f'H5舌诊登录地址生成失败: {str(e)}', 500)


@b_tongue_bp.route('/open/<int:task_id>', methods=['GET'])
def open_h5_sso(task_id):
    """手机扫码入口：跳转到第三方 H5 SSO 地址。"""
    task = BTongueDiagnosis.query.get(task_id)
    h5_url = (task.request_payload or {}).get('h5_url') if task and isinstance(task.request_payload, dict) else None
    if not h5_url:
        return FlaskResponse('tongue h5 url not found', status=404, mimetype='text/plain')
    return redirect(h5_url, code=302)


@b_tongue_bp.route('/tasks/<int:task_id>', methods=['GET'])
@login_required
def get_tongue_task(current_user, task_id):
    task = BTongueDiagnosis.query.get(task_id)
    if not task:
        return Response.error('舌诊任务不存在', 404)
    return Response.success({'task': task.to_dict()})


@b_tongue_bp.route('/tasks/<int:task_id>/confirm', methods=['POST'])
@login_required
def confirm_tongue_task(current_user, task_id):
    """兼容旧直连接口确认提交；默认停用。"""
    if os.getenv('TONGUE_DIRECT_API_ENABLED', 'false').lower() != 'true':
        return Response.error('当前舌诊已切换为H5单点登录接入，纯接口确认提交已停用', 400)
    task = BTongueDiagnosis.query.get(task_id)
    if not task:
        return Response.error('舌诊任务不存在', 404)
    if task.status == 'pre_invalid':
        return Response.error('舌诊预判不合格，不能提交检测', 400)
    patient = BPatient.query.get(task.patient_id)
    record = BHealthRecord.query.get(task.record_id) if task.record_id else None
    try:
        result = tongue_diagnosis_service.submit_confirm(out_id=task.out_id, patient=patient, record=record)
        task.confirm_response = result
        task.status = 'detecting'
        task.result_status = 'dry_run' if result.get('dry_run') else 'submitted'
        db.session.commit()
        return Response.success({'task': task.to_dict()}, '舌诊检测已提交')
    except Exception as e:
        db.session.rollback()
        return Response.error(f'舌诊检测提交失败: {str(e)}', 500)


@b_tongue_bp.route('/tasks/by-record/<int:record_id>', methods=['GET'])
@login_required
def list_tongue_tasks_by_record(current_user, record_id):
    tasks = BTongueDiagnosis.query.filter_by(record_id=record_id).order_by(BTongueDiagnosis.created_at.desc()).all()
    return Response.success({'items': [task.to_dict() for task in tasks], 'total': len(tasks)})


@b_tongue_bp.route('/callback', methods=['POST'])
def tongue_callback():
    """第三方异步回调。成功处理后必须返回纯文本 success。"""
    json_body = request.get_json(silent=True) if request.is_json else {}
    out_id = request.form.get('outId') or (json_body or {}).get('outId')
    signature = request.form.get('signature') or (json_body or {}).get('signature')
    encrypt_data = request.form.get('encryptData') or (json_body or {}).get('encryptData')

    payload = None
    try:
        if encrypt_data:
            payload = tongue_diagnosis_service.decrypt_payload(encrypt_data)
        elif request.is_json:
            payload = request.get_json(silent=True) or {}
        else:
            payload = request.form.to_dict()
        out_id = out_id or payload.get('outId')
        if not out_id:
            return FlaskResponse('missing outId', status=400, mimetype='text/plain')
        if signature and not tongue_diagnosis_service.verify_signature(out_id, signature):
            return FlaskResponse('invalid signature', status=400, mimetype='text/plain')

        task = BTongueDiagnosis.query.filter_by(out_id=out_id).first()
        if not task:
            print(f'舌诊回调未匹配到任务: outId={out_id}; payload={payload}')
            return FlaskResponse('success', mimetype='text/plain')

        return_type = int(payload.get('returnType', -1))
        task.callback_payload = payload
        task.callback_received_at = datetime.utcnow()

        if return_type == 31:
            task.status = 'pre_valid'
            task.pre_status = 'valid'
        elif return_type == 32:
            task.status = 'pre_invalid'
            task.pre_status = 'invalid'
            task.error_json = payload.get('errorMap') or payload
        elif return_type == 0:
            task.status = 'waiting_inquiry'
            task.result_status = 'waiting_inquiry'
        elif return_type == 1:
            task.status = 'completed'
            task.result_status = 'completed'
            task.result_json = payload
            task.tongue_feature = tongue_diagnosis_service.extract_tongue_feature(payload)
            _write_tongue_result_to_record_and_report(task, payload)
        elif return_type == 2:
            task.status = 'failed'
            task.result_status = 'failed'
            task.error_json = payload.get('errorMap') or payload
        else:
            task.status = 'callback_unknown'

        db.session.commit()
        return FlaskResponse('success', mimetype='text/plain')
    except Exception as e:
        db.session.rollback()
        print(f'舌诊回调处理失败: {e}; payload={payload}')
        return FlaskResponse('error', status=500, mimetype='text/plain')
