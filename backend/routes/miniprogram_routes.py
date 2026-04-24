"""
微信小程序专用路由
结合B端系统，实现小程序问卷 → B端报告生成流程
"""
from flask import Blueprint, request, jsonify
from config import Config
from sqlalchemy import Date, DateTime, Integer, Float, Boolean, Text
from models import db, User, CPatient, CHealthRecord, CReport, MiniprogramImagingUpload
from utils.response import Response
from utils.id_generator import generate_record_code, generate_report_code
from services.llm_service import llm_generator
from routes.llm_helpers import (
    generate_comprehensive_conclusion_with_llm,
    generate_imaging_conclusion_with_llm,
    generate_recommendations_by_category,
    clean_markdown_formatting,
    format_text_with_line_breaks
)
from utils.report_manager import (
    get_template_path,
    extract_template_fields,
    prepare_llm_patient_data
)
from utils.data_normalizer import (
    clean_empty_string,
    clean_numeric_value,
    list_to_string,
    pick_first,
    parse_date
)
from datetime import datetime
import re
import uuid
import os
import threading

miniprogram_bp = Blueprint('miniprogram', __name__, url_prefix='/api/miniprogram')


@miniprogram_bp.route('/config', methods=['GET'])
def get_miniprogram_config():
    """
    ISDoc
    @description 小程序运行时配置下发（用于避免前端发版）
    @response 200 { ai_tongue: { id_code: string } }
    """
    return Response.success({
        'ai_tongue': {
            'id_code': getattr(Config, 'AI_TONGUE_ID_CODE', '') or ''
        }
    }, '获取成功')


def _detect_file_type(filename: str) -> str:
    """
    ISDoc
    @description 根据扩展名判断文件类型（pdf/image）
    """
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    if ext == 'pdf':
        return 'pdf'
    if ext in ('jpg', 'jpeg', 'png', 'webp'):
        return 'image'
    return 'unknown'


def _save_miniprogram_upload(file_storage, subdir: str = 'uploads/miniprogram') -> tuple:
    """
    ISDoc
    @description 保存小程序上传文件到本地目录，返回 (file_path, file_size)
    """
    os.makedirs(subdir, exist_ok=True)
    original = file_storage.filename or 'upload'
    ext = original.rsplit('.', 1)[-1].lower() if '.' in original else ''
    safe_ext = ext if ext and len(ext) <= 10 else ''
    unique_name = f"{uuid.uuid4().hex}{('.' + safe_ext) if safe_ext else ''}"
    file_path = os.path.join(subdir, unique_name)
    file_storage.save(file_path)
    file_size = os.path.getsize(file_path) if os.path.exists(file_path) else None
    return file_path, file_size


@miniprogram_bp.route('/imaging-reports/upload', methods=['POST'])
def upload_imaging_report():
    """
    ISDoc
    @description 小程序上传影像报告（图片/PDF），用于提交前暂存；返回 upload_id
    @request form-data: file, phone(optional), openid(optional), nodule_type(optional)
    """
    try:
        f = request.files.get('file')
        if not f or not f.filename:
            return Response.error('文件不能为空', 400)

        # 20MB 限制
        f.seek(0, os.SEEK_END)
        size = f.tell()
        f.seek(0)
        if size > 20 * 1024 * 1024:
            return Response.error('文件大小不能超过20MB', 400)

        file_type = _detect_file_type(f.filename)
        if file_type == 'unknown':
            return Response.error('不支持的文件类型（仅支持PDF/JPG/PNG/WebP）', 400)

        phone = (request.form.get('phone') or '').strip()
        openid = (request.form.get('openid') or '').strip()
        nodule_type = (request.form.get('nodule_type') or '').strip()

        file_path, file_size = _save_miniprogram_upload(f)

        extracted_text = None
        extracted_data = None
        if file_type == 'pdf':
            # 轻量提取文本（结构化提取留到提交后结合nodule_type再做）
            try:
                from services.pdf_parser import pdf_parser
                extracted_text = pdf_parser.extract_text_from_pdf(file_path)
            except Exception:
                extracted_text = None

        upload = MiniprogramImagingUpload(
            phone=phone or None,
            openid=openid or None,
            nodule_type=nodule_type or None,
            file_name=f.filename,
            file_path=file_path,
            file_size=file_size,
            file_type=file_type,
            extracted_text=extracted_text,
            extracted_data=extracted_data,
            status='uploaded'
        )
        db.session.add(upload)
        db.session.commit()

        return Response.success({
            'upload_id': upload.id,
            'file_name': upload.file_name,
            'file_type': upload.file_type,
            'file_size': upload.file_size
        }, '上传成功')
    except Exception as e:
        db.session.rollback()
        return Response.error(f'上传失败: {str(e)}', 500)


@miniprogram_bp.route('/imaging-reports/<int:upload_id>', methods=['DELETE'])
def delete_imaging_report(upload_id: int):
    """
    ISDoc
    @description 删除小程序临时上传文件（仅影响本次提交引用）
    """
    try:
        upload = MiniprogramImagingUpload.query.get(upload_id)
        if not upload:
            return Response.success({'deleted': False}, '文件不存在或已删除')

        # 删除文件
        try:
            if upload.file_path and os.path.exists(upload.file_path):
                os.remove(upload.file_path)
        except Exception:
            pass

        upload.status = 'deleted'
        db.session.delete(upload)
        db.session.commit()
        return Response.success({'deleted': True}, '删除成功')
    except Exception as e:
        db.session.rollback()
        return Response.error(f'删除失败: {str(e)}', 500)

# 字段中文标签映射表（基于B端BHealthRecord字段）
FIELD_LABEL_MAP = {
    # 基本信息
    'age': '年龄',
    'gender': '性别',
    'height': '身高(cm)',
    'weight': '体重(kg)',
    'phone': '联系电话',
    'gaofang_address': '可接收膏方的收货地址',
    'diabetes_history': '糖尿病史',
    
    # 病程信息
    'nodule_discovery_time': '结节发现时间',
    'breast_discovery_date': '乳腺结节发现时间',
    'lung_discovery_date': '肺结节发现时间',
    'thyroid_discovery_date': '甲状腺结节发现时间',
    'course_stage': '病程阶段',
    'tnm_stage': 'TNM分期',
    
    # 影像学信息
    'birads_level': 'BI-RADS分级',
    'lung_rads_level': 'Lung-RADS分级',
    'nodule_location': '结节位置',
    'nodule_size': '结节大小',
    'lung_nodule_size': '肺结节大小',
    'lung_nodule_count': '肺结节数量',
    'lung_nodule_location': '肺结节位置',
    'thyroid_nodule_size': '甲状腺结节大小',
    'thyroid_nodule_count': '甲状腺结节数量',
    'thyroid_nodule_quantity': '甲状腺结节数量（单发/多发）',
    'boundary_features': '边界特征',
    'lung_boundary_features': '肺结节边界特征',
    'internal_echo': '内部回声',
    'lung_internal_echo': '肺结节内部回声',
    'blood_flow_signal': '血流信号',
    'lung_blood_flow_signal': '肺结节血流信号',
    'elasticity_score': '弹性评分',
    
    # 症状信息
    'symptoms': '症状',
    'symptoms_other': '其他症状',
    'breast_symptoms_other': '乳腺其他症状',
    'lung_symptoms': '肺部症状',
    'lung_symptoms_other': '肺部其他症状',
    'thyroid_symptoms_other': '甲状腺其他症状',
    'pain_level': '疼痛程度',
    'pain_type': '疼痛类型',
    'nipple_discharge_type': '乳头溢液类型',
    'skin_change_type': '皮肤变化类型',
    
    # 家族史
    'family_history': '家族史',
    'family_history_other': '其他家族史',
    'family_genetic_history': '家族遗传史',
    'breast_family_history': '乳腺家族史',
    'breast_family_history_other': '乳腺家族史其他',
    'lung_family_history': '肺部家族史',
    'lung_family_history_other': '肺部家族史其他',
    'thyroid_family_history': '甲状腺家族史',
    'thyroid_family_history_other': '甲状腺家族史其他',
    'hereditary_breast_history': '遗传性乳腺病史',
    
    # 疾病史
    'breast_disease_history': '乳腺疾病史',
    'breast_disease_history_other': '其他乳腺疾病史',
    'breast_hyperplasia_history': '乳腺增生病史',
    'breast_fibroadenoma_history': '乳腺纤维瘤病史',
    'breast_cyst_history': '乳腺囊肿病史',
    'breast_inflammation_history': '乳腺炎病史',
    'breast_cancer_history': '乳腺癌病史',
    'autoimmune_disease_history': '自身免疫疾病',
    'autoimmune_other': '其他自身免疫疾病',
    'radiation_exposure_history': '辐射暴露史',
    'radiation_other': '其他辐射暴露',
    'dust_exposure_history': '粉尘/有害气体接触史',
    
    # 用药史
    'medication_history': '药物使用史',
    'medication_other': '其他药物使用',
    'breast_medication_history': '乳腺用药史',
    'breast_medication_other': '乳腺用药史其他',
    'lung_medication_history': '肺部用药史',
    'lung_medication_other': '肺部用药史其他',
    'thyroid_medication_history': '甲状腺用药史',
    'thyroid_medication_other': '甲状腺用药史其他',
    
    # 检查史
    'exam_history_type': '检查史类型',
    'exam_subcategory': '检查史子分类',
    'exam_special_situation': '特殊检查史情况',
    'exam_history_detail': '检查史详情',
    'previous_exam_history': '既往检查史',
    'previous_biopsy_history': '既往活检史',
    'tumor_marker_test': '肿瘤标志物检查',
    
    # 结节数量
    'nodule_quantity': '结节数量（单发/多发）',
    'nodule_count': '多发结节个数',
    'lung_nodule_quantity': '肺结节数量（单发/多发）',
    
    # 风险因素
    'contraceptive_risk_level': '避孕药风险档位',
    'smoking_risk_level': '吸烟风险档位',
    'diabetes_control_level': '糖尿病控制档位',
    
    # 生物节律
    'rhythm_type': '节律类型',
    'cycle_phase': '周期阶段',
    'sleep_quality': '睡眠质量',
    'sleep_condition': '睡眠状况',
    
    # 生活方式
    'exercise_frequency': '运动频率',
    'lifestyle': '生活方式',
}

