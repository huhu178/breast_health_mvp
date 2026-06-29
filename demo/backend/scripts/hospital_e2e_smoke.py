"""医院场景端到端冒烟测试。

覆盖链路：
医生看待填写报告建议 -> 医生提交报告随访建议 -> 健康管理师创建并发送随访任务
-> 小程序提交打卡 -> B端查看打卡记录。
"""

from datetime import datetime
from io import BytesIO
from pathlib import Path
import os
import sys


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app import create_app
from models import (
    db,
    BFollowUpCheckin,
    BFollowUpEvent,
    BFollowUpMessage,
    BFollowUpTask,
    BHealthRecord,
    BPatient,
    BReport,
    BReportFollowupAdvice,
    Department,
    MiniprogramImagingUpload,
    User,
)


def _assert_ok(resp, label, expected=(200, 201)):
    body = resp.get_json(silent=True) or {}
    if resp.status_code not in expected or body.get('success') is False:
        raise AssertionError(f'{label} failed: {resp.status_code} {body}')
    print(f'[OK] {label}: {resp.status_code} {body.get("message", "")}')
    return body


def _login_as(app, user):
    client = app.test_client()
    with client.session_transaction() as sess:
        sess['user_id'] = user.id
        sess['username'] = user.username
    return client


def _cleanup(patient_id, extra_patient_id=None, extra_user_ids=None, extra_department_id=None):
    extra_user_ids = extra_user_ids or []

    for cleanup_patient_id in [patient_id, extra_patient_id]:
        if cleanup_patient_id:
            _cleanup_patient(cleanup_patient_id)

    if extra_user_ids:
        User.query.filter(User.id.in_(extra_user_ids)).delete(synchronize_session=False)
    if extra_department_id:
        Department.query.filter(Department.id == extra_department_id).delete(synchronize_session=False)
    db.session.commit()


def _cleanup_patient(patient_id):
    task_ids = [
        row[0]
        for row in BFollowUpTask.query
        .filter(BFollowUpTask.patient_id == patient_id)
        .with_entities(BFollowUpTask.id)
        .all()
    ]
    report_ids = [
        row[0]
        for row in BReport.query
        .filter(BReport.patient_id == patient_id)
        .with_entities(BReport.id)
        .all()
    ]
    record_ids = [
        row[0]
        for row in BHealthRecord.query
        .filter(BHealthRecord.patient_id == patient_id)
        .with_entities(BHealthRecord.id)
        .all()
    ]

    if task_ids:
        BFollowUpTask.query.filter(BFollowUpTask.id.in_(task_ids)).update(
            {BFollowUpTask.last_message_id: None},
            synchronize_session=False,
        )
        db.session.flush()
        BFollowUpEvent.query.filter(BFollowUpEvent.task_id.in_(task_ids)).delete(synchronize_session=False)
        BFollowUpCheckin.query.filter(BFollowUpCheckin.task_id.in_(task_ids)).delete(synchronize_session=False)
        BFollowUpMessage.query.filter(BFollowUpMessage.task_id.in_(task_ids)).delete(synchronize_session=False)
        BFollowUpTask.query.filter(BFollowUpTask.id.in_(task_ids)).delete(synchronize_session=False)

    if report_ids:
        BReportFollowupAdvice.query.filter(BReportFollowupAdvice.report_id.in_(report_ids)).delete(synchronize_session=False)
        BReport.query.filter(BReport.id.in_(report_ids)).delete(synchronize_session=False)

    if record_ids:
        BHealthRecord.query.filter(BHealthRecord.id.in_(record_ids)).delete(synchronize_session=False)

    uploads = [
        upload for upload in MiniprogramImagingUpload.query.all()
        if isinstance(upload.extracted_data, dict)
        and (
            upload.extracted_data.get('source') == 'mini_program_followup_smoke'
            or upload.extracted_data.get('patient_id') == patient_id
        )
    ]
    for upload in uploads:
        try:
            if upload.file_path and os.path.exists(upload.file_path):
                os.remove(upload.file_path)
        except Exception:
            pass
        db.session.delete(upload)

    BPatient.query.filter(BPatient.id == patient_id).delete(synchronize_session=False)


