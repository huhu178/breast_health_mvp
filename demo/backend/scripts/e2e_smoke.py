#!/usr/bin/env python3
"""End-to-end smoke test for the B-side patient/report/follow-up flow.

This script uses Flask's test client against the configured local database.
It monkeypatches the LLM helper calls with deterministic content so the smoke
test does not require external model/network access.
"""

import argparse
import os
import sys
import time

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from werkzeug.security import generate_password_hash

from app import app
from models import BPatient, User, db


SMOKE_USERNAME = 'smoke_admin'
SMOKE_PASSWORD = 'Smoke@123456'


def patch_llm_helpers():
    import routes.llm_helpers as helpers

    def fake_recommendations(patient_data, matched_knowledge):
        return {
            'recommendations': [
                {
                    'category': '复查随访',
                    'recommendation': '按风险分层完成复查，并保留影像资料。',
                    'is_approved': False,
                },
                {
                    'category': '生活方式',
                    'recommendation': '保持规律作息，记录症状变化。',
                    'is_approved': False,
                },
            ]
        }

    def fake_imaging_conclusion(patient_data, tree_result, matched_knowledge, nodule_type='breast'):
        return {
            'conclusion': '本次冒烟测试生成固定影像学结论。结构化分级提示需要进入健康管理复核流程。',
            'risk_warning': '该风险提示由冒烟测试固定生成，仅用于验证报告生成、审核和锁定链路。',
        }

    helpers.generate_recommendations_by_category = fake_recommendations
    helpers.generate_imaging_conclusion_with_llm = fake_imaging_conclusion


def expect_success(resp, label, expected_status=None):
    payload = resp.get_json(silent=True) or {}
    if expected_status and resp.status_code != expected_status:
        raise AssertionError(f'{label}: expected HTTP {expected_status}, got {resp.status_code}: {payload}')
    if resp.status_code >= 400 or payload.get('success') is False:
        raise AssertionError(f'{label}: failed HTTP {resp.status_code}: {payload}')
    print(f'[OK] {label}')
    return payload.get('data', payload)


def expect_failure(resp, label, expected_status=None):
    payload = resp.get_json(silent=True) or {}
    if expected_status and resp.status_code != expected_status:
        raise AssertionError(f'{label}: expected HTTP {expected_status}, got {resp.status_code}: {payload}')
    if resp.status_code < 400 and payload.get('success') is not False:
        raise AssertionError(f'{label}: expected failure, got HTTP {resp.status_code}: {payload}')
    print(f'[OK] {label}')
    return payload


def ensure_smoke_user():
    user = User.query.filter_by(username=SMOKE_USERNAME).first()
    if not user:
        user = User(
            username=SMOKE_USERNAME,
            password_hash=generate_password_hash(SMOKE_PASSWORD),
            real_name='冒烟测试管理员',
            role='health_manager',
            is_active=True,
        )
        db.session.add(user)
        db.session.commit()
    elif not user.password_hash:
        user.password_hash = generate_password_hash(SMOKE_PASSWORD)
        user.is_active = True
        db.session.commit()
    return user