def _get_field_label(field_name: str) -> str:
    """
    获取字段的中文标签
    
    Args:
        field_name: 字段名
        
    Returns:
        中文标签，如果没有映射则返回字段名
    """
    return FIELD_LABEL_MAP.get(field_name, field_name)

def _get_field_options(field_name: str, nodule_type: str = 'breast') -> dict:
    """
    获取字段的选项配置（基于B端前端配置）
    
    Returns:
        {
            'type': 'radio' | 'checkbox-group' | 'text' | 'number' | 'date' | etc,
            'options': [...],  # 选项列表（如果是radio/checkbox-group）
            'otherField': 'xxx_other',  # "其他"字段名（如果有）
            'placeholder': '...'  # 占位符（如果有）
        }
    """
    # 乳腺结节字段选项（基于 breast-fields.js）
    breast_field_configs = {
        'diabetes_history': {
            'type': 'radio',
            'options': [
                {'value': '无', 'label': '无'},
                {'value': '有', 'label': '有'}
            ]
        },
        'symptoms': {
            'type': 'checkbox-group',
            'options': ['无症状', '乳房肿块', '乳房疼痛', '乳房胀满感', '乳头溢液', '乳房皮肤改变', '腋下淋巴结肿大', '其他'],
            'otherField': 'symptoms_other',
            'otherPlaceholder': '请输入其他症状'
        },
        'birads_level': {
            'type': 'radio',
            'options': [
                {'value': '不清楚', 'label': '不清楚'},
                {'value': '1', 'label': '1级'},
                {'value': '2', 'label': '2级'},
                {'value': '3', 'label': '3级'},
                {'value': '4A', 'label': '4A级'},
                {'value': '4B', 'label': '4B级'},
                {'value': '4C', 'label': '4C级'},
                {'value': '5', 'label': '5级'},
                {'value': '6', 'label': '6级'}
            ]
        },
        'nodule_quantity': {
            'type': 'radio',
            'options': [
                {'value': '单发', 'label': '单发'},
                {'value': '多发', 'label': '多发'}
            ]
        },
        'breast_disease_history': {
            'type': 'checkbox-group',
            'options': ['无', '乳腺增生病史', '乳腺纤维瘤病史', '乳腺囊肿病史', '乳腺炎病史', '乳腺癌病史', '其他'],
            'otherField': 'breast_disease_history_other',
            'otherPlaceholder': '请输入其他基础疾病史'
        },
        'family_history': {
            'type': 'checkbox-group',
            'options': ['无', '一级亲属（父母、子女、亲兄弟姐妹）', '二级亲属（伯父、姑妈、舅舅、姨妈、祖父母）', '三级亲属（表/堂兄妹）', '其他'],
            'otherField': 'family_history_other',
            'otherPlaceholder': '请输入其他家族史'
        },
        'medication_history': {
            'type': 'checkbox-group',
            'options': ['无', '中成药治疗', '激素调节药物', '维生素辅助治疗', '乳腺癌治疗药物', '其他'],
            'otherField': 'medication_other',
            'otherPlaceholder': '请输入其他药物使用史'
        },
        'height': {'type': 'number', 'placeholder': '例如: 165', 'unit': 'cm'},
        'weight': {'type': 'number', 'placeholder': '例如: 60', 'unit': 'kg'},
        'nodule_size': {'type': 'number', 'placeholder': '例如: 12.5', 'unit': 'mm'},
        'nodule_count': {'type': 'number', 'placeholder': '例如: 3'},
        'gaofang_address': {'type': 'text', 'placeholder': '如：XX省XX市XX区XX路XX号'},
        'breast_discovery_date': {'type': 'date'},
        'symptoms_other': {'type': 'text', 'placeholder': '请输入其他症状'},
        'breast_disease_history_other': {'type': 'text', 'placeholder': '请输入其他基础疾病史'},
        'family_history_other': {'type': 'text', 'placeholder': '请输入其他家族史'},
        'medication_other': {'type': 'text', 'placeholder': '请输入其他药物使用史'}
    }
    
    # 肺结节字段选项（基于 lung-options.js 和 LungRecordFormView.vue）
    lung_field_configs = {
        'lung_discovery_date': {'type': 'date'},
        'lung_symptoms': {
            'type': 'checkbox-group',
            'options': ['无症状', '咳嗽', '胸痛', '呼吸困难', '咯血', '全身症状', '其他'],
            'otherField': 'lung_symptoms_other',
            'otherPlaceholder': '请输入其他肺部症状'
        },
        'lung_rads_level': {
            'type': 'radio',
            'options': [
                {'value': '不清楚', 'label': '不清楚'},
                {'value': '1', 'label': 'LR 1 - 阴性 (几乎为0%，年度筛查)'},
                {'value': '2', 'label': 'LR 2 - 良性发现 (<1%，年度筛查)'},
                {'value': '3', 'label': 'LR 3 - 可能良性 (1%-2%，6个月随访LDCT)'},
                {'value': '4A', 'label': 'LR 4A - 低度可疑 (5%-15%，3个月随访CT或PET/CT)'},
                {'value': '4B', 'label': 'LR 4B - 高度可疑 (>15%，PET/CT或活检)'},
                {'value': '4X', 'label': 'LR 4X - 附加高度可疑 (>50%，极高风险)'}
            ]
        },
        'lung_nodule_quantity': {
            'type': 'radio',
            'options': [
                {'value': '单发', 'label': '单发'},
                {'value': '多发', 'label': '多发'}
            ]
        },
        'lung_cancer_history': {
            'type': 'checkbox-group',
            'options': ['无', '肺炎病史', '肺结核病史', '慢性阻塞性肺疾病', '肺纤维化', '肺癌病史', '其他'],
            'otherField': 'lung_cancer_history_other',
            'otherPlaceholder': '请输入其他肺部疾病史'
        },
        'lung_family_history': {
            'type': 'checkbox-group',
            'options': ['无', '一级亲属（父母、子女、亲兄弟姐妹）', '二级亲属（伯父、姑妈、舅舅、姨妈、祖父母）', '三级亲属（表/堂兄妹）', '其他'],
            'otherField': 'lung_family_history_other',
            'otherPlaceholder': '请输入其他家族史'
        },
        'lung_medication_history': {
            'type': 'checkbox-group',
            'options': ['无', '中成药治疗', '激素调节药物', '维生素辅助治疗', '其他'],
            'otherField': 'lung_medication_other',
            'otherPlaceholder': '请输入其他药物使用史'
        }
    }
    
    # 甲状腺结节字段选项
    thyroid_field_configs = {
        'thyroid_discovery_date': {'type': 'date'},
        'thyroid_symptoms': {
            'type': 'checkbox-group',
            'options': ['无症状', '颈部肿块', '压迫症状', '疼痛症状', '其他'],
            'otherField': 'thyroid_symptoms_other',
            'otherPlaceholder': '请输入其他甲状腺症状'
        },
        'tirads_level': {
            'type': 'radio',
            'options': [
                {'value': '不清楚', 'label': '不清楚'},
                {'value': '1', 'label': 'TI-RADS 1 - 正常甲状腺'},
                {'value': '2', 'label': 'TI-RADS 2 - 良性 (恶性风险0%)'},
                {'value': '3', 'label': 'TI-RADS 3 - 可能良性 (恶性风险<5%)'},
                {'value': '4A', 'label': 'TI-RADS 4A - 低度可疑 (恶性风险5%-10%)'},
                {'value': '4B', 'label': 'TI-RADS 4B - 中度可疑 (恶性风险10%-50%)'},
                {'value': '4C', 'label': 'TI-RADS 4C - 高度可疑 (恶性风险50%-95%)'},
                {'value': '5', 'label': 'TI-RADS 5 - 高度提示恶性 (恶性风险>95%)'},
                {'value': '6', 'label': 'TI-RADS 6 - 已确诊恶性'}
            ]
        },
        'thyroid_nodule_quantity': {
            'type': 'radio',
            'options': [
                {'value': '单发', 'label': '单发'},
                {'value': '多发', 'label': '多发'}
            ]
        },
        'hypothyroidism_history': {
            'type': 'checkbox-group',
            'options': ['无', '甲状腺功能亢进（甲亢）', '甲状腺功能减退（甲减）', '桥本甲状腺炎', '亚急性甲状腺炎', '甲状腺癌病史', '其他'],
            'otherField': 'hypothyroidism_history_other',
            'otherPlaceholder': '请输入其他甲状腺疾病史'
        },
        'thyroid_family_history': {
            'type': 'checkbox-group',
            'options': ['无', '一级亲属（父母、子女、亲兄弟姐妹）', '二级亲属（伯父、姑妈、舅舅、姨妈、祖父母）', '三级亲属（表/堂兄妹）', '其他'],
            'otherField': 'thyroid_family_history_other',
            'otherPlaceholder': '请输入其他家族史'
        },
        'thyroid_medication_history': {
            'type': 'checkbox-group',
            'options': ['无', '甲状腺激素治疗', '抗甲状腺药物', '放射性碘治疗', '中成药治疗', '其他'],
            'otherField': 'thyroid_medication_other',
            'otherPlaceholder': '请输入其他药物使用史'
        }
    }
    
    # 合并所有配置
    all_configs = {**breast_field_configs}
    if 'lung' in nodule_type:
        all_configs.update(lung_field_configs)
    if 'thyroid' in nodule_type:
        all_configs.update(thyroid_field_configs)
    
    # 返回字段配置，如果没有则返回默认
    config = all_configs.get(field_name, {})
    
    # 如果没有配置，使用默认类型推断
    if not config:
        # 根据字段名推断类型
        if field_name.endswith('_date') or field_name.endswith('discovery_date'):
            config = {'type': 'date'}
        elif field_name in ['height', 'weight', 'nodule_count', 'nodule_size', 'lung_nodule_count', 'lung_nodule_size', 'thyroid_nodule_count', 'thyroid_nodule_size', 'age']:
            config = {'type': 'number'}
        else:
            config = {'type': 'text'}
    
    return config

