"""
B端患者管理统一路由
包含：患者管理、档案管理、报告管理
"""
import os
from flask import Blueprint, request, g, jsonify
from models import (
    db, BPatient, BHealthRecord, BReport, BFollowUpRecord, 
    CPatient, CHealthRecord, CReport, CConversation
)
from utils.response import Response
from utils.decorators import login_required
from datetime import datetime
from services.llm_service import llm_generator
from config import Config
import uuid

# 创建蓝图
b_patient_bp = Blueprint('b_patient', __name__, url_prefix='/api/b/patients')

# LLM服务已在 llm_service.py 模块加载时自动配置，无需重复设置

# ============================================
# 患者管理
# ============================================

@b_patient_bp.route('', methods=['GET'])
@login_required
def get_all_patients():
    """获取所有患者（B端+C端）"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    patient_type = request.args.get('type', 'all')  # all, b_end, c_end
    status = request.args.get('status', 'all')  # all, active, inactive
    is_new = request.args.get('is_new')  # true, false, all
    search = request.args.get('search', '').strip()  # 搜索关键词
    nodule_type = request.args.get('nodule_type', '').strip()  # 结节类型筛选

    # 构建查询
    b_query = BPatient.query
    c_query = CPatient.query

    # 结节类型筛选（只对B端患者有效）
    if nodule_type:
        b_query = b_query.filter_by(nodule_type=nodule_type)
    
    # 🔍 搜索功能：按姓名、手机号、患者编号搜索
    if search:
        b_query = b_query.filter(
            db.or_(
                BPatient.name.like(f'%{search}%'),
                BPatient.phone.like(f'%{search}%'),
                BPatient.patient_code.like(f'%{search}%')
            )
        )
        c_query = c_query.filter(
            db.or_(
                CPatient.name.like(f'%{search}%'),
                CPatient.phone.like(f'%{search}%'),
                CPatient.patient_code.like(f'%{search}%')
            )
        )
    
    # 状态过滤
    if status != 'all':
        b_query = b_query.filter_by(status=status)
        c_query = c_query.filter_by(status=status)
    
    # 新患者过滤
    if is_new == 'true':
        b_query = b_query.filter_by(is_new=True)
        c_query = c_query.filter_by(is_contacted=False)
    elif is_new == 'false':
        b_query = b_query.filter_by(is_new=False)
        c_query = c_query.filter_by(is_contacted=True)
    
    # 获取数据（根据 type 参数决定是否合并 B/C）
    # type=all: B端 + C端 合并展示
    # type=b_end: 仅 B端（对应表 b_patients）
    # type=c_end: 仅 C端（对应表 c_patients）
    if patient_type == 'b_end':
        b_patients = b_query.all()
        c_patients = []
    elif patient_type == 'c_end':
        b_patients = []
        c_patients = c_query.all()
    else:
        b_patients = b_query.all()
        c_patients = c_query.all()
    
    # 合并数据
    all_patients = []
    
    # 添加B端患者
    for patient in b_patients:
        patient_data = patient.to_dict()
        patient_data['patient_type'] = 'b_end'
        patient_data['manager_name'] = patient.manager.real_name if patient.manager else None
        all_patients.append(patient_data)
    
    # 添加C端患者
    for patient in c_patients:
        patient_data = patient.to_dict()
        patient_data['patient_type'] = 'c_end'
        patient_data['manager_name'] = None
        all_patients.append(patient_data)
    
    # 按创建时间排序
    all_patients.sort(key=lambda x: x['created_at'], reverse=True)
    
    # 分页
    total = len(all_patients)
    start = (page - 1) * per_page
    end = start + per_page
    items = all_patients[start:end]
    
    return Response.paginate(
        items=items,
        total=total,
        page=page,
        per_page=per_page
    )


@b_patient_bp.route('/new', methods=['GET'])
@login_required
def get_new_patients():
    """获取新患者提醒"""
    # B端新患者
    b_new = BPatient.query.filter_by(is_new=True).all()
    
    # C端未联系患者
    c_new = CPatient.query.filter_by(is_contacted=False).all()
    
    new_patients = []
    
    # 添加B端新患者
    for patient in b_new:
        patient_data = patient.to_dict()
        patient_data['patient_type'] = 'b_end'
        patient_data['alert_type'] = 'new_patient'
        new_patients.append(patient_data)
    
    # 添加C端未联系患者
    for patient in c_new:
        patient_data = patient.to_dict()
        patient_data['patient_type'] = 'c_end'
        patient_data['alert_type'] = 'uncontacted_patient'
        new_patients.append(patient_data)
    
    # 按创建时间排序
    new_patients.sort(key=lambda x: x['created_at'], reverse=True)
    
    return Response.success({
        'new_patients': new_patients,
        'total_count': len(new_patients),
        'b_end_count': len(b_new),
        'c_end_count': len(c_new)
    })


@b_patient_bp.route('', methods=['POST'])
@login_required
def create_patient():
    """创建B端患者"""
    data = request.json

    try:
        # 生成患者编号
        patient_code = f"BP{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # 创建B端患者
        patient = BPatient(
            patient_code=patient_code,
            name=data.get('name'),
            age=data.get('age'),
            gender=data.get('gender'),
            phone=data.get('phone'),
            wechat_id=data.get('wechat_id'),
            nodule_type=data.get('nodule_type'),  # 结节类型
            manager_id=g.user_id,  # 分配给当前登录的管理师
            source_channel=data.get('source_channel', 'manual'),
            status='active',
            is_new=True
        )
        
        db.session.add(patient)
        db.session.commit()
        
        return Response.success(patient.to_dict(), '患者创建成功', 201)
        
    except Exception as e:
        db.session.rollback()
        return Response.error(f'创建失败: {str(e)}')


@b_patient_bp.route('/from-c/<int:c_patient_id>/ensure-b', methods=['POST'])
@login_required
def ensure_b_patient_from_c(c_patient_id):
    """
    ISDoc
    @description 将 C 端患者同步/转化为 B 端患者，用于「C 端患者创建 B 端档案」的场景
    @pathParam c_patient_id {int} C 端患者 ID（c_patients.id）
    @response 200 {b_patient_id, b_patient_code, created, matched_by_phone}
    """
    from models import BPatient, CPatient  # 避免循环导入
    from flask import g
    from datetime import datetime

    try:
        c_patient = CPatient.query.get(c_patient_id)
        if not c_patient:
            return Response.error('C端患者不存在', 404)

        b_patient = None
        matched_by_phone = False

        # 1. 尝试通过手机号匹配已存在的 B 端患者（避免重复创建）
        if c_patient.phone:
            b_patient = BPatient.query.filter_by(phone=c_patient.phone).first()
            if b_patient:
                matched_by_phone = True

        created = False
        if not b_patient:
            # 2. 创建新的 B 端患者
            patient_code = f"BP{datetime.now().strftime('%Y%m%d%H%M%S')}"
            b_patient = BPatient(
                patient_code=patient_code,
                name=c_patient.name,
                age=c_patient.age,
                gender=c_patient.gender,
                phone=c_patient.phone,
                wechat_id=c_patient.wechat_id,
                nodule_type=c_patient.nodule_type,
                manager_id=getattr(g, 'user_id', None),
                source_channel='from_c_end',
                status='active',
                is_new=True
            )
            db.session.add(b_patient)
            created = True
        else:
            # 3. 适度同步基础信息（只在 B 端为空时补充）
            if not b_patient.name and c_patient.name:
                b_patient.name = c_patient.name
            if not b_patient.age and c_patient.age:
                b_patient.age = c_patient.age
            if not b_patient.gender and c_patient.gender:
                b_patient.gender = c_patient.gender
            if not b_patient.nodule_type and c_patient.nodule_type:
                b_patient.nodule_type = c_patient.nodule_type

        # 4. 更新 C 端线索状态（分配管理师 & 标记已联系）
        if not c_patient.assigned_manager_id and getattr(g, 'user_id', None):
            c_patient.assigned_manager_id = g.user_id
        c_patient.is_contacted = True
        if not c_patient.lead_status or c_patient.lead_status in ['new', 'reported']:
            c_patient.lead_status = 'contacted'

        db.session.commit()

        return Response.success({
            'b_patient_id': b_patient.id,
            'b_patient_code': b_patient.patient_code,
            'created': created,
            'matched_by_phone': matched_by_phone,
            'from_c_patient_id': c_patient.id
        }, 'C端患者已同步到B端')

    except Exception as e:
        db.session.rollback()
        return Response.error(f'从C端同步B端患者失败: {str(e)}')


@b_patient_bp.route('/<int:patient_id>', methods=['PUT'])
@login_required
def update_patient(patient_id):
    """更新B端患者信息"""
    data = request.json
    patient_type = data.get('type', 'b_end')
    
    try:
        if patient_type == 'b_end':
            patient = BPatient.query.get_or_404(patient_id)
        else:
            patient = CPatient.query.get_or_404(patient_id)
        
        # 更新字段
        if 'name' in data:
            patient.name = data['name']
        if 'age' in data:
            patient.age = data['age']
        if 'gender' in data:
            patient.gender = data['gender']
        if 'phone' in data:
            patient.phone = data['phone']
        if 'wechat_id' in data:
            patient.wechat_id = data['wechat_id']
        
        db.session.commit()
        
        return Response.success(patient.to_dict(), '更新成功')
        
    except Exception as e:
        db.session.rollback()
        return Response.error(f'更新失败: {str(e)}')


@b_patient_bp.route('/<int:patient_id>', methods=['DELETE'])
@login_required
def delete_patient(patient_id):
    """删除患者（同时删除关联的健康档案、报告、随访记录等）"""
    patient_type = request.args.get('type', 'b_end')
    
    try:
        if patient_type == 'b_end':
            patient = BPatient.query.get_or_404(patient_id)
            
            # ✅ 先删报告：BReport.record_id 外键指向 b_health_records.id
            # 若先删档案会触发外键约束，导致 commit() 失败 -> 400
            reports = BReport.query.filter_by(patient_id=patient_id).all()
            for report in reports:
                db.session.delete(report)

            # 删除关联的健康档案（同时删除关联的影像报告文件）
            records = BHealthRecord.query.filter_by(patient_id=patient_id).all()
            for record in records:
                # 删除关联的影像报告文件
                from models import BImagingReport
                from utils.file_upload import file_upload_manager
                imaging_reports = BImagingReport.query.filter_by(record_id=record.id).all()
                for img_report in imaging_reports:
                    # 删除文件
                    if img_report.file_path:
                        file_upload_manager.delete_file(img_report.file_path)
                    # 删除数据库记录
                    db.session.delete(img_report)
                
                # 删除健康档案
                db.session.delete(record)
            
            # 删除关联的随访记录
            follow_ups = BFollowUpRecord.query.filter_by(patient_id=patient_id).all()
            for follow_up in follow_ups:
                db.session.delete(follow_up)
        else:
            patient = CPatient.query.get_or_404(patient_id)
            
            # ✅ 先删报告：CReport.record_id 外键指向 c_health_records.id
            reports = CReport.query.filter_by(patient_id=patient_id).all()
            for report in reports:
                db.session.delete(report)

            # 删除关联的健康档案
            records = CHealthRecord.query.filter_by(patient_id=patient_id).all()
            for record in records:
                db.session.delete(record)
            
            # 删除关联的对话
            conversations = CConversation.query.filter_by(patient_id=patient_id).all()
            for conversation in conversations:
                db.session.delete(conversation)
        
        # 删除患者
        db.session.delete(patient)
        db.session.commit()
        
        return Response.success(None, '患者删除成功')
        
    except Exception as e:
        db.session.rollback()
        return Response.error(f'删除患者失败: {str(e)}')


@b_patient_bp.route('/<int:patient_id>', methods=['GET'])
@login_required
def get_patient_detail(patient_id):
    """获取患者详情"""
    patient_type = request.args.get('type', 'b_end')
    
    if patient_type == 'b_end':
        patient = BPatient.query.get_or_404(patient_id)
    else:
        patient = CPatient.query.get_or_404(patient_id)
    
    patient_data = patient.to_dict()
    patient_data['patient_type'] = patient_type
    
    # 获取健康档案
    if patient_type == 'b_end':
        records = BHealthRecord.query.filter_by(patient_id=patient_id).all()
        reports = BReport.query.filter_by(patient_id=patient_id).all()
        follow_ups = BFollowUpRecord.query.filter_by(patient_id=patient_id).all()
    else:
        records = CHealthRecord.query.filter_by(patient_id=patient_id).all()
        reports = CReport.query.filter_by(patient_id=patient_id).all()
        follow_ups = []
    
    patient_data['health_records'] = [record.to_dict() for record in records]
    patient_data['reports'] = [report.to_dict() for report in reports]
    patient_data['follow_ups'] = [follow_up.to_dict() for follow_up in follow_ups]
    
    return Response.success(patient_data)


@b_patient_bp.route('/<int:patient_id>/mark_contacted', methods=['POST'])
@login_required
def mark_patient_contacted(patient_id):
    """标记患者已联系"""
    patient_type = request.json.get('type', 'b_end')
    
    if patient_type == 'b_end':
        patient = BPatient.query.get_or_404(patient_id)
        patient.is_new = False
    else:
        patient = CPatient.query.get_or_404(patient_id)
        patient.is_contacted = True
    
    db.session.commit()
    
    return Response.success({'message': '患者已标记为已联系'})


# ============================================
# 档案管理
# ============================================

@b_patient_bp.route('/<int:patient_id>/records', methods=['GET'])
@login_required
def get_patient_records(patient_id):
    """获取患者健康档案"""
    patient_type = request.args.get('type', 'b_end')
    
    if patient_type == 'b_end':
        records = BHealthRecord.query.filter_by(patient_id=patient_id).all()
    else:
        records = CHealthRecord.query.filter_by(patient_id=patient_id).all()
    
    return Response.success([record.to_dict() for record in records])


@b_patient_bp.route('/<int:patient_id>/records', methods=['POST'])
@login_required
def create_patient_record(patient_id):
    """创建患者健康档案（含AI西医评估，支持文件上传）"""
    # 兼容两种提交方式：
    # - application/json：仅表单数据
    # - multipart/form-data：表单数据 + 影像报告文件（imaging_reports）
    data = request.get_json(silent=True)
    files = []
    if data is None:
        data = request.form.to_dict()
        files = request.files.getlist('imaging_reports')

    patient_type = data.get('type', 'b_end') if isinstance(data, dict) else 'b_end'

    # 生成档案编号
    record_code = f"R{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # 数据清洗函数：将空字符串转换为 None
    def clean_empty_string(value):
        """将空字符串转换为None，避免数据库类型转换错误"""
        if value == '' or value == ' ' or (isinstance(value, str) and value.strip() == ''):
            return None
        return value

    # 清理数值类型字段：将空字符串转换为 None，并转换为正确的数值类型
    def clean_numeric_value(value, value_type='float'):
        """清理数值类型字段：空字符串转为None，字符串数字转为数值"""
        if value is None or value == '' or value == ' ':
            return None
        if value_type == 'float':
            try:
                return float(value) if value else None
            except (ValueError, TypeError):
                return None
        elif value_type == 'int':
            try:
                return int(value) if value else None
            except (ValueError, TypeError):
                return None
        return value

    # 处理列表类型字段（多选框）：将列表转换为逗号分隔的字符串
    def list_to_string(value):
        """将列表转换为逗号分隔的字符串"""
        if isinstance(value, list):
            return ','.join(value) if value else None
        return clean_empty_string(value)
    
    def pick_first(*keys):
        """
        从多个候选字段名中按顺序取第一个非空值
        
        Args:
            *keys: 字段名列表
        
        Returns:
            第一个非空（非空字符串）的值，否则返回 None
        """
        for k in keys:
            v = data.get(k) if isinstance(data, dict) else None
            if v is None:
                continue
            if isinstance(v, str) and v.strip() == '':
                continue
            return v
        return None

    try:
        if patient_type == 'b_end':
            # 只使用 BHealthRecord 中真实存在的字段，避免与新多结节表重复
            record = BHealthRecord(
                patient_id=patient_id,
                record_code=record_code,
                # ========== （一）基本信息 ==========
                age=clean_numeric_value(data.get('age'), 'int'),
                height=clean_numeric_value(data.get('height'), 'float'),
                weight=clean_numeric_value(data.get('weight'), 'float'),
                phone=clean_empty_string(data.get('phone')),
                diabetes_history=clean_empty_string(data.get('diabetes_history')),
                gaofang_address=clean_empty_string(data.get('gaofang_address')),
                birads_level=clean_empty_string(data.get('birads_level')),  # String类型，支持4A/4B/4C
                # 兼容旧字段：family_history / medication_history 仍保留，但多器官场景优先走器官级字段
                # 注意：前端 JSON 提交可能传数组，这里统一用 list_to_string 以确保多选完整保存
                family_history=list_to_string(pick_first('family_history', 'breast_family_history')),
                family_history_other=clean_empty_string(pick_first('family_history_other', 'breast_family_history_other')),
                breast_family_history=list_to_string(pick_first('breast_family_history', 'family_history')),
                breast_family_history_other=clean_empty_string(pick_first('breast_family_history_other', 'family_history_other')),
                lung_family_history=list_to_string(data.get('lung_family_history')),
                lung_family_history_other=clean_empty_string(data.get('lung_family_history_other')),
                thyroid_family_history=list_to_string(data.get('thyroid_family_history')),
                thyroid_family_history_other=clean_empty_string(data.get('thyroid_family_history_other')),

                # 病程信息 - 各结节类型的发现时间
                breast_discovery_date=datetime.strptime(
                    pick_first('breast_discovery_date', 'discovery_date'), '%Y-%m-%d'
                ).date() if pick_first('breast_discovery_date', 'discovery_date') else None,
                thyroid_discovery_date=datetime.strptime(
                    data.get('thyroid_discovery_date'), '%Y-%m-%d'
                ).date() if data.get('thyroid_discovery_date') else None,
                lung_discovery_date=datetime.strptime(
                    data.get('lung_discovery_date'), '%Y-%m-%d'
                ).date() if data.get('lung_discovery_date') else None,
                course_stage=data.get('course_stage'),

                # ========== （二）症状信息与影像学特征 ==========
                # 兼容：合并/三结节表单 multipart 会使用 symptoms_breast 字段名
                symptoms=list_to_string(pick_first('symptoms', 'symptoms_breast')),
                symptoms_other=clean_empty_string(pick_first('symptoms_other', 'breast_symptoms_other')),
                breast_symptoms_other=clean_empty_string(pick_first('breast_symptoms_other', 'symptoms_other')),
                lung_symptoms_other=clean_empty_string(data.get('lung_symptoms_other')),
                thyroid_symptoms_other=clean_empty_string(data.get('thyroid_symptoms_other')),
                pain_level=clean_numeric_value(data.get('pain_level'), 'int'),
                pain_type=clean_empty_string(data.get('pain_type')),
                nipple_discharge_type=clean_empty_string(data.get('nipple_discharge_type')),
                skin_change_type=clean_empty_string(data.get('skin_change_type')),

                # 乳腺影像学信息
                nodule_location=clean_empty_string(data.get('nodule_location')),
                # 乳腺结节大小：兼容单结节(nodule_size)与合并表单(breast_size)
                nodule_size=clean_empty_string(pick_first('nodule_size', 'breast_size')),
                # 通用结节数量（用于单一结节类型：乳腺/肺/甲状腺）
                # 约定：双/三结节场景下，这里的 nodule_quantity/nodule_count 代表“乳腺结节”的数量/个数
                nodule_quantity=clean_empty_string(pick_first(
                    'nodule_quantity',
                    'nodule_quantity_breast',
                    'breast_nodule_quantity',
                    'thyroid_nodule_quantity',
                    'lung_nodule_quantity'
                )),
                nodule_count=clean_empty_string(pick_first(
                    'nodule_count',
                    'nodule_count_breast',
                    'breast_nodule_count',
                    'nodule_count_thyroid',
                    'nodule_count_lung'
                )),
                lung_nodule_quantity=clean_empty_string(pick_first('lung_nodule_quantity', 'nodule_quantity_lung')),
                thyroid_nodule_quantity=clean_empty_string(pick_first('thyroid_nodule_quantity', 'nodule_quantity_thyroid')),
                boundary_features=clean_empty_string(data.get('boundary_features')),
                internal_echo=clean_empty_string(data.get('internal_echo')),
                blood_flow_signal=clean_empty_string(data.get('blood_flow_signal')),
                elasticity_score=clean_empty_string(data.get('elasticity_score')),

                # 甲状腺结节字段
                thyroid_symptoms=clean_empty_string(pick_first('thyroid_symptoms', 'symptoms_thyroid')),
                tirads_level=clean_empty_string(data.get('tirads_level')),
                thyroid_nodule_location=clean_empty_string(data.get('thyroid_nodule_location')),
                thyroid_nodule_size=clean_empty_string(pick_first('thyroid_nodule_size', 'thyroid_size')),
                # 甲状腺“多发结节个数”（注意与“数量：单发/多发”区分）
                thyroid_nodule_count=clean_empty_string(pick_first('thyroid_nodule_count', 'nodule_count_thyroid')),
                thyroid_boundary_features=clean_empty_string(data.get('thyroid_boundary_features')),
                thyroid_internal_echo=clean_empty_string(data.get('thyroid_internal_echo')),
                thyroid_blood_flow_signal=clean_empty_string(data.get('thyroid_blood_flow_signal')),

                # 肺部结节字段
                lung_symptoms=clean_empty_string(pick_first('lung_symptoms', 'symptoms_lung')),
                lung_rads_level=clean_empty_string(data.get('lung_rads_level')),
                lung_nodule_location=clean_empty_string(data.get('lung_nodule_location')),
                lung_nodule_size=clean_empty_string(pick_first('lung_nodule_size', 'lung_size')),
                lung_nodule_count=clean_empty_string(pick_first('lung_nodule_count', 'nodule_count_lung')),  # 肺部结节数量（个数）
                lung_boundary_features=clean_empty_string(data.get('lung_boundary_features')),
                lung_internal_echo=clean_empty_string(data.get('lung_internal_echo')),
                lung_blood_flow_signal=clean_empty_string(data.get('lung_blood_flow_signal')),

                # 生物节律
                rhythm_type=clean_empty_string(data.get('rhythm_type')),
                cycle_phase=clean_empty_string(data.get('cycle_phase')),
                sleep_quality=clean_empty_string(data.get('sleep_quality')),
                sleep_condition=clean_empty_string(data.get('sleep_condition')),

                # 检查历史
                exam_history_type=data.get('exam_history_type'),
                exam_special_situation=clean_empty_string(data.get('exam_special_situation')),
                exam_subcategory=clean_empty_string(data.get('exam_subcategory')),
                exam_history_detail=clean_empty_string(data.get('exam_history_detail')),
                previous_exam_history=clean_empty_string(data.get('previous_exam_history')),

                # 生活方式
                exercise_frequency=data.get('exercise_frequency'),
                lifestyle=data.get('lifestyle'),

                # （三）既往病史 - 乳腺相关
                breast_hyperplasia_history=clean_empty_string(data.get('breast_hyperplasia_history')),
                breast_fibroadenoma_history=clean_empty_string(data.get('breast_fibroadenoma_history')),
                breast_cyst_history=clean_empty_string(data.get('breast_cyst_history')),
                breast_inflammation_history=clean_empty_string(data.get('breast_inflammation_history')),
                breast_cancer_history=clean_empty_string(data.get('breast_cancer_history')),
                # 乳腺基础疾病史（多选，逗号分隔）与“其他”说明（双/三结节表单使用）
                breast_disease_history=list_to_string(data.get('breast_disease_history')),
                breast_disease_history_other=clean_empty_string(data.get('breast_disease_history_other')),

                # 甲状腺病史
                hyperthyroidism_history=clean_empty_string(data.get('hyperthyroidism_history')),
                hypothyroidism_history=clean_empty_string(data.get('hypothyroidism_history')),
                hypothyroidism_history_other=clean_empty_string(data.get('hypothyroidism_history_other')),
                hashimoto_history=clean_empty_string(data.get('hashimoto_history')),
                subacute_thyroiditis_history=clean_empty_string(data.get('subacute_thyroiditis_history')),
                thyroid_cancer_history=clean_empty_string(data.get('thyroid_cancer_history')),
                hereditary_thyroid_history=clean_empty_string(data.get('hereditary_thyroid_history')),

                # 肺部病史
                pneumonia_history=clean_empty_string(data.get('pneumonia_history')),
                tb_history=clean_empty_string(data.get('tb_history')),
                copd_history=clean_empty_string(data.get('copd_history')),
                fibrosis_history=clean_empty_string(data.get('fibrosis_history')),
                lung_cancer_history=clean_empty_string(data.get('lung_cancer_history')),
                lung_cancer_history_other=clean_empty_string(data.get('lung_cancer_history_other')),
                hereditary_lung_history=clean_empty_string(data.get('hereditary_lung_history')),

                # 其他风险因素
                dust_exposure_history=clean_empty_string(data.get('dust_exposure_history')),
                radiation_exposure_history=clean_empty_string(data.get('radiation_exposure_history')),
                radiation_other=clean_empty_string(data.get('radiation_other')),
                autoimmune_disease_history=clean_empty_string(data.get('autoimmune_disease_history')),
                autoimmune_other=clean_empty_string(data.get('autoimmune_other')),
                medication_history=list_to_string(pick_first('medication_history', 'breast_medication_history')),
                medication_other=clean_empty_string(pick_first('medication_other', 'breast_medication_other')),
                breast_medication_history=list_to_string(pick_first('breast_medication_history', 'medication_history')),
                breast_medication_other=clean_empty_string(pick_first('breast_medication_other', 'medication_other')),
                lung_medication_history=list_to_string(data.get('lung_medication_history')),
                lung_medication_other=clean_empty_string(data.get('lung_medication_other')),
                thyroid_medication_history=list_to_string(data.get('thyroid_medication_history')),
                thyroid_medication_other=clean_empty_string(data.get('thyroid_medication_other')),
                tumor_marker_test=clean_empty_string(data.get('tumor_marker_test')),
                hereditary_breast_history=clean_empty_string(data.get('hereditary_breast_history')),

                # 状态
                data_completeness='full',
                created_by=g.user_id,
                status='completed'
            )
        else:
            record = CHealthRecord(
                patient_id=patient_id,
                record_code=record_code,
                age=data.get('age'),
                birads_level=data.get('birads_level'),
                family_history=data.get('family_history'),
                symptoms=data.get('symptoms'),
                pain_level=clean_empty_string(data.get('pain_level')),
                pain_type=clean_empty_string(data.get('pain_type')),
                nodule_location=data.get('nodule_location'),
                nodule_size=data.get('nodule_size'),
                boundary_features=data.get('boundary_features'),
                internal_echo=data.get('internal_echo'),
                blood_flow_signal=data.get('blood_flow_signal'),
                elasticity_score=data.get('elasticity_score'),
                rhythm_type=clean_empty_string(data.get('rhythm_type')),
                sleep_quality=clean_empty_string(data.get('sleep_quality')),
                exam_history_type=data.get('exam_history_type'),
                exercise_frequency=data.get('exercise_frequency'),
                data_completeness='partial',
                status='completed'
            )

        # 保存档案
        db.session.add(record)
        db.session.flush()  # 先flush获取record.id，但不commit

        # （可选）处理上传的影像报告文件
        imaging_reports_data = []
        if files:
            from models import BImagingReport
            from utils.file_upload import file_upload_manager
            from services.pdf_parser import pdf_parser
            from services.imaging_report_service import imaging_report_service

            # 结节类型：优先使用前端传的 nodule_types / nodule_type
            nodule_type = (data.get('nodule_types') or data.get('nodule_type') or '').strip() or 'breast'

            for file in files:
                if not file or not file.filename:
                    continue

                try:
                    # 1) 保存文件
                    file_path, original_filename, file_size = file_upload_manager.save_file(file, record.id)
                    if not file_path:
                        continue

                    # 2) 尝试解析（PDF 优先走多模态；失败则降级文本提取）
                    extracted_text = None
                    extracted_data = None
                    file_type = file_upload_manager.get_file_type(original_filename)
                    if file_type == 'pdf':
                        extracted_data = imaging_report_service.extract_structured_data_from_pdf(file_path, nodule_type)
                        if not extracted_data:
                            extracted_text = pdf_parser.extract_text_from_pdf(file_path)
                            if extracted_text:
                                extracted_data = imaging_report_service.extract_structured_data_from_text(extracted_text, nodule_type)

                    # 3) 写入影像报告表
                    imaging_report = BImagingReport(
                        record_id=record.id,
                        file_name=original_filename,
                        file_path=file_path,
                        file_size=file_size,
                        file_type=file_type,
                        extracted_text=extracted_text,
                        extracted_data=extracted_data,
                        uploaded_by=getattr(g, 'user_id', None)
                    )
                    db.session.add(imaging_report)
                    imaging_reports_data.append(imaging_report.to_dict())
                except Exception:
                    # 单个文件失败不影响整体档案创建
                    continue

        db.session.commit()

        print(f"✅ 健康档案创建成功 - 档案ID: {record.id}")

        # 返回档案数据
        result = record.to_dict()
        if imaging_reports_data:
            result['imaging_reports'] = imaging_reports_data
        return Response.success(result, '档案创建成功', 201)

    except Exception as e:
        db.session.rollback()
        print(f"❌ 档案创建失败: {str(e)}")
        return Response.error(f'档案创建失败: {str(e)}')


# ============================================
# 报告管理
# ============================================

@b_patient_bp.route('/<int:patient_id>/reports', methods=['GET'])
@login_required
def get_patient_reports(patient_id):
    """获取患者报告"""
    patient_type = request.args.get('type', 'b_end')
    
    if patient_type == 'b_end':
        reports = BReport.query.filter_by(patient_id=patient_id).all()
    else:
        reports = CReport.query.filter_by(patient_id=patient_id).all()
    
    return Response.success([report.to_dict() for report in reports])


@b_patient_bp.route('/<int:patient_id>/reports/generate', methods=['POST'])
@login_required
def generate_patient_report(patient_id):
    """
    生成患者报告草稿（调用LLM生成AI评估）

    新流程：
    1. 调用LLM生成影像学评估和疾病史评估
    2. 创建报告记录，保存评估内容
    3. 报告状态：draft（草稿）
    4. 等待管理师审核
    """
    data = request.json
    record_id = data.get('record_id')
    patient_type = data.get('type', 'b_end')

    if not record_id:
        return Response.error('档案ID不能为空')

    try:
        print(f"\n[REPORT] ========== 开始生成报告草稿 ==========")
        print(f"[REPORT] 患者ID: {patient_id}, 档案ID: {record_id}")

        # 1. 获取健康档案和患者
        if patient_type == 'b_end':
            record = BHealthRecord.query.get_or_404(record_id)
            patient = BPatient.query.get_or_404(patient_id)
        else:
            record = CHealthRecord.query.get_or_404(record_id)
            patient = CPatient.query.get_or_404(patient_id)

        print(f"[REPORT] [1/4] 档案数据加载完成")

        # 2. 获取结节类型
        nodule_type = patient.nodule_type if hasattr(patient, 'nodule_type') and patient.nodule_type else 'breast'
        print(f"[REPORT] 结节类型: {nodule_type}")

        # 3. 准备LLM数据
        print(f"[REPORT] [2/4] 准备LLM数据...")
        from utils.report_manager import prepare_llm_patient_data
        patient_data = prepare_llm_patient_data(record, nodule_type, patient=patient)
        print(f"[REPORT] 患者性别: {patient_data.get('gender', '未记录')}")

        # 知识库匹配和决策树处理（已移除，直接使用空值）
        # 注：知识库只有乳腺数据，其他结节类型暂不支持，后续可添加
        matched_knowledge = []  # 空列表，LLM会显示"无相关医学知识"
        tree_result = {}  # 空字典，LLM会使用默认值
        print(f"[REPORT] 知识库匹配和决策树: 已移除（使用空值）")

        # 4. 调用LLM生成AI评估
        print(f"[REPORT] [3/4] 调用LLM生成AI评估...（需要10-30秒）")
        # 标记本次是否会真实调用大模型（OPENROUTER_API_KEY 未配置时会走 mock）
        llm_enabled = bool(os.getenv('OPENROUTER_API_KEY', '').strip())

        # 4.1 生成影像学综合结论（包含影像学评估、综合分析和随访建议）
        # 注意：不再单独生成疾病史评估，因为已经包含在影像学评估的"其次"部分
        print(f"[REPORT]   - 生成总体评估与随访建议...")
        from routes.llm_helpers import generate_imaging_conclusion_with_llm
        imaging_result = generate_imaging_conclusion_with_llm(
            patient_data, tree_result, matched_knowledge, nodule_type=nodule_type
        )
        imaging_conclusion = imaging_result.get('conclusion', '总体评估生成失败')
        imaging_risk_warning = imaging_result.get('risk_warning', '暂无风险提示')
        
        # 不再使用风险评估字段
        risk_score = None
        risk_level = None
        
        # 清理文本中的多余字符，并格式化换行
        from routes.llm_helpers import clean_markdown_formatting, format_text_with_line_breaks
        imaging_conclusion = clean_markdown_formatting(imaging_conclusion)
        imaging_risk_warning = clean_markdown_formatting(imaging_risk_warning)
        # 将换行符转换为HTML的<br/>标签，确保"首先"、"其次"、"最后"前面有换行
        imaging_conclusion = format_text_with_line_breaks(imaging_conclusion)
        imaging_risk_warning = format_text_with_line_breaks(imaging_risk_warning)

        # 4.3 生成分类建议（按类别分组）
        print(f"[REPORT]   - 生成分类建议...")
        from routes.llm_helpers import generate_recommendations_by_category
        # 将结节类型添加到 patient_data 中，用于生成基础建议
        patient_data['nodule_type'] = nodule_type
        recommendations_draft = generate_recommendations_by_category(
            patient_data, matched_knowledge
        )
        print(f"[REPORT]   已生成 {len(recommendations_draft.get('recommendations', []))} 条分类建议")

        print(f"[REPORT] [3/4] AI评估生成完成")

        # 5. 创建草稿报告
        print(f"[REPORT] [4/4] 保存报告草稿到数据库...")
        report_code = f"RPT{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # 5.1 转换 Markdown 格式为 HTML（用于前端显示）
        from utils.markdown_helper import safe_markdown_to_html
        imaging_conclusion_html = safe_markdown_to_html(imaging_conclusion)
        imaging_risk_warning_html = safe_markdown_to_html(imaging_risk_warning)

        if patient_type == 'b_end':
            report = BReport(
                patient_id=patient_id,
                record_id=record_id,
                report_code=report_code,
                status='draft',  # 草稿状态
                imaging_conclusion=imaging_conclusion_html,  # 总体评估与随访建议
                imaging_risk_warning=imaging_risk_warning_html,  # 风险提示
                medical_conclusion=None,  # 不再单独保存疾病史评估，因为已包含在imaging_conclusion中
                medical_risk_warning=None,  # 不再单独保存疾病史评估，因为已包含在imaging_conclusion中
                risk_score=None,  # 不再使用风险评估
                risk_level=None,  # 不再使用风险评估
                recommendations_draft=recommendations_draft,  # 保存分类建议草稿（JSON格式）
                report_type='professional',
                access_level='b_only',
                generated_by=g.user_id
            )
        else:
            # C端暂时保持旧逻辑（TODO: 后续也可以改造）
            report_result = llm_generator.generate_report(patient_data, tree_result, matched_knowledge)
            report = CReport(
                patient_id=patient_id,
                record_id=record_id,
                conversation_id=None,
                report_code=report_code,
                report_html=report_result['report_html'],
                report_summary=report_result['report_summary'],
                risk_level=None,  # 不再使用风险评估
                # 兼容B端审核页/报告详情页展示：同样保存“总体评估与随访建议/风险提示”
                imaging_conclusion=imaging_conclusion_html,
                imaging_risk_warning=imaging_risk_warning_html,
                report_type='patient_friendly',
                access_level='c_accessible',
                download_token=None,
                status='generated'
            )

        db.session.add(report)
        db.session.commit()

        print(f"[REPORT] [4/4] 报告草稿保存成功！")
        print(f"[REPORT] 报告ID: {report.id}, 报告编号: {report_code}, 状态: draft")
        print(f"[REPORT] ========== 报告草稿生成完成，等待审核 ==========\n")

        return Response.success({
            'report_id': report.id,
            'report_code': report_code,
            'status': 'draft',
            'llm_enabled': llm_enabled,
            'imaging_conclusion': imaging_conclusion,
            'imaging_risk_warning': imaging_risk_warning,
            'medical_conclusion': None,  # 不再单独保存疾病史评估，因为已包含在imaging_conclusion中
            'medical_risk_warning': None,  # 不再单独保存疾病史评估，因为已包含在imaging_conclusion中
            'message': '报告草稿已生成，请管理师审核后发布'
        }, '报告草稿生成成功', 201)

    except Exception as e:
        import traceback
        print(f"[REPORT] ❌ 报告生成失败: {str(e)}")
        print(f"[REPORT] 完整错误信息:")
        traceback.print_exc()
        db.session.rollback()
        return Response.error(f'大模型调用失败，未生成报告: {str(e)}')


@b_patient_bp.route('/<int:patient_id>/reports/<int:report_id>', methods=['GET'])
@login_required
def get_report_detail(patient_id, report_id):
    """获取报告详情"""
    patient_type = request.args.get('type', 'b_end')
    
    if patient_type == 'b_end':
        report = BReport.query.filter_by(id=report_id, patient_id=patient_id).first_or_404()
    else:
        report = CReport.query.filter_by(id=report_id, patient_id=patient_id).first_or_404()
    
    report_data = report.to_dict()
    report_data['report_html'] = report.report_html
    
    return Response.success(report_data)


# ============================================
# 跟进管理
# ============================================

@b_patient_bp.route('/<int:patient_id>/follow-ups', methods=['GET'])
@login_required
def get_patient_follow_ups(patient_id):
    """获取患者跟进记录"""
    follow_ups = BFollowUpRecord.query.filter_by(patient_id=patient_id).all()
    return Response.success([follow_up.to_dict() for follow_up in follow_ups])


@b_patient_bp.route('/<int:patient_id>/follow-ups', methods=['POST'])
@login_required
def create_follow_up(patient_id):
    """创建跟进记录"""
    data = request.json
    
    follow_up = BFollowUpRecord(
        patient_id=patient_id,
        manager_id=g.user_id,
        follow_up_type=data.get('follow_up_type'),
        follow_up_date=datetime.strptime(data.get('follow_up_date'), '%Y-%m-%d').date() if data.get('follow_up_date') else None,
        content=data.get('content'),
        next_follow_up_date=datetime.strptime(data.get('next_follow_up_date'), '%Y-%m-%d').date() if data.get('next_follow_up_date') else None,
        next_follow_up_action=data.get('next_follow_up_action')
    )
    
    db.session.add(follow_up)
    db.session.commit()
    
    return Response.success(follow_up.to_dict(), '跟进记录创建成功', 201)
