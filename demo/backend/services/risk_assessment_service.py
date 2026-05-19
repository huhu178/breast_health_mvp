"""Workflow risk stratification helpers.

The risk level in this module is for queueing, report review, follow-up
template matching, and messaging intensity. It is not a diagnosis.
"""


RISK_SCOPE = 'workflow_triage'
RISK_DISCLAIMER = '该风险分层用于健康管理工作流排序和随访模板匹配，不替代医生诊断或治疗决策。'


def normalize_risk_level(risk):
    mapping = {
        'high': '高风险',
        '高': '高风险',
        '高危': '高风险',
        '高风险': '高风险',
        'mid': '中风险',
        'medium': '中风险',
        '中': '中风险',
        '中危': '中风险',
        '中风险': '中风险',
        'low': '低风险',
        '低': '低风险',
        '低危': '低风险',
        '低风险': '低风险',
    }
    text = str(risk or '').strip()
    return mapping.get(text.lower(), mapping.get(text, text or '未评估'))


def _normalize_level(value):
    text = str(value or '').strip().upper().replace('类', '').replace('级', '')
    if not text or text in {'不清楚', '未知', '未填写', 'NONE'}:
        return ''
    return text


def _risk_from_level(system_name, value):
    level = _normalize_level(value)
    if not level:
        return None
    if system_name == 'breast':
        if level.startswith(('4', '5', '6')):
            return '高风险'
        if level.startswith('3'):
            return '中风险'
        if level.startswith(('1', '2', '0')):
            return '低风险'
    if system_name == 'lung':
        if level.startswith('4'):
            return '高风险'
        if level.startswith('3'):
            return '中风险'
        if level.startswith(('1', '2')):
            return '低风险'
    if system_name == 'thyroid':
        if level.startswith(('4', '5', '6')):
            return '高风险'
        if level.startswith('3'):
            return '中风险'
        if level.startswith(('1', '2')):
            return '低风险'
    return None


def derive_report_risk_level(record, nodule_type, patient_data=None):
    """
    Derive low/mid/high workflow risk from available structured data.

    Returns: (risk_level, risk_score, risk_basis)
    """
    patient_data = patient_data or {}

    from utils.report_manager import derive_tcm_risk_level
    tcm_risk = derive_tcm_risk_level(record)
    if tcm_risk:
        return tcm_risk

    candidates = []
    nodule_type = nodule_type or ''
    if nodule_type == 'triple' or 'breast' in nodule_type:
        candidates.append(('乳腺BI-RADS', _risk_from_level('breast', getattr(record, 'birads_level', None))))
    if nodule_type == 'triple' or 'lung' in nodule_type:
        candidates.append(('肺部Lung-RADS', _risk_from_level('lung', getattr(record, 'lung_rads_level', None))))
    if nodule_type == 'triple' or 'thyroid' in nodule_type:
        candidates.append(('甲状腺TI-RADS', _risk_from_level('thyroid', getattr(record, 'tirads_level', None))))

    rank = {'低风险': 1, '中风险': 2, '高风险': 3}
    known = [(label, risk) for label, risk in candidates if risk]

    if not known:
        return '中风险', 50, '分级不清，按资料缺口进入中风险复核'

    top_label, top_risk = max(known, key=lambda item: rank[item[1]])
    score = {'低风险': 25, '中风险': 55, '高风险': 85}[top_risk]

    if not patient_data.get('has_imaging_upload') and top_risk == '低风险':
        return top_risk, score, f'{top_label}提示{top_risk}，未上传原始影像报告'
    return top_risk, score, f'{top_label}提示{top_risk}'


def append_risk_metadata(report_dict):
    """Append risk source/basis metadata to a report response dict."""
    summary = str(report_dict.get('report_summary') or '')
    risk_level = normalize_risk_level(report_dict.get('risk_level') or '未评估')
    basis = ''
    if ' · ' in summary:
        prefix, basis = summary.split(' · ', 1)
        if not risk_level or risk_level == '未评估':
            risk_level = normalize_risk_level(prefix)
    elif summary and summary != risk_level:
        basis = summary

    source = 'unknown'
    if '中医健康指数' in basis:
        source = 'tcm_health_index'
    elif 'BI-RADS' in basis or 'Lung-RADS' in basis or 'TI-RADS' in basis:
        source = 'imaging_grade'
    elif '资料缺口' in basis or '分级不清' in basis:
        source = 'data_gap'

    report_dict['risk_level'] = risk_level
    report_dict['risk_basis'] = basis
    report_dict['risk_source'] = source
    report_dict['risk_scope'] = RISK_SCOPE
    report_dict['risk_disclaimer'] = RISK_DISCLAIMER
    return report_dict
