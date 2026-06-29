"""医院场景 V1.0 接口。"""

from datetime import datetime, timedelta

from flask import Blueprint, request
from sqlalchemy import func, or_

from models import (
    db,
    BFollowUpCheckin,
    BFollowUpTask,
    BHealthRecord,
    BPatient,
    BReport,
    BReportFollowupAdvice,
    Department,
    User,
)
from utils.decorators import login_required
from utils.hospital_permissions import (
    apply_patient_scope,
    can_view_patient,
    can_operate_patient,
    doctor_query,
    is_admin,
    is_department_director,
    is_doctor,
)
from utils.response import Response


hospital_bp = Blueprint('hospital', __name__, url_prefix='/api/hospital')


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        return None


def _page_params():
    try:
        page = max(int(request.args.get('page', 1)), 1)
    except ValueError:
        page = 1
    try:
        page_size = min(max(int(request.args.get('page_size', request.args.get('per_page', 20))), 1), 200)
    except ValueError:
        page_size = 20
    return page, page_size


def _optional_int(value, field_label):
    if value in (None, ''):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValueError(f'{field_label}格式错误')


def _patient_query(current_user):
    return apply_patient_scope(BPatient.query, current_user)


def _latest_report(patient_id):
    return (
        BReport.query
        .filter(BReport.patient_id == patient_id)
        .order_by(BReport.updated_at.desc(), BReport.id.desc())
        .first()
    )


def _latest_record(patient_id):
    return (
        BHealthRecord.query
        .filter(BHealthRecord.patient_id == patient_id)
        .order_by(BHealthRecord.updated_at.desc(), BHealthRecord.id.desc())
        .first()
    )


def _task_status_done(status):
    return status in {'completed', 'done', 'closed'}


def _risk_bucket(value):
    raw = (value or '').strip()
    if raw in {'高风险', '高危', 'high'}:
        return 'high'
    if raw in {'中风险', '中危', 'medium', 'mid'}:
        return 'mid'
    if raw in {'低风险', '低危', 'low'}:
        return 'low'
    return 'unknown'


def _nodule_label(value):
    labels = {
        'breast': '乳腺结节',
        'lung': '肺部结节',
        'thyroid': '甲状腺结节',
        'breast_lung': '肺部合并乳腺结节',
        'breast_thyroid': '甲状腺合并乳腺结节',
        'lung_thyroid': '肺部合并甲状腺结节',
        'triple': '三合并结节',
    }
    return labels.get(value or '', value or '其他结节')


def _patient_list_item(patient):
    latest_report = _latest_report(patient.id)
    latest_task = (
        BFollowUpTask.query
        .filter(BFollowUpTask.patient_id == patient.id)
        .order_by(BFollowUpTask.due_at.desc().nullslast(), BFollowUpTask.id.desc())
        .first()
    )
    return {
        **patient.to_dict(),
        'latest_report_id': latest_report.id if latest_report else None,
        'latest_report_status': latest_report.status if latest_report else None,
        'latest_report_code': latest_report.report_code if latest_report else None,
        'latest_report_risk_level': latest_report.risk_level if latest_report else None,
        'latest_task_id': latest_task.id if latest_task else None,
        'latest_task_status': latest_task.status if latest_task else None,
        'next_followup_at': latest_task.due_at.strftime('%Y-%m-%d %H:%M:%S') if latest_task and latest_task.due_at else None,
    }


