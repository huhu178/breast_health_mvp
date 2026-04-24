"""
知识库管理路由
"""
from flask import Blueprint, request, jsonify
from models import db, KnowledgeItem
from functools import wraps
import jwt
from config import Config

knowledge_bp = Blueprint('knowledge', __name__, url_prefix='/api/knowledge')

def token_required(f):
    """JWT验证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': '未提供token'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
            request.current_user = data
        except:
            return jsonify({'error': 'Token无效'}), 401
        
        return f(*args, **kwargs)
    return decorated


@knowledge_bp.route('', methods=['GET'])
@token_required
def get_knowledge_items():
    """获取知识库列表（支持多维度筛选）"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # 构建查询
    query = KnowledgeItem.query
    
    # 多维度筛选
    source_type = request.args.get('source_type')
    if source_type:
        query = query.filter(KnowledgeItem.source_type == source_type)
    
    risk_level = request.args.get('risk_level')
    if risk_level:
        query = query.filter(KnowledgeItem.risk_level == risk_level)
    
    age = request.args.get('age', type=int)
    if age:
        query = query.filter(
            (KnowledgeItem.age_min.is_(None) | (KnowledgeItem.age_min <= age)) &
            (KnowledgeItem.age_max.is_(None) | (KnowledgeItem.age_max >= age))
        )
    
    birads = request.args.get('birads', type=int)
    if birads:
        query = query.filter(
            (KnowledgeItem.birads_min.is_(None) | (KnowledgeItem.birads_min <= birads)) &
            (KnowledgeItem.birads_max.is_(None) | (KnowledgeItem.birads_max >= birads))
        )
    
    symptoms = request.args.get('symptoms')
    if symptoms:
        query = query.filter(KnowledgeItem.symptoms.ilike(f'%{symptoms}%'))
    
    # 搜索关键词
    search = request.args.get('search')
    if search:
        query = query.filter(
            (KnowledgeItem.title.ilike(f'%{search}%')) |
            (KnowledgeItem.content.ilike(f'%{search}%'))
        )
    
    # 排序
    query = query.order_by(KnowledgeItem.priority.desc(), KnowledgeItem.id.desc())
    
    # 分页
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'items': [item.to_dict() for item in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })


@knowledge_bp.route('/<int:item_id>', methods=['GET'])
@token_required
def get_knowledge_item(item_id):
    """获取单个知识条目详情"""
    item = KnowledgeItem.query.get_or_404(item_id)
    return jsonify(item.to_dict())


@knowledge_bp.route('', methods=['POST'])
@token_required
def create_knowledge_item():
    """新增知识条目"""
    data = request.json
    
    new_item = KnowledgeItem(
        title=data.get('title'),
        content=data.get('content'),
        priority=data.get('priority', 5),
        source_type=data.get('source_type'),
        
        # 匹配维度
        risk_level=data.get('risk_level'),
        age_min=data.get('age_min'),
        age_max=data.get('age_max'),
        age_range=data.get('age_range'),
        birads_min=data.get('birads_min'),
        birads_max=data.get('birads_max'),
        course_stage=data.get('course_stage'),
        tnm_stage=data.get('tnm_stage'),
        symptoms=data.get('symptoms'),
        symptom_subtype=data.get('symptom_subtype'),
        pain_type=data.get('pain_type'),
        family_history=data.get('family_history'),
        family_category=data.get('family_category'),
        family_subcategory=data.get('family_subcategory'),
        rhythm_type=data.get('rhythm_type'),
        cycle_phase=data.get('cycle_phase'),
        phase_timing=data.get('phase_timing'),
        core_task=data.get('core_task'),
        sleep_quality=data.get('sleep_quality'),
        sleep_condition=data.get('sleep_condition'),
        exam_history_type=data.get('exam_history_type'),
        exam_subcategory=data.get('exam_subcategory'),
        nodule_location=data.get('nodule_location'),
        nodule_size=data.get('nodule_size'),
        boundary_features=data.get('boundary_features'),
        internal_echo=data.get('internal_echo'),
        risk_features=data.get('risk_features'),
        blood_flow_signal=data.get('blood_flow_signal'),
        elasticity_score=data.get('elasticity_score'),
        alert_rule=data.get('alert_rule'),
        interventions=data.get('interventions'),
        details=data.get('details')
    )
    
    db.session.add(new_item)
    db.session.commit()
    
    return jsonify(new_item.to_dict()), 201