def _infer_input_type(column) -> str:
    """
    推断字段在小程序端的输入类型（已废弃，使用 _get_field_options）

    Returns:
        str: text/number/float/date/datetime/boolean/textarea
    """
    try:
        t = getattr(column, 'type', None)
        if isinstance(t, (Integer, )):
            return 'number'
        if isinstance(t, (Float, )):
            return 'float'
        if isinstance(t, (Date, )):
            return 'date'
        if isinstance(t, (DateTime, )):
            return 'datetime'
        if isinstance(t, (Boolean, )):
            return 'boolean'
        if isinstance(t, (Text, )):
            return 'textarea'
    except Exception:
        pass
    return 'text'


@miniprogram_bp.route('/questionnaire/schema', methods=['GET'])
def get_questionnaire_schema():
    """
    获取“引导式问卷”schema（基于B端BHealthRecord全字段自动生成）
    根据结节类型智能过滤字段，只显示相关字段

    Query:
        nodule_type: 结节类型（breast/lung/thyroid/breast_lung/breast_thyroid/lung_thyroid/triple）

    Returns:
        groups: 分组后的字段列表（每个字段包含 name/label/type/required）
    """
    nodule_type = (request.args.get('nodule_type') or 'breast').strip()

    # 需要排除的系统字段（不对患者提问）
    exclude_fields = {
        'id', 'patient_id', 'record_code', 'created_by', 'created_at', 'updated_at',
        'status', 'data_completeness'
    }

    # ========== 基于B端前端实际使用的字段定义 ==========
    # 参考：frontend/vue-app/src/config/breast-fields.js
    # 以及：frontend/vue-app/src/views/LungRecordFormView.vue 等
    
    # 基础信息字段（这些字段在首页已填写，问卷中不显示）
    # 首页填写：name, age, gender, phone, height, weight, diabetes_history, gaofang_address
    basic_fields_skipped = ['name', 'age', 'gender', 'phone', 'height', 'weight', 'diabetes_history', 'gaofang_address']
    
    # 问卷中的基础字段（通常为空，因为都在首页填写了）
    basic_fields = []
    
    # 乳腺结节字段（基于 breast-fields.js）
    # 注意：基本信息（姓名、年龄、性别、身高、体重、糖尿病史、地址、手机号）已在首页填写
    # 问卷中只显示影像学特征相关字段
    breast_fields_map = {
        '基本信息': [],  # 首页已填写，问卷中跳过
        '影像学特征': [
            # 按用户要求的顺序：等级、发现时间、结节数量和大小、症状、基础病史、家族史、药物史（共7题）
            'birads_level',  # 等级
            'breast_discovery_date',  # 发现时间
            'nodule_quantity',  # 结节数量（单发/多发，会组合显示大小）
            'symptoms',  # 结节症状
            'breast_disease_history',  # 基础病史
            'family_history',  # 家族病史
            'medication_history',  # 药物使用史
            # 注意：不再单独显示 _other 字段，它们会在对应的多选题中显示输入框
        ]
    }
    
    # 肺结节字段（基于 LungRecordFormView.vue）
    # 注意：基本信息已在首页填写，问卷中只显示影像学特征
    lung_fields_map = {
        '基本信息': [],  # 首页已填写，问卷中跳过
        '影像学特征': [
            # 按用户要求的顺序：等级、发现时间、结节数量和大小、症状、家族史、药物史
            'lung_rads_level',  # 等级
            'lung_discovery_date',  # 发现时间
            'lung_nodule_quantity',  # 结节数量（单发/多发，会组合显示大小）
            'lung_symptoms',  # 结节症状
            'lung_family_history',  # 家族病史（多结节用器官级字段）
            'lung_medication_history',  # 药物使用史（多结节用器官级字段）
            # 单肺结节时使用通用字段
            'family_history',  # 单肺结节用通用字段
            'medication_history',  # 单肺结节用通用字段
            # 注意：不再单独显示 _other 字段
        ]
    }
    
    # 甲状腺结节字段（基于 ThyroidRecordFormView.vue）
    # 注意：基本信息已在首页填写，问卷中只显示影像学特征
    thyroid_fields_map = {
        '基本信息': [],  # 首页已填写，问卷中跳过
        '影像学特征': [
            # 按用户要求的顺序：等级、发现时间、结节数量和大小、症状、家族史、药物史
            'tirads_level',  # 等级
            'thyroid_discovery_date',  # 发现时间
            'thyroid_nodule_quantity',  # 结节数量（单发/多发，会组合显示大小）
            'thyroid_symptoms',  # 结节症状
            'thyroid_family_history',  # 家族病史
            'thyroid_medication_history',  # 药物使用史
            # 注意：不再单独显示 _other 字段
        ]
    }

    # 根据结节类型获取相关字段列表（不依赖数据库模型，直接基于配置）
    def get_fields_by_nodule_type(nodule_type):
        """根据结节类型返回相关字段列表（基于B端前端实际使用的字段）
        
        注意：基础字段（name, age, gender, phone, height, weight, diabetes_history, gaofang_address）
        已在首页填写，问卷中不显示这些字段
        """
        # 解析结节类型
        is_breast = 'breast' in nodule_type
        is_lung = 'lung' in nodule_type
        is_thyroid = 'thyroid' in nodule_type

        # 收集所有相关字段（排除已在首页填写的基础字段）
        relevant_fields = set()
        
        # 不在问卷中显示基础字段（已在首页填写）
        # 基础字段包括：name, age, gender, phone, height, weight, diabetes_history, gaofang_address

        # 按器官添加字段（只添加影像学特征字段，不添加基础字段）
        if is_breast:
            # 只添加影像学特征字段
            relevant_fields.update(breast_fields_map.get('影像学特征', []))

        if is_lung:
            # 只添加影像学特征字段
            relevant_fields.update(lung_fields_map.get('影像学特征', []))
            # 单肺结节场景下，可能需要兼容 nodule_quantity（如果前端用这个）
            if nodule_type == 'lung':
                relevant_fields.add('nodule_quantity')

        if is_thyroid:
            # 只添加影像学特征字段
            relevant_fields.update(thyroid_fields_map.get('影像学特征', []))

        # 多结节场景：添加器官特定的字段前缀
        if nodule_type in ['breast_lung', 'breast_thyroid', 'lung_thyroid', 'triple']:
            # 多结节场景下，字段名带有器官前缀（避免混淆）
            if is_breast and is_lung:
                # 乳腺+肺：确保使用带前缀的字段
                relevant_fields.update([
                    'breast_family_history', 'breast_family_history_other',
                    'breast_medication_history', 'breast_medication_other',
                    'lung_family_history', 'lung_family_history_other',
                    'lung_medication_history', 'lung_medication_other'
                ])
            if is_breast and is_thyroid:
                # 乳腺+甲状腺
                relevant_fields.update([
                    'breast_family_history', 'breast_family_history_other',
                    'breast_medication_history', 'breast_medication_other',
                    'thyroid_family_history', 'thyroid_family_history_other',
                    'thyroid_medication_history', 'thyroid_medication_other'
                ])
            if is_lung and is_thyroid:
                # 肺+甲状腺
                relevant_fields.update([
                    'lung_family_history', 'lung_family_history_other',
                    'lung_medication_history', 'lung_medication_other',
                    'thyroid_family_history', 'thyroid_family_history_other',
                    'thyroid_medication_history', 'thyroid_medication_other'
                ])

        return list(relevant_fields)

    # 根据结节类型获取相关字段（只包含B端前端实际使用的字段）
    relevant_field_names = get_fields_by_nodule_type(nodule_type)
    
    # 直接基于 relevant_field_names 构建字段定义（不依赖数据库模型）
    # 这样即使字段不在 CHealthRecord 中，也能正常显示
    def build_field_def(field_name):
        """为指定字段名构建字段定义"""
        # 获取字段配置（包含类型、选项等）
        field_config = _get_field_options(field_name, nodule_type)
        
        # 构建字段定义
        field_def = {
            'name': field_name,
            'label': _get_field_label(field_name),
            'type': field_config.get('type', 'text'),
            'required': False
        }
        
        # 添加选项（如果有）
        if 'options' in field_config:
            field_def['options'] = field_config['options']
        
        # 添加"其他"字段配置（如果有）
        if 'otherField' in field_config:
            field_def['otherField'] = field_config['otherField']
            field_def['otherPlaceholder'] = field_config.get('otherPlaceholder', '请输入其他')
        
        # 添加占位符和单位（如果有）
        if 'placeholder' in field_config:
            field_def['placeholder'] = field_config['placeholder']
        if 'unit' in field_config:
            field_def['unit'] = field_config['unit']
        
        return field_def
    
    # 为所有相关字段构建定义
    all_field_defs = [build_field_def(name) for name in relevant_field_names]

    # 分组：基础信息 / 影像学特征（与B端前端保持一致）
    # 注意：基础字段已在首页填写，问卷中不显示
    basic_group = []  # 应该是空的

    # 影像学特征字段（根据结节类型）
    imaging_field_names = []
    if 'breast' in nodule_type:
        imaging_field_names.extend(breast_fields_map.get('影像学特征', []))
    if 'lung' in nodule_type:
        imaging_field_names.extend(lung_fields_map.get('影像学特征', []))
        if nodule_type == 'lung':
            imaging_field_names.append('nodule_quantity')  # 单肺结节可能用这个
    if 'thyroid' in nodule_type:
        imaging_field_names.extend(thyroid_fields_map.get('影像学特征', []))

    # 从所有字段定义中筛选出影像学特征字段
    imaging_group = [f for f in all_field_defs if f['name'] in imaging_field_names]

    # 过滤掉 nodule_count 和 nodule_size（因为它们会和 nodule_quantity 一起显示）
    # 同样处理 lung_nodule_count/size 和 thyroid_nodule_count/size
    # 注意：只隐藏单独的 count 和 size 字段，保留 quantity 字段（它会组合显示）
    fields_to_hide = set()
    
    # 检查是否存在 quantity 字段
    existing_field_names = {f['name'] for f in imaging_group}
    
    # 如果存在 nodule_quantity，隐藏 nodule_count 和 nodule_size
    if 'nodule_quantity' in existing_field_names:
        if 'nodule_count' in existing_field_names:
            fields_to_hide.add('nodule_count')
        if 'nodule_size' in existing_field_names:
            fields_to_hide.add('nodule_size')
    
    # 如果存在 lung_nodule_quantity，隐藏 lung_nodule_count 和 lung_nodule_size
    if 'lung_nodule_quantity' in existing_field_names:
        if 'lung_nodule_count' in existing_field_names:
            fields_to_hide.add('lung_nodule_count')
        if 'lung_nodule_size' in existing_field_names:
            fields_to_hide.add('lung_nodule_size')
    
    # 如果存在 thyroid_nodule_quantity，隐藏 thyroid_nodule_count 和 thyroid_nodule_size
    if 'thyroid_nodule_quantity' in existing_field_names:
        if 'thyroid_nodule_count' in existing_field_names:
            fields_to_hide.add('thyroid_nodule_count')
        if 'thyroid_nodule_size' in existing_field_names:
            fields_to_hide.add('thyroid_nodule_size')
    
    # 移除需要隐藏的字段
    imaging_group = [f for f in imaging_group if f['name'] not in fields_to_hide]
    
    # 过滤掉所有单独的 "_other" 字段（它们会在对应的多选题中显示输入框，不应该单独显示）
    imaging_group = [f for f in imaging_group if not f['name'].endswith('_other')]
    
    # 确保 family_history 相关字段存在（它们是必需的）
    # 检查 family_history 是否存在，如果不在则添加（但不包括 _other 字段）
    family_history_fields = []
    if 'breast' in nodule_type:
        family_history_fields.append('family_history')
    if 'lung' in nodule_type:
        family_history_fields.append('lung_family_history')
        # 单肺结节时也使用通用字段
        if nodule_type == 'lung':
            family_history_fields.append('family_history')
    if 'thyroid' in nodule_type:
        family_history_fields.append('thyroid_family_history')
    
    # 确保这些字段存在（不包括 _other）
    existing_field_names = {f['name'] for f in imaging_group}
    for field_name in family_history_fields:
        if field_name not in existing_field_names:
            # 如果字段不存在，从 all_field_defs 中添加
            for field_def in all_field_defs:
                if field_def['name'] == field_name:
                    imaging_group.append(field_def)
                    break
            # 如果还是找不到，直接构建字段定义
            if field_name not in {f['name'] for f in imaging_group}:
                imaging_group.append(build_field_def(field_name))
    
    # 重新排序字段，按照用户要求的顺序：
    # 1. 等级（birads_level/lung_rads_level/tirads_level）
    # 2. 发现时间（discovery_date）
    # 3. 结节数量和大小（nodule_quantity，组合显示）
    # 4. 症状（symptoms）
    # 5. 家族史（family_history）
    # 6. 药物史（medication_history）
    
    def get_field_order(field_name):
        """获取字段的排序优先级"""
        # 等级字段
        if 'birads_level' in field_name or 'rads_level' in field_name or 'tirads_level' in field_name:
            return 1
        # 发现时间
        if 'discovery_date' in field_name:
            return 2
        # 结节数量（组合显示大小）
        if 'nodule_quantity' in field_name:
            return 3
        # 症状
        if 'symptoms' in field_name:
            return 4
        # 家族史
        if 'family_history' in field_name:
            return 5
        # 药物史
        if 'medication_history' in field_name:
            return 6
        # 其他字段放在后面
        return 99
    
    # 按照优先级排序
    imaging_group.sort(key=lambda f: get_field_order(f['name']))

    # 构建分组（只显示影像学特征，基础字段已在首页填写）
    groups = []
    
    # 如果基础组有字段才添加（通常应该是空的）
    if basic_group:
        groups.append({'id': 'basic', 'title': '基本信息', 'fields': basic_group})
    
    # 影像学特征组
    if imaging_group:
        groups.append({'id': 'imaging', 'title': '影像学特征', 'fields': imaging_group})

    return Response.success({
        'nodule_type': nodule_type,
        'groups': groups,
        'total_fields': len(imaging_group),
        'basic_count': 0,  # 基础字段已在首页填写
        'imaging_count': len(imaging_group)
    }, '获取schema成功')