@hospital_bp.route('/analytics/nodule-overview', methods=['GET'])
@login_required
def nodule_overview(current_user):
    patients = _patient_query(current_user).order_by(BPatient.id.asc()).all()
    patient_ids = [patient.id for patient in patients]
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)

    reports_by_patient = {}
    reports = []
    tasks_by_patient = {}
    submitted_advice_report_ids = set()

    if patient_ids:
        reports = (
            BReport.query
            .filter(BReport.patient_id.in_(patient_ids))
            .order_by(BReport.updated_at.desc(), BReport.id.desc())
            .all()
        )
        for report in reports:
            reports_by_patient.setdefault(report.patient_id, []).append(report)

        tasks = (
            BFollowUpTask.query
            .filter(BFollowUpTask.patient_id.in_(patient_ids))
            .order_by(BFollowUpTask.updated_at.desc(), BFollowUpTask.id.desc())
            .all()
        )
        for task in tasks:
            tasks_by_patient.setdefault(task.patient_id, []).append(task)

        submitted_advice_report_ids = {
            row[0] for row in BReportFollowupAdvice.query
            .filter(BReportFollowupAdvice.patient_id.in_(patient_ids), BReportFollowupAdvice.status == 'submitted')
            .with_entities(BReportFollowupAdvice.report_id)
            .all()
        }

    rows_by_type = {}
    risk_distribution = {'high': 0, 'mid': 0, 'low': 0, 'unknown': 0}
    report_status = {'not_generated': 0, 'pending_review': 0, 'pending_advice': 0, 'finalized': 0}
    followup_status = {'active': 0, 'completed': 0, 'overdue': 0, 'abnormal': 0}

    for patient in patients:
        nodule_type = patient.nodule_type or 'unknown'
        row = rows_by_type.setdefault(nodule_type, {
            'nodule_type': nodule_type,
            'type': _nodule_label(nodule_type),
            'total': 0,
            'new_today': 0,
            'high': 0,
            'mid': 0,
            'low': 0,
            'unknown_risk': 0,
            'pending_report': 0,
            'pending_review': 0,
            'pending_advice': 0,
            'finalized_report': 0,
            'active_followup': 0,
            'completed_followup': 0,
            'overdue_followup': 0,
            'abnormal': 0,
        })
        row['total'] += 1
        if patient.created_at and patient.created_at >= today_start:
            row['new_today'] += 1

        patient_reports = reports_by_patient.get(patient.id, [])
        latest_report = patient_reports[0] if patient_reports else None
        risk = _risk_bucket(latest_report.risk_level if latest_report else None)
        risk_distribution[risk] += 1
        if risk == 'high':
            row['high'] += 1
        elif risk == 'mid':
            row['mid'] += 1
        elif risk == 'low':
            row['low'] += 1
        else:
            row['unknown_risk'] += 1

        if not patient_reports:
            row['pending_report'] += 1
            report_status['not_generated'] += 1

        for report in patient_reports:
            if report.status in {'draft', 'generated', 'pending_review', 'reviewing'}:
                row['pending_review'] += 1
                report_status['pending_review'] += 1
            if report.status in {'finalized', 'published', 'archived'}:
                row['finalized_report'] += 1
                report_status['finalized'] += 1
            if report.status in {'draft', 'generated', 'pending_review', 'finalized'} and report.id not in submitted_advice_report_ids:
                row['pending_advice'] += 1
                report_status['pending_advice'] += 1

        patient_tasks = tasks_by_patient.get(patient.id, [])
        for task in patient_tasks:
            done = _task_status_done(task.status)
            if done:
                row['completed_followup'] += 1
                followup_status['completed'] += 1
            elif task.status not in {'cancelled', 'failed'}:
                row['active_followup'] += 1
                followup_status['active'] += 1
            if task.due_at and task.due_at < now and not done and task.status not in {'cancelled', 'failed'}:
                row['overdue_followup'] += 1
                followup_status['overdue'] += 1
            if task.abnormal_flag:
                row['abnormal'] += 1
                followup_status['abnormal'] += 1

    preferred_order = ['triple', 'breast_lung', 'lung_thyroid', 'breast_thyroid', 'lung', 'thyroid', 'breast']
    nodule_rows = sorted(
        rows_by_type.values(),
        key=lambda row: (preferred_order.index(row['nodule_type']) if row['nodule_type'] in preferred_order else len(preferred_order), -row['total']),
    )
    for row in nodule_rows:
        total_followups = row['active_followup'] + row['completed_followup']
        row['followup_completion_rate'] = round((row['completed_followup'] / total_followups) * 100, 1) if total_followups else 0

    nodule_distribution = [
        {
            'nodule_type': row['nodule_type'],
            'type': row['type'],
            'value': row['total'],
            'pct': round((row['total'] / len(patients)) * 100, 1) if patients else 0,
        }
        for row in nodule_rows
    ]

    return Response.success({
        'patient_count': len(patients),
        'nodule_rows': nodule_rows,
        'nodule_distribution': nodule_distribution,
        'risk_distribution': risk_distribution,
        'report_status': report_status,
        'followup_status': followup_status,
    })