@knowledge_bp.route('/<int:item_id>', methods=['PUT'])
@token_required
def update_knowledge_item(item_id):
    """更新知识条目"""
    item = KnowledgeItem.query.get_or_404(item_id)
    data = request.json
    
    # 更新基本字段
    if 'title' in data:
        item.title = data['title']
    if 'content' in data:
        item.content = data['content']
    if 'priority' in data:
        item.priority = data['priority']
    if 'source_type' in data:
        item.source_type = data['source_type']
    
    # 更新匹配维度字段
    dimension_fields = [
        'risk_level', 'age_min', 'age_max', 'age_range', 'birads_min', 'birads_max',
        'course_stage', 'tnm_stage', 'symptoms', 'symptom_subtype', 'pain_type',
        'family_history', 'family_category', 'family_subcategory', 'rhythm_type',
        'cycle_phase', 'phase_timing', 'core_task', 'sleep_quality', 'sleep_condition',
        'exam_history_type', 'exam_subcategory', 'nodule_location', 'nodule_size',
        'boundary_features', 'internal_echo', 'risk_features', 'blood_flow_signal',
        'elasticity_score', 'alert_rule', 'interventions', 'details'
    ]
    
    for field in dimension_fields:
        if field in data:
            setattr(item, field, data[field])
    
    db.session.commit()
    return jsonify(item.to_dict())


@knowledge_bp.route('/<int:item_id>', methods=['DELETE'])
@token_required
def delete_knowledge_item(item_id):
    """删除知识条目"""
    item = KnowledgeItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': '知识条目已删除'}), 200


@knowledge_bp.route('/match', methods=['POST'])
@token_required
def match_knowledge():
    """
    智能匹配知识库（核心功能）
    根据患者健康档案数据，匹配相关知识
    """
    data = request.json
    
    # 构建匹配查询
    query = KnowledgeItem.query
    matched_items = []
    
    # 1. 年龄匹配
    if 'age' in data and data['age']:
        age = data['age']
        age_items = query.filter(
            (KnowledgeItem.age_min.is_(None) | (KnowledgeItem.age_min <= age)) &
            (KnowledgeItem.age_max.is_(None) | (KnowledgeItem.age_max >= age))
        ).all()
        matched_items.extend(age_items)
    
    # 2. BI-RADS分级匹配
    if 'birads_level' in data and data['birads_level']:
        birads = data['birads_level']
        birads_items = query.filter(
            (KnowledgeItem.birads_min.is_(None) | (KnowledgeItem.birads_min <= birads)) &
            (KnowledgeItem.birads_max.is_(None) | (KnowledgeItem.birads_max >= birads))
        ).all()
        matched_items.extend(birads_items)
    
    # 3. 症状匹配
    if 'symptoms' in data and data['symptoms']:
        symptoms = data['symptoms']
        symptom_items = query.filter(KnowledgeItem.symptoms.ilike(f'%{symptoms}%')).all()
        matched_items.extend(symptom_items)
    
    # 4. 家族史匹配
    if 'family_history' in data and data['family_history']:
        family = data['family_history']
        family_items = query.filter(KnowledgeItem.family_history.ilike(f'%{family}%')).all()
        matched_items.extend(family_items)
    
    # 5. 病程阶段匹配
    if 'course_stage' in data and data['course_stage']:
        stage = data['course_stage']
        stage_items = query.filter(KnowledgeItem.course_stage == stage).all()
        matched_items.extend(stage_items)
    
    # 6. 生物节律匹配
    if 'rhythm_type' in data and data['rhythm_type']:
        rhythm = data['rhythm_type']
        rhythm_items = query.filter(KnowledgeItem.rhythm_type == rhythm).all()
        matched_items.extend(rhythm_items)
    
    # 7. 检查历史匹配
    if 'exam_history_type' in data and data['exam_history_type']:
        exam = data['exam_history_type']
        exam_items = query.filter(KnowledgeItem.exam_history_type == exam).all()
        matched_items.extend(exam_items)
    
    # 去重并按优先级排序
    unique_items = list({item.id: item for item in matched_items}.values())
    unique_items.sort(key=lambda x: (x.priority, x.id), reverse=True)
    
    return jsonify({
        'matched_count': len(unique_items),
        'items': [item.to_dict() for item in unique_items[:50]]  # 最多返回50条
    })


@knowledge_bp.route('/stats', methods=['GET'])
@token_required
def get_knowledge_stats():
    """获取知识库统计信息"""
    total = KnowledgeItem.query.count()
    
    # 按来源类型统计
    source_types = db.session.query(
        KnowledgeItem.source_type,
        db.func.count(KnowledgeItem.id)
    ).group_by(KnowledgeItem.source_type).all()
    
    # 按风险等级统计
    risk_levels = db.session.query(
        KnowledgeItem.risk_level,
        db.func.count(KnowledgeItem.id)
    ).filter(KnowledgeItem.risk_level.isnot(None)).group_by(KnowledgeItem.risk_level).all()
    
    return jsonify({
        'total': total,
        'by_source_type': [{'type': t, 'count': c} for t, c in source_types],
        'by_risk_level': [{'level': r, 'count': c} for r, c in risk_levels]
    })