def verify_phone(phone):
    """验证手机号格式"""
    if not phone:
        return False, "手机号不能为空"
    if not re.match(r'^1[3-9]\d{9}$', phone):
        return False, "手机号格式错误"
    return True, "验证通过"


def normalize_miniprogram_data(raw_data: dict) -> dict:
    """
    将小程序提交的问卷数据转换为B端格式
    
    通用处理规则：
    1. 数组/列表字段 → 逗号分隔字符串
    2. 日期字段 → date对象
    3. 数值字段 → int/float
    4. 空值清理
    
    Args:
        raw_data: 小程序提交的原始数据
        
    Returns:
        规范化后的数据字典
    """
    data = raw_data.copy() if raw_data else {}
    
    # 所有日期字段（包括通用和器官特定）
    date_fields = [
        'nodule_discovery_time',
        'breast_discovery_date', 'lung_discovery_date', 'thyroid_discovery_date'
    ]
    
    # 整数字段
    int_fields = ['age', 'pain_level']
    
    # 浮点数字段
    float_fields = ['height', 'weight']
    
    # 多选字段（数组转逗号字符串）
    multi_select_fields = [
        'symptoms', 'lung_symptoms',
        'family_history', 'breast_family_history', 'lung_family_history', 'thyroid_family_history',
        'medication_history', 'breast_medication_history', 'lung_medication_history', 'thyroid_medication_history',
        'breast_disease_history', 'autoimmune_disease_history', 'radiation_exposure_history',
        'previous_biopsy_history',
        'lung_nodule_location', 'lung_boundary_features', 'lung_internal_echo', 'lung_blood_flow_signal'
    ]
    
    # 处理数组/列表字段 → 逗号字符串
    for field in multi_select_fields:
        if field in data and data[field] is not None:
            if isinstance(data[field], list):
                # 过滤空值并转为字符串
                cleaned = [str(s).strip() for s in data[field] if s and str(s).strip()]
                data[field] = ','.join(cleaned) if cleaned else None
            elif isinstance(data[field], str):
                # 已经是字符串，保持原样
                pass
    
    # 处理所有数组字段（通用规则：如果字段值是数组，都转成逗号字符串）
    for key, value in list(data.items()):
        if isinstance(value, list) and key not in multi_select_fields:
            # 未在列表中的数组字段也处理
            cleaned = [str(s).strip() for s in value if s and str(s).strip()]
            data[key] = ','.join(cleaned) if cleaned else None
    
    # 处理日期字段
    for field in date_fields:
        if field in data and data[field]:
            try:
                if isinstance(data[field], str):
                    # 尝试解析日期字符串（支持 YYYY-MM-DD 格式）
                    data[field] = datetime.strptime(data[field], '%Y-%m-%d').date()
                elif isinstance(data[field], datetime):
                    data[field] = data[field].date()
            except (ValueError, TypeError, AttributeError):
                data[field] = None
    
    # 处理整数字段
    for field in int_fields:
        if field in data and data[field] is not None:
            try:
                data[field] = int(data[field])
            except (ValueError, TypeError):
                data[field] = None
    
    # 处理浮点数字段
    for field in float_fields:
        if field in data and data[field] is not None:
            try:
                data[field] = float(data[field])
            except (ValueError, TypeError):
                data[field] = None
    
    # 处理结节类型（小程序可能传 nodule_types 或 nodule_type）
    if 'nodule_types' in data and not data.get('nodule_type'):
        data['nodule_type'] = data['nodule_types']
    
    # 默认结节类型为 breast
    if not data.get('nodule_type'):
        data['nodule_type'] = 'breast'
    
    # 清理空值：将空字符串、None、空列表转为None（但保留0和False）
    for key in list(data.keys()):
        value = data[key]
        if value is None:
            continue
        if isinstance(value, str) and value.strip() == '':
            data[key] = None
        elif isinstance(value, list) and len(value) == 0:
            data[key] = None
    
    return data