def run():
    app = create_app()
    patient_id = None
    extra_patient_id = None
    extra_department_id = None
    extra_user_ids = []

    with app.app_context():
        dept = Department.query.filter_by(code='BREAST').first() or Department.query.order_by(Department.id.asc()).first()
        doctor = User.query.filter_by(username='doctor_li').first() or User.query.filter_by(role='doctor').first()
        director = User.query.filter_by(username='director_breast').first() or User.query.filter_by(role='department_director').first()
        manager = (
            User.query.filter_by(username='assistant_chen').first()
            or User.query.filter(User.role.in_(['health_manager', 'doctor_assistant', 'admin'])).first()
        )
        if not all([dept, doctor, director, manager]):
            raise RuntimeError('缺少科室/医生/主任/健康管理师测试账号，请先运行 init_hospital_scene_data.py')

        try:
            code = f'E2E{datetime.now().strftime("%Y%m%d%H%M%S")}'
            manager_client = _login_as(app, manager)
            patient_resp = _assert_ok(
                manager_client.post(
                    '/api/b/patients',
                    json={
                        'name': '端到端测试患者',
                        'age': 45,
                        'gender': '女',
                        'phone': '13900000000',
                        'nodule_type': 'breast',
                        'department_id': dept.id,
                        'primary_doctor_id': doctor.id,
                        'manager_id': manager.id,
                        'source_channel': 'hospital_e2e_smoke',
                    },
                ),
                '新增患者同步医院字段',
            )
            patient = BPatient.query.get(patient_resp['data']['id'])
            if not patient:
                raise AssertionError('新增患者接口未返回有效患者')
            if patient.department_id != dept.id or patient.primary_doctor_id != doctor.id or patient.manager_id != manager.id:
                raise AssertionError('新增患者医院字段未正确入库')
            patient_id = patient.id

            record = BHealthRecord(
                patient_id=patient.id,
                record_code=f'REC{code}',
                age=45,
                phone='13900000000',
                birads_level='3',
                nodule_location='左乳外上象限',
                nodule_size='8mm',
                created_by=manager.id,
            )
            db.session.add(record)
            db.session.flush()

            report = BReport(
                patient_id=patient.id,
                record_id=record.id,
                report_code=f'RPT{code}',
                status='finalized',
                risk_level='中危',
                report_summary='端到端测试报告摘要',
                generated_by=manager.id,
                reviewed_by=manager.id,
                reviewed_at=datetime.utcnow(),
                source_channel='hospital_e2e_smoke',
            )
            db.session.add(report)
            db.session.commit()

            other_dept = Department(
                name=f'端到端权限测试科室{code}',
                code=f'E2E_SCOPE_{code}',
                hospital_name='示例医院',
                is_active=True,
            )
            db.session.add(other_dept)
            db.session.flush()
            extra_department_id = other_dept.id

            other_doctor = User(
                username=f'e2e_scope_doctor_{code}',
                password_hash='hospital-e2e-smoke',
                real_name='权限测试医生',
                role='doctor',
                department_id=other_dept.id,
                is_active=True,
            )
            db.session.add(other_doctor)
            db.session.flush()
            extra_user_ids.append(other_doctor.id)

            other_patient = BPatient(
                patient_code=f'SCOPE{code}',
                name='越权测试患者',
                age=48,
                gender='女',
                phone='13900000001',
                nodule_type='lung',
                department_id=other_dept.id,
                primary_doctor_id=other_doctor.id,
                manager_id=manager.id,
                source_channel='hospital_e2e_scope_smoke',
                status='active',
            )
            db.session.add(other_patient)
            db.session.commit()
            extra_patient_id = other_patient.id

            _assert_ok(
                manager_client.put(
                    f'/api/hospital/patients/{patient.id}',
                    json={
                        'name': patient.name,
                        'gender': patient.gender,
                        'age': patient.age,
                        'phone': patient.phone,
                        'source_channel': patient.source_channel,
                        'nodule_type': patient.nodule_type,
                        'department_id': dept.id,
                        'primary_doctor_id': doctor.id,
                        'manager_id': manager.id,
                        'status': patient.status,
                    },
                ),
                '健康管理师保存患者医院字段',
            )

            doctor_client = _login_as(app, doctor)
            forbidden = doctor_client.put(f'/api/hospital/patients/{patient.id}', json={'name': '医生不应修改'})
            if forbidden.status_code != 403:
                raise AssertionError(f'医生修改患者信息应被拒绝: {forbidden.status_code} {forbidden.get_json(silent=True)}')
            print('[OK] 医生修改患者信息被拒绝: 403')
            _assert_ok(doctor_client.get(f'/api/hospital/patients/{patient.id}'), '医生查看本人患者详情')
            forbidden = doctor_client.get(f'/api/hospital/patients/{other_patient.id}')
            if forbidden.status_code != 403:
                raise AssertionError(f'医生查看其他医生患者应被拒绝: {forbidden.status_code} {forbidden.get_json(silent=True)}')
            print('[OK] 医生查看其他医生患者被拒绝: 403')
            scoped = _assert_ok(doctor_client.get('/api/hospital/patients?page_size=200'), '医生患者列表数据范围')
            scoped_ids = [item['id'] for item in scoped['data']['patients']]
            if patient.id not in scoped_ids or other_patient.id in scoped_ids:
                raise AssertionError('医生患者列表数据范围错误')
            print('[OK] 医生患者列表仅包含本人患者')
            doctor_overview = _assert_ok(doctor_client.get('/api/hospital/analytics/nodule-overview'), '医生结节看板聚合数据')
            if doctor_overview['data']['patient_count'] != scoped['data']['total']:
                raise AssertionError('医生结节看板数据范围错误')
            print('[OK] 医生结节看板仅汇总本人患者')
            _assert_ok(doctor_client.get('/api/hospital/doctor-workbench/summary'), '医生工作台概览')
            pending = _assert_ok(doctor_client.get('/api/hospital/doctor-workbench/pending-advice'), '医生待填写建议')
            pending_ids = [item['id'] for item in pending['data']['reports']]
            if report.id not in pending_ids:
                raise AssertionError('医生待填写建议列表未包含测试报告')
            _assert_ok(
                doctor_client.post(
                    f'/api/hospital/health-reports/{report.id}/followup-advice/submit',
                    json={
                        'advice_content': '建议 6 个月后复查乳腺超声，并保持随访。',
                        'suggested_next_followup_at': '2026-12-25',
                    },
                ),
                '医生提交报告随访建议',
            )

            director_client = _login_as(app, director)
            forbidden = director_client.put(f'/api/hospital/patients/{patient.id}', json={'name': '主任不应修改'})
            if forbidden.status_code != 403:
                raise AssertionError(f'科室主任修改患者信息应被拒绝: {forbidden.status_code} {forbidden.get_json(silent=True)}')
            print('[OK] 科室主任修改患者信息被拒绝: 403')
            _assert_ok(director_client.get(f'/api/hospital/patients/{patient.id}'), '科室主任查看本科室患者详情')
            forbidden = director_client.get(f'/api/hospital/patients/{other_patient.id}')
            if forbidden.status_code != 403:
                raise AssertionError(f'科室主任查看其他科室患者应被拒绝: {forbidden.status_code} {forbidden.get_json(silent=True)}')
            print('[OK] 科室主任查看其他科室患者被拒绝: 403')
            scoped = _assert_ok(director_client.get('/api/hospital/patients?page_size=200'), '科室主任患者列表数据范围')
            scoped_ids = [item['id'] for item in scoped['data']['patients']]
            if patient.id not in scoped_ids or other_patient.id in scoped_ids:
                raise AssertionError('科室主任患者列表数据范围错误')
            print('[OK] 科室主任患者列表仅包含本科室患者')
            director_overview = _assert_ok(director_client.get('/api/hospital/analytics/nodule-overview'), '科室主任结节看板聚合数据')
            if director_overview['data']['patient_count'] != scoped['data']['total']:
                raise AssertionError('科室主任结节看板数据范围错误')
            print('[OK] 科室主任结节看板仅汇总本科室患者')
            _assert_ok(director_client.get('/api/hospital/department-dashboard/summary'), '科室主任看板概览')
            _assert_ok(director_client.get('/api/hospital/department-dashboard/abnormal-patients'), '科室主任异常患者')

            forbidden = doctor_client.post(f'/api/b/followup/tasks/from-report/{report.id}', json={})
            if forbidden.status_code != 403:
                raise AssertionError(f'医生创建随访任务应被拒绝: {forbidden.status_code} {forbidden.get_json(silent=True)}')
            print('[OK] 医生创建随访任务被拒绝: 403')

            forbidden = director_client.post(f'/api/b/followup/tasks/from-report/{report.id}', json={})
            if forbidden.status_code != 403:
                raise AssertionError(f'科室主任创建随访任务应被拒绝: {forbidden.status_code} {forbidden.get_json(silent=True)}')
            print('[OK] 科室主任创建随访任务被拒绝: 403')

            task_resp = _assert_ok(
                manager_client.post(f'/api/b/followup/tasks/from-report/{report.id}', json={}),
                '健康管理师创建报告后随访任务',
            )
            task_id = task_resp['data']['id']
            task_code = task_resp['data']['task_code']
            payload = task_resp['data'].get('task_payload') or {}
            if '建议 6 个月后复查乳腺超声' not in (payload.get('doctor_followup_advice_content') or ''):
                raise AssertionError('报告后随访任务未带入医生报告随访建议')
            print('[OK] 报告后随访任务已带入医生建议')
            _assert_ok(
                manager_client.post(
                    f'/api/b/followup/tasks/{task_id}/send',
                    json={'content': '请完成本次报告后随访打卡。'},
                ),
                '健康管理师发送随访任务',
            )

            public_client = app.test_client()
            _assert_ok(public_client.get(f'/api/miniprogram/followup/tasks/{task_code}'), '小程序获取随访任务')
            upload_resp = _assert_ok(
                public_client.post(
                    f'/api/miniprogram/followup/tasks/{task_code}/files',
                    data={'file': (BytesIO(b'fake image smoke'), 'followup-smoke.jpg')},
                    content_type='multipart/form-data',
                ),
                '小程序上传复查资料',
            )
            upload_id = upload_resp['data']['upload_id']
            upload = MiniprogramImagingUpload.query.get(upload_id)
            upload.extracted_data = {
                **(upload.extracted_data or {}),
                'source': 'mini_program_followup_smoke',
            }
            db.session.commit()
            _assert_ok(
                public_client.post(
                    f'/api/miniprogram/followup/tasks/{task_code}/submit',
                    json={
                        'checkin_type': 'symptom_checkin',
                        'content_text': '已完成复查，目前无明显不适。',
                        'structured_data': {'复查结果': '稳定'},
                        'uploaded_files': [
                            {
                                'upload_id': upload_id,
                                'file_name': '复查报告.jpg',
                                'file_type': 'image',
                                'file_path': upload_resp['data']['file_path'],
                            }
                        ],
                        'analyze': False,
                    },
                ),
                '小程序提交随访打卡',
            )
            duplicate = public_client.post(
                f'/api/miniprogram/followup/tasks/{task_code}/submit',
                json={'checkin_type': 'symptom_checkin', 'content_text': '重复提交', 'analyze': False},
            )
            if duplicate.status_code != 409:
                raise AssertionError(f'重复提交应被拒绝: {duplicate.status_code} {duplicate.get_json(silent=True)}')
            print('[OK] 小程序重复提交被拒绝: 409')

            _assert_ok(manager_client.get(f'/api/b/followup/tasks/{task_id}'), 'B端查看随访任务')
            checkins = _assert_ok(manager_client.get(f'/api/b/followup/tasks/{task_id}/checkins'), 'B端查看随访打卡')
            if not checkins['data']:
                raise AssertionError('B端任务打卡列表为空')

            print('[OK] 医院场景端到端冒烟测试通过')
        finally:
            _cleanup(patient_id, extra_patient_id, extra_user_ids, extra_department_id)
            print('[OK] 临时测试数据已清理')


if __name__ == '__main__':
    run()
