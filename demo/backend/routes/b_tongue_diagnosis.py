"""
B端舌诊 H5 接入路由。

当前业务入口只生成手机 H5 单点登录地址；电脑 B 端不作为拍照采集终端。
"""
import os
import json
import uuid
from datetime import datetime

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


def _task_response(task):
    data = task.to_dict()
    if task.status == 'h5_sso_created':
        data['mobile_open_url'] = _mobile_open_url(task.id)
    return data


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


def _stringify_tongue_value(value):
    if value is None or value == '':
        return ''
    if isinstance(value, (list, tuple, set)):
        return '、'.join(str(v) for v in value if v not in (None, ''))
    if isinstance(value, dict):
        return '；'.join(
            f'{k}: {_stringify_tongue_value(v)}'
            for k, v in value.items()
            if v not in (None, '', [], {})
        )
    return str(value)


def _pick_nested(payload, *keys):
    for key in keys:
        current = payload
        ok = True
        for part in key.split('.'):
            if isinstance(current, dict) and part in current:
                current = current.get(part)
            else:
                ok = False
                break
        if ok and current not in (None, '', [], {}):
            return current
    return None


def _collect_readable_tongue_fields(payload):
    lines = []
    seen = set()

    def add(label, value):
        text = _stringify_tongue_value(value).strip()
        if not text:
            return
        pair = (label, text)
        if pair in seen:
            return
        seen.add(pair)
        lines.append(f'{label}：{text}')

    def build_overall_assessment():
        health_index = _stringify_tongue_value(
            _pick_nested(payload, 'healthIndex', 'health_index')
        ).strip()
        constitution = _stringify_tongue_value(
            _pick_nested(payload, 'constitutionNames', 'constitutionName', 'constitution_names')
        ).strip()
        symptom = _stringify_tongue_value(
            _pick_nested(payload, 'symptomName', 'symptomNames', 'symptom_name')
        ).strip()
        tongue_feature = _stringify_tongue_value(
            _pick_nested(payload, 'tongueFeature', 'tongue_feature', 'result.characterMap.tongue.feature')
        ).strip()
        parts = []
        if health_index:
            parts.append(f'本次中医检测健康指数为{health_index}')
        if constitution:
            parts.append(f'体质倾向为{constitution}')
        if symptom:
            parts.append(f'证型提示为{symptom}')
        if tongue_feature:
            parts.append(f'舌象提示：{tongue_feature}')
        text = '，'.join(parts)
        return text if text.endswith(('。', '！', '？')) else f'{text}。'

    direct_fields = [
        ('综合评估', 'conclusion', 'result.conclusion'),
        ('舌象特征', 'tongueFeature', 'tongue_feature', 'result.characterMap.tongue.feature'),
        ('舌色', 'colorOfTongueNames', 'colorOfTongueName', 'tongueColorNames', 'tongueColorName'),
        ('苔色', 'colorOfMossNames', 'colorOfMossName', 'mossColorNames', 'mossColorName'),
        ('舌苔', 'mossNames', 'mossName', 'tongueCoatingNames', 'tongueCoatingName'),
        ('津液', 'bodyfluidNames', 'bodyfluidName', 'bodyFluidNames', 'bodyFluidName'),
        ('舌形', 'shapeOfTongueNames', 'shapeOfTongueName', 'tongueShapeNames', 'tongueShapeName'),
        ('舌下络脉', 'veinNames', 'veinName', 'sublingualVeinNames', 'sublingualVeinName'),
        ('面象特征', 'faceFeature', 'face_feature'),
        ('面色', 'mianse', 'faceColorNames', 'faceColorName'),
        ('主色', 'zhuse'),
        ('光泽', 'guangze'),
        ('左侧黑眼圈', 'heiyanquanLeft'),
        ('右侧黑眼圈', 'heiyanquanRight'),
        ('唇色', 'chunse'),
        ('眼神', 'yanshen'),
        ('左目色', 'museLeft'),
        ('右目色', 'museRight'),
        ('两颧红', 'liangquanhong'),
        ('鼻褶', 'bizhe'),
        ('眉间青', 'meijianqing'),
        ('面部皮损', 'mianbuPiSun'),
        ('左耳色', 'erseLeft'),
        ('右耳色', 'erseRight'),
        ('左耳褶', 'erzheLeft'),
        ('右耳褶', 'erzheRight'),
        ('健康指数', 'healthIndex', 'health_index'),
        ('体质类型', 'constitutionNames', 'constitutionName', 'constitution_names'),
        ('证型提示', 'symptomName', 'symptomNames', 'symptom_name'),
        ('调理建议', 'suggest', 'suggestion', 'advice', 'result.suggest', 'result.suggestion'),
        ('检测时间', 'time', 'reportTime', 'createdTime'),
    ]
    for label, *keys in direct_fields:
        add(label, _pick_nested(payload, *keys))
    if '综合评估' not in {line.split('：', 1)[0] for line in lines}:
        overall_assessment = build_overall_assessment()
        if overall_assessment:
            lines.insert(0, f'综合评估：{overall_assessment}')
            seen.add(('综合评估', overall_assessment))

    disease_risks = payload.get('diseaseRisksJson') if isinstance(payload, dict) else None
    if isinstance(disease_risks, str):
        try:
            disease_risks = json.loads(disease_risks)
        except Exception:
            disease_risks = None
    if isinstance(disease_risks, list):
        risk_lines = []
        for item in disease_risks:
            if not isinstance(item, dict):
                continue
            name = item.get('diseaseName')
            level = item.get('riskLevel') or item.get('riskName')
            explain = item.get('explain')
            tip = item.get('tip')
            if not str(name or '').strip():
                continue
            risk_text = str(name).strip()
            if str(level or '').strip():
                risk_text += f'｜风险等级：{str(level).strip()}'
            if str(explain or '').strip():
                risk_text += f'｜风险说明：{str(explain).strip()}'
            if str(tip or '').strip():
                risk_text += f'｜建议：{str(tip).strip()}'
            risk_lines.append(risk_text)
        if risk_lines:
            add('相关风险提示', '\n'.join(risk_lines))

    return '\n'.join(lines).strip()