@miniprogram_bp.route('/auth/wechat', methods=['POST'])
def wechat_auth():
    """
    微信小程序授权登录
    
    请求参数:
        code: 微信登录code（通过wx.login获取）
        encryptedData: 加密数据（可选）
        iv: 初始向量（可选）
        
    返回:
        openid: 微信OpenID
        session_key: 会话密钥（可选，用于后续解密）
        token: 访问令牌（可选）
    """
    data = request.json or {}
    code = data.get('code')
    
    if not code:
        return Response.error('缺少微信授权码', 400)
    
    try:
        # TODO: 调用微信API获取openid和session_key
        # 这里需要配置微信小程序的 AppID 和 AppSecret
        # import requests
        # wechat_appid = os.getenv('WECHAT_APPID')
        # wechat_secret = os.getenv('WECHAT_SECRET')
        # response = requests.get(
        #     f'https://api.weixin.qq.com/sns/jscode2session',
        #     params={
        #         'appid': wechat_appid,
        #         'secret': wechat_secret,
        #         'js_code': code,
        #         'grant_type': 'authorization_code'
        #     }
        # )
        # result = response.json()
        # openid = result.get('openid')
        # session_key = result.get('session_key')
        
        # 临时实现：返回模拟数据（实际使用时需要接入微信API）
        openid = data.get('openid') or f"OPENID_{uuid.uuid4().hex[:16]}"
        
        return Response.success({
            'openid': openid,
            'token': f"TOKEN_{uuid.uuid4().hex[:16]}"
        }, '授权成功')
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response.error(f'微信授权失败: {str(e)}', 500)


