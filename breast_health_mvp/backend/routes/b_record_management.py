"""
B端档案管理路由
处理健康档案的创建、查看、编辑
"""
from flask import Blueprint, request, jsonify
from models import db, BPatient, BHealthRecord, BImagingReport, CPatient, CHealthRecord
from utils.decorators import login_required
from utils.response import Response
from datetime import datetime
import random
import string
from utils.id_generator import generate_record_code
from utils.file_upload import file_upload_manager
from services.pdf_parser import pdf_parser
from services.imaging_report_service import imaging_report_service

b_record_bp = Blueprint('b_record', __name__, url_prefix='/api/b/records')


@b_record_bp.route('', methods=['GET'])
@login_required
def get_all_records(current_user):
    """获取所有健康档案（支持分页和筛选）"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        patient_id = request.args.get('patient_id', type=int)
        status = request.args.get('status')
        
        query = BHealthRecord.query
        
        # 筛选条件
        if patient_id:
            query = query.filter_by(patient_id=patient_id)
        if status:
            query = query.filter_by(status=status)
        
        # 排序
        query = query.order_by(BHealthRecord.created_at.desc())
        
        # 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        records_data = []
        for record in pagination.items:
            record_dict = record.to_dict()
            # 添加患者信息
            patient = BPatient.query.get(record.patient_id)
            if patient:
                record_dict['patient_name'] = patient.name
                record_dict['patient_code'] = patient.patient_code
            # 添加档案类型
            record_dict['record_type'] = 'b_end'
            records_data.append(record_dict)
        
        return Response.success({
            'items': records_data,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        })
        
    except Exception as e:
        return Response.error(f'获取档案列表失败: {str(e)}')


@b_record_bp.route('/<int:record_id>', methods=['GET'])
@login_required
def get_record_detail(current_user, record_id):
    """
    获取健康档案详情

    ISDoc
    @description 兼容B端/C端两套档案：通过 query 参数 type=b_end/c_end 区分
    @queryParam type {string} 可选，默认 b_end
    """
    try:
        record_type = request.args.get('type', 'b_end')

        if record_type == 'c_end':
            record = CHealthRecord.query.get(record_id)
            if not record:
                return Response.error('档案不存在', 404)

            record_dict = record.to_dict()
            patient = CPatient.query.get(record.patient_id)
            if patient:
                record_dict['patient'] = patient.to_dict()
            record_dict['record_type'] = 'c_end'
            return Response.success(record_dict)

        record = BHealthRecord.query.get(record_id)
        if not record:
            return Response.error('档案不存在', 404)
        
        record_dict = record.to_dict()
        patient = BPatient.query.get(record.patient_id)
        if patient:
            record_dict['patient'] = patient.to_dict()
        record_dict['record_type'] = 'b_end'
        
        return Response.success(record_dict)
        
    except Exception as e:
        return Response.error(f'获取档案详情失败: {str(e)}')


@b_record_bp.route('', methods=['POST'])
@login_required
def create_record(current_user):
    """
    ISDoc: 创建健康档案（支持文件上传）
    
    兼容说明：
    - 前端在不同表单/版本中可能提交 `discovery_date` / `breast_discovery_date` / `nodule_discovery_time` 等字段名
    - 多选字段可能以 list（JSON）或 逗号分隔字符串（multipart/form-data）传入
    本接口需要统一规范化后写入 `BHealthRecord`，避免“结节时间/基础病史写不进去”。
    """
    try:
        # 支持multipart/form-data（表单+文件）和application/json（仅表单）
        if request.is_json:
            data = request.json
            files = []
        else:
            # multipart/form-data
            data = request.form.to_dict()
            # 获取上传的文件（支持多文件）
            files = request.files.getlist('imaging_reports')  # 前端使用字段名 'imaging_reports'
        
        patient_id = data.get('patient_id')

        # 调试日志：打印接收到的关键字段
        print(f"\n=== 创建档案接收到的数据 ===")
        print(f"patient_id: {data.get('patient_id')}")
        print(f"nodule_types: {data.get('nodule_types')}")
        print(f"age: {data.get('age')} (type: {type(data.get('age'))})")
        print(f"height: {data.get('height')} (type: {type(data.get('height'))})")
        print(f"weight: {data.get('weight')} (type: {type(data.get('weight'))})")
        print(f"phone: {data.get('phone')} (type: {type(data.get('phone'))})")
        print(f"diabetes_history: {data.get('diabetes_history')}")
        print(f"gaofang_address: {data.get('gaofang_address')}")
        print(f"breast_discovery_date: {data.get('breast_discovery_date')}")
        print(f"thyroid_discovery_date: {data.get('thyroid_discovery_date')}")
        print(f"lung_discovery_date: {data.get('lung_discovery_date')}")
        print(f"========================\n")

        # 验证患者存在
        patient = BPatient.query.get(patient_id)
        if not patient:
            return Response.error('患者不存在', 404)
        
        # 辅助函数：将空字符串转换为 None，并处理数值类型
        def clean_value(value, value_type=None):
            """清理值：空字符串转为None，数值类型进行转换"""
            if value is None or value == '':
                return None
            if value_type == 'float':
                try:
                    result = float(value) if value else None
                    print(f"[clean_value] 转换 {value} (type: {type(value)}) -> {result} (float)")
                    return result
                except (ValueError, TypeError) as e:
                    print(f"[clean_value] 转换失败: {value} -> None (错误: {e})")
                    return None
            if value_type == 'int':
                try:
                    result = int(value) if value else None
                    print(f"[clean_value] 转换 {value} (type: {type(value)}) -> {result} (int)")
                    return result
                except (ValueError, TypeError) as e:
                    print(f"[clean_value] 转换失败: {value} -> None (错误: {e})")
                    return None
            return value

        def list_to_string(value):
            """
            ISDoc: 多选字段规范化
            
            - JSON 提交：可能是 list
            - multipart 提交：通常是逗号分隔字符串
            """
            if value is None:
                return None
            if isinstance(value, list):
                return ','.join([str(x) for x in value if str(x).strip() != '']) or None
            if isinstance(value, str):
                v = value.strip()
                return v if v != '' else None
            return str(value)

        def pick_first(*keys):
            """
            ISDoc: 从多个候选字段名中按顺序取第一个非空值
            """
            for k in keys:
                v = data.get(k)
                if v is None:
                    continue
                if isinstance(v, str) and v.strip() == '':
                    continue
                return v
            return None

        def parse_date(value):
            """
            ISDoc: 解析 YYYY-MM-DD 日期字符串为 date
            """
            if value is None:
                return None
            if hasattr(value, 'year') and hasattr(value, 'month') and hasattr(value, 'day'):
                # 已经是 date/datetime
                return value.date() if hasattr(value, 'date') else value
            if isinstance(value, str):
                v = value.strip()
                if v == '':
                    return None
                try:
                    return datetime.strptime(v, '%Y-%m-%d').date()
                except Exception:
                    return None
            return None

        # 清理 height 和 weight
        cleaned_height = clean_value(data.get('height'), 'float')
        cleaned_weight = clean_value(data.get('weight'), 'float')
        print(f"[创建档案] height: {data.get('height')} -> {cleaned_height}")
        print(f"[创建档案] weight: {data.get('weight')} -> {cleaned_weight}")

        # 创建档案
        record = BHealthRecord(
            patient_id=patient_id,
            record_code=generate_record_code(),

            # （一）基本信息
            age=patient.age if hasattr(patient, 'age') else clean_value(data.get('age'), 'int'),
            height=cleaned_height,
            weight=cleaned_weight,
            phone=data.get('phone'),
            diabetes_history=data.get('diabetes_history'),
            gaofang_address=data.get('gaofang_address'),
            birads_level=data.get('birads_level'),
            family_history=list_to_string(data.get('family_history')),

            # 病程信息
            course_stage=data.get('course_stage'),

            # （二）乳腺影像学特征
            symptoms=list_to_string(pick_first('symptoms', 'symptoms_breast')),
            symptoms_other=data.get('symptoms_other'),
            breast_symptoms_other=data.get('breast_symptoms_other') or data.get('symptoms_other'),
            pain_level=data.get('pain_level'),
            pain_type=data.get('pain_type'),
            nipple_discharge_type=data.get('nipple_discharge_type'),
            skin_change_type=data.get('skin_change_type'),
            nodule_location=data.get('nodule_location'),
            nodule_size=data.get('nodule_size'),
            boundary_features=data.get('boundary_features'),
            internal_echo=data.get('internal_echo'),
            blood_flow_signal=data.get('blood_flow_signal'),
            elasticity_score=data.get('elasticity_score'),
            breast_discovery_date=parse_date(pick_first('breast_discovery_date', 'discovery_date', 'nodule_discovery_time', 'breast_discovery_time')),

            # （二）肺部影像学特征（仅包含报告实际使用的字段）
            lung_symptoms=data.get('lung_symptoms'),
            lung_symptoms_other=data.get('lung_symptoms_other') or data.get('symptoms_other'),
            lung_rads_level=data.get('lung_rads_level'),
            lung_nodule_size=data.get('lung_nodule_size'),
            lung_nodule_count=data.get('lung_nodule_count'),
            lung_discovery_date=parse_date(pick_first('lung_discovery_date', 'nodule_discovery_time_lung', 'lung_discovery_time')),
            # 注意：以下字段已从报告移除，不再接收：
            # - lung_nodule_location, lung_boundary_features, lung_internal_echo, lung_blood_flow_signal

            # （二）甲状腺影像学特征
            thyroid_symptoms=data.get('thyroid_symptoms'),
            thyroid_symptoms_other=data.get('thyroid_symptoms_other') or data.get('symptoms_other'),
            tirads_level=data.get('tirads_level'),
            thyroid_nodule_location=data.get('thyroid_nodule_location'),
            thyroid_nodule_size=data.get('thyroid_nodule_size'),
            thyroid_nodule_count=data.get('thyroid_nodule_count'),
            thyroid_boundary_features=data.get('thyroid_boundary_features'),
            thyroid_internal_echo=data.get('thyroid_internal_echo'),
            thyroid_blood_flow_signal=data.get('thyroid_blood_flow_signal'),
            thyroid_discovery_date=parse_date(pick_first('thyroid_discovery_date', 'nodule_discovery_time_thyroid', 'thyroid_discovery_time')),

            # 生物节律
            rhythm_type=data.get('rhythm_type'),
            cycle_phase=data.get('cycle_phase'),
            sleep_quality=data.get('sleep_quality'),
            sleep_condition=data.get('sleep_condition'),

            # 检查历史
            exam_history_type=data.get('exam_history_type'),
            exam_special_situation=data.get('exam_special_situation'),
            exam_subcategory=data.get('exam_subcategory'),
            exam_history_detail=data.get('exam_history_detail'),
            previous_exam_history=data.get('previous_exam_history'),

            # 生活方式
            exercise_frequency=data.get('exercise_frequency'),
            lifestyle=data.get('lifestyle'),

            # （三）既往病史与风险分层
            breast_disease_history=list_to_string(data.get('breast_disease_history')),
            breast_disease_history_other=data.get('breast_disease_history_other'),
            family_genetic_history=data.get('family_genetic_history'),
            family_history_other=data.get('family_history_other'),
            previous_biopsy_history=data.get('previous_biopsy_history'),
            contraceptive_risk_level=data.get('contraceptive_risk_level'),
            smoking_risk_level=data.get('smoking_risk_level'),
            diabetes_control_level=data.get('diabetes_control_level'),
            
            # 乳腺基础疾病史
            breast_hyperplasia_history=data.get('breast_hyperplasia_history'),
            breast_fibroadenoma_history=data.get('breast_fibroadenoma_history'),
            breast_cyst_history=data.get('breast_cyst_history'),
            breast_inflammation_history=data.get('breast_inflammation_history'),
            breast_cancer_history=data.get('breast_cancer_history'),
            hereditary_breast_history=data.get('hereditary_breast_history'),
            
            # 肺部基础疾病史（已整合到lung_cancer_history字段，不再使用单独的病史字段）
            lung_cancer_history=list_to_string(data.get('lung_cancer_history')),
            lung_cancer_history_other=data.get('lung_cancer_history_other'),
            # 注意：以下单独的病史字段已合并，不再使用：
            # - pneumonia_history, tb_history, copd_history, fibrosis_history, hereditary_lung_history
            
            # 甲状腺病史
            hyperthyroidism_history=data.get('hyperthyroidism_history'),
            hypothyroidism_history=data.get('hypothyroidism_history'),
            hashimoto_history=data.get('hashimoto_history'),
            subacute_thyroiditis_history=data.get('subacute_thyroiditis_history'),
            thyroid_cancer_history=data.get('thyroid_cancer_history'),
            hereditary_thyroid_history=data.get('hereditary_thyroid_history'),
            
            # 其他风险因素
            # 注意：diabetes_history 已在上面"（一）基本信息"部分定义（第148行），这里不再重复
            dust_exposure_history=data.get('dust_exposure_history'),
            radiation_exposure_history=data.get('radiation_exposure_history'),
            radiation_other=data.get('radiation_other'),
            autoimmune_disease_history=data.get('autoimmune_disease_history'),
            autoimmune_other=data.get('autoimmune_other'),
            medication_history=list_to_string(data.get('medication_history')),
            medication_other=data.get('medication_other'),
            tumor_marker_test=data.get('tumor_marker_test'),
            
            # 乳腺结节数量
            nodule_quantity=pick_first('nodule_quantity', 'nodule_quantity_breast', 'breast_nodule_quantity'),  # 数量：单发/多发
            nodule_count=pick_first('nodule_count', 'nodule_count_breast', 'breast_nodule_count'),  # 多发结节个数

            # 状态
            status='completed',
            created_by=current_user.id
        )
        
        db.session.add(record)
        db.session.flush()  # 先flush获取record.id，但不commit
        
        # 处理上传的影像报告文件
        imaging_reports_data = []
        if files:
            print(f"\n📎 开始处理 {len(files)} 个上传的影像报告文件...")
            
            # 获取结节类型（用于LLM分析）
            nodule_type = patient.nodule_type if hasattr(patient, 'nodule_type') else 'breast'
            
            for file in files:
                if not file or not file.filename:
                    continue
                
                try:
                    # 1. 保存文件
                    file_path, original_filename, file_size = file_upload_manager.save_file(
                        file, record.id
                    )
                    
                    if not file_path:
                        print(f"⚠️ 文件保存失败: {original_filename}")
                        continue
                    
                    # 2. 解析PDF提取文本
                    extracted_text = None
                    extracted_data = None
                    
                    file_type = file_upload_manager.get_file_type(original_filename)
                    if file_type == 'pdf':
                        # 3. 直接使用LLM分析PDF（多模态，无需OCR）
                        print(f"🤖 开始使用LLM直接分析PDF文件...")
                        extracted_data = imaging_report_service.extract_structured_data_from_pdf(
                            file_path, nodule_type
                        )
                        
                        # 如果多模态分析失败，尝试文本提取作为降级方案
                        if not extracted_data:
                            print(f"⚠️ LLM多模态分析失败，尝试文本提取...")
                            extracted_text = pdf_parser.extract_text_from_pdf(file_path)
                            if extracted_text:
                                extracted_data = imaging_report_service.extract_structured_data_from_text(
                                    extracted_text, nodule_type
                                )
                            else:
                                print(f"⚠️ PDF解析未提取到文本（可能是扫描件，且多模态分析失败）")
                    else:
                        print(f"⚠️ 暂不支持的文件类型: {file_type}，跳过解析")
                    
                    # 4. 创建影像报告记录
                    imaging_report = BImagingReport(
                        record_id=record.id,
                        file_name=original_filename,
                        file_path=file_path,
                        file_size=file_size,
                        file_type=file_type,
                        extracted_text=extracted_text,
                        extracted_data=extracted_data,
                        uploaded_by=current_user.id
                    )
                    
                    db.session.add(imaging_report)
                    imaging_reports_data.append(imaging_report.to_dict())
                    
                    print(f"✅ 影像报告处理完成: {original_filename}")
                    
                except Exception as e:
                    print(f"❌ 处理影像报告失败: {str(e)}")
                    # 继续处理其他文件，不中断整个流程
                    continue
        
        # 提交所有更改
        db.session.commit()
        
        # 调试日志：确认保存后的数据
        print(f"\n=== 档案保存成功后的数据 ===")
        print(f"record.height: {record.height}")
        print(f"record.weight: {record.weight}")
        print(f"record.breast_discovery_date: {record.breast_discovery_date}")
        print(f"record.thyroid_discovery_date: {record.thyroid_discovery_date}")
        print(f"record.lung_discovery_date: {record.lung_discovery_date}")
        print(f"========================\n")

        result_dict = record.to_dict()
        result_dict['imaging_reports'] = imaging_reports_data  # 添加影像报告信息
        
        print(f"\n=== to_dict() 返回的数据 ===")
        print(f"height: {result_dict.get('height')}")
        print(f"weight: {result_dict.get('weight')}")
        print(f"breast_discovery_date: {result_dict.get('breast_discovery_date')}")
        print(f"imaging_reports count: {len(imaging_reports_data)}")
        print(f"========================\n")

        return Response.success(result_dict, '档案创建成功', 201)
        
    except Exception as e:
        db.session.rollback()
        return Response.error(f'创建档案失败: {str(e)}')


@b_record_bp.route('/<int:record_id>', methods=['PUT'])
@login_required
def update_record(current_user, record_id):
    """
    更新健康档案

    ISDoc
    @description 兼容B端/C端两套档案：通过 query 参数 type=b_end/c_end 区分
    @queryParam type {string} 可选，默认 b_end
    """
    try:
        record_type = request.args.get('type', 'b_end')
        if record_type == 'c_end':
            record = CHealthRecord.query.get(record_id)
            if not record:
                return Response.error('档案不存在', 404)

            data = request.json or {}
            for key, value in data.items():
                if hasattr(record, key):
                    setattr(record, key, value)

            record.updated_at = datetime.utcnow()
            db.session.commit()
            return Response.success(record.to_dict(), '档案更新成功')

        record = BHealthRecord.query.get(record_id)
        if not record:
            return Response.error('档案不存在', 404)
        
        data = request.json
        
        # 辅助函数：将空字符串转换为 None，并处理数值类型
        def clean_value(value, value_type=None):
            """清理值：空字符串转为None，数值类型进行转换"""
            if value is None or value == '':
                return None
            if value_type == 'float':
                try:
                    return float(value) if value else None
                except (ValueError, TypeError):
                    return None
            if value_type == 'int':
                try:
                    return int(value) if value else None
                except (ValueError, TypeError):
                    return None
            return value

        def list_to_string(value):
            """
            ISDoc: 多选字段规范化（list -> 逗号分隔字符串；空字符串 -> None）
            """
            if value is None:
                return None
            if isinstance(value, list):
                return ','.join([str(x) for x in value if str(x).strip() != '']) or None
            if isinstance(value, str):
                v = value.strip()
                return v if v != '' else None
            return str(value)

        def parse_date(value):
            """
            ISDoc: 解析 YYYY-MM-DD 日期字符串为 date；空值返回 None
            """
            if value is None:
                return None
            if isinstance(value, str):
                v = value.strip()
                if v == '':
                    return None
                try:
                    return datetime.strptime(v, '%Y-%m-%d').date()
                except Exception:
                    return None
            if hasattr(value, 'year') and hasattr(value, 'month') and hasattr(value, 'day'):
                return value.date() if hasattr(value, 'date') else value
            return None

        # 更新字段
        # （一）基本信息
        if 'age' in data:
            record.age = clean_value(data['age'], 'int')
        if 'height' in data:
            record.height = clean_value(data['height'], 'float')
        if 'weight' in data:
            record.weight = clean_value(data['weight'], 'float')
        if 'phone' in data:
            record.phone = data['phone']
        if 'diabetes_history' in data:
            record.diabetes_history = data['diabetes_history']
        if 'gaofang_address' in data:
            record.gaofang_address = data['gaofang_address']
        if 'birads_level' in data:
            record.birads_level = data['birads_level']
        if 'family_history' in data:
            record.family_history = list_to_string(data['family_history'])

        # 病程信息 - 各结节类型的发现时间
        # 允许前端清空日期（传空字符串）时置空；乳腺兼容 discovery_date 别名
        if 'breast_discovery_date' in data or 'discovery_date' in data:
            record.breast_discovery_date = parse_date(data.get('breast_discovery_date', data.get('discovery_date')))
        if 'thyroid_discovery_date' in data:
            record.thyroid_discovery_date = parse_date(data.get('thyroid_discovery_date'))
        if 'lung_discovery_date' in data:
            record.lung_discovery_date = parse_date(data.get('lung_discovery_date'))
        if 'course_stage' in data:
            record.course_stage = data['course_stage']
        if 'tnm_stage' in data:
            record.tnm_stage = data['tnm_stage']

        # （二）乳腺影像学特征
        if 'symptoms' in data:
            record.symptoms = list_to_string(data['symptoms'])
        if 'symptoms_other' in data:
            record.symptoms_other = data['symptoms_other']
        if 'breast_symptoms_other' in data:
            record.breast_symptoms_other = data['breast_symptoms_other']
        if 'pain_level' in data:
            record.pain_level = data['pain_level']
        if 'pain_type' in data:
            record.pain_type = data['pain_type']
        if 'nipple_discharge_type' in data:
            record.nipple_discharge_type = data['nipple_discharge_type']
        if 'skin_change_type' in data:
            record.skin_change_type = data['skin_change_type']
        if 'nodule_location' in data:
            record.nodule_location = data['nodule_location']
        if 'nodule_size' in data:
            record.nodule_size = data['nodule_size']
        if 'boundary_features' in data:
            record.boundary_features = data['boundary_features']
        if 'internal_echo' in data:
            record.internal_echo = data['internal_echo']
        if 'blood_flow_signal' in data:
            record.blood_flow_signal = data['blood_flow_signal']
        if 'elasticity_score' in data:
            record.elasticity_score = data['elasticity_score']
        if 'nodule_quantity' in data:
            record.nodule_quantity = data['nodule_quantity']
        if 'nodule_count' in data:
            record.nodule_count = data['nodule_count']

        # （二）肺部影像学特征（仅包含报告实际使用的字段）
        if 'lung_symptoms' in data:
            record.lung_symptoms = data['lung_symptoms']
        if 'lung_symptoms_other' in data:
            record.lung_symptoms_other = data['lung_symptoms_other']
        if 'lung_rads_level' in data:
            record.lung_rads_level = data['lung_rads_level']
        if 'lung_nodule_size' in data:
            record.lung_nodule_size = data['lung_nodule_size']
        if 'lung_nodule_count' in data:
            record.lung_nodule_count = data['lung_nodule_count']
        if 'lung_cancer_history' in data:
            record.lung_cancer_history = data['lung_cancer_history']
        if 'lung_cancer_history_other' in data:
            record.lung_cancer_history_other = data['lung_cancer_history_other']
        # 注意：以下字段已从报告移除，不再更新：
        # - lung_nodule_location, lung_boundary_features, lung_internal_echo, lung_blood_flow_signal

        # （二）甲状腺影像学特征
        if 'thyroid_symptoms' in data:
            record.thyroid_symptoms = data['thyroid_symptoms']
        if 'thyroid_symptoms_other' in data:
            record.thyroid_symptoms_other = data['thyroid_symptoms_other']
        if 'tirads_level' in data:
            record.tirads_level = data['tirads_level']
        if 'thyroid_nodule_location' in data:
            record.thyroid_nodule_location = data['thyroid_nodule_location']
        if 'thyroid_nodule_size' in data:
            record.thyroid_nodule_size = data['thyroid_nodule_size']
        if 'thyroid_nodule_count' in data:
            record.thyroid_nodule_count = data['thyroid_nodule_count']
        if 'thyroid_boundary_features' in data:
            record.thyroid_boundary_features = data['thyroid_boundary_features']
        if 'thyroid_internal_echo' in data:
            record.thyroid_internal_echo = data['thyroid_internal_echo']
        if 'thyroid_blood_flow_signal' in data:
            record.thyroid_blood_flow_signal = data['thyroid_blood_flow_signal']

        # 生物节律
        if 'rhythm_type' in data:
            record.rhythm_type = data['rhythm_type']
        if 'cycle_phase' in data:
            record.cycle_phase = data['cycle_phase']
        if 'sleep_quality' in data:
            record.sleep_quality = data['sleep_quality']
        if 'sleep_condition' in data:
            record.sleep_condition = data['sleep_condition']

        # 检查历史
        if 'exam_history_type' in data:
            record.exam_history_type = data['exam_history_type']
        if 'exam_special_situation' in data:
            record.exam_special_situation = data['exam_special_situation']
        if 'exam_subcategory' in data:
            record.exam_subcategory = data['exam_subcategory']
        if 'exam_history_detail' in data:
            record.exam_history_detail = data['exam_history_detail']
        if 'previous_exam_history' in data:
            record.previous_exam_history = data['previous_exam_history']

        # 生活方式
        if 'exercise_frequency' in data:
            record.exercise_frequency = data['exercise_frequency']
        if 'lifestyle' in data:
            record.lifestyle = data['lifestyle']

        # （三）既往病史与风险分层
        if 'breast_disease_history' in data:
            record.breast_disease_history = list_to_string(data['breast_disease_history'])
        if 'breast_disease_history_other' in data:
            record.breast_disease_history_other = data['breast_disease_history_other']
        if 'family_genetic_history' in data:
            record.family_genetic_history = data['family_genetic_history']
        if 'family_history_other' in data:
            record.family_history_other = data['family_history_other']
            record.family_genetic_history = data['family_genetic_history']
        if 'previous_biopsy_history' in data:
            record.previous_biopsy_history = data['previous_biopsy_history']
        if 'contraceptive_risk_level' in data:
            record.contraceptive_risk_level = data['contraceptive_risk_level']
        if 'smoking_risk_level' in data:
            record.smoking_risk_level = data['smoking_risk_level']
        if 'diabetes_control_level' in data:
            record.diabetes_control_level = data['diabetes_control_level']
        
        if 'status' in data:
            record.status = data['status']
        
        record.updated_at = datetime.utcnow()
        db.session.commit()
        
        return Response.success(record.to_dict(), '档案更新成功')
        
    except Exception as e:
        db.session.rollback()
        return Response.error(f'更新档案失败: {str(e)}')


@b_record_bp.route('/<int:record_id>', methods=['DELETE'])
@login_required
def delete_record(current_user, record_id):
    """
    删除健康档案（同时删除关联的影像报告文件）

    ISDoc
    @description 兼容B端/C端两套档案：通过 query 参数 type=b_end/c_end 区分
    @queryParam type {string} 可选，默认 b_end
    """
    try:
        record_type = request.args.get('type', 'b_end')
        if record_type == 'c_end':
            record = CHealthRecord.query.get(record_id)
            if not record:
                return Response.error('档案不存在', 404)

            # C端档案的报告外键指向 c_health_records.id
            from models import CReport
            reports = CReport.query.filter_by(record_id=record_id).all()
            for report in reports:
                db.session.delete(report)

            db.session.delete(record)
            db.session.commit()
            return Response.success(None, '档案删除成功')

        record = BHealthRecord.query.get(record_id)
        if not record:
            return Response.error('档案不存在', 404)

        # ✅ 先删关联的健康报告：BReport.record_id 外键指向 b_health_records.id
        # 否则先删档案会触发外键约束，导致 commit() 失败 -> 400
        from models import BReport
        reports = BReport.query.filter_by(record_id=record_id).all()
        for report in reports:
            db.session.delete(report)
        
        # 删除关联的影像报告文件
        from models import BImagingReport
        from utils.file_upload import file_upload_manager
        
        imaging_reports = BImagingReport.query.filter_by(record_id=record_id).all()
        for img_report in imaging_reports:
            # 删除文件
            if img_report.file_path:
                file_upload_manager.delete_file(img_report.file_path)
            # 删除数据库记录
            db.session.delete(img_report)
        
        print(f"✅ 已删除 {len(reports)} 个关联的健康报告")
        print(f"✅ 已删除 {len(imaging_reports)} 个关联的影像报告文件")
        
        # 删除健康档案
        db.session.delete(record)
        db.session.commit()
        
        return Response.success(None, '档案删除成功')
        
    except Exception as e:
        db.session.rollback()
        return Response.error(f'删除档案失败: {str(e)}')