def _extract_full_tongue_report_text(payload):
    summary = _collect_readable_tongue_fields(payload)
    feature = tongue_diagnosis_service.extract_tongue_feature(payload)
    if feature and '舌象特征' not in summary:
        summary = f'舌象特征：{feature}' + (f'\n{summary}' if summary else '')
    return summary or feature or '（舌诊报告已回流，原始报告已保存）'


def _write_tongue_result_to_record_and_report(task, payload):
    if not task.record_id:
        return
    full_report_text = _extract_full_tongue_report_text(payload)

    record = BHealthRecord.query.get(task.record_id)
    if record:
        record.tongue_check_result_id = task.out_id
        record.tongue_result_raw = json.dumps(payload, ensure_ascii=False)
        record.tongue_result_summary = full_report_text
        record.tongue_checked_at = datetime.utcnow()

    report = None
    if task.report_id:
        report = BReport.query.get(task.report_id)
    if not report:
        report = BReport.query.filter_by(record_id=task.record_id).order_by(BReport.created_at.desc()).first()
    if not report:
        return

    from sqlalchemy.orm.attributes import flag_modified
    draft = report.recommendations_draft or {}
    advice = draft.get('advice') or {}
    sections = advice.get('sections') or {}
    sections['tongue_conclusion'] = full_report_text
    advice['sections'] = sections
    advice['updated_at'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    draft['advice'] = advice
    report.recommendations_draft = draft
    flag_modified(report, 'recommendations_draft')
    from utils.report_manager import derive_tcm_risk_level
    tcm_risk = derive_tcm_risk_level(record)
    if tcm_risk:
        risk_level, risk_score, risk_basis = tcm_risk
        report.risk_level = risk_level
        report.risk_score = risk_score
        report.report_summary = f'{risk_level} · {risk_basis}'
    if report.report_html:
        from utils.report_manager import inject_tcm_report_html
        report.report_html = inject_tcm_report_html(report.report_html, record)


def _parse_record_id_from_third_id(third_id):
    parts = str(third_id or '').split('-')
    if len(parts) >= 4 and parts[0] == 'BH' and parts[1] == 'B':
        try:
            return int(parts[3])
        except Exception:
            return None
    return None


def _write_hand_result_to_record_and_report(third_id, payload):
    record_id = _parse_record_id_from_third_id(third_id)
    if not record_id:
        return False

    record = BHealthRecord.query.get(record_id)
    if not record:
        return False

    full_report_text = _extract_full_tongue_report_text(payload)
    record.hand_check_result_id = third_id
    record.hand_result_raw = json.dumps(payload, ensure_ascii=False)
    record.hand_result_summary = full_report_text
    record.hand_checked_at = datetime.utcnow()

    report = BReport.query.filter_by(record_id=record.id).order_by(BReport.created_at.desc()).first()
    if report:
        from sqlalchemy.orm.attributes import flag_modified
        from utils.report_manager import build_tcm_report_text, derive_tcm_risk_level, inject_tcm_report_html

        draft = report.recommendations_draft or {}
        advice = draft.get('advice') or {}
        sections = advice.get('sections') or {}
        sections['tongue_conclusion'] = build_tcm_report_text(record)
        advice['sections'] = sections
        advice['updated_at'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        draft['advice'] = advice
        report.recommendations_draft = draft
        flag_modified(report, 'recommendations_draft')
        tcm_risk = derive_tcm_risk_level(record)
        if tcm_risk:
            risk_level, risk_score, risk_basis = tcm_risk
            report.risk_level = risk_level
            report.risk_score = risk_score
            report.report_summary = f'{risk_level} · {risk_basis}'
        if report.report_html:
            report.report_html = inject_tcm_report_html(report.report_html, record)

    return True


def _apply_tongue_report_payload(task, payload, *, source):
    default_return_type = 1 if source == 'report_query' and (payload.get('tongueFeature') or payload.get('pdf')) else -1
    return_type = int(payload.get('returnType', default_return_type))
    task.callback_received_at = datetime.utcnow() if source == 'callback' else task.callback_received_at

    if return_type in (1, 3):
        task.status = 'completed'
        task.result_status = 'pdf_generated' if return_type == 3 else 'completed'
        task.result_json = payload
        task.tongue_feature = _extract_full_tongue_report_text(payload)
        _write_tongue_result_to_record_and_report(task, payload)
    elif return_type == 2:
        task.status = 'failed'
        task.result_status = 'failed'
        task.error_json = {
            'source': source,
            'errorMsg': payload.get('errorMsg'),
            'payload': payload
        }
    else:
        task.status = 'callback_unknown' if source == 'callback' else 'sync_unknown'
        task.result_status = f'unknown_return_type_{return_type}'


def _read_callback_payload():
    json_body = request.get_json(silent=True) if request.is_json else {}
    out_id = request.form.get('outId') or (json_body or {}).get('outId')
    signature = request.form.get('signature') or (json_body or {}).get('signature')
    encrypt_data = request.form.get('encryptData') or (json_body or {}).get('encryptData')
    encrypted_json = request.form.get('encryptedJson') or (json_body or {}).get('encryptedJson')
    sign_encrypted_json = request.form.get('signEncryptedJson') or (json_body or {}).get('signEncryptedJson')

    if encrypted_json:
        payload = tongue_diagnosis_service.decrypt_payload(encrypted_json)
    elif encrypt_data:
        payload = tongue_diagnosis_service.decrypt_payload(encrypt_data)
    elif request.is_json:
        payload = request.get_json(silent=True) or {}
    else:
        payload = request.form.to_dict()

    if sign_encrypted_json:
        sign_source = f"{payload.get('thirdId')}_{payload.get('time')}"
        if not payload.get('thirdId') or not payload.get('time'):
            return None, None, None, FlaskResponse('missing signature source', status=400, mimetype='text/plain')
        if not tongue_diagnosis_service.verify_value_signature(sign_source, sign_encrypted_json):
            return None, None, None, FlaskResponse('invalid signature', status=400, mimetype='text/plain')

    out_id = out_id or payload.get('outId') or payload.get('thirdId')
    if not out_id:
        return None, None, None, FlaskResponse('missing thirdId', status=400, mimetype='text/plain')
    if signature and not tongue_diagnosis_service.verify_signature(out_id, signature):
        return None, None, None, FlaskResponse('invalid signature', status=400, mimetype='text/plain')

    return out_id, signature, payload, None


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
            'task': _task_response(task),
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
    return Response.success({'task': _task_response(task)})


@b_tongue_bp.route('/tasks/<int:task_id>/sync-report', methods=['POST'])
@login_required
def sync_tongue_report(current_user, task_id):
    """按 thirdId 主动检索 H5 舌诊报告，作为回调兜底。"""
    task = BTongueDiagnosis.query.get(task_id)
    if not task:
        return Response.error('舌诊任务不存在', 404)

    try:
        query_response = tongue_diagnosis_service.query_h5_reports(third_id=task.out_id)
        if query_response.get('code') not in (0, '0'):
            task.error_json = {
                'source': 'report_query',
                'response': query_response
            }
            db.session.commit()
            return Response.error(query_response.get('msg') or '舌诊报告检索失败', 502)

        report_row = tongue_diagnosis_service.find_report_row(query_response, task.out_id)
        if not report_row:
            task.confirm_response = {
                'source': 'report_query',
                'response': query_response,
                'message': '未查询到匹配thirdId的舌诊报告'
            }
            db.session.commit()
            return Response.success({
                'task': _task_response(task),
                'query_response': query_response
            }, '暂未查询到舌诊报告')

        _apply_tongue_report_payload(task, report_row, source='report_query')
        task.confirm_response = {
            'source': 'report_query',
            'response': query_response
        }
        db.session.commit()
        return Response.success({
            'task': _task_response(task),
            'report': report_row
        }, '舌诊报告已同步')
    except Exception as e:
        db.session.rollback()
        return Response.error(f'舌诊报告同步失败: {str(e)}', 500)


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
    return Response.success({'items': [_task_response(task) for task in tasks], 'total': len(tasks)})


@b_tongue_bp.route('/callback', methods=['POST'])
def tongue_callback():
    """第三方异步回调。成功处理后必须返回纯文本 success。"""
    payload = None
    try:
        out_id, _signature, payload, error_response = _read_callback_payload()
        if error_response:
            return error_response

        task = BTongueDiagnosis.query.filter_by(out_id=out_id).first()
        if not task:
            print(f'舌诊回调未匹配到任务: outId={out_id}; payload={payload}')
            return FlaskResponse('success', mimetype='text/plain')

        task.callback_payload = payload
        task.callback_received_at = datetime.utcnow()
        _apply_tongue_report_payload(task, payload, source='callback')

        db.session.commit()
        return FlaskResponse('success', mimetype='text/plain')
    except Exception as e:
        db.session.rollback()
        print(f'舌诊回调处理失败: {e}; payload={payload}')
        return FlaskResponse('error', status=500, mimetype='text/plain')


@b_tongue_bp.route('/hand-callback', methods=['POST'])
def hand_callback():
    """第三方手诊异步回调。协议与舌诊一致，成功处理后返回纯文本 success。"""
    payload = None
    try:
        out_id, _signature, payload, error_response = _read_callback_payload()
        if error_response:
            return error_response

        saved = _write_hand_result_to_record_and_report(out_id, payload)
        if not saved:
            print(f'手诊回调未匹配到档案: thirdId={out_id}; payload={payload}')
        db.session.commit()
        return FlaskResponse('success', mimetype='text/plain')
    except Exception as e:
        db.session.rollback()
        print(f'手诊回调处理失败: {e}; payload={payload}')
        return FlaskResponse('error', status=500, mimetype='text/plain')