@miniprogram_bp.route('/questionnaire/submit', methods=['POST'])
def submit_questionnaire():
    """
    小程序提交问卷并生成报告
    
    请求参数:
        openid: 微信OpenID（可选，如果已授权）
        phone: 手机号（必填）
        name: 姓名（必填）
        questionnaire_data: 问卷数据（必填）
            - 基本信息：age, gender, height, weight
            - 结节类型：nodule_type (breast/lung/thyroid/breast_lung/breast_thyroid/lung_thyroid/triple)
            - 影像学信息：birads_level, nodule_size, nodule_location 等
            - 症状：symptoms, pain_level 等
            - 家族史：family_history
            - 其他B端健康档案字段...
        
    返回:
        report_id: 报告ID
        report_code: 报告编号
        report_html: 报告HTML内容（可选）
        download_token: 下载令牌
        risk_level: 风险等级
    """
    data = request.json or {}
    
    # 验证必填字段
    phone = data.get('phone')
    name = data.get('name')
    questionnaire_data = data.get('questionnaire_data', {})
    openid = data.get('openid')  # 可选
    
    if not phone:
        return Response.error('手机号不能为空', 400)
    if not name:
        return Response.error('姓名不能为空', 400)
    if not questionnaire_data:
        return Response.error('问卷数据不能为空', 400)
    
    # 验证手机号格式
    is_valid, message = verify_phone(phone)
    if not is_valid:
        return Response.error(message, 400)
    
    try:
        now = datetime.utcnow()
        
        # 1. 规范化问卷数据
        # 注意：小程序提交的 questionnaire_data 应该包含首页填写的基本信息（age, gender, height, weight, diabetes_history, gaofang_address）
        # 以及问卷中填写的影像学特征信息
        print(f"\n{'='*60}")
        print(f"📱 小程序问卷提交 - 原始数据检查")
        print(f"{'='*60}")
        print(f"原始 questionnaire_data 中的字段: {list(questionnaire_data.keys())}")
        print(f"age: {questionnaire_data.get('age')}")
        print(f"gender: {questionnaire_data.get('gender')}")
        print(f"height: {questionnaire_data.get('height')}")
        print(f"weight: {questionnaire_data.get('weight')}")
        print(f"diabetes_history: {questionnaire_data.get('diabetes_history')}")
        print(f"gaofang_address: {questionnaire_data.get('gaofang_address')}")
        
        normalized_data = normalize_miniprogram_data(questionnaire_data)
        nodule_type = normalized_data.get('nodule_type', 'breast')
        imaging_report_ids = normalized_data.get('imaging_report_ids') or []
        if isinstance(imaging_report_ids, str) and imaging_report_ids.strip():
            imaging_report_ids = [x.strip() for x in imaging_report_ids.split(',') if x.strip()]
        if not isinstance(imaging_report_ids, list):
            imaging_report_ids = []
        
        print(f"\n{'='*60}")
        print(f"📱 小程序问卷提交 - 结节类型: {nodule_type}")
        print(f"规范化后的数据检查:")
        print(f"  age: {normalized_data.get('age')}")
        print(f"  gender: {normalized_data.get('gender')}")
        print(f"  height: {normalized_data.get('height')}")
        print(f"  weight: {normalized_data.get('weight')}")
        print(f"  diabetes_history: {normalized_data.get('diabetes_history')}")
        print(f"  gaofang_address: {normalized_data.get('gaofang_address')}")
        print(f"{'='*60}")
        
        # 2. 查找或创建C端患者（只保留C端数据，不再创建B端影分身）
        c_patient = CPatient.query.filter_by(phone=phone).first()
        if not c_patient:
            c_patient_code = f"CP{now.strftime('%Y%m%d%H%M%S')}"
            c_patient = CPatient(
                patient_code=c_patient_code,
                name=name,
                phone=phone,
                age=clean_numeric_value(normalized_data.get('age'), 'int'),
                gender=normalized_data.get('gender'),
                nodule_type=nodule_type,
                wechat_openid=openid,
                source_channel='miniprogram',
                lead_status='reported',
                status='active'
            )
            db.session.add(c_patient)
            db.session.flush()
            print(f"✅ 创建C端患者: {c_patient_code}")
        else:
            c_patient.name = name or c_patient.name
            c_patient.age = clean_numeric_value(normalized_data.get('age'), 'int') or c_patient.age
            c_patient.gender = normalized_data.get('gender') or c_patient.gender
            c_patient.nodule_type = nodule_type or c_patient.nodule_type
            if openid:
                c_patient.wechat_openid = openid
            c_patient.source_channel = c_patient.source_channel or 'miniprogram'
            # 用户完成问卷后标记为已出报告
            c_patient.lead_status = c_patient.lead_status or 'reported'
            print(f"✅ 更新C端患者: {c_patient.patient_code}")
        
        # 3. 创建C端健康档案（只保留C端数据，不再创建B端影分身）
        def _to_int_or_none(v):
            try:
                if v is None or v == '':
                    return None
                return int(str(v).strip())
            except Exception:
                return None

        # 调试：打印即将保存的字段值
        # 注意：这里使用 normalized_data，因为 data 变量在后面才定义
        record_height = clean_numeric_value(normalized_data.get('height'), 'float')
        record_weight = clean_numeric_value(normalized_data.get('weight'), 'float')
        record_diabetes = clean_empty_string(normalized_data.get('diabetes_history'))
        record_address = clean_empty_string(normalized_data.get('gaofang_address'))
        print(f"\n[DEBUG] 即将保存到 CHealthRecord 的字段值:")
        print(f"  height: {record_height} (type: {type(record_height)})")
        print(f"  weight: {record_weight} (type: {type(record_weight)})")
        print(f"  diabetes_history: {record_diabetes} (type: {type(record_diabetes)})")
        print(f"  gaofang_address: {record_address} (type: {type(record_address)})")
        
        # 结节数量：单发/多发，以及多发时的个数
        # 逻辑：如果nodule_quantity是"单发"，nodule_count设为"1"；如果是"多发"，nodule_count使用实际个数
        nodule_quantity_val = clean_empty_string(pick_first(normalized_data, 'nodule_quantity', 'nodule_quantity_breast', 'breast_nodule_quantity'))
        nodule_count_val = clean_empty_string(pick_first(normalized_data, 'nodule_count', 'nodule_count_breast', 'breast_nodule_count'))
        nodule_count_final = '1' if nodule_quantity_val == '单发' else (nodule_count_val if nodule_quantity_val == '多发' else None)
        
        c_record = CHealthRecord(
            patient_id=c_patient.id,
            record_code=f"CR{now.strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:4].upper()}",
            age=clean_numeric_value(normalized_data.get('age'), 'int'),
            height=record_height,
            weight=record_weight,
            phone=phone,
            diabetes_history=record_diabetes,
            gaofang_address=record_address,
            birads_level=_to_int_or_none(normalized_data.get('birads_level')),
            family_history=list_to_string(pick_first(normalized_data, 'family_history', 'breast_family_history')),
            family_history_other=clean_empty_string(pick_first(normalized_data, 'family_history_other', 'breast_family_history_other')),
            symptoms=list_to_string(pick_first(normalized_data, 'symptoms', 'symptoms_breast')),
            symptoms_other=clean_empty_string(pick_first(normalized_data, 'symptoms_other', 'breast_symptoms_other')),
            breast_symptoms_other=clean_empty_string(pick_first(normalized_data, 'breast_symptoms_other', 'symptoms_other')),
            pain_level=clean_numeric_value(normalized_data.get('pain_level'), 'int'),
            pain_type=clean_empty_string(normalized_data.get('pain_type')),
            nodule_location=clean_empty_string(normalized_data.get('nodule_location')),
            nodule_size=clean_empty_string(pick_first(normalized_data, 'nodule_size', 'breast_size')),
            nodule_quantity=nodule_quantity_val,
            nodule_count=nodule_count_final,
            boundary_features=clean_empty_string(normalized_data.get('boundary_features')),
            internal_echo=clean_empty_string(normalized_data.get('internal_echo')),
            blood_flow_signal=clean_empty_string(normalized_data.get('blood_flow_signal')),
            elasticity_score=clean_empty_string(normalized_data.get('elasticity_score')),
            rhythm_type=clean_empty_string(normalized_data.get('rhythm_type')),
            sleep_quality=clean_empty_string(normalized_data.get('sleep_quality')),
            exam_history_type=clean_empty_string(normalized_data.get('exam_history_type')),
            exercise_frequency=clean_empty_string(normalized_data.get('exercise_frequency')),
            # 发现时间（兼容多种字段名）
            breast_discovery_date=parse_date(pick_first(normalized_data, 'breast_discovery_date', 'discovery_date', 'nodule_discovery_time', 'breast_discovery_time')),
            lung_discovery_date=parse_date(normalized_data.get('lung_discovery_date')),
            thyroid_discovery_date=parse_date(normalized_data.get('thyroid_discovery_date')),
            # 疾病史和用药史
            # 注意：如果字段为空或None，不设置默认值"无"，保持为None（前端会显示"-"）
            # 只有当用户明确选择了"无"时，才保存为"无"
            breast_disease_history=(list_to_string(normalized_data.get('breast_disease_history')) or None),
            breast_disease_history_other=clean_empty_string(normalized_data.get('breast_disease_history_other')),
            medication_history=(list_to_string(pick_first(normalized_data, 'medication_history', 'breast_medication_history')) or None),
            medication_other=clean_empty_string(pick_first(normalized_data, 'medication_other', 'breast_medication_other')),
            breast_medication_history=(list_to_string(pick_first(normalized_data, 'breast_medication_history', 'medication_history')) or None),
            breast_medication_other=clean_empty_string(pick_first(normalized_data, 'breast_medication_other', 'medication_other')),
            data_completeness='partial',
            status='completed'
        )
        db.session.add(c_record)
        db.session.flush()
        print(f"✅ 创建C端健康档案: {c_record.record_code}")
        
        # 4. 基于C端数据和提交的问卷数据生成报告
        # 4.1 从 normalized_data 直接构建 patient_data（用于LLM）
        # 注意：normalized_data 包含了所有提交的数据，比 CHealthRecord 字段更完整
        data = normalized_data  # 为了与代码一致，使用 data 变量名
        
        # 构建 patient_data 字典（用于 LLM 生成报告）
        patient_data = {
            'gender': data.get('gender', '女'),  # 必需字段
            'age': clean_numeric_value(data.get('age'), 'int'),
            'height': clean_numeric_value(data.get('height'), 'float'),
            'weight': clean_numeric_value(data.get('weight'), 'float'),
        }
        
        # 根据结节类型添加特定字段（复用 extract_breast_fields 等函数的逻辑）
        # 乳腺字段
        if nodule_type == 'triple' or 'breast' in nodule_type:
            patient_data.update({
                'birads_level': clean_empty_string(data.get('birads_level')),
                'nodule_size': clean_empty_string(pick_first(data, 'nodule_size', 'breast_size')),
                'nodule_quantity': clean_empty_string(pick_first(data, 'nodule_quantity', 'nodule_quantity_breast', 'breast_nodule_quantity')),
                'nodule_quantity_breast': clean_empty_string(pick_first(data, 'nodule_quantity', 'nodule_quantity_breast', 'breast_nodule_quantity')),
                'nodule_count': clean_empty_string(pick_first(data, 'nodule_count', 'nodule_count_breast', 'breast_nodule_count')),
                'nodule_count_breast': clean_empty_string(pick_first(data, 'nodule_count', 'nodule_count_breast', 'breast_nodule_count')),
                'symptoms': list_to_string(pick_first(data, 'symptoms', 'symptoms_breast')),
                'symptoms_other': clean_empty_string(pick_first(data, 'symptoms_other', 'breast_symptoms_other')),
                'breast_symptoms_other': clean_empty_string(pick_first(data, 'breast_symptoms_other', 'symptoms_other')),
                'family_history': list_to_string(pick_first(data, 'family_history', 'breast_family_history')),
                'family_history_other': clean_empty_string(pick_first(data, 'family_history_other', 'breast_family_history_other')),
                'breast_family_history': list_to_string(pick_first(data, 'breast_family_history', 'family_history')),
                'breast_family_history_other': clean_empty_string(pick_first(data, 'breast_family_history_other', 'family_history_other')),
                'medication_history': list_to_string(pick_first(data, 'medication_history', 'breast_medication_history')),
                'medication_other': clean_empty_string(pick_first(data, 'medication_other', 'breast_medication_other')),
                'breast_medication_history': list_to_string(pick_first(data, 'breast_medication_history', 'medication_history')),
                'breast_medication_other': clean_empty_string(pick_first(data, 'breast_medication_other', 'medication_other')),
                'breast_disease_history': list_to_string(data.get('breast_disease_history')) or '无',
                'breast_disease_history_other': clean_empty_string(data.get('breast_disease_history_other')),
                'breast_discovery_date': parse_date(pick_first(data, 'breast_discovery_date', 'discovery_date')),
            })
            # 格式化日期（从normalized_data中获取，因为可能已经被parse_date处理过）
            breast_date = pick_first(normalized_data, 'breast_discovery_date', 'discovery_date', 'nodule_discovery_time', 'breast_discovery_time')
            if breast_date:
                # 如果已经是date对象，直接格式化
                if hasattr(breast_date, 'strftime'):
                    patient_data['breast_discovery_date'] = breast_date.strftime('%Y年%m月%d日')
                # 如果是字符串，尝试解析
                elif isinstance(breast_date, str):
                    parsed_date = parse_date(breast_date)
                    if parsed_date:
                        patient_data['breast_discovery_date'] = parsed_date.strftime('%Y年%m月%d日')
                    else:
                        patient_data['breast_discovery_date'] = '未知'
                else:
                    patient_data['breast_discovery_date'] = '未知'
            else:
                patient_data['breast_discovery_date'] = '未知'
        
        # 肺字段
        if nodule_type == 'triple' or 'lung' in nodule_type:
            patient_data.update({
                'lung_rads_level': clean_empty_string(data.get('lung_rads_level')),
                'lung_nodule_size': clean_empty_string(pick_first(data, 'lung_nodule_size', 'lung_size')),
                'lung_nodule_quantity': clean_empty_string(pick_first(data, 'lung_nodule_quantity', 'nodule_quantity_lung')),
                'lung_nodule_count': clean_empty_string(pick_first(data, 'lung_nodule_count', 'nodule_count_lung')),
                'lung_symptoms': clean_empty_string(pick_first(data, 'lung_symptoms', 'symptoms_lung')),
                'lung_symptoms_other': clean_empty_string(data.get('lung_symptoms_other')),
                'lung_family_history': list_to_string(data.get('lung_family_history')),
                'lung_family_history_other': clean_empty_string(data.get('lung_family_history_other')),
                'lung_medication_history': list_to_string(data.get('lung_medication_history')),
                'lung_medication_other': clean_empty_string(data.get('lung_medication_other')),
                'lung_discovery_date': parse_date(data.get('lung_discovery_date')),
            })
            if patient_data.get('lung_discovery_date'):
                if hasattr(patient_data['lung_discovery_date'], 'strftime'):
                    patient_data['lung_discovery_date'] = patient_data['lung_discovery_date'].strftime('%Y年%m月%d日')
        
        # 甲状腺字段
        if nodule_type == 'triple' or 'thyroid' in nodule_type:
            patient_data.update({
                'tirads_level': clean_empty_string(data.get('tirads_level')),
                'thyroid_nodule_size': clean_empty_string(pick_first(data, 'thyroid_nodule_size', 'thyroid_size')),
                'thyroid_nodule_quantity': clean_empty_string(pick_first(data, 'thyroid_nodule_quantity', 'nodule_quantity_thyroid')),
                'thyroid_nodule_count': clean_empty_string(pick_first(data, 'thyroid_nodule_count', 'nodule_count_thyroid')),
                'thyroid_symptoms': clean_empty_string(pick_first(data, 'thyroid_symptoms', 'symptoms_thyroid')),
                'thyroid_symptoms_other': clean_empty_string(data.get('thyroid_symptoms_other')),
                'thyroid_family_history': list_to_string(data.get('thyroid_family_history')),
                'thyroid_family_history_other': clean_empty_string(data.get('thyroid_family_history_other')),
                'thyroid_medication_history': list_to_string(data.get('thyroid_medication_history')),
                'thyroid_medication_other': clean_empty_string(data.get('thyroid_medication_other')),
                'thyroid_discovery_date': parse_date(data.get('thyroid_discovery_date')),
            })
            if patient_data.get('thyroid_discovery_date'):
                if hasattr(patient_data['thyroid_discovery_date'], 'strftime'):
                    patient_data['thyroid_discovery_date'] = patient_data['thyroid_discovery_date'].strftime('%Y年%m月%d日')
        
        # 通用字段
        patient_data.update({
            'pain_level': clean_numeric_value(data.get('pain_level'), 'int'),
            'pain_type': clean_empty_string(data.get('pain_type')),
            'rhythm_type': clean_empty_string(data.get('rhythm_type')),
            'sleep_quality': clean_empty_string(data.get('sleep_quality')),
            'exam_history_type': clean_empty_string(data.get('exam_history_type')),
            'exercise_frequency': clean_empty_string(data.get('exercise_frequency')),
            'diabetes_history': clean_empty_string(data.get('diabetes_history')) or '无',
        })
        
        print(f"✅ 从问卷数据构建患者数据字段数: {len([k for k, v in patient_data.items() if v is not None and v != ''])}")
        
        # 4.2 知识库匹配和决策树处理（已移除，直接使用空值）
        # 注：知识库只有乳腺数据，其他结节类型暂不支持，后续可添加
        matched_knowledge = []  # 空列表，LLM会显示"无相关医学知识"
        tree_result = {}  # 空字典，LLM会使用默认值
        print(f"📚 知识库匹配和决策树: 已移除（使用空值）")
        
        # 5. 先保存占位报告，立即返回 report_id（避免小程序超时）
        report_code = generate_report_code()
        c_report = CReport(
            patient_id=c_patient.id,
            record_id=c_record.id,
            report_code=f"CPR{now.strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:4].upper()}",
            report_html='',  # 占位，后台线程填充
            imaging_conclusion='',
            imaging_risk_warning='',
            risk_level=None,
            status='pending_llm',  # 标记为待LLM处理
            download_token=uuid.uuid4().hex
        )
        db.session.add(c_report)
        db.session.commit()
        report_id = c_report.id
        print(f"✅ 占位报告已保存: id={report_id}, status=pending_llm")

        # 检查是否已分配健康管理师
        need_manager_contact = not c_patient.assigned_manager_id

        # 6. 后台线程：LLM调用 + 渲染HTML + 更新报告
        from flask import current_app
        app = current_app._get_current_object()

        def _run_llm_and_render(app, report_id, patient_data, tree_result, matched_knowledge,
                                nodule_type, c_patient_id, c_record_id, data_snapshot):
            with app.app_context():
                try:
                    print(f"[BG] 开始后台LLM处理, report_id={report_id}")

                    # 4.4 生成分类建议草稿
                    recommendations_draft = generate_recommendations_by_category(
                        patient_data, matched_knowledge
                    )
                    print(f"[BG] ✅ 已生成 {len(recommendations_draft.get('recommendations', []))} 条分类建议")

                    # 4.5 生成影像学综合结论
                    imaging_conclusion_dict = generate_imaging_conclusion_with_llm(
                        patient_data, tree_result, matched_knowledge, nodule_type=nodule_type
                    )
                    conclusion = clean_markdown_formatting(imaging_conclusion_dict.get('conclusion', ''))
                    risk_warning = clean_markdown_formatting(imaging_conclusion_dict.get('risk_warning', ''))
                    conclusion = format_text_with_line_breaks(conclusion)
                    risk_warning = format_text_with_line_breaks(risk_warning)

                    # 4.6 生成综合分析结论
                    comprehensive_conclusion = generate_comprehensive_conclusion_with_llm(
                        patient_data, tree_result, matched_knowledge, nodule_type=nodule_type
                    )

                    # 6. 渲染HTML报告
                    template_path = get_template_path(nodule_type)

                    class TempPatient:
                        def __init__(self, name, gender, phone, age):
                            self.name = name
                            self.gender = gender
                            self.phone = phone
                            self.age = age

                    class TempRecord:
                        def __init__(self, c_record_snapshot, data):
                            self._data = data
                            self._snap = c_record_snapshot
                            self.age = c_record_snapshot.get('age') or clean_numeric_value(data.get('age'), 'int')
                            self.height = clean_numeric_value(data.get('height'), 'float')
                            self.weight = clean_numeric_value(data.get('weight'), 'float')
                            self.phone = c_record_snapshot.get('phone')
                            self.breast_discovery_date = parse_date(pick_first(data, 'breast_discovery_date', 'discovery_date'))
                            self.lung_discovery_date = parse_date(data.get('lung_discovery_date'))
                            self.thyroid_discovery_date = parse_date(data.get('thyroid_discovery_date'))

                        def __getattr__(self, name):
                            if name in self._data:
                                value = self._data.get(name)
                                if value is not None:
                                    return value
                            if name in self._snap:
                                return self._snap[name]
                            return None

                    snap = data_snapshot
                    temp_patient = TempPatient(
                        name=snap['patient_name'],
                        gender=snap['patient_gender'],
                        phone=snap['patient_phone'],
                        age=snap['patient_age'],
                    )
                    temp_record = TempRecord(snap['record_snap'], patient_data)
                    template_fields = extract_template_fields(temp_patient, temp_record, nodule_type)

                    if nodule_type == 'triple':
                        template_fields.update({
                            'imaging_conclusion': conclusion,
                            'imaging_risk_warning': risk_warning,
                            'risk_warning': risk_warning,
                            'comprehensive_conclusion': comprehensive_conclusion,
                            'tcm_analysis': '（中医分析接口数据待接入）',
                            'report_code': snap['report_code'],
                        })
                    elif nodule_type in ['breast_lung', 'breast_thyroid', 'lung_thyroid']:
                        template_fields.update({
                            'imaging_conclusion': conclusion,
                            'imaging_risk_warning': risk_warning,
                            'risk_warning': risk_warning,
                            'comprehensive_conclusion': comprehensive_conclusion,
                            'report_code': snap['report_code'],
                        })
                    else:
                        template_fields.update({
                            'imaging_conclusion': conclusion,
                            'imaging_risk_warning': risk_warning,
                            'report_code': snap['report_code'],
                        })

                    from flask import render_template
                    report_html = render_template(template_path, **template_fields)

                    # 更新报告
                    c_report_obj = CReport.query.get(report_id)
                    if c_report_obj:
                        c_report_obj.report_html = report_html
                        c_report_obj.imaging_conclusion = conclusion
                        c_report_obj.imaging_risk_warning = risk_warning
                        c_report_obj.status = 'generated'
                        db.session.commit()
                        print(f"[BG] ✅ 报告已更新: id={report_id}, status=generated")
                    else:
                        print(f"[BG] ❌ 找不到报告记录: id={report_id}")

                except Exception as e:
                    import traceback
                    print(f"[BG] ❌ 后台LLM处理失败, report_id={report_id}: {e}")
                    traceback.print_exc()
                    try:
                        c_report_obj = CReport.query.get(report_id)
                        if c_report_obj:
                            c_report_obj.status = 'llm_failed'
                            db.session.commit()
                    except Exception:
                        pass

        # 构建快照（避免跨线程访问 SQLAlchemy 对象）
        c_record_snap = {
            'age': c_record.age,
            'phone': c_patient.phone,
        }
        data_snapshot = {
            'patient_name': c_patient.name,
            'patient_gender': data.get('gender', '女'),
            'patient_phone': c_patient.phone,
            'patient_age': clean_numeric_value(data.get('age'), 'int'),
            'record_snap': c_record_snap,
            'report_code': report_code,
        }

        t = threading.Thread(
            target=_run_llm_and_render,
            args=(app, report_id, patient_data, tree_result, matched_knowledge,
                  nodule_type, c_patient.id, c_record.id, data_snapshot),
            daemon=True
        )
        t.start()
        print(f"[BG] 后台线程已启动, report_id={report_id}")

        # 立即返回，不等待LLM
        return Response.success({
            'report_id': report_id,
            'report_code': report_code,
            'report_html': '',  # 报告生成中，result页面无需展示HTML
            'patient_code': c_patient.patient_code,
            'openid': openid,
            'need_manager_contact': need_manager_contact,
            'patient_id': c_patient.id
        }, '问卷提交成功，报告生成中')
        
    except Exception as e:
        db.session.rollback()
        import traceback
        error_trace = traceback.format_exc()
        print(f"\n❌ 小程序问卷提交失败:")
        print(error_trace)
        return Response.error(f'问卷提交失败: {str(e)}', 500)


