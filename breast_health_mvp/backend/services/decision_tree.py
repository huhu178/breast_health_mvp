"""
乳腺结节健康管理决策树引擎
基于172条知识库和医疗逻辑规则
"""
from typing import Dict, List, Any
from models import KnowledgeItem

class BreastNoduleDecisionTree:
    """乳腺结节决策树引擎"""
    
    def __init__(self):
        """初始化决策树规则"""
        self.decision_rules = self._load_decision_rules()
    
    @staticmethod
    def _get_attr(obj, attr_name, default=None):
        """兼容获取属性值（支持对象和字典）"""
        if isinstance(obj, dict):
            return obj.get(attr_name, default)
        return getattr(obj, attr_name, default)
    
    @staticmethod
    def _extract_number(value, default=0):
        """从字符串中提取数字（处理各种格式）"""
        if value is None:
            return default
        
        # 转为字符串
        value_str = str(value).strip()
        if not value_str:
            return default
        
        # 使用正则提取第一个数字
        import re
        match = re.search(r'\d+', value_str)
        if match:
            try:
                return int(match.group())
            except:
                return default
        
        return default
    
    def _load_decision_rules(self) -> Dict:
        """加载决策树规则"""
        # 创建辅助函数用于 lambda 表达式
        def get_birads(data):
            return self._extract_number(data.get('birads_level'), 0)
        def get_age(data):
            return self._extract_number(data.get('age'), 999)
        
        return {
            # 第一层：风险评估层
            "risk_assessment": {
                "priority": 1,
                "rules": [
                    {
                        "name": "极高风险",
                        "conditions": lambda data: (
                            get_birads(data) >= 5 or
                            (get_birads(data) == 4 and 
                             data.get('family_history') == '有' and 
                             get_age(data) < 40)
                        ),
                        "risk_score": 95,
                        "risk_level": "极高风险",
                        "immediate_actions": [
                            "72小时内完成穿刺活检",
                            "多学科会诊（MDT）评估",
                            "遗传咨询（BRCA基因检测）"
                        ],
                        "knowledge_filters": {
                            "source_types": ["medical_imaging", "family_history", "timeline"],
                            "priority_min": 7
                        }
                    },
                    {
                        "name": "高风险",
                        "conditions": lambda data: (
                            get_birads(data) == 4 or
                            (get_birads(data) == 3 and 
                             data.get('family_history') == '有')
                        ),
                        "risk_score": 75,
                        "risk_level": "高风险",
                        "immediate_actions": [
                            "2周内完成穿刺活检",
                            "建议遗传咨询"
                        ],
                        "knowledge_filters": {
                            "source_types": ["medical_imaging", "family_history", "timeline"],
                            "priority_min": 5
                        }
                    },
                    {
                        "name": "中风险",
                        "conditions": lambda data: get_birads(data) == 3,
                        "risk_score": 50,
                        "risk_level": "中风险",
                        "immediate_actions": [
                            "3-6个月复查超声",
                            "密切观察结节变化"
                        ],
                        "knowledge_filters": {
                            "source_types": ["medical_imaging", "symptoms", "timeline"],
                            "priority_min": 3
                        }
                    },
                    {
                        "name": "低风险",
                        "conditions": lambda data: get_birads(data) <= 2,
                        "risk_score": 20,
                        "risk_level": "低风险",
                        "immediate_actions": [
                            "每年常规体检",
                            "保持健康生活方式"
                        ],
                        "knowledge_filters": {
                            "source_types": ["age_general", "symptoms", "rhythm"],
                            "priority_min": 2
                        }
                    }
                ]
            },
            
            # 第二层：影像学评估层
            "imaging_assessment": {
                "priority": 2,
                "rules": [
                    {
                        "name": "恶性征象",
                        "conditions": lambda data: (
                            '毛刺' in str(data.get('boundary_features') or '') or
                            '高阻' in str(data.get('blood_flow_signal') or '') or
                            self._extract_number(data.get('elasticity_score'), 0) >= 4
                        ),
                        "urgency": "紧急",
                        "recommendations": [
                            "立即穿刺活检",
                            "增强MRI评估"
                        ],
                        "knowledge_filters": {
                            "source_types": ["medical_imaging"],
                            "priority_min": 6
                        }
                    },
                    {
                        "name": "良性特征",
                        "conditions": lambda data: (
                            '清晰' in str(data.get('boundary_features') or '') and
                            '无回声' in str(data.get('internal_echo') or '')
                        ),
                        "urgency": "常规",
                        "recommendations": [
                            "定期超声随访",
                            "观察大小变化"
                        ],
                        "knowledge_filters": {
                            "source_types": ["medical_imaging"],
                            "priority_min": 3
                        }
                    }
                ]
            },
            
            # 第三层：症状管理层
            "symptom_management": {
                "priority": 3,
                "rules": [
                    {
                        "name": "周期性疼痛",
                        "conditions": lambda data: (
                            '疼痛' in str(data.get('symptoms') or '') and
                            data.get('pain_type') == '周期性'
                        ),
                        "interpretation": "激素波动引起的生理性疼痛",
                        "recommendations": [
                            "月经前7天避免咖啡因",
                            "中医调理（疏肝理气）",
                            "情绪管理"
                        ],
                        "knowledge_filters": {
                            "source_types": ["symptoms", "rhythm"],
                            "symptoms": "疼痛",
                            "priority_min": 4
                        }
                    },
                    {
                        "name": "非周期性疼痛",
                        "conditions": lambda data: (
                            '疼痛' in str(data.get('symptoms') or '') and
                            data.get('pain_type') == '非周期性'
                        ),
                        "interpretation": "需要排查炎症或结节压迫",
                        "recommendations": [
                            "排查乳腺炎",
                            "评估结节位置",
                            "必要时止痛治疗"
                        ],
                        "knowledge_filters": {
                            "source_types": ["symptoms"],
                            "priority_min": 5
                        }
                    },
                    {
                        "name": "乳头溢液",
                        "conditions": lambda data: '溢液' in str(data.get('symptoms') or ''),
                        "interpretation": "需要重点关注的预警信号",
                        "recommendations": [
                            "乳管镜检查",
                            "溢液细胞学检查",
                            "排查乳管内病变"
                        ],
                        "knowledge_filters": {
                            "source_types": ["symptoms"],
                            "priority_min": 7
                        }
                    }
                ]
            },
            
            # 第四层：生物节律调节层
            "rhythm_regulation": {
                "priority": 4,
                "rules": [
                    {
                        "name": "月经周期相关",
                        "conditions": lambda data: data.get('rhythm_type') == '月经周期相关',
                        "recommendations": [
                            "避开黄体期复查（月经前7-10天）",
                            "记录症状与月经周期的关系",
                            "必要时调节激素水平"
                        ],
                        "knowledge_filters": {
                            "source_types": ["rhythm"],
                            "rhythm_type": "月经周期相关",
                            "priority_min": 3
                        }
                    },
                    {
                        "name": "睡眠质量差",
                        "conditions": lambda data: data.get('sleep_quality') in ['差', '很差'],
                        "recommendations": [
                            "建立规律作息（22:30前入睡）",
                            "睡前避免电子设备",
                            "必要时睡眠门诊咨询"
                        ],
                        "knowledge_filters": {
                            "source_types": ["sleep"],
                            # sleep_quality 在运行时动态匹配
                            "priority_min": 3
                        }
                    }
                ]
            },
            
            # 第五层：生活方式干预层
            "lifestyle_intervention": {
                "priority": 5,
                "rules": [
                    {
                        "name": "运动不足",
                        "conditions": lambda data: data.get('exercise_frequency') in ['很少', '从不'],
                        "recommendations": [
                            "每周至少150分钟中等强度有氧运动",
                            "推荐：快走、游泳、瑜伽",
                            "循序渐进，避免剧烈运动"
                        ],
                        "knowledge_filters": {
                            "source_types": ["age_general"],
                            "priority_min": 2
                        }
                    },
                    {
                        "name": "年龄特定建议",
                        "conditions": lambda data: True,  # 所有患者都需要
                        "recommendations": [],  # 由知识库动态生成
                        "knowledge_filters": {
                            "source_types": ["age_general"],
                            "age_based": True
                        }
                    }
                ]
            },
            
            # 第六层：家族史管理层
            "family_history_management": {
                "priority": 6,
                "rules": [
                    {
                        "name": "有家族史",
                        "conditions": lambda data: data.get('family_history') == '有',
                        "recommendations": [
                            "遗传咨询（BRCA1/2基因检测）",
                            "提前至30岁开始筛查",
                            "考虑预防性措施"
                        ],
                        "knowledge_filters": {
                            "source_types": ["family_history"],
                            "family_history": "有",
                            "priority_min": 5
                        }
                    }
                ]
            },
            
            # 第七层：检查历史分析层
            "exam_history_analysis": {
                "priority": 7,
                "rules": [
                    {
                        "name": "无检查史",
                        "conditions": lambda data: data.get('exam_history_type') == '无检查史',
                        "recommendations": [
                            "建立基线影像学资料",
                            "制定个性化随访计划"
                        ],
                        "knowledge_filters": {
                            "source_types": ["exam_history"],
                            "exam_history_type": "无检查史"
                        }
                    },
                    {
                        "name": "有既往检查",
                        "conditions": lambda data: data.get('exam_history_type') != '无检查史',
                        "recommendations": [
                            "对比既往影像学资料",
                            "评估结节动态变化"
                        ],
                        "knowledge_filters": {
                            "source_types": ["exam_history", "timeline"]
                        }
                    }
                ]
            },
            
            # 第八层：随访计划制定层
            "follow_up_planning": {
                "priority": 8,
                "rules": [
                    {
                        "name": "密集随访",
                        "conditions": lambda data: data.get('_risk_score', 0) >= 70,
                        "follow_up": {
                            "frequency": "3个月",
                            "duration": "至少2年",
                            "modalities": ["超声", "钼靶", "必要时MRI"],
                            "escalation": "结节增大>20%或出现新发可疑征象"
                        }
                    },
                    {
                        "name": "常规随访",
                        "conditions": lambda data: 40 <= data.get('_risk_score', 0) < 70,
                        "follow_up": {
                            "frequency": "6个月",
                            "duration": "至少1年",
                            "modalities": ["超声"],
                            "escalation": "结节增大或症状加重"
                        }
                    },
                    {
                        "name": "年度随访",
                        "conditions": lambda data: data.get('_risk_score', 0) < 40,
                        "follow_up": {
                            "frequency": "12个月",
                            "duration": "长期",
                            "modalities": ["超声"],
                            "escalation": "结节性质改变"
                        }
                    }
                ]
            }
        }
    
    def process(self, patient_data: Dict, matched_knowledge: List[KnowledgeItem]) -> Dict:
        """
        决策树处理主流程
        
        Args:
            patient_data: 患者健康档案数据
            matched_knowledge: 知识库匹配到的知识条目列表
        
        Returns:
            结构化的诊疗建议
        """
        result = {
            "patient_summary": self._create_patient_summary(patient_data),
            "risk_assessment": {},
            "imaging_findings": {},
            "symptom_management": {},
            "rhythm_regulation": {},
            "lifestyle_recommendations": {},
            "family_management": {},
            "follow_up_plan": {},
            "knowledge_references": [],
            "decision_path": []
        }
        
        # 第一层：风险评估
        risk_result = self._assess_risk(patient_data, matched_knowledge)
        result["risk_assessment"] = risk_result
        patient_data['_risk_score'] = risk_result['risk_score']
        result["decision_path"].append(f"风险评估: {risk_result['risk_level']}")
        
        # 第二层：影像学评估
        if patient_data.get('birads_level'):
            imaging_result = self._assess_imaging(patient_data, matched_knowledge)
            result["imaging_findings"] = imaging_result
            result["decision_path"].append(f"影像学: {imaging_result.get('category', '已评估')}")
        
        # 第三层：症状管理
        if patient_data.get('symptoms'):
            symptom_result = self._manage_symptoms(patient_data, matched_knowledge)
            result["symptom_management"] = symptom_result
            result["decision_path"].append(f"症状: {len(symptom_result.get('recommendations', []))}项建议")
        
        # 第四层：生物节律
        if patient_data.get('rhythm_type') or patient_data.get('sleep_quality'):
            rhythm_result = self._regulate_rhythm(patient_data, matched_knowledge)
            result["rhythm_regulation"] = rhythm_result
            result["decision_path"].append("生物节律: 已评估")
        
        # 第五层：生活方式
        lifestyle_result = self._intervene_lifestyle(patient_data, matched_knowledge)
        result["lifestyle_recommendations"] = lifestyle_result
        result["decision_path"].append(f"生活方式: {len(lifestyle_result.get('recommendations', []))}项建议")
        
        # 第六层：家族史
        if patient_data.get('family_history') == '有':
            family_result = self._manage_family_history(patient_data, matched_knowledge)
            result["family_management"] = family_result
            result["decision_path"].append("家族史: 重点关注")
        
        # 第八层：随访计划
        follow_up_result = self._plan_follow_up(patient_data, matched_knowledge)
        result["follow_up_plan"] = follow_up_result
        result["decision_path"].append(f"随访: {follow_up_result.get('frequency', '待定')}")
        
        # 汇总使用的知识条目
        result["knowledge_references"] = self._collect_knowledge_references(matched_knowledge)
        
        return result
    
    def _create_patient_summary(self, data: Dict) -> Dict:
        """创建患者摘要"""
        return {
            "age": data.get('age'),
            "birads": data.get('birads_level'),
            "family_history": data.get('family_history', '无'),
            "symptoms": data.get('symptoms', '无'),
            "key_features": self._extract_key_features(data)
        }
    
    def _extract_key_features(self, data: Dict) -> List[str]:
        """提取关键特征"""
        features = []
        birads = self._extract_number(data.get('birads_level'), 0)
        if birads >= 4:
            features.append("BI-RADS ≥4级")
        if data.get('family_history') == '有':
            features.append("有家族史")
        if data.get('symptoms'):
            features.append(f"症状: {data['symptoms']}")
        if data.get('nodule_size'):
            features.append(f"结节: {data['nodule_size']}")
        return features
    
    def _assess_risk(self, data: Dict, knowledge: List) -> Dict:
        """风险评估"""
        rules = self.decision_rules['risk_assessment']['rules']
        
        for rule in rules:
            if rule['conditions'](data):
                # 筛选相关知识
                filtered_knowledge = self._filter_knowledge(
                    knowledge,
                    rule['knowledge_filters']
                )
                
                return {
                    "risk_level": rule['risk_level'],
                    "risk_score": rule['risk_score'],
                    "category": rule['name'],
                    "immediate_actions": rule['immediate_actions'],
                    "knowledge_count": len(filtered_knowledge),
                    "knowledge_ids": [self._get_attr(k, 'id') for k in filtered_knowledge[:10]]
                }
        
        # 默认低风险
        return {
            "risk_level": "低风险",
            "risk_score": 20,
            "category": "低风险",
            "immediate_actions": ["保持健康生活方式"],
            "knowledge_count": 0,
            "knowledge_ids": []
        }
    
    def _assess_imaging(self, data: Dict, knowledge: List) -> Dict:
        """影像学评估"""
        # 检查恶性征象
        if ('毛刺' in str(data.get('boundary_features') or '') or
            '高阻' in str(data.get('blood_flow_signal') or '') or
            self._extract_number(data.get('elasticity_score'), 0) >= 4):
            
            filtered_knowledge = self._filter_knowledge(
                knowledge,
                {"source_types": ["medical_imaging"], "priority_min": 6}
            )
            
            return {
                "category": "恶性征象",
                "urgency": "紧急",
                "recommendations": ["立即穿刺活检", "增强MRI评估"],
                "knowledge_ids": [self._get_attr(k, 'id') for k in filtered_knowledge[:5]]
            }
        
        # 检查良性特征
        if ('清晰' in str(data.get('boundary_features') or '') and
            '无回声' in str(data.get('internal_echo') or '')):
            
            filtered_knowledge = self._filter_knowledge(
                knowledge,
                {"source_types": ["medical_imaging"], "priority_min": 3}
            )
            
            return {
                "category": "良性特征",
                "urgency": "常规",
                "recommendations": ["定期超声随访", "观察大小变化"],
                "knowledge_ids": [self._get_attr(k, 'id') for k in filtered_knowledge[:5]]
            }
        
        # 默认常规影像
        return {
            "category": "常规影像",
            "urgency": "常规",
            "recommendations": ["定期复查"],
            "knowledge_ids": []
        }
    
    def _manage_symptoms(self, data: Dict, knowledge: List) -> Dict:
        """症状管理"""
        rules = self.decision_rules['symptom_management']['rules']
        recommendations = []
        all_knowledge_ids = []
        
        for rule in rules:
            if rule['conditions'](data):
                filtered_knowledge = self._filter_knowledge(
                    knowledge,
                    rule['knowledge_filters']
                )
                
                recommendations.extend(rule['recommendations'])
                all_knowledge_ids.extend([self._get_attr(k, 'id') for k in filtered_knowledge])
        
        # 处理symptoms字段（可能是字符串或列表）
        symptoms = data.get('symptoms', '')
        if isinstance(symptoms, str):
            symptom_list = symptoms.split(',') if symptoms else []
        elif isinstance(symptoms, list):
            symptom_list = symptoms
        else:
            symptom_list = []
        
        return {
            "symptom_types": symptom_list,
            "recommendations": recommendations,
            "knowledge_ids": list(set(all_knowledge_ids))[:10]
        }
    
    def _regulate_rhythm(self, data: Dict, knowledge: List) -> Dict:
        """生物节律调节"""
        rules = self.decision_rules['rhythm_regulation']['rules']
        recommendations = []
        all_knowledge_ids = []
        
        for rule in rules:
            if rule['conditions'](data):
                filtered_knowledge = self._filter_knowledge(
                    knowledge,
                    rule['knowledge_filters']
                )
                
                recommendations.extend(rule['recommendations'])
                all_knowledge_ids.extend([self._get_attr(k, 'id') for k in filtered_knowledge])
        
        return {
            "rhythm_type": data.get('rhythm_type'),
            "sleep_quality": data.get('sleep_quality'),
            "recommendations": recommendations,
            "knowledge_ids": list(set(all_knowledge_ids))[:10]
        }
    
    def _intervene_lifestyle(self, data: Dict, knowledge: List) -> Dict:
        """生活方式干预"""
        rules = self.decision_rules['lifestyle_intervention']['rules']
        recommendations = []
        all_knowledge_ids = []
        
        for rule in rules:
            if rule['conditions'](data):
                filtered_knowledge = self._filter_knowledge(
                    knowledge,
                    rule['knowledge_filters']
                )
                
                if rule['name'] == '年龄特定建议':
                    # 使用年龄通用建议
                    for k in filtered_knowledge:
                        content = self._get_attr(k, 'content')
                        if content:
                            recommendations.append(content)
                else:
                    recommendations.extend(rule.get('recommendations', []))
                
                all_knowledge_ids.extend([self._get_attr(k, 'id') for k in filtered_knowledge])
        
        return {
            "exercise_level": data.get('exercise_frequency'),
            "recommendations": recommendations,
            "knowledge_ids": list(set(all_knowledge_ids))[:10]
        }
    
    def _manage_family_history(self, data: Dict, knowledge: List) -> Dict:
        """家族史管理"""
        rules = self.decision_rules['family_history_management']['rules']
        
        for rule in rules:
            if rule['conditions'](data):
                filtered_knowledge = self._filter_knowledge(
                    knowledge,
                    rule['knowledge_filters']
                )
                
                return {
                    "has_family_history": True,
                    "recommendations": rule['recommendations'],
                    "knowledge_ids": [self._get_attr(k, 'id') for k in filtered_knowledge[:5]]
                }
        
        return {}
    
    def _plan_follow_up(self, data: Dict, knowledge: List) -> Dict:
        """制定随访计划"""
        rules = self.decision_rules['follow_up_planning']['rules']
        
        for rule in rules:
            if rule['conditions'](data):
                return {
                    "plan_type": rule['name'],
                    **rule['follow_up']
                }
        
        return {
            "plan_type": "常规随访",
            "frequency": "12个月",
            "duration": "长期",
            "modalities": ["超声"]
        }
    
    def _filter_knowledge(self, knowledge: List, filters: Dict) -> List:
        """根据规则过滤知识库（兼容对象和字典）"""
        result = []
        
        for item in knowledge:
            # 来源类型过滤
            if 'source_types' in filters:
                source_type = self._get_attr(item, 'source_type')
                if source_type not in filters['source_types']:
                    continue
            
            # 优先级过滤
            if 'priority_min' in filters:
                priority = self._get_attr(item, 'priority', 0)
                if priority < filters['priority_min']:
                    continue
            
            # 症状过滤
            if 'symptoms' in filters:
                symptoms = self._get_attr(item, 'symptoms')
                if not symptoms or filters['symptoms'] not in symptoms:
                    continue
            
            # 家族史过滤
            if 'family_history' in filters:
                family_history = self._get_attr(item, 'family_history')
                if family_history != filters['family_history']:
                    continue
            
            # 节律类型过滤
            if 'rhythm_type' in filters:
                rhythm_type = self._get_attr(item, 'rhythm_type')
                if rhythm_type != filters['rhythm_type']:
                    continue
            
            # 睡眠质量过滤
            if 'sleep_quality' in filters:
                sleep_quality = self._get_attr(item, 'sleep_quality')
                if sleep_quality != filters['sleep_quality']:
                    continue
            
            # 检查史过滤
            if 'exam_history_type' in filters:
                exam_history_type = self._get_attr(item, 'exam_history_type')
                if exam_history_type != filters['exam_history_type']:
                    continue
            
            # 年龄特定过滤（暂时跳过，需要传入patient_data）
            # if filters.get('age_based'):
            #     pass
            
            result.append(item)
        
        # 按优先级排序
        try:
            result.sort(key=lambda x: self._get_attr(x, 'priority', 0), reverse=True)
        except:
            pass
        return result
    
    def _collect_knowledge_references(self, knowledge: List) -> List[Dict]:
        """收集知识引用（兼容对象和字典）"""
        return [
            {
                "id": self._get_attr(k, 'id'),
                "title": self._get_attr(k, 'title'),
                "source_type": self._get_attr(k, 'source_type'),
                "priority": self._get_attr(k, 'priority', 0)
            }
            for k in knowledge[:30]  # 最多30条
        ]


# 全局决策树实例
decision_tree = BreastNoduleDecisionTree()