def run_smoke(keep=False):
    patch_llm_helpers()
    patient_id = None

    with app.app_context():
        ensure_smoke_user()

    with app.test_client() as client:
        expect_success(
            client.post('/api/auth/login', json={'username': SMOKE_USERNAME, 'password': SMOKE_PASSWORD}),
            '登录测试账号'
        )

        suffix = str(int(time.time()))[-6:]
        patient = expect_success(
            client.post('/api/b/patients', json={
                'name': f'冒烟患者{suffix}',
                'age': 46,
                'gender': '女',
                'phone': f'199{suffix}00',
                'nodule_type': 'breast',
                'source_channel': 'smoke',
            }),
            '创建患者',
            expected_status=201
        )
        patient_id = patient['id']

        record = expect_success(
            client.post('/api/b/records', json={
                'patient_id': patient_id,
                'age': 46,
                'height': 165,
                'weight': 58,
                'phone': patient['phone'],
                'birads_level': '4A',
                'nodule_size': '12x8mm',
                'nodule_quantity': '单发',
                'symptoms': ['疼痛'],
                'family_history': ['无'],
                'breast_discovery_date': '2026-05-01',
            }),
            '创建健康档案',
            expected_status=201
        )
        record_id = record['id']

        report = expect_success(
            client.post('/api/b/reports/generate', json={'record_id': record_id}),
            '生成健康报告',
            expected_status=201
        )
        report_id = report['report_id']

        detail = expect_success(client.get(f'/api/b/reports/{report_id}'), '查看报告详情')
        assert detail['risk_level'] == '高风险', detail
        assert detail['risk_source'] == 'imaging_grade', detail
        assert detail.get('report_html'), 'report_html should exist'
        print('[OK] 风险分层元信息')

        advice = expect_success(client.get(f'/api/b/reports/{report_id}/advice'), '获取建议草稿')
        assert advice['advice']['status'] == 'draft', advice

        expect_success(
            client.put(f'/api/b/reports/{report_id}/advice', json={
                'content': '冒烟测试：人工编辑后的健康管理建议。',
                'sections': {
                    'imaging_report_advice': '冒烟测试：影像建议。',
                    'overall_assessment': '冒烟测试：总体评估。',
                    'risk_assessment': '冒烟测试：风险提示。',
                },
            }),
            '保存建议草稿'
        )
        expect_success(client.post(f'/api/b/reports/{report_id}/advice/submit-review'), '提交建议审核')
        expect_success(client.post(f'/api/b/reports/{report_id}/advice/approve'), '审核通过并写入最终报告')

        expect_failure(
            client.put(f'/api/b/reports/{report_id}/advice', json={'content': '归档后不应允许修改'}),
            '最终报告锁定后禁止编辑',
            expected_status=409
        )

        task = expect_success(
            client.post(f'/api/b/followup/tasks/from-report/{report_id}', json={}),
            '根据报告创建随访任务',
            expected_status=201
        )
        assert task['patient_id'] == patient_id, task
        assert task['channel'] == 'manual', task
        assert task['public_checkin_path'].endswith(task['task_code']), task
        assert task['task_payload']['first_followup_days'] == 7, task
        assert task['task_payload']['node']['name'] == '报告后首次随访', task

        expect_failure(
            client.post(f'/api/b/followup/tasks/from-report/{report_id}', json={}),
            '同一报告禁止重复生成随访任务',
            expected_status=409
        )

        report_tasks = expect_success(
            client.get(f'/api/b/followup/tasks?report_id={report_id}&source=report&per_page=20'),
            '按报告查询随访任务'
        )
        assert report_tasks['total'] == 1, report_tasks
        assert report_tasks['items'][0]['id'] == task['id'], report_tasks

        sent_task = expect_success(
            client.post(f"/api/b/followup/tasks/{task['id']}/send", json={}),
            '发送随访任务并生成公开打卡链接'
        )
        assert sent_task['status'] == 'sent', sent_task
        outbound = sent_task['messages'][-1]
        assert outbound['send_status'] == 'dry_run', outbound
        assert task['task_code'] in outbound['content'], outbound

        public_task = expect_success(
            client.get(f"/api/followup/checkin/{task['task_code']}"),
            '免登录查看随访打卡任务'
        )
        assert public_task['task_code'] == task['task_code'], public_task

        public_result = expect_success(
            client.post(f"/api/followup/checkin/{task['task_code']}", json={
                'checkin_type': 'daily_checkin',
                'content_text': '冒烟测试：今日睡眠正常，饮食清淡，步行20分钟。',
                'analyze': True,
            }),
            '免登录提交随访打卡'
        )
        assert public_result['task']['status'] == 'replied', public_result

        task_list = expect_success(
            client.get(f'/api/b/followup/tasks?patient_id={patient_id}&per_page=20'),
            '按患者查询随访任务'
        )
        assert task_list['total'] >= 1, task_list

        task_detail = expect_success(client.get(f"/api/b/followup/tasks/{task['id']}"), '查看随访任务消息流水')
        assert any(m['channel'] == 'public_checkin' for m in task_detail['messages']), task_detail

        checkins = expect_success(client.get(f"/api/b/followup/tasks/{task['id']}/checkins"), '查看患者公开打卡记录')
        assert len(checkins) >= 1, checkins
        print('[OK] 主流程冒烟测试完成')

        if patient_id and not keep:
            expect_success(client.delete(f'/api/b/patients/{patient_id}?type=b_end'), '清理冒烟患者')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--keep', action='store_true', help='保留冒烟测试创建的数据')
    args = parser.parse_args()
    run_smoke(keep=args.keep)


if __name__ == '__main__':
    main()