@miniprogram_bp.route('/manager/contact', methods=['POST'])
def submit_manager_contact():
    """
    小程序提交健康管理师联系方式
    
    请求参数:
        patient_id: 患者ID（必填）
        manager_name: 健康管理师姓名（必填）
        manager_phone: 健康管理师电话（必填）
        manager_wechat: 健康管理师微信号（可选）
        manager_email: 健康管理师邮箱（可选）
        
    返回:
        success: 是否成功
        message: 提示信息
    """
    data = request.json or {}
    
    patient_id = data.get('patient_id')
    manager_name = data.get('manager_name', '').strip()
    manager_phone = data.get('manager_phone', '').strip()
    manager_wechat = data.get('manager_wechat', '').strip()
    manager_email = data.get('manager_email', '').strip()
    
    if not patient_id:
        return Response.error('患者ID不能为空', 400)
    if not manager_name:
        return Response.error('健康管理师姓名不能为空', 400)
    if not manager_phone:
        return Response.error('健康管理师电话不能为空', 400)
    
    # 验证手机号格式
    is_valid, message = verify_phone(manager_phone)
    if not is_valid:
        return Response.error(f'健康管理师电话格式错误: {message}', 400)
    
    try:
        # 查找患者
        c_patient = CPatient.query.get(patient_id)
        if not c_patient:
            return Response.error('患者不存在', 404)
        
        # 查找或创建健康管理师用户
        # 先按手机号查找
        manager = User.query.filter_by(phone=manager_phone).first()
        
        if not manager:
            # 如果不存在，创建新的健康管理师用户
            from werkzeug.security import generate_password_hash
            import random
            import string
            
            # 生成随机用户名（基于手机号）
            username = f"manager_{manager_phone[-4:]}_{''.join(random.choices(string.ascii_lowercase + string.digits, k=4))}"
            
            # 生成随机密码（8位）
            random_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            
            manager = User(
                username=username,
                password_hash=generate_password_hash(random_password),
                real_name=manager_name,
                phone=manager_phone,
                email=manager_email or None,
                wechat_id=manager_wechat or None,
                role='health_manager',
                is_active=True
            )
            db.session.add(manager)
            db.session.flush()
            print(f"✅ 创建新健康管理师: {username} ({manager_name})")
        else:
            # 更新现有管理师信息
            if manager_name:
                manager.real_name = manager_name
            if manager_email:
                manager.email = manager_email
            if manager_wechat:
                manager.wechat_id = manager_wechat
            print(f"✅ 更新健康管理师: {manager.username} ({manager_name})")
        
        # 分配管理师给患者
        c_patient.assigned_manager_id = manager.id
        c_patient.is_contacted = True
        c_patient.lead_status = 'contacted'  # 标记为已联系
        
        # 不再同步更新B端患者（只保留C端数据）
        
        db.session.commit()
        
        return Response.success({
            'manager_id': manager.id,
            'manager_name': manager.real_name,
            'manager_phone': manager.phone,
            'manager_wechat': manager.wechat_id,
            'patient_id': c_patient.id
        }, '健康管理师联系方式已保存')
        
    except Exception as e:
        db.session.rollback()
        import traceback
        error_trace = traceback.format_exc()
        print(f"\n❌ 提交健康管理师联系方式失败:")
        print(error_trace)
        return Response.error(f'提交失败: {str(e)}', 500)


