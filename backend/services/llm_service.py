"""
LLM报告生成服务
使用OpenRouter API调用gemini模型
"""
import requests
import json
import time
from typing import Dict, List, Any, Tuple
from models import KnowledgeItem
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def _mask_api_key(key: str | None) -> str:
    """
    @isdoc
    @description 脱敏显示 API Key（只展示前缀与后4位），用于启动自检与排障日志。
    @param key 原始 key
    @returns {str} 脱敏后的 key 描述
    """
    if key is None:
        return "(missing)"
    k = str(key).strip()
    if not k:
        return "(missing)"
    if len(k) <= 10:
        return f"{k[:2]}***"
    return f"{k[:6]}***{k[-4:]}"

class LLMReportGenerator:
    """LLM报告生成器"""
    
    def __init__(self):
        """初始化LLM配置"""
        # OpenRouter配置
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.api_key = None  # 从环境变量读取

        # 模型配置（从环境变量读取，不硬编码）
        self.model = None  # 将在模块加载时从环境变量设置
        
        # 默认参数
        self.default_params = {
            "temperature": 0.7,
            "max_tokens": 8000,  # 增加到8000，确保中文输出不被截断
            "top_p": 0.9
        }

        # HTTP 会话：连接复用 + 失败重试（解决偶发 TLS 断连 / 网关抖动）
        self.session = requests.Session()
        retry = Retry(
            total=3,
            connect=3,
            read=3,
            status=3,
            backoff_factor=0.8,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"],
            raise_on_status=False,
            respect_retry_after_header=True,
        )
        adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=10)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def _post_chat_completions(self, headers: Dict[str, str], payload: Dict[str, Any], timeout: int, context: str) -> Dict[str, Any]:
        """
        统一的 OpenRouter 调用封装：
        - 连接复用 + urllib3 重试（含 429/5xx）
        - 对常见网络抖动异常做额外退避重试
        """
        last_err: Exception | None = None
        extra_retries = 2  # 在 urllib3 重试之外，再做少量“异常级别”的重试

        for attempt in range(1, extra_retries + 2):
            try:
                response = self.session.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=timeout,
                )

                if response.status_code != 200:
                    # 不打印 prompt，避免日志泄露；只打印必要信息
                    print(f"ERROR: [{context}] API returned status {response.status_code}")
                    body_text = (response.text or "")[:2000]
                    # 优先尝试解析 OpenRouter 标准错误结构：{"error":{"message":"...","code":...}}
                    try:
                        body_json = response.json()
                        msg = (
                            body_json.get("error", {}).get("message")
                            or body_json.get("message")
                            or None
                        )
                        if msg:
                            print(f"错误详情: {msg}")
                        else:
                            print(f"错误详情: {body_text}")
                    except Exception:
                        print(f"错误详情: {body_text}")

                response.raise_for_status()
                response.encoding = "utf-8"
                return response.json()

            except (requests.exceptions.SSLError, requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                # 典型错误：SSLEOFError / 对端断开 / 超时等，通常属于瞬态
                last_err = e
                if attempt <= extra_retries:
                    sleep_s = 0.8 * (2 ** (attempt - 1))
                    print(f"⚠️  [{context}] 网络抖动/连接异常（第{attempt}次重试，{sleep_s:.1f}s后继续）: {e}")
                    time.sleep(sleep_s)
                    continue
                break
            except Exception as e:
                # 非预期错误：不盲目重试，直接抛出
                raise e

        raise Exception(f"[{context}] 请求失败（已重试）：{last_err}")
    
    def set_api_key(self, api_key: str):
        """设置API Key"""
        self.api_key = api_key
    
    def set_model(self, model: str):
        """设置模型"""
        self.model = model
    
    def generate_report(
        self, 
        patient_data: Dict, 
        decision_result: Dict,
        knowledge_items: List[KnowledgeItem]
    ) -> Dict[str, str]:
        """
        生成健康管理报告
        
        Args:
            patient_data: 患者健康档案数据
            decision_result: 决策树处理结果
            knowledge_items: 匹配的知识条目列表
        
        Returns:
            {
                "report_html": "HTML格式的报告",
                "report_summary": "报告摘要",
                "risk_level": "风险等级"
            }
        """
        # 构建Prompt
        prompt = self._build_prompt(patient_data, decision_result, knowledge_items)
        
        # 调用LLM API
        response = self._call_llm_api(prompt)
        
        # 解析响应
        report_html = self._extract_html(response)
        report_summary = self._extract_summary(decision_result)
        # 不再使用风险评估字段
        risk_level = None
        
        return {
            "report_html": report_html,
            "report_summary": report_summary,
            "risk_level": risk_level
        }

    def generate_patient_friendly_report(
        self,
        patient_data: Dict,
        decision_result: Dict,
        knowledge_items: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        """生成C端用户友好的健康报告（不影响B端）"""

        prompt = self._build_patient_friendly_prompt(patient_data, decision_result, knowledge_items)
        response = self._call_llm_api(prompt)
        report_html = self._extract_html(response)

        if not report_html or 'breast-health-report' not in report_html:
            # 如果LLM未按要求输出HTML，则回退到通用的专业版本
            return self.generate_report(patient_data, decision_result, knowledge_items)

        report_summary = self._extract_summary(decision_result)
        # 不再使用风险评估字段
        risk_level = None

        return {
            "report_html": report_html,
            "report_summary": report_summary,
            "risk_level": risk_level
        }
    
    def _build_prompt(
        self, 
        patient_data: Dict, 
        decision_result: Dict,
        knowledge_items: List[KnowledgeItem]
    ) -> str:
        """构建Prompt"""
        
        # 患者信息摘要
        patient_summary = self._format_patient_info(patient_data, decision_result)
        
        # 风险评估（已移除，不再使用）
        risk_section = "风险评估：暂未评估"
        
        # 影像学发现
        imaging_section = self._format_imaging_findings(decision_result.get('imaging_findings', {}))
        
        # 症状管理
        symptom_section = self._format_symptom_management(decision_result.get('symptom_management', {}))
        
        # 生物节律
        rhythm_section = self._format_rhythm_regulation(decision_result.get('rhythm_regulation', {}))
        
        # 生活方式
        lifestyle_section = self._format_lifestyle_recommendations(decision_result.get('lifestyle_recommendations', {}))
        
        # 家族史
        family_section = self._format_family_management(decision_result.get('family_management', {}))
        
        # 随访计划
        followup_section = self._format_follow_up_plan(decision_result.get('follow_up_plan', {}))
        
        # 知识库依据
        knowledge_section = self._format_knowledge_references(knowledge_items, decision_result)
        
        # 完整Prompt
        prompt = f"""你是一位资深的乳腺外科医生和健康管理专家，请根据以下患者信息和专业诊疗建议，生成一份专业、易懂、有温度的健康管理报告。

# 患者基本信息
{patient_summary}

# 风险评估
{risk_section}

# 影像学发现
{imaging_section}

# 症状管理建议
{symptom_section}

# 生物节律调节
{rhythm_section}

# 生活方式干预
{lifestyle_section}

# 家族史管理
{family_section}

# 随访计划
{followup_section}

# 专业知识依据
本报告基于{len(knowledge_items)}条专业知识库和医疗决策树生成。
{knowledge_section}

---

# 报告生成要求

请生成一份**完整的HTML格式健康管理报告**，要求如下：

## 1. 内容要求
- **专业性**：使用规范的医学术语，但要通俗易懂
- **温度感**：语气亲切，让患者感受到关怀
- **可操作性**：建议具体明确，患者知道该做什么
- **完整性**：包含所有上述模块的内容
- **安全性**：高风险患者必须强调紧急性

## 2. 结构要求
请按以下结构生成HTML：

```html
<div class="breast-health-report">
    <header class="report-header">
        <h1>🏥 乳腺结节健康管理报告</h1>
        <div class="report-meta">
            <span>生成日期：[当前日期]</span>
            <span>风险等级：<span class="risk-badge [risk-class]">[风险等级]</span></span>
        </div>
    </header>
    
    <section class="executive-summary">
        <h2>📋 健康状况总结</h2>
        <div class="summary-content">
            [用2-3句话总结患者当前状况和关键建议]
        </div>
    </section>
    
    <section class="risk-assessment">
        <h2>🎯 风险评估</h2>
        <div class="risk-details">
            [详细解释风险等级、评分依据、关键风险因素]
        </div>
        
        <div class="immediate-actions">
            <h3>🔴 需要立即采取的行动</h3>
            <ol class="action-list">
                [列出所有立即行动项，突出紧急性]
            </ol>
        </div>
    </section>
    
    <section class="imaging-findings">
        <h2>📊 影像学发现与建议</h2>
        [根据影像学数据给出专业解读和建议]
    </section>
    
    <!-- 分页符：第一页结束（概述+风险评估+影像学） -->
    <div style="page-break-after: always;"></div>
    
    <!-- 第二页开始：症状管理与生活方式干预 -->
    <section class="symptom-management">
        <h2>💊 症状管理方案</h2>
        [针对具体症状给出管理建议]
    </section>
    
    <section class="rhythm-regulation">
        <h2>🌙 生物节律调节</h2>
        [节律管理和睡眠改善建议]
    </section>
    
    <section class="lifestyle-intervention">
        <h2>🏃 生活方式改善计划</h2>
        <div class="lifestyle-categories">
            <div class="category">
                <h3>运动建议</h3>
                [具体运动方案]
            </div>
            <div class="category">
                <h3>饮食调整</h3>
                [具体饮食建议]
            </div>
            <div class="category">
                <h3>作息管理</h3>
                [具体作息建议]
            </div>
        </div>
    </section>
    
    <section class="family-history">
        <h2>👨‍👩‍👧 家族史管理</h2>
        [家族史相关建议，如果有的话]
    </section>
    
    <section class="follow-up-plan">
        <h2>📅 随访计划</h2>
        <table class="follow-up-table">
            <tr>
                <th>随访频率</th>
                <td>[频率]</td>
            </tr>
            <tr>
                <th>持续时间</th>
                <td>[时间]</td>
            </tr>
            <tr>
                <th>检查方式</th>
                <td>[检查项目]</td>
            </tr>
            <tr>
                <th>升级条件</th>
                <td>[何时需要升级]</td>
            </tr>
        </table>
    </section>
    
    <section class="important-notes">
        <h2>⚠️ 重要提示</h2>
        <ul class="notes-list">
            <li>本报告仅供参考，具体诊疗请遵医嘱</li>
            <li>如有任何不适，请及时就医</li>
            <li>定期复查非常重要，请按时随访</li>
            [根据风险等级添加其他注意事项]
        </ul>
    </section>
    
    <footer class="report-footer">
        <p class="knowledge-reference">
            本报告基于{len(knowledge_items)}条专业知识库和医疗决策树生成
        </p>
        <p class="disclaimer">
            声明：本报告由AI辅助生成，仅供参考，不构成医疗建议。
        </p>
    </footer>
</div>

<style>
/* ===================================
   完整的PDF/打印专用样式
   =================================== */

/* 通用样式 */
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: 'Microsoft YaHei', '微软雅黑', SimHei, sans-serif;
    font-size: 14px;
    line-height: 1.8;
    color: #333;
    background: #fff;
}}

/* 页面设置 */
@page {{
    size: A4;
    margin: 20mm;
}}

/* 报告容器 */
.breast-health-report {{{{
    font-family: "Microsoft YaHei", Arial, sans-serif;
    max-width: 900px;
    margin: 0 auto;
    padding: 30px;
    line-height: 1.8;
    color: #333;
}}}}

.report-header {{{{
    text-align: center;
    padding: 30px 0;
    border-bottom: 3px solid #409eff;
    margin-bottom: 30px;
}}}}

.report-header h1 {{{{
    color: #409eff;
    font-size: 28px;
    margin-bottom: 15px;
}}}}

.report-meta {{{{
    display: flex;
    justify-content: center;
    gap: 30px;
    color: #666;
}}}}

.risk-badge {{{{
    padding: 5px 15px;
    border-radius: 20px;
    font-weight: bold;
}}}}

.risk-high {{{{
    background: #fef0f0;
    color: #f56c6c;
}}}}

.risk-medium {{{{
    background: #fdf6ec;
    color: #e6a23c;
}}}}

.risk-low {{{{
    background: #f0f9ff;
    color: #409eff;
}}}}

section {{{{
    margin-bottom: 40px;
    padding: 25px;
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.05);
}}}}

section h2 {{{{
    color: #409eff;
    font-size: 22px;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 2px solid #e4e7ed;
}}}}

section h3 {{{{
    color: #606266;
    font-size: 18px;
    margin: 20px 0 15px 0;
}}}}

.executive-summary {{{{
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}}}}

.executive-summary h2 {{{{
    color: white;
    border-bottom-color: rgba(255,255,255,0.3);
}}}}

.summary-content {{{{
    font-size: 16px;
    line-height: 2;
}}}}

.immediate-actions {{{{
    background: #fef0f0;
    padding: 20px;
    border-radius: 8px;
    border-left: 4px solid #f56c6c;
    margin-top: 20px;
}}}}

.action-list {{{{
    list-style: none;
    counter-reset: action-counter;
    padding-left: 0;
}}}}

.action-list li {{{{
    counter-increment: action-counter;
    margin: 15px 0;
    padding-left: 40px;
    position: relative;
    font-size: 16px;
    font-weight: 500;
}}}}

.action-list li:before {{{{
    content: counter(action-counter);
    position: absolute;
    left: 0;
    top: 0;
    background: #f56c6c;
    color: white;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    text-align: center;
    line-height: 28px;
    font-weight: bold;
}}}}

.lifestyle-categories {{{{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin-top: 20px;
}}}}

.category {{{{
    padding: 20px;
    background: #f5f7fa;
    border-radius: 8px;
    border-left: 4px solid #409eff;
}}}}

.follow-up-table {{{{
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
}}}}

.follow-up-table th,
.follow-up-table td {{{{
    padding: 15px;
    border: 1px solid #ebeef5;
    text-align: left;
}}}}

.follow-up-table th {{{{
    background: #f5f7fa;
    font-weight: 600;
    width: 30%;
}}}}

.important-notes {{{{
    background: #fff7e6;
    border-left: 4px solid #e6a23c;
}}}}

.notes-list {{{{
    list-style: none;
    padding-left: 0;
}}}}

.notes-list li {{{{
    padding: 10px 0 10px 30px;
    position: relative;
}}}}

.notes-list li:before {{{{
    content: "⚠️";
    position: absolute;
    left: 0;
}}}}

.report-footer {{{{
    margin-top: 40px;
    padding-top: 20px;
    border-top: 2px solid #e4e7ed;
    text-align: center;
    color: #909399;
    font-size: 14px;
}}}}

.knowledge-reference {{{{
    margin: 10px 0;
    font-weight: 500;
}}}}

.disclaimer {{{{
    margin: 10px 0;
    font-style: italic;
}}}}

/* ===================================
   PDF/打印优化样式
   =================================== */
@media print {{{{
    /* 页面设置 */
    @page {{{{
        size: A4;
        margin: 20mm 15mm;
    }}}}
    
    body {{{{
        background: #fff !important;
        font-size: 12pt;
        line-height: 1.6;
    }}}}
    
    .breast-health-report {{{{
        padding: 0;
        max-width: 100%;
        box-shadow: none;
    }}}}
    
    /* ===== 重点：防止孤标题和内容断裂 ===== */
    
    /* 标题必须与后续至少一段内容在一起 */
    h1, h2, h3 {{{{
        page-break-after: avoid;      /* 标题后不分页 */
        page-break-inside: avoid;      /* 标题内部不断裂 */
    }}}}
    
    /* 标题后的第一个元素（段落/列表/div）必须跟标题在一起 */
    h1 + *, h2 + *, h3 + * {{{{
        page-break-before: avoid !important;  /* 强制不在标题后分页 */
        margin-top: 0;
    }}}}
    
    /* 标题后的前2个元素都不要分页（确保至少有一段内容） */
    h2 + * + * {{{{
        page-break-before: avoid;
    }}}}
    
    /* section可以分页，但要控制好孤行 */
    section {{{{
        page-break-inside: auto;       /* 允许分页，不强制完整 */
        box-shadow: none;
        margin-bottom: 20px;
        orphans: 4;                    /* 页面底部至少保留4行 */
        widows: 4;                     /* 页面顶部至少保留4行 */
    }}}}
    
    /* 短section尽量不断页 */
    section.short-section {{{{
        page-break-inside: avoid;
    }}}}
    
    /* 段落不要孤行 */
    p {{{{
        orphans: 3;
        widows: 3;
        page-break-inside: avoid;
    }}}}
    
    /* 表格、列表、图片不断页 */
    table, ul, ol, img, .category, .action-list {{{{
        page-break-inside: avoid;
    }}}}
    
    /* 列表项保持完整 */
    li {{{{
        page-break-inside: avoid;
        orphans: 2;
        widows: 2;
    }}}}
    
    /* 重要区块（如行动清单、重要提示）整体保持 */
    .immediate-actions, .important-notes, .executive-summary {{{{
        page-break-inside: avoid;
        page-break-before: auto;
        page-break-after: auto;
    }}}}
    
    /* 确保文字可读性 */
    * {{{{
        color-adjust: exact;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }}}}
    
    /* 隐藏不必要的元素 */
    .no-print {{{{
        display: none !important;
    }}}}
    
    /* ===== 强制分页符生效 ===== */
    div[style*="page-break-after: always"] {{{{
        page-break-after: always !important;
        display: block !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        border: none !important;
        visibility: hidden;
    }}}}
    
    /* 优化间距，避免浪费空间 */
    section {{{{
        padding: 15px 0;
        margin: 10px 0;
    }}}}
    
    h2 {{{{
        margin-top: 20px;
        margin-bottom: 12px;
    }}}}
    
    p {{{{
        margin-bottom: 10px;
    }}}}
    
    ul, ol {{{{
        margin: 10px 0;
    }}}}
    
    /* 避免渐变背景在打印时消失 */
    .executive-summary {{{{
        background: #f0f0f0 !important;
        color: #333 !important;
        border: 2px solid #409eff;
    }}}}
    
    .executive-summary h2 {{{{
        color: #409eff !important;
        border-bottom-color: #409eff !important;
    }}}}
    
    /* 确保边框和背景色打印出来 */
    .risk-badge, .category, .action-list {{{{
        border: 1px solid #ccc !important;
    }}}}
}}}}

/* 额外的样式优化 */
p {{{{
    margin-bottom: 12px;
    line-height: 2;
    text-align: justify;
}}}}

section p:first-of-type {{{{
    text-indent: 0;  /* 第一段不缩进 */
}}}}

ul, ol {{{{
    margin: 15px 0 15px 2em;
}}}}

li {{{{
    margin-bottom: 8px;
    line-height: 1.8;
}}}}

strong {{{{
    font-weight: 600;
    color: #2c3e50;
}}}}

table {{{{
    font-size: 13px;
}}}}

table td {{{{
    line-height: 1.6;
}}}}

/* 确保emoji正常显示 */
.report-header h1 {{{{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
}}}}

/* ===================================
   屏幕显示时的分页提示
   =================================== */
@media screen {{{{
    div[style*="page-break-after: always"] {{{{
        margin: 30px 0;
        padding: 15px;
        text-align: center;
        background: linear-gradient(to right, #e3f2fd 0%, #fff 50%, #e3f2fd 100%);
        border-top: 2px dashed #90caf9;
        border-bottom: 2px dashed #90caf9;
        color: #1976d2;
        font-size: 13px;
        font-weight: 500;
    }}}}
    
    div[style*="page-break-after: always"]::after {{{{
        content: "━━━━━ 📄 第一页结束 / 第二页开始 ━━━━━";
        letter-spacing: 2px;
    }}}}
}}}}
</style>
```

## 3. 语言风格
- 第二人称"您"，增加亲切感
- 避免过于学术的表达
- 关键信息用**粗体**强调
- 紧急事项用🔴标注

## 4. 特别注意
- 如果是高风险/极高风险，必须在开头就强调紧急性
- 所有建议要有知识库支撑，不要自己编造
- 时间、频率等数据要准确
- 保持专业性和温度感的平衡

请直接输出完整的HTML代码，不要有任何其他说明文字。
"""
        
        return prompt

    def _build_patient_friendly_prompt(
        self,
        patient_data: Dict,
        decision_result: Dict,
        knowledge_items: List[Dict[str, Any]]
    ) -> str:
        """构建C端友好型Prompt"""

        patient_summary = decision_result.get('patient_summary') or {}
        risk = decision_result.get('risk_assessment') or {}
        imaging = decision_result.get('imaging_findings') or {}
        lifestyle = decision_result.get('lifestyle_recommendations') or {}
        symptoms = decision_result.get('symptom_management') or {}
        family = decision_result.get('family_management') or {}
        follow_up = decision_result.get('follow_up_plan') or {}
        rhythm = decision_result.get('rhythm_regulation') or {}

        knowledge_brief = self._compose_c_knowledge_brief(knowledge_items)

        return f"""
你是一位温暖、专业的乳腺健康管理师。请基于以下数据，写一份让普通用户也能看懂的健康报告。

【患者概况】
- 年龄：{patient_summary.get('age', patient_data.get('age', '未知'))}岁
- BI-RADS分级：{patient_summary.get('birads', patient_data.get('birads_level', '未知'))}级
- 家族史：{patient_summary.get('family_history', patient_data.get('family_history', '未提供'))}
- 主要症状：{patient_summary.get('symptoms', '暂无明显症状')}
- 关键特征：{', '.join(patient_summary.get('key_features', [])) or '暂无'}

【风险评估】
- 风险等级：{risk.get('risk_level', '未知')}
- 风险评分：{risk.get('risk_score', 0)}
- 风险类型说明：{risk.get('category', '暂无说明')}
- 重点关注事项：{'; '.join(risk.get('immediate_actions', []) or ['暂无'])}

【影像学要点】
- 分类：{imaging.get('category', '常规随访')}
- 紧急度：{imaging.get('urgency', '常规')}
- 结节特征：{imaging.get('summary', imaging.get('description', '暂无详细描述'))}

【生活方式建议】
- 核心目标：{lifestyle.get('core_goal', '保持健康生活方式')}
- 饮食建议：{'; '.join(lifestyle.get('diet', []) or ['清淡饮食，少油少盐'])}
- 运动建议：{'; '.join(lifestyle.get('exercise', []) or ['每周至少150分钟中等强度运动'])}
- 睡眠/节律：{'; '.join(lifestyle.get('sleep', []) or rhythm.get('recommendations', ['保持规律作息']))}

【症状与家族管理】
- 症状应对：{'; '.join(symptoms.get('recommendations', []) or ['当前无明显症状风险'])}
- 家族史管理：{'; '.join(family.get('recommendations', []) or ['关注亲属健康变化，保持沟通'])}

【随访计划】
- 建议复诊频率：{follow_up.get('frequency', '遵循医生安排')}
- 推荐检查项目：{'; '.join(follow_up.get('check_items', []) or ['根据医生建议安排检查'])}
- 预警提示：{'; '.join(follow_up.get('warning_signs', []) or ['如出现新症状需及时就医'])}

【知识库重点（供你参考，请用自己的话总结）】
{knowledge_brief}

输出要求：
1. 只输出完整的HTML片段，根节点必须是 <div class="breast-health-report">。
2. 报告需包含：标题、风险总览、关键发现、日常管理建议、随访计划、知识库依据、温馨提示。
3. 小标题清晰，语气温暖易懂，必要时解释医学术语。
4. 对缺失数据写“暂无相关信息”，不得编造。
5. “知识库依据”部分请结合上方知识要点说明理由，不要逐条复制原文。
"""

    def _compose_c_knowledge_brief(self, knowledge_items: List[Dict[str, Any]]) -> str:
        """提炼C端知识库摘要"""

        if not knowledge_items:
            return "- 暂无匹配的医学知识"

        def sort_key(item: Dict[str, Any]) -> Tuple[int, int]:
            priority = item.get('priority')
            if priority is None:
                priority = 0
            return priority, item.get('id', 0)

        top_items = sorted(knowledge_items, key=sort_key, reverse=True)[:5]

        lines: List[str] = []
        for entry in top_items:
            title = entry.get('title', '未命名知识点')
            content = (entry.get('content') or '').replace('\n', ' ').strip()
            if len(content) > 120:
                content = content[:120].rstrip() + '...'
            source = entry.get('source_type', '未知来源')
            lines.append(f"- [{source}] {title}：{content}")

        return '\n'.join(lines) if lines else "- 暂无匹配的医学知识"

    def _call_llm_api(self, prompt: str) -> str:
        """调用LLM API"""
        if not self.api_key:
            raise Exception("OPENROUTER_API_KEY 未配置，无法调用大模型")
        
        print(f"[LLM] Using model: {self.model}")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5000",  # OpenRouter要求
            "X-Title": "Breast Nodule Health Management System"  # Header必须是ASCII
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一位资深的乳腺外科医生和健康管理专家，擅长生成专业、易懂、有温度的健康管理报告。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            **self.default_params
        }
        
        try:
            result = self._post_chat_completions(headers=headers, payload=payload, timeout=60, context="LLM文本")
            
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content']
            else:
                raise Exception("API返回格式错误")
                
        except Exception as e:
            # 不使用降级方案，直接抛出异常（上层必须失败并停止生成报告）
            msg = str(e)
            print(f"❌ LLM API调用失败: {msg}")
            if "403" in msg:
                raise Exception(
                    "OpenRouter 拒绝调用（403 Forbidden）。"
                    "请检查：API key 是否有效；账号是否有权限调用当前模型；额度是否正常；"
                    "以及 Referer/来源限制是否允许 localhost；"
                    "如果错误详情提示“not available in your region”，则需更换模型或更换出口地区。"
                )
            raise Exception(f"LLM API调用失败: {msg}")
    
    def _call_llm_api_with_pdf(self, prompt: str, pdf_base64: str, file_path: str = None) -> str:
        """
        调用LLM API（直接发送PDF文件给大模型）
        
        Args:
            prompt: 文本提示词
            pdf_base64: base64编码的PDF文件
            file_path: PDF文件路径（用于日志）
            
        Returns:
            str: LLM返回的文本内容
        """
        if not self.api_key:
            raise Exception("API Key未配置")

        print(f"[LLM] Using model: {self.model} (PDF)")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5000",
            "X-Title": "Breast Nodule Health Management System"
        }
        
        # 构建多模态消息内容（直接发送PDF）
        content = [
            {"type": "text", "text": prompt},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:application/pdf;base64,{pdf_base64}"
                }
            }
        ]
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一位专业的医学影像报告分析专家，擅长从影像报告中提取结构化信息。"
                },
                {
                    "role": "user",
                    "content": content
                }
            ],
            **self.default_params
        }
        
        try:
            file_info = f" ({file_path})" if file_path else ""
            print(f"📤 发送PDF文件到LLM直接分析{file_info}...")
            # 额外提示：扫描版PDF直传给LLM链路更脆弱（体积大/不一定被上游当作图片处理）
            if pdf_base64 and len(pdf_base64) > 5_000_000:
                print("⚠️  提示：PDF较大（base64长度>5,000,000），更容易触发网络/网关断连；建议启用本地OCR或缩小PDF后再试。")

            result = self._post_chat_completions(headers=headers, payload=payload, timeout=180, context="LLM-PDF")
            
            if 'choices' in result and len(result['choices']) > 0:
                print("✅ LLM PDF分析响应成功")
                return result['choices'][0]['message']['content']
            else:
                raise Exception("API返回格式错误")
                
        except Exception as e:
            print(f"❌ LLM PDF分析API调用失败: {e}")
            raise Exception(f"LLM PDF分析API调用失败: {str(e)}")
    
    def _generate_mock_response(self, prompt: str) -> str:
        """生成模拟响应（用于测试或API失败时的降级方案）"""
        return """
<div class="breast-health-report">
    <header class="report-header">
        <h1>🏥 乳腺结节健康管理报告</h1>
        <div class="report-meta">
            <span>生成日期：2025年10月27日</span>
            <span>风险等级：<span class="risk-badge risk-high">高风险</span></span>
        </div>
    </header>
    
    <section class="executive-summary">
        <h2>📋 健康状况总结</h2>
        <div class="summary-content">
            根据您的影像学检查（BI-RADS 4级）和家族史情况，目前处于高风险状态。
            建议您尽快完成穿刺活检以明确诊断，同时需要遗传咨询评估基因风险。
            请保持积极心态，及时采取必要的医疗措施。
        </div>
    </section>
    
    <section class="risk-assessment">
        <h2>🎯 风险评估</h2>
        <div class="risk-details">
            <p>根据综合评估，您的风险评分为<strong>75分（满分100分）</strong>，属于<strong>高风险人群</strong>。</p>
            <p>主要风险因素包括：</p>
            <ul>
                <li>BI-RADS 4级：存在可疑恶性征象</li>
                <li>有乳腺癌家族史：增加遗传风险</li>
                <li>年龄因素：需要密切关注</li>
            </ul>
        </div>
        
        <div class="immediate-actions">
            <h3>🔴 需要立即采取的行动</h3>
            <ol class="action-list">
                <li><strong>2周内完成穿刺活检</strong>：明确结节性质，这是最重要的</li>
                <li><strong>遗传咨询</strong>：建议进行BRCA1/2基因检测</li>
                <li><strong>影像学复查</strong>：安排超声和钼靶检查</li>
            </ol>
        </div>
    </section>
    
    <section class="symptom-management">
        <h2>💊 症状管理方案</h2>
        <p>您目前的主要症状是<strong>周期性疼痛</strong>，这通常与激素波动有关，属于良性表现。</p>
        <h3>疼痛缓解建议：</h3>
        <ul>
            <li><strong>饮食调整</strong>：月经前7天避免咖啡因、浓茶、辛辣食物</li>
            <li><strong>中医调理</strong>：可考虑疏肝理气的中药调理</li>
            <li><strong>情绪管理</strong>：保持心情舒畅，避免过度焦虑</li>
            <li><strong>局部护理</strong>：可用温热毛巾热敷缓解</li>
        </ul>
    </section>
    
    <section class="rhythm-regulation">
        <h2>🌙 生物节律调节</h2>
        <p>您的症状与月经周期相关，同时睡眠质量不佳，需要重点改善。</p>
        <h3>节律调节方案：</h3>
        <ul>
            <li><strong>复查时机</strong>：建议避开月经前7-10天（黄体期），选择月经后第7-14天复查最准确</li>
            <li><strong>症状记录</strong>：建议记录症状与月经周期的关系，有助于诊断</li>
            <li><strong>睡眠改善</strong>：
                <ul>
                    <li>建立规律作息，每晚22:30前入睡</li>
                    <li>睡前1小时避免使用电子设备</li>
                    <li>睡前可进行轻度拉伸或冥想</li>
                    <li>保持卧室温度适宜（18-22℃）</li>
                </ul>
            </li>
        </ul>
    </section>
    
    <section class="lifestyle-intervention">
        <h2>🏃 生活方式改善计划</h2>
        <div class="lifestyle-categories">
            <div class="category">
                <h3>🏃‍♀️ 运动建议</h3>
                <p><strong>目标</strong>：每周至少150分钟中等强度有氧运动</p>
                <p><strong>推荐项目</strong>：</p>
                <ul>
                    <li>快走：每天30-45分钟</li>
                    <li>游泳：每周2-3次</li>
                    <li>瑜伽：改善心情，缓解压力</li>
                </ul>
                <p><strong>注意</strong>：循序渐进，避免剧烈运动</p>
            </div>
            
            <div class="category">
                <h3>🥗 饮食调整</h3>
                <p><strong>增加摄入</strong>：</p>
                <ul>
                    <li>十字花科蔬菜（西兰花、卷心菜）</li>
                    <li>豆制品（适量）</li>
                    <li>新鲜水果</li>
                </ul>
                <p><strong>减少摄入</strong>：</p>
                <ul>
                    <li>高脂肪食物</li>
                    <li>酒精和咖啡因</li>
                    <li>加工肉类</li>
                </ul>
                <p><strong>严格忌口</strong>：蜂王浆、雪蛤等含雌激素食物</p>
            </div>
            
            <div class="category">
                <h3>⏰ 作息管理</h3>
                <ul>
                    <li>规律作息，每天同一时间起床和睡觉</li>
                    <li>避免熬夜，保证7-8小时睡眠</li>
                    <li>午休不超过30分钟</li>
                    <li>减少压力，学会放松</li>
                </ul>
            </div>
        </div>
        
        <h3>👙 内衣选择</h3>
        <p>避免穿着过紧的内衣，选择合适尺寸、无钢圈的舒适内衣。</p>
    </section>
    
    <section class="family-history">
        <h2>👨‍👩‍👧 家族史管理</h2>
        <p>由于您有乳腺癌家族史，需要特别关注：</p>
        <ul>
            <li><strong>遗传咨询</strong>：建议尽快进行BRCA1/2基因检测，评估遗传风险</li>
            <li><strong>提前筛查</strong>：建议比一般人群提前10年开始筛查</li>
            <li><strong>家族沟通</strong>：建议一级亲属（母亲、姐妹、女儿）也进行筛查</li>
            <li><strong>预防措施</strong>：根据基因检测结果，可能需要考虑预防性措施</li>
        </ul>
    </section>
    
    <section class="follow-up-plan">
        <h2>📅 随访计划</h2>
        <p>根据您的风险等级，为您制定以下密集随访方案：</p>
        <table class="follow-up-table">
            <tr>
                <th>随访频率</th>
                <td><strong>每3个月</strong>一次（高频随访）</td>
            </tr>
            <tr>
                <th>持续时间</th>
                <td>至少2年，后续根据情况调整</td>
            </tr>
            <tr>
                <th>检查方式</th>
                <td>
                    <ul style="margin: 0; padding-left: 20px;">
                        <li>乳腺超声（每次必做）</li>
                        <li>钼靶检查（每6个月）</li>
                        <li>必要时增强MRI</li>
                    </ul>
                </td>
            </tr>
            <tr>
                <th>复查时机</th>
                <td>建议选择月经后第7-14天复查，避开黄体期</td>
            </tr>
            <tr>
                <th>升级条件</th>
                <td>
                    如出现以下情况，需立即就医：
                    <ul style="margin: 0; padding-left: 20px;">
                        <li>结节增大超过20%</li>
                        <li>出现新发可疑征象</li>
                        <li>乳头出现血性溢液</li>
                        <li>皮肤出现橘皮样改变</li>
                    </ul>
                </td>
            </tr>
        </table>
    </section>
    
    <section class="important-notes">
        <h2>⚠️ 重要提示</h2>
        <ul class="notes-list">
            <li><strong>本报告仅供参考，具体诊疗请遵医嘱</strong></li>
            <li>请务必在2周内完成穿刺活检，这是明确诊断的关键</li>
            <li>定期复查非常重要，请按时随访，不要拖延</li>
            <li>如有任何不适或新发症状，请及时就医，不要等到复查时间</li>
            <li>保持积极乐观的心态，大部分乳腺结节是良性的</li>
            <li>有任何疑问，请及时咨询您的主治医生</li>
        </ul>
    </section>
    
    <footer class="report-footer">
        <p class="knowledge-reference">
            📚 本报告基于172条专业知识库和医疗决策树生成
        </p>
        <p class="knowledge-reference">
            🎯 决策路径：风险评估 → 影像学分析 → 症状管理 → 生活方式干预 → 随访计划
        </p>
        <p class="disclaimer">
            声明：本报告由AI辅助生成，基于专业知识库和医疗决策树，仅供参考，不构成医疗建议。
            请在专业医生指导下进行诊疗。
        </p>
    </footer>
</div>

<style>
.breast-health-report {
    font-family: "Microsoft YaHei", Arial, sans-serif;
    max-width: 900px;
    margin: 0 auto;
    padding: 30px;
    line-height: 1.8;
    color: #333;
}

.report-header {
    text-align: center;
    padding: 30px 0;
    border-bottom: 3px solid #409eff;
    margin-bottom: 30px;
}

.report-header h1 {
    color: #409eff;
    font-size: 28px;
    margin-bottom: 15px;
}

.report-meta {
    display: flex;
    justify-content: center;
    gap: 30px;
    color: #666;
}

.risk-badge {
    padding: 5px 15px;
    border-radius: 20px;
    font-weight: bold;
}

.risk-high {
    background: #fef0f0;
    color: #f56c6c;
}

.risk-medium {
    background: #fdf6ec;
    color: #e6a23c;
}

.risk-low {
    background: #f0f9ff;
    color: #409eff;
}

section {
    margin-bottom: 40px;
    padding: 25px;
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.05);
}

section h2 {
    color: #409eff;
    font-size: 22px;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 2px solid #e4e7ed;
}

section h3 {
    color: #606266;
    font-size: 18px;
    margin: 20px 0 15px 0;
}

.executive-summary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

.executive-summary h2 {
    color: white;
    border-bottom-color: rgba(255,255,255,0.3);
}

.summary-content {
    font-size: 16px;
    line-height: 2;
}

.immediate-actions {
    background: #fef0f0;
    padding: 20px;
    border-radius: 8px;
    border-left: 4px solid #f56c6c;
    margin-top: 20px;
}

.action-list {
    list-style: none;
    counter-reset: action-counter;
    padding-left: 0;
}

.action-list li {
    counter-increment: action-counter;
    margin: 15px 0;
    padding-left: 40px;
    position: relative;
    font-size: 16px;
    font-weight: 500;
}

.action-list li:before {
    content: counter(action-counter);
    position: absolute;
    left: 0;
    top: 0;
    background: #f56c6c;
    color: white;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    text-align: center;
    line-height: 28px;
    font-weight: bold;
}

.lifestyle-categories {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin-top: 20px;
}

.category {
    padding: 20px;
    background: #f5f7fa;
    border-radius: 8px;
    border-left: 4px solid #409eff;
}

.follow-up-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
}

.follow-up-table th,
.follow-up-table td {
    padding: 15px;
    border: 1px solid #ebeef5;
    text-align: left;
}

.follow-up-table th {
    background: #f5f7fa;
    font-weight: 600;
    width: 30%;
}

.important-notes {
    background: #fff7e6;
    border-left: 4px solid #e6a23c;
}

.notes-list {
    list-style: none;
    padding-left: 0;
}

.notes-list li {
    padding: 10px 0 10px 30px;
    position: relative;
}

.notes-list li:before {
    content: "⚠️";
    position: absolute;
    left: 0;
}

.report-footer {
    margin-top: 40px;
    padding-top: 20px;
    border-top: 2px solid #e4e7ed;
    text-align: center;
    color: #909399;
    font-size: 14px;
}

.knowledge-reference {
    margin: 10px 0;
    font-weight: 500;
}

.disclaimer {
    margin: 10px 0;
    font-style: italic;
}

@media print {
    .breast-health-report {
        padding: 20px;
    }
    
    section {
        page-break-inside: avoid;
    }
}
</style>
"""
    
    def _extract_html(self, response: str) -> str:
        """从LLM响应中提取HTML"""
        # 如果响应已经是HTML，直接返回
        if '<div class="breast-health-report">' in response:
            return response
        
        # 否则，尝试提取HTML代码块
        if '```html' in response:
            start = response.find('```html') + 7
            end = response.find('```', start)
            if end > start:
                return response[start:end].strip()
        
        # 如果都没有，返回原响应
        return response
    
    def _extract_summary(self, decision_result: Dict) -> str:
        """提取报告摘要"""
        # 不再使用风险评估字段，返回简单摘要
        patient_summary = decision_result.get('patient_summary', {})
        age = patient_summary.get('age', '未知')
        birads = patient_summary.get('birads', '未知')
        summary = f"患者年龄{age}岁，BI-RADS分级{birads}级。"
        
        return summary
    
    # 格式化辅助方法
    def _format_patient_info(self, data: Dict, decision_result: Dict) -> str:
        """
        @isdoc
        @description 生成“患者基本信息”摘要。兼容两种来源：
        - decision_result['patient_summary']（旧决策树结构）
        - 直接从 patient_data/data 中取值（当前 B/C 端已移除决策树时）
        """
        summary = decision_result.get('patient_summary') or {}

        # 兼容：当未提供 patient_summary 时，使用 patient_data 里的字段兜底
        if not summary:
            age = data.get('age', '未知')
            birads = data.get('birads_level', data.get('birads', '未知'))
            family_history = data.get('family_history', '未提供')
            symptoms = data.get('symptoms', '无')
            key_features = data.get('key_features', [])
            if isinstance(key_features, str):
                key_features = [key_features]
            return f"""
- 年龄：{age}岁
- BI-RADS分级：{birads}级
- 家族史：{family_history}
- 主要症状：{symptoms}
- 关键特征：{', '.join(key_features) if key_features else '无'}
"""

        return f"""
- 年龄：{summary['age']}岁
- BI-RADS分级：{summary['birads']}级
- 家族史：{summary['family_history']}
- 主要症状：{summary.get('symptoms', '无')}
- 关键特征：{', '.join(summary.get('key_features', []))}
"""
    
    def _format_risk_assessment(self, risk: Dict) -> str:
        """格式化风险评估（已移除，不再使用）"""
        # 不再使用风险评估字段
        return "风险评估：暂未评估"
    
    def _format_imaging_findings(self, imaging: Dict) -> str:
        if not imaging:
            return "（无特殊影像学发现）"
        
        return f"""
- **分类**: {imaging.get('category', '常规')}
- **紧急度**: {imaging.get('urgency', '常规')}
- **建议**:
  {self._format_list(imaging.get('recommendations', []))}
"""
    
    def _format_symptom_management(self, symptom: Dict) -> str:
        if not symptom:
            return "（无特殊症状）"
        
        return f"""
- **症状类型**: {', '.join(symptom.get('symptom_types', []))}
- **管理建议**:
  {self._format_list(symptom.get('recommendations', []))}
"""
    
    def _format_rhythm_regulation(self, rhythm: Dict) -> str:
        if not rhythm:
            return "（无特殊节律问题）"
        
        return f"""
- **节律类型**: {rhythm.get('rhythm_type', '未记录')}
- **睡眠质量**: {rhythm.get('sleep_quality', '未记录')}
- **调节建议**:
  {self._format_list(rhythm.get('recommendations', []))}
"""
    
    def _format_lifestyle_recommendations(self, lifestyle: Dict) -> str:
        if not lifestyle:
            return "（无特殊生活方式建议）"
        
        recs = lifestyle.get('recommendations', [])[:5]  # 只显示前5条
        return f"""
- **运动水平**: {lifestyle.get('exercise_level', '未记录')}
- **改善建议**:
  {self._format_list(recs)}
"""
    
    def _format_family_management(self, family: Dict) -> str:
        if not family:
            return "（无家族史）"
        
        return f"""
- **有家族史**: 是
- **管理建议**:
  {self._format_list(family.get('recommendations', []))}
"""
    
    def _format_follow_up_plan(self, followup: Dict) -> str:
        if not followup:
            return "（待制定）"
        
        return f"""
- **计划类型**: {followup.get('plan_type', '常规随访')}
- **随访频率**: {followup.get('frequency', '12个月')}
- **持续时间**: {followup.get('duration', '长期')}
- **检查方式**: {', '.join(followup.get('modalities', ['超声']))}
- **升级条件**: {followup.get('escalation', '结节性质改变')}
"""
    
    def _format_knowledge_references(self, knowledge_items: List[KnowledgeItem], decision_result: Dict) -> str:
        """格式化知识引用"""
        refs = decision_result.get('knowledge_references', [])[:10]  # 前10条
        
        lines = []
        for ref in refs:
            lines.append(f"  - [{ref['id']}] {ref['title']} ({ref['source_type']}, 优先级{ref['priority']})")
        
        return '\n'.join(lines) if lines else "（无特定知识引用）"
    
    def _format_list(self, items: List[str]) -> str:
        """格式化列表"""
        if not items:
            return "  （无）"
        return '\n'.join(f"  - {item}" for item in items)

    def generate_western_medical_assessment(self, patient_data: Dict, nodule_types: str = 'breast') -> Dict[str, Any]:
        """
        生成西医风险评估分析

        严格基于相应的评估标准和临床指南，不涉及中医内容

        Args:
            patient_data: 患者完整健康档案数据，包含：
                - 基本信息（age, height, weight, phone）
                - 影像学特征（birads_level/lung_rads_level/thyroid_tirads_level, symptoms, nodule_location, etc.）
                - 既往病史（breast_hyperplasia_history/lung_cancer_history/thyroid_cancer_history, etc.）
                - 风险因素（dust_exposure_history, diabetes_history, etc.）
            nodule_types: 结节类型 ('breast', 'lung', 'thyroid')

        Returns:
            {
                "conclusion": str (100-150字，包含评估标准解读和复查建议),
                "risk_score": int (0-100),
                "risk_level": str (低危/中危/高危),
                "risk_reason": str (≤50字，高危因素归因)
            }
        """
        # 构建严格的西医评估提示词
        prompt = self._build_western_medical_prompt(patient_data, nodule_types)

        # 调用LLM API
        response = self._call_llm_api(prompt)

        # 解析结构化输出
        result = self._parse_western_medical_response(response)

        return result

    def _build_western_medical_prompt(self, patient_data: Dict, nodule_types: str = 'breast') -> str:
        """构建西医评估Prompt（使用统一提示词管理）"""

        # 导入提示词配置
        from prompt_config import get_prompt_template, format_prompt

        # 提取关键数据
        age = patient_data.get('age', '未知')
        height = patient_data.get('height', '未知')
        weight = patient_data.get('weight', '未知')
        gender = patient_data.get('gender', '未知')  # 性别：用于称呼（先生/女士）

        # 计算BMI（如果有身高体重）
        bmi_info = ""
        if height and weight and height != '未知' and weight != '未知':
            try:
                bmi = float(weight) / ((float(height) / 100) ** 2)
                bmi_info = f"- BMI: {bmi:.1f}"
            except:
                bmi_info = ""

        # 根据结节类型获取影像学特征
        if nodule_types == 'triple':
            # 三结节类型：需要提取所有三种器官的数据
            birads_level = patient_data.get('birads_level') or '未知'
            lung_rads_level = patient_data.get('lung_rads_level') or '未知'
            tirads_level = patient_data.get('tirads_level') or '未知'
            # 其他字段在prompt_vars中单独处理
            assessment_level = None  # triple类型不使用单一assessment_level
        elif nodule_types == 'lung':
            assessment_level = patient_data.get('lung_rads_level') or '未知'
            nodule_location = patient_data.get('lung_nodule_location') or '未记录'
            nodule_size = patient_data.get('lung_nodule_size') or '未记录'
            boundary_features = patient_data.get('lung_boundary_features') or '未记录'
            internal_feature = patient_data.get('lung_internal_density') or '未记录'
            symptoms = patient_data.get('lung_symptoms', '无明显症状')
            lung_calcification = patient_data.get('lung_calcification') or '未记录'
        elif nodule_types == 'thyroid':
            assessment_level = patient_data.get('tirads_level') or '未知'  # 修复：应该是tirads_level
            nodule_location = patient_data.get('thyroid_nodule_location') or '未记录'
            nodule_size = patient_data.get('thyroid_nodule_size') or '未记录'
            boundary_features = patient_data.get('thyroid_boundary_features') or '未记录'
            internal_feature = patient_data.get('thyroid_internal_echo') or '未记录'
            blood_flow_signal = patient_data.get('thyroid_blood_flow_signal') or '未记录'
            symptoms = patient_data.get('thyroid_symptoms', '无明显症状')
            thyroid_calcification = patient_data.get('thyroid_calcification') or '未记录'
        else:  # breast
            assessment_level = patient_data.get('birads_level') or '未知'
            nodule_location = patient_data.get('nodule_location') or '未记录'
            nodule_size = patient_data.get('nodule_size') or '未记录'
            boundary_features = patient_data.get('boundary_features') or '未记录'
            internal_feature = patient_data.get('internal_echo') or '未记录'
            blood_flow_signal = patient_data.get('blood_flow_signal') or '未记录'
            elasticity_score = patient_data.get('elasticity_score') or '未记录'
            symptoms = patient_data.get('symptoms', '无明显症状')

        # 提取疾病史和风险因素
        if nodule_types == 'triple':
            # 三结节类型：需要传递所有三种器官的数据
            prompt_vars = {
                'age': age,
                'gender': gender,  # 性别：用于称呼（先生/女士）
                'height': height,
                'weight': weight,
                'bmi_info': bmi_info,
                
                # 三器官影像学分级
                'birads_level': birads_level,
                'lung_rads_level': lung_rads_level,
                'tirads_level': tirads_level,
                
                # 乳腺相关疾病史
                'breast_hyperplasia_history': patient_data.get('breast_hyperplasia_history', '无'),
                'breast_fibroadenoma_history': patient_data.get('breast_fibroadenoma_history', '无'),
                'breast_cyst_history': patient_data.get('breast_cyst_history', '无'),
                'breast_inflammation_history': patient_data.get('breast_inflammation_history', '无'),
                'breast_cancer_history': patient_data.get('breast_cancer_history', '无'),
                'hereditary_breast_history': patient_data.get('hereditary_breast_history', '无'),
                
                # 肺部相关疾病史
                'pneumonia_history': patient_data.get('pneumonia_history', '无'),
                'tb_history': patient_data.get('tb_history', '无'),
                'copd_history': patient_data.get('copd_history', '无'),
                'fibrosis_history': patient_data.get('fibrosis_history', '无'),
                'lung_cancer_history': patient_data.get('lung_cancer_history', '无'),
                'hereditary_lung_history': patient_data.get('hereditary_lung_history', '无'),
                
                # 甲状腺相关疾病史
                'hyperthyroidism_history': patient_data.get('hyperthyroidism_history', '无'),
                'hypothyroidism_history': patient_data.get('hypothyroidism_history', '无'),
                'hashimoto_history': patient_data.get('hashimoto_history', '无'),
                'thyroid_cancer_history': patient_data.get('thyroid_cancer_history', '无'),
                'hereditary_thyroid_history': patient_data.get('hereditary_thyroid_history', '无'),
                
                # 通用风险因素
                'dust_exposure_history': patient_data.get('dust_exposure_history', '无'),
                'diabetes_history': patient_data.get('diabetes_history', '无'),
                'radiation_exposure_history': patient_data.get('radiation_exposure_history', '无'),
                'autoimmune_disease_history': patient_data.get('autoimmune_disease_history', '无'),
                'medication_history': patient_data.get('medication_history', '无'),
                'tumor_marker_test': patient_data.get('tumor_marker_test', '无'),
                'smoking_risk_level': patient_data.get('smoking_risk_level', '未记录'),
                'diabetes_control_level': patient_data.get('diabetes_control_level', '未记录'),
            }
        elif nodule_types == 'breast_lung':
            # 乳腺+肺部组合类型
            prompt_vars = {
                'age': age,
                'gender': gender,  # 性别：用于称呼（先生/女士）
                'height': height,
                'weight': weight,
                'bmi_info': bmi_info,
                
                # 两器官影像学分级
                'birads_level': patient_data.get('birads_level', '未知'),
                'lung_rads_level': patient_data.get('lung_rads_level', '未知'),
                
                # 乳腺相关疾病史
                'breast_hyperplasia_history': patient_data.get('breast_hyperplasia_history', '无'),
                'breast_fibroadenoma_history': patient_data.get('breast_fibroadenoma_history', '无'),
                'breast_cyst_history': patient_data.get('breast_cyst_history', '无'),
                'breast_inflammation_history': patient_data.get('breast_inflammation_history', '无'),
                'breast_cancer_history': patient_data.get('breast_cancer_history', '无'),
                'hereditary_breast_history': patient_data.get('hereditary_breast_history', '无'),
                
                # 肺部相关疾病史
                'pneumonia_history': patient_data.get('pneumonia_history', '无'),
                'tb_history': patient_data.get('tb_history', '无'),
                'copd_history': patient_data.get('copd_history', '无'),
                'fibrosis_history': patient_data.get('fibrosis_history', '无'),
                'lung_cancer_history': patient_data.get('lung_cancer_history', '无'),
                'hereditary_lung_history': patient_data.get('hereditary_lung_history', '无'),
                
                # 通用风险因素
                'dust_exposure_history': patient_data.get('dust_exposure_history', '无'),
                'diabetes_history': patient_data.get('diabetes_history', '无'),
                'radiation_exposure_history': patient_data.get('radiation_exposure_history', '无'),
                'autoimmune_disease_history': patient_data.get('autoimmune_disease_history', '无'),
                'medication_history': patient_data.get('medication_history', '无'),
                'tumor_marker_test': patient_data.get('tumor_marker_test', '无'),
                'smoking_risk_level': patient_data.get('smoking_risk_level', '未记录'),
                'diabetes_control_level': patient_data.get('diabetes_control_level', '未记录'),
            }
        elif nodule_types == 'breast_thyroid':
            # 乳腺+甲状腺组合类型
            prompt_vars = {
                'age': age,
                'gender': gender,  # 性别：用于称呼（先生/女士）
                'height': height,
                'weight': weight,
                'bmi_info': bmi_info,
                
                # 两器官影像学分级
                'birads_level': patient_data.get('birads_level', '未知'),
                'tirads_level': patient_data.get('tirads_level', '未知'),
                
                # 乳腺相关疾病史
                'breast_hyperplasia_history': patient_data.get('breast_hyperplasia_history', '无'),
                'breast_fibroadenoma_history': patient_data.get('breast_fibroadenoma_history', '无'),
                'breast_cyst_history': patient_data.get('breast_cyst_history', '无'),
                'breast_inflammation_history': patient_data.get('breast_inflammation_history', '无'),
                'breast_cancer_history': patient_data.get('breast_cancer_history', '无'),
                'hereditary_breast_history': patient_data.get('hereditary_breast_history', '无'),
                
                # 甲状腺相关疾病史
                'hyperthyroidism_history': patient_data.get('hyperthyroidism_history', '无'),
                'hypothyroidism_history': patient_data.get('hypothyroidism_history', '无'),
                'hashimoto_history': patient_data.get('hashimoto_history', '无'),
                'thyroid_cancer_history': patient_data.get('thyroid_cancer_history', '无'),
                'hereditary_thyroid_history': patient_data.get('hereditary_thyroid_history', '无'),
                
                # 通用风险因素
                'dust_exposure_history': patient_data.get('dust_exposure_history', '无'),
                'diabetes_history': patient_data.get('diabetes_history', '无'),
                'radiation_exposure_history': patient_data.get('radiation_exposure_history', '无'),
                'autoimmune_disease_history': patient_data.get('autoimmune_disease_history', '无'),
                'medication_history': patient_data.get('medication_history', '无'),
                'tumor_marker_test': patient_data.get('tumor_marker_test', '无'),
                'smoking_risk_level': patient_data.get('smoking_risk_level', '未记录'),
                'diabetes_control_level': patient_data.get('diabetes_control_level', '未记录'),
            }
        elif nodule_types == 'lung_thyroid':
            # 肺部+甲状腺组合类型
            prompt_vars = {
                'age': age,
                'gender': gender,  # 性别：用于称呼（先生/女士）
                'height': height,
                'weight': weight,
                'bmi_info': bmi_info,
                
                # 两器官影像学分级
                'lung_rads_level': patient_data.get('lung_rads_level', '未知'),
                'tirads_level': patient_data.get('tirads_level', '未知'),
                
                # 肺部相关疾病史
                'pneumonia_history': patient_data.get('pneumonia_history', '无'),
                'tb_history': patient_data.get('tb_history', '无'),
                'copd_history': patient_data.get('copd_history', '无'),
                'fibrosis_history': patient_data.get('fibrosis_history', '无'),
                'lung_cancer_history': patient_data.get('lung_cancer_history', '无'),
                'hereditary_lung_history': patient_data.get('hereditary_lung_history', '无'),
                
                # 甲状腺相关疾病史
                'hyperthyroidism_history': patient_data.get('hyperthyroidism_history', '无'),
                'hypothyroidism_history': patient_data.get('hypothyroidism_history', '无'),
                'hashimoto_history': patient_data.get('hashimoto_history', '无'),
                'thyroid_cancer_history': patient_data.get('thyroid_cancer_history', '无'),
                'hereditary_thyroid_history': patient_data.get('hereditary_thyroid_history', '无'),
                
                # 通用风险因素
                'dust_exposure_history': patient_data.get('dust_exposure_history', '无'),
                'diabetes_history': patient_data.get('diabetes_history', '无'),
                'radiation_exposure_history': patient_data.get('radiation_exposure_history', '无'),
                'autoimmune_disease_history': patient_data.get('autoimmune_disease_history', '无'),
                'medication_history': patient_data.get('medication_history', '无'),
                'tumor_marker_test': patient_data.get('tumor_marker_test', '无'),
                'smoking_risk_level': patient_data.get('smoking_risk_level', '未记录'),
                'diabetes_control_level': patient_data.get('diabetes_control_level', '未记录'),
            }
        else:
            # 单一结节类型：保持原有逻辑
            prompt_vars = {
                'age': age,
                'gender': gender,  # 性别：用于称呼（先生/女士）
                'height': height,
                'weight': weight,
                'bmi_info': bmi_info,
                'assessment_level': assessment_level,
                'nodule_location': nodule_location,
                'nodule_size': nodule_size,
                'boundary_features': boundary_features,
                'internal_feature': internal_feature,
                'symptoms': symptoms,

                # 乳腺相关
                'blood_flow_signal': patient_data.get('blood_flow_signal', '未记录'),
                'elasticity_score': patient_data.get('elasticity_score', '未记录'),
                'hyperplasia': patient_data.get('breast_hyperplasia_history', '无'),
                'fibroadenoma': patient_data.get('breast_fibroadenoma_history', '无'),
                'cyst': patient_data.get('breast_cyst_history', '无'),
                'inflammation': patient_data.get('breast_inflammation_history', '无'),
                'cancer_history': patient_data.get('breast_cancer_history', '无'),

                # 肺部相关
                'lung_calcification': patient_data.get('lung_calcification', '未记录'),
                'lung_disease_history': patient_data.get('lung_disease_history', '无'),
                'lung_cancer_history': patient_data.get('lung_cancer_history', '无'),
                'smoking_history': patient_data.get('smoking_history', '无'),

                # 甲状腺相关
                'thyroid_calcification': patient_data.get('thyroid_calcification', '未记录'),
                'hyperthyroidism_history': patient_data.get('hyperthyroidism_history', '无'),
                'hypothyroidism_history': patient_data.get('hypothyroidism_history', '无'),
                'hashimoto_history': patient_data.get('hashimoto_history', '无'),
                'thyroid_cancer_history': patient_data.get('thyroid_cancer_history', '无'),

                # 其他风险因素
                'dust_exposure': patient_data.get('dust_exposure_history', '无'),
                'diabetes': patient_data.get('diabetes_history', '无'),
                'radiation_exposure': patient_data.get('radiation_exposure_history', '无'),
                'autoimmune': patient_data.get('autoimmune_disease_history', '无'),
                'medication': patient_data.get('medication_history', '无'),
                'tumor_marker': patient_data.get('tumor_marker_test', '无'),
                'hereditary': patient_data.get('hereditary_breast_history', '无'),
                'contraceptive_risk': patient_data.get('contraceptive_risk_level', '未记录'),
                'smoking_risk': patient_data.get('smoking_risk_level', '未记录'),
                'diabetes_control': patient_data.get('diabetes_control_level', '未记录'),
            }

        # 获取提示词模板并格式化
        template = get_prompt_template(nodule_types, 'western_medical')
        prompt = format_prompt(template, **prompt_vars)
        
        # 调试：打印完整数据（可选，通过环境变量控制）
        import os
        if os.getenv('DEBUG_LLM_DATA', 'False').lower() == 'true':
            from utils.llm_data_debugger import print_full_llm_data, save_llm_prompt_to_file
            from datetime import datetime
            print_full_llm_data(patient_data, prompt_vars, nodule_types, 'western_medical')
            save_llm_prompt_to_file(prompt, f"western_medical_{nodule_types}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        
        return prompt

    def _parse_western_medical_response(self, response: str) -> Dict[str, Any]:
        """解析西医评估响应（提取JSON结构化数据，带容错机制）"""

        try:
            # 使用带容错机制的JSON解析函数
            from routes.llm_helpers import parse_json_response
            result = parse_json_response(response)

            # 验证必需字段，如果缺失则使用默认值
            if 'conclusion' not in result:
                result['conclusion'] = "评估数据不完整，建议遵循医嘱进行后续检查。"
            if 'risk_warning' not in result:
                result['risk_warning'] = "数据不完整，建议联系医生进行人工评估。"
            if 'risk_score' not in result:
                result['risk_score'] = 50
            if 'risk_level' not in result:
                result['risk_level'] = '中危'

            # 验证数据类型和范围
            if not isinstance(result['risk_score'], (int, float)):
                result['risk_score'] = int(result['risk_score'])

            result['risk_score'] = max(0, min(100, int(result['risk_score'])))

            if result['risk_level'] not in ['低危', '中危', '高危']:
                # 根据分数自动判定
                score = result['risk_score']
                if score <= 30:
                    result['risk_level'] = '低危'
                elif score <= 60:
                    result['risk_level'] = '中危'
                else:
                    result['risk_level'] = '高危'

            # 直接使用LLM返回的内容，不做任何字数修改
            print(f"✅ LLM响应: conclusion={len(result['conclusion'])}字, risk_warning={len(result['risk_warning'])}字")
            return result

        except Exception as e:
            print(f"❌ 解析西医评估响应失败: {e}")
            print(f"原始响应: {response[:500]}")

            # 返回默认值
            return {
                "conclusion": "评估数据解析失败，请联系技术支持。建议遵循医嘱进行后续检查。",
                "risk_score": 50,
                "risk_level": "中危",
                "risk_warning": "数据解析失败，请联系技术支持进行人工评估。"
            }


# 全局LLM服务实例
llm_generator = LLMReportGenerator()

# 从环境变量加载配置
import os
_openrouter_api_key = os.getenv('OPENROUTER_API_KEY', '')
_openrouter_model = os.getenv('OPENROUTER_MODEL', 'google/gemini-2.5-pro')

if _openrouter_api_key:
    llm_generator.set_api_key(_openrouter_api_key)
    print(f"OK: OpenRouter API Key loaded: {_mask_api_key(_openrouter_api_key)}")
else:
    print("WARNING: OPENROUTER_API_KEY missing (LLM disabled)")
if _openrouter_model:
    llm_generator.set_model(_openrouter_model)
    print(f"OK: LLM model set to: {_openrouter_model}")