@hospital_bp.route('/departments', methods=['GET'])
@login_required
def list_departments(current_user):
    departments = (
        Department.query
        .filter(Department.is_active.is_(True))
        .order_by(Department.id.asc())
        .all()
    )
    return Response.success({'departments': [item.to_dict() for item in departments]})


@hospital_bp.route('/doctors', methods=['GET'])
@login_required
def list_doctors(current_user):
    query = doctor_query()
    department_id = request.args.get('department_id')
    if department_id:
        query = query.filter(User.department_id == department_id)
    doctors = query.order_by(User.id.asc()).all()
    return Response.success({'doctors': [doctor.to_dict() for doctor in doctors]})


@hospital_bp.route('/managers', methods=['GET'])
@login_required
def list_managers(current_user):
    query = User.query.filter(User.role.in_(['health_manager', 'doctor_assistant']), User.is_active.is_(True))
    department_id = request.args.get('department_id')
    if department_id:
        query = query.filter(User.department_id == department_id)
    managers = query.order_by(User.id.asc()).all()
    return Response.success({'managers': [manager.to_dict() for manager in managers]})


@hospital_bp.route('/patients', methods=['GET'])
@login_required
def list_patients(current_user):
    query = _patient_query(current_user)

    keyword = (request.args.get('keyword') or '').strip()
    if keyword:
        like = f'%{keyword}%'
        query = query.filter(or_(BPatient.name.ilike(like), BPatient.phone.ilike(like), BPatient.patient_code.ilike(like)))

    for arg_name, column in (
        ('department_id', BPatient.department_id),
        ('doctor_id', BPatient.primary_doctor_id),
        ('manager_id', BPatient.manager_id),
        ('risk_level', None),
        ('status', BPatient.status),
        ('nodule_type', BPatient.nodule_type),
    ):
        value = request.args.get(arg_name)
        if not value:
            continue
        if arg_name == 'risk_level':
            # 风险等级主要来自报告/任务，患者表暂不强制落风险字段；这里保留兼容，不过滤。
            continue
        query = query.filter(column == value)

    page, page_size = _page_params()
    total = query.count()
    patients = (
        query
        .order_by(BPatient.updated_at.desc(), BPatient.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return Response.success({
        'patients': [_patient_list_item(patient) for patient in patients],
        'total': total,
        'page': page,
        'page_size': page_size,
    })


@hospital_bp.route('/patients/<int:patient_id>', methods=['GET'])
@login_required
def patient_detail(current_user, patient_id):
    patient = BPatient.query.get(patient_id)
    if not patient:
        return Response.error('患者不存在', 404)
    if not can_view_patient(current_user, patient):
        return Response.error('无权查看该患者', 403)

    records = (
        BHealthRecord.query
        .filter(BHealthRecord.patient_id == patient_id)
        .order_by(BHealthRecord.updated_at.desc(), BHealthRecord.id.desc())
        .limit(10)
        .all()
    )
    reports = (
        BReport.query
        .filter(BReport.patient_id == patient_id)
        .order_by(BReport.updated_at.desc(), BReport.id.desc())
        .limit(20)
        .all()
    )
    tasks = (
        BFollowUpTask.query
        .filter(BFollowUpTask.patient_id == patient_id)
        .order_by(BFollowUpTask.created_at.desc(), BFollowUpTask.id.desc())
        .limit(50)
        .all()
    )
    advices = (
        BReportFollowupAdvice.query
        .filter(BReportFollowupAdvice.patient_id == patient_id)
        .order_by(BReportFollowupAdvice.updated_at.desc(), BReportFollowupAdvice.id.desc())
        .all()
    )
    latest_record = records[0] if records else None
    nodules = []
    if latest_record:
        record_dict = latest_record.to_dict()
        nodules.append({
            'nodule_type': patient.nodule_type,
            'birads_level': record_dict.get('birads_level'),
            'nodule_location': record_dict.get('nodule_location'),
            'nodule_size': record_dict.get('nodule_size'),
            'lung_rads_level': record_dict.get('lung_rads_level'),
            'lung_nodule_location': record_dict.get('lung_nodule_location'),
            'lung_nodule_size': record_dict.get('lung_nodule_size'),
            'thyroid_tirads_level': record_dict.get('thyroid_tirads_level'),
            'thyroid_nodule_location': record_dict.get('thyroid_nodule_location'),
            'thyroid_nodule_size': record_dict.get('thyroid_nodule_size'),
        })

    return Response.success({
        'patient': patient.to_dict(),
        'nodules': nodules,
        'records': [record.to_dict() for record in records],
        'reports': [report.to_dict() for report in reports],
        'followup_tasks': [task.to_dict() for task in tasks],
        'followup_advices': [advice.to_dict() for advice in advices],
    })


@hospital_bp.route('/patients/<int:patient_id>', methods=['PUT'])
@login_required
def update_patient_hospital_fields(current_user, patient_id):
    patient = BPatient.query.get(patient_id)
    if not patient:
        return Response.error('患者不存在', 404)
    if not can_view_patient(current_user, patient):
        return Response.error('无权查看该患者', 403)
    if not can_operate_patient(current_user):
        return Response.error('仅健康管理师、医生助手或管理员可修改患者信息', 403)

    data = request.get_json(silent=True) or {}
    text_fields = {
        'name': 50,
        'gender': 10,
        'phone': 20,
        'wechat_id': 50,
        'nodule_type': 50,
        'source_channel': 50,
        'status': 20,
    }
    for field, max_len in text_fields.items():
        if field not in data:
            continue
        value = data.get(field)
        if value is None:
            setattr(patient, field, None)
        else:
            setattr(patient, field, str(value).strip()[:max_len])

    if 'age' in data:
        try:
            patient.age = int(data.get('age')) if data.get('age') not in (None, '') else None
        except (TypeError, ValueError):
            return Response.error('年龄格式错误', 400)

    if 'department_id' in data:
        try:
            department_id = _optional_int(data.get('department_id'), '所属科室')
        except ValueError as e:
            return Response.error(str(e), 400)
        if department_id:
            department = Department.query.filter_by(id=department_id, is_active=True).first()
            if not department:
                return Response.error('所属科室不存在或已停用', 400)
        patient.department_id = department_id

    if 'primary_doctor_id' in data:
        try:
            doctor_id = _optional_int(data.get('primary_doctor_id'), '主要负责医生')
        except ValueError as e:
            return Response.error(str(e), 400)
        if doctor_id:
            doctor = doctor_query().filter(User.id == doctor_id).first()
            if not doctor:
                return Response.error('主要负责医生不存在或不可用', 400)
            if patient.department_id and doctor.department_id and doctor.department_id != patient.department_id:
                return Response.error('主要负责医生不属于患者当前科室', 400)
        patient.primary_doctor_id = doctor_id

    if 'manager_id' in data:
        try:
            manager_id = _optional_int(data.get('manager_id'), '健康管理师/医生助手')
        except ValueError as e:
            return Response.error(str(e), 400)
        if manager_id:
            manager = User.query.filter(
                User.id == manager_id,
                User.role.in_(['health_manager', 'doctor_assistant']),
                User.is_active.is_(True),
            ).first()
            if not manager:
                return Response.error('健康管理师/医生助手不存在或不可用', 400)
        patient.manager_id = manager_id

    patient.updated_at = datetime.utcnow()
    db.session.commit()
    return Response.success({'patient': patient.to_dict()}, '患者信息已保存')


def _get_report_for_advice(current_user, report_id):
    report = BReport.query.get(report_id)
    if not report:
        return None, Response.error('报告不存在', 404)
    patient = BPatient.query.get(report.patient_id)
    if not patient:
        return None, Response.error('患者不存在', 404)
    if not can_view_patient(current_user, patient):
        return None, Response.error('无权查看该报告', 403)
    if not (is_doctor(current_user) or is_admin(current_user)):
        return None, Response.error('仅医生可填写报告随访建议', 403)
    return report, None


def _save_report_advice(current_user, report_id, status):
    report, error = _get_report_for_advice(current_user, report_id)
    if error:
        return error

    data = request.get_json(silent=True) or {}
    advice_content = (data.get('advice_content') or '').strip()
    suggested_next_followup_at = _parse_date(data.get('suggested_next_followup_at'))
    if status == 'submitted' and not advice_content:
        return Response.error('报告随访建议不能为空', 400)

    advice = (
        BReportFollowupAdvice.query
        .filter_by(report_id=report.id, doctor_id=current_user.id)
        .order_by(BReportFollowupAdvice.id.desc())
        .first()
    )
    if not advice:
        advice = BReportFollowupAdvice(
            patient_id=report.patient_id,
            report_id=report.id,
            doctor_id=current_user.id,
        )
        db.session.add(advice)

    advice.advice_content = advice_content
    advice.suggested_next_followup_at = suggested_next_followup_at
    advice.status = status
    advice.updated_at = datetime.utcnow()
    db.session.commit()
    return Response.success({'advice': advice.to_dict()}, '报告随访建议已保存' if status == 'draft' else '报告随访建议已提交')


@hospital_bp.route('/health-reports/<int:report_id>/followup-advice/draft', methods=['POST'])
@login_required
def save_report_followup_advice_draft(current_user, report_id):
    return _save_report_advice(current_user, report_id, 'draft')


@hospital_bp.route('/health-reports/<int:report_id>/followup-advice/submit', methods=['POST'])
@login_required
def submit_report_followup_advice(current_user, report_id):
    return _save_report_advice(current_user, report_id, 'submitted')


@hospital_bp.route('/health-reports/<int:report_id>/followup-advice', methods=['GET'])
@login_required
def get_report_followup_advice(current_user, report_id):
    report = BReport.query.get(report_id)
    if not report:
        return Response.error('报告不存在', 404)
    patient = BPatient.query.get(report.patient_id)
    if not patient or not can_view_patient(current_user, patient):
        return Response.error('无权查看该报告', 403)
    advices = (
        BReportFollowupAdvice.query
        .filter(BReportFollowupAdvice.report_id == report_id)
        .order_by(BReportFollowupAdvice.updated_at.desc(), BReportFollowupAdvice.id.desc())
        .all()
    )
    return Response.success({'advices': [advice.to_dict() for advice in advices]})


@hospital_bp.route('/doctor-workbench/summary', methods=['GET'])
@login_required
def doctor_workbench_summary(current_user):
    if not is_doctor(current_user):
        return Response.error('仅医生可查看医生工作台', 403)

    patient_query = BPatient.query.filter(BPatient.primary_doctor_id == current_user.id)
    patient_ids = [row[0] for row in patient_query.with_entities(BPatient.id).all()]
    high_risk_count = 0
    pending_advice_count = 0
    recent_review_count = 0
    if patient_ids:
        high_risk_count = BReport.query.filter(BReport.patient_id.in_(patient_ids), BReport.risk_level.in_(['高风险', '高危', 'high'])).count()
        advice_report_ids = [
            row[0] for row in BReportFollowupAdvice.query
            .filter(BReportFollowupAdvice.doctor_id == current_user.id, BReportFollowupAdvice.status == 'submitted')
            .with_entities(BReportFollowupAdvice.report_id)
            .all()
        ]
        report_query = BReport.query.filter(BReport.patient_id.in_(patient_ids))
        if advice_report_ids:
            report_query = report_query.filter(~BReport.id.in_(advice_report_ids))
        pending_advice_count = report_query.filter(BReport.status.in_(['draft', 'generated', 'pending_review', 'finalized'])).count()
        recent_review_count = BFollowUpTask.query.filter(
            BFollowUpTask.patient_id.in_(patient_ids),
            BFollowUpTask.due_at >= datetime.utcnow(),
            BFollowUpTask.due_at <= datetime.utcnow() + timedelta(days=30),
        ).count()

    return Response.success({
        'patient_count': patient_query.count(),
        'pending_advice_count': pending_advice_count,
        'high_risk_count': high_risk_count,
        'recent_review_count': recent_review_count,
    })


@hospital_bp.route('/doctor-workbench/patients', methods=['GET'])
@login_required
def doctor_workbench_patients(current_user):
    if not is_doctor(current_user):
        return Response.error('仅医生可查看医生工作台', 403)
    patients = (
        BPatient.query
        .filter(BPatient.primary_doctor_id == current_user.id)
        .order_by(BPatient.updated_at.desc(), BPatient.id.desc())
        .limit(100)
        .all()
    )
    return Response.success({'patients': [_patient_list_item(patient) for patient in patients]})


@hospital_bp.route('/doctor-workbench/pending-advice', methods=['GET'])
@login_required
def doctor_pending_advice(current_user):
    if not is_doctor(current_user):
        return Response.error('仅医生可查看医生工作台', 403)
    patient_ids = [row[0] for row in BPatient.query.filter(BPatient.primary_doctor_id == current_user.id).with_entities(BPatient.id).all()]
    if not patient_ids:
        return Response.success({'reports': []})
    submitted_report_ids = [
        row[0] for row in BReportFollowupAdvice.query
        .filter(BReportFollowupAdvice.doctor_id == current_user.id, BReportFollowupAdvice.status == 'submitted')
        .with_entities(BReportFollowupAdvice.report_id)
        .all()
    ]
    query = BReport.query.filter(BReport.patient_id.in_(patient_ids))
    if submitted_report_ids:
        query = query.filter(~BReport.id.in_(submitted_report_ids))
    reports = query.order_by(BReport.updated_at.desc(), BReport.id.desc()).limit(100).all()
    rows = []
    for report in reports:
        item = report.to_dict()
        patient = BPatient.query.get(report.patient_id)
        item['patient'] = patient.to_dict() if patient else None
        item['patient_name'] = patient.name if patient else ''
        rows.append(item)
    return Response.success({'reports': rows})


@hospital_bp.route('/department-dashboard/summary', methods=['GET'])
@login_required
def department_dashboard_summary(current_user):
    if not is_department_director(current_user):
        return Response.error('仅科室主任可查看科室看板', 403)
    if not current_user.department_id:
        return Response.error('当前用户未配置科室', 400)

    patient_query = BPatient.query.filter(BPatient.department_id == current_user.department_id)
    patient_ids = [row[0] for row in patient_query.with_entities(BPatient.id).all()]
    now = datetime.utcnow()
    month_start = datetime(now.year, now.month, 1)
    task_query = BFollowUpTask.query.filter(BFollowUpTask.patient_id.in_(patient_ids)) if patient_ids else BFollowUpTask.query.filter(False)
    total_tasks = task_query.count()
    completed_tasks = len([task for task in task_query.all() if _task_status_done(task.status)])
    followup_completion_rate = round((completed_tasks / total_tasks) * 100, 1) if total_tasks else 0

    risk_rows = []
    if patient_ids:
        risk_rows = (
            BReport.query
            .filter(BReport.patient_id.in_(patient_ids))
            .with_entities(BReport.risk_level, func.count(BReport.id))
            .group_by(BReport.risk_level)
            .all()
        )
    risk_distribution = {risk or '未评估': count for risk, count in risk_rows}

    return Response.success({
        'department_id': current_user.department_id,
        'patient_count': patient_query.count(),
        'new_this_month': patient_query.filter(BPatient.created_at >= month_start).count(),
        'risk_distribution': risk_distribution,
        'followup_completion_rate': followup_completion_rate,
        'overdue_task_count': task_query.filter(BFollowUpTask.due_at < now, ~BFollowUpTask.status.in_(['completed', 'done', 'closed', 'cancelled'])).count(),
        'pending_report_count': BReport.query.filter(BReport.patient_id.in_(patient_ids), BReport.status.in_(['draft', 'generated', 'pending_review'])).count() if patient_ids else 0,
    })


@hospital_bp.route('/department-dashboard/doctors', methods=['GET'])
@login_required
def department_dashboard_doctors(current_user):
    if not is_department_director(current_user):
        return Response.error('仅科室主任可查看科室看板', 403)
    doctors = doctor_query().filter(User.department_id == current_user.department_id).all()
    rows = []
    for doctor in doctors:
        doctor_patient_query = BPatient.query.filter(
            BPatient.department_id == current_user.department_id,
            BPatient.primary_doctor_id == doctor.id,
        )
        patient_ids = [row[0] for row in doctor_patient_query.with_entities(BPatient.id).all()]
        patient_count = len(patient_ids)
        pending_advice_count = 0
        high_risk_count = 0
        followup_completion_rate = 0
        if patient_ids:
            submitted_report_ids = [
                row[0] for row in BReportFollowupAdvice.query
                .filter(BReportFollowupAdvice.doctor_id == doctor.id, BReportFollowupAdvice.status == 'submitted')
                .with_entities(BReportFollowupAdvice.report_id)
                .all()
            ]
            report_query = BReport.query.filter(BReport.patient_id.in_(patient_ids))
            if submitted_report_ids:
                report_query = report_query.filter(~BReport.id.in_(submitted_report_ids))
            pending_advice_count = report_query.filter(BReport.status.in_(['draft', 'generated', 'pending_review', 'finalized'])).count()
            high_risk_count = BReport.query.filter(BReport.patient_id.in_(patient_ids), BReport.risk_level.in_(['高风险', '高危', 'high'])).count()
            task_query = BFollowUpTask.query.filter(BFollowUpTask.patient_id.in_(patient_ids))
            total_tasks = task_query.count()
            completed_tasks = len([task for task in task_query.all() if _task_status_done(task.status)])
            followup_completion_rate = round((completed_tasks / total_tasks) * 100, 1) if total_tasks else 0
        rows.append({
            'doctor': doctor.to_dict(),
            'patient_count': patient_count,
            'pending_advice_count': pending_advice_count,
            'high_risk_count': high_risk_count,
            'followup_completion_rate': followup_completion_rate,
        })
    return Response.success({'doctors': rows})


@hospital_bp.route('/department-dashboard/abnormal-patients', methods=['GET'])
@login_required
def department_dashboard_abnormal_patients(current_user):
    if not is_department_director(current_user):
        return Response.error('仅科室主任可查看科室看板', 403)
    patient_ids = [
        row[0] for row in BPatient.query
        .filter(BPatient.department_id == current_user.department_id)
        .with_entities(BPatient.id)
        .all()
    ]
    if not patient_ids:
        return Response.success({'patients': []})
    tasks = (
        BFollowUpTask.query
        .filter(BFollowUpTask.patient_id.in_(patient_ids), BFollowUpTask.abnormal_flag.is_(True))
        .order_by(BFollowUpTask.updated_at.desc(), BFollowUpTask.id.desc())
        .limit(50)
        .all()
    )
    rows = []
    for task in tasks:
        latest_checkin = (
            BFollowUpCheckin.query
            .filter(BFollowUpCheckin.task_id == task.id)
            .order_by(BFollowUpCheckin.submitted_at.desc(), BFollowUpCheckin.id.desc())
            .first()
        )
        rows.append({
            'patient': task.patient.to_dict() if task.patient else None,
            'task': task.to_dict(),
            'abnormal_reason': task.abnormal_reason,
            'latest_followup_at': (
                latest_checkin.submitted_at.strftime('%Y-%m-%d %H:%M:%S')
                if latest_checkin and latest_checkin.submitted_at
                else task.updated_at.strftime('%Y-%m-%d %H:%M:%S') if task.updated_at else None
            ),
        })
    return Response.success({'patients': rows})