@miniprogram_bp.route('/reports/<int:report_id>', methods=['GET'])
def get_report(report_id):
    """
    小程序查看报告
    
    请求参数:
        openid: 微信OpenID（可选，用于验证）
        phone: 手机号（可选，用于验证）
        
    返回:
        report_html: 报告HTML内容
        report_code: 报告编号
        risk_level: 风险等级
    """
    openid = request.args.get('openid')
    phone = request.args.get('phone')
    
    try:
        report = CReport.query.get(report_id)
        if not report:
            return Response.error('报告不存在', 404)

        # 可选：通过openid或phone验证访问权限（C端）
        if openid or phone:
            patient = CPatient.query.get(report.patient_id)
            if patient:
                if openid and patient.wechat_openid != openid:
                    return Response.error('OpenID不匹配', 403)
                if phone and patient.phone != phone:
                    return Response.error('手机号不匹配', 403)

        return Response.success({
            'report_id': report.id,
            'report_code': report.report_code,
            'report_html': report.report_html,
            'risk_level': report.risk_level,
            'generated_at': report.generated_at.strftime('%Y-%m-%d %H:%M:%S') if report.generated_at else None
        }, '获取成功')
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response.error(f'获取报告失败: {str(e)}', 500)


@miniprogram_bp.route('/reports/<int:report_id>/summary', methods=['GET'])
def get_report_summary(report_id):
    """
    ISDoc
    @description 小程序「报告生成结果」页专用：返回报告基础信息 + 健康管理师联系方式
    @queryParam report_code {string} 必填，用于校验 report_id 的有效性（避免顺序ID被撞库）
    @response 200 {report_id, report_code, patient_code, need_review, manager_contact}
    """
    report_code = (request.args.get('report_code') or '').strip()
    if not report_code:
        return Response.error('report_code不能为空', 400)

    try:
        report = CReport.query.get(report_id)
        if not report:
            return Response.error('报告不存在', 404)
        if report.report_code != report_code:
            return Response.error('report_code不匹配', 403)

        patient = CPatient.query.get(report.patient_id)
        if not patient:
            return Response.error('患者不存在', 404)

        manager_contact = None
        if patient.assigned_manager_id:
            manager = User.query.get(patient.assigned_manager_id)
            if manager:
                manager_contact = {
                    'manager_id': manager.id,
                    'manager_name': manager.real_name or '',
                    'manager_phone': manager.phone or '',
                    'manager_wechat': getattr(manager, 'wechat_id', '') or ''
                }

        # 业务：默认都需要健康管理师审核后再发送给患者
        need_review = True

        return Response.success({
            'report_id': report.id,
            'report_code': report.report_code,
            'patient_code': patient.patient_code,
            'need_review': need_review,
            'manager_contact': manager_contact
        }, '获取成功')

    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response.error(f'获取报告摘要失败: {str(e)}', 500)


@miniprogram_bp.route('/tongue/result/submit', methods=['POST'])
def submit_tongue_result():
    """
    ISDoc
    @description 小程序提交舌诊结果（先写入C端健康档案，待管理师审核后再写入报告）
    @bodyParam patient_id {number} 必填，C端患者ID（c_patients.id）
    @bodyParam report_id {number} 可选，C端报告ID（c_reports.id，用于校验/关联）
    @bodyParam tongue_result_id {string} 可选，外部检测结果ID（插件resultId等）
    @bodyParam tongue_result_data {object} 必填，插件回调 resultData 原始对象
    @response 200 {record_id, updated, summary}
    """
    data = request.get_json(silent=True) or {}
    patient_id = data.get('patient_id')
    report_id = data.get('report_id')
    tongue_result_id = (data.get('tongue_result_id') or '').strip()
    tongue_result_data = data.get('tongue_result_data')

    if not patient_id:
        return Response.error('patient_id不能为空', 400)
    if not tongue_result_data or not isinstance(tongue_result_data, (dict,)):
        return Response.error('tongue_result_data不能为空且必须为对象', 400)

    try:
        # 1) 校验患者存在
        c_patient = CPatient.query.get(patient_id)
        if not c_patient:
            return Response.error('患者不存在', 404)

        # 2) 选择要写入的档案：优先使用 report_id 关联的 record；否则取最新档案
        target_record = None
        if report_id:
            report = CReport.query.get(report_id)
            if report and report.patient_id == c_patient.id and report.record_id:
                target_record = CHealthRecord.query.get(report.record_id)

        if not target_record:
            target_record = CHealthRecord.query.filter_by(patient_id=c_patient.id).order_by(CHealthRecord.created_at.desc()).first()

        if not target_record:
            return Response.error('未找到可写入的健康档案', 404)

        # 3) 构建摘要（用于后续审核写入报告）
        def _pick(d, k):
            v = d.get(k)
            return str(v).strip() if v is not None else ''

        summary_parts = []
        constitution = _pick(tongue_result_data, 'constitutionName')
        symptom = _pick(tongue_result_data, 'symptomName')
        if constitution:
            summary_parts.append(f"健康状态：{constitution}")
        if symptom:
            summary_parts.append(f"证型：{symptom}")

        # 舌象要素
        mapping = [
            ('colorOfTongueName', '舌色'),
            ('colorOfMossName', '苔色'),
            ('shapeOfTongueName', '舌形'),
            ('mossName', '苔质'),
            ('bodyfluidName', '津液'),
            ('veinName', '舌下脉络'),
        ]
        features = []
        for key, label in mapping:
            v = _pick(tongue_result_data, key)
            if v:
                features.append(f"{label}：{v}")
        if features:
            summary_parts.append("舌象要点：" + "；".join(features))

        summary = "\n".join(summary_parts).strip() or "（舌诊结果已提交）"

        # 4) 写入档案
        import json
        target_record.tongue_check_result_id = tongue_result_id or target_record.tongue_check_result_id
        target_record.tongue_result_raw = json.dumps(tongue_result_data, ensure_ascii=False)
        target_record.tongue_result_summary = summary
        target_record.tongue_checked_at = datetime.utcnow()

        db.session.commit()

        return Response.success({
            'record_id': target_record.id,
            'updated': True,
            'summary': summary
        }, '舌诊结果已写入健康档案')

    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return Response.error(f'提交舌诊结果失败: {str(e)}', 500)


@miniprogram_bp.route('/reports/list', methods=['GET'])
def list_reports():
    """
    小程序查询用户报告列表
    
    请求参数:
        phone: 手机号（必填）
        openid: 微信OpenID（可选，用于验证）
        
    返回:
        reports: 报告列表
    """
    phone = request.args.get('phone')
    openid = request.args.get('openid')
    
    if not phone:
        return Response.error('手机号不能为空', 400)
    
    try:
        # 查找C端患者
        patient = CPatient.query.filter_by(phone=phone).first()
        if not patient:
            return Response.success([], '暂无报告')
        
        # 可选：验证OpenID（如果提供了）
        if openid and patient.wechat_openid != openid:
            return Response.error('OpenID不匹配', 403)
        
        # 查询该患者的所有报告（C端）
        reports = CReport.query.filter_by(
            patient_id=patient.id
        ).order_by(CReport.generated_at.desc()).all()
        
        report_list = []
        for r in reports:
            report_list.append({
                'report_id': r.id,
                'report_code': r.report_code,
                'risk_level': r.risk_level,
                'generated_at': r.generated_at.strftime('%Y-%m-%d %H:%M:%S') if r.generated_at else None
            })
        
        return Response.success({
            'reports': report_list,
            'patient_name': patient.name,
            'patient_code': patient.patient_code
        }, f'查询成功，共{len(report_list)}份报告')
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response.error(f'查询失败: {str(e)}', 500)

