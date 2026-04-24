"""
LLM辅助函数
用于生成综合分析结论和影像学结论
支持七种结节类型的动态提示词管理
"""
import re
import json
import os
from datetime import datetime
from services.llm_service import llm_generator
from models import KnowledgeItem
from prompt_config import get_prompt_template, format_prompt


def parse_json_response(response: str) -> dict:
    """
    解析LLM返回的JSON响应（带容错机制）

    Args:
        response: LLM返回的原始响应字符串

    Returns:
        dict: 解析后的JSON对象

    Raises:
        Exception: 如果解析失败
    """
    original_response = response

    # 调试：打印原始响应（完整响应，用于诊断）
    print(f"\n[DEBUG] LLM原始响应（完整）：")
    print("="*60)
    print(original_response)
    print("="*60)
    print(f"[DEBUG] 响应总长度: {len(original_response)} 字符\n")

    try:
        # 去除markdown代码块标记
        response = response.strip()
        if response.startswith('```json'):
            response = response[7:]
        if response.startswith('```'):
            response = response[3:]
        if response.endswith('```'):
            response = response[:-3]

        response = response.strip()

        # 尝试直接解析
        try:
            result = json.loads(response)
            # 清理"尊敬的"前面的空格
            if 'conclusion' in result and result['conclusion']:
                result['conclusion'] = re.sub(r'^[\s\u3000\u00A0]*尊敬的', '尊敬的', result['conclusion'])
                result['conclusion'] = result['conclusion'].lstrip()
            return result
        except json.JSONDecodeError:
            pass

        # 提取JSON对象（支持嵌套）
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            try:
                result = json.loads(json_str)
                # 清理"尊敬的"前面的空格
                if 'conclusion' in result and result['conclusion']:
                    result['conclusion'] = re.sub(r'^[\s\u3000\u00A0]*尊敬的', '尊敬的', result['conclusion'])
                    result['conclusion'] = result['conclusion'].lstrip()
                return result
            except json.JSONDecodeError:
                pass

        # 容错机制1：尝试修复被截断的JSON
        # 找到最后一个完整的字段值，然后闭合JSON
        truncated_json = response
        if '"conclusion"' in truncated_json:
            # 尝试修复：添加闭合引号和括号
            if not truncated_json.rstrip().endswith('}'):
                # 找到conclusion的值开始位置
                match = re.search(r'"conclusion"\s*:\s*"', truncated_json)
                if match:
                    # 检查是否有未闭合的引号
                    content_after = truncated_json[match.end():]
                    # 如果没有找到闭合引号，尝试修复
                    if '"' not in content_after or content_after.count('"') % 2 == 1:
                        # 截取到最后一个完整句子（支持中英文标点）
                        last_sentence_end = max(
                            truncated_json.rfind('。'),
                            truncated_json.rfind('.'),
                            truncated_json.rfind('！'),
                            truncated_json.rfind('？'),
                            truncated_json.rfind('!'),
                            truncated_json.rfind('?')
                        )
                        if last_sentence_end > match.end():
                            # 在句子边界处截断，然后闭合JSON
                            truncated_json = truncated_json[:last_sentence_end + 1] + '"\n}'
                            # 如果还有其他字段，尝试添加默认值
                            if '"risk_score"' not in truncated_json:
                                truncated_json = truncated_json[:-1] + ',\n  "risk_score": 50,\n  "risk_level": "中危",\n  "risk_warning": "数据解析不完整，建议联系医生进行人工评估。"\n}'
                            try:
                                result = json.loads(truncated_json)
                                # 清理"尊敬的"前面的空格
                                if 'conclusion' in result and result['conclusion']:
                                    result['conclusion'] = re.sub(r'^[\s\u3000\u00A0]*尊敬的', '尊敬的', result['conclusion'])
                                    result['conclusion'] = result['conclusion'].lstrip()
                                return result
                            except json.JSONDecodeError:
                                pass

        # 容错机制2：使用正则表达式提取conclusion和risk_warning字段（即使被截断）
        result = {}

        # 提取conclusion字段（改进正则表达式）
        conclusion_match = re.search(
            r'"conclusion"\s*:\s*"((?:[^"\\]|\\.)*)"',
            response,
            re.DOTALL
        )
        if conclusion_match:
            conclusion_text = conclusion_match.group(1)
            # 处理转义字符
            conclusion_text = conclusion_text.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
            # 立即清理"尊敬的"前面的所有空格（包括全角空格、半角空格等）
            conclusion_text = re.sub(r'^[\s\u3000\u00A0]*尊敬的', '尊敬的', conclusion_text)
            conclusion_text = conclusion_text.lstrip()  # 移除开头所有空格
            result['conclusion'] = conclusion_text
            print(f"✅ 成功提取conclusion字段（{len(conclusion_text)}字符）")
        else:
            print(f"⚠️ 未能提取conclusion字段")

        # 提取risk_warning字段（改进正则表达式，支持多种格式）
        warning_match = re.search(
            r'"risk_warning"\s*:\s*"((?:[^"\\]|\\.)*)"',
            response,
            re.DOTALL
        )

        if not warning_match:
            # 尝试更宽松的匹配（可能JSON不规范）
            print(f"⚠️ 标准正则匹配失败，尝试宽松匹配...")
            warning_match = re.search(
                r'"risk_warning"\s*:\s*"([^"]*(?:\\"[^"]*)*)"',
                response,
                re.DOTALL
            )

        if warning_match:
            warning_text = warning_match.group(1)
            # 处理转义字符
            warning_text = warning_text.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
            result['risk_warning'] = warning_text
            print(f"✅ 成功提取risk_warning字段（{len(warning_text)}字符）")
        else:
            # 尝试提取被截断的risk_warning（在句子边界截断）
            print(f"⚠️ 未能提取risk_warning字段，尝试提取被截断的内容...")
            if '"risk_warning"' in response:
                idx = response.find('"risk_warning"')
                # 查找冒号后的引号
                start_quote = response.find('"', idx + len('"risk_warning"') + 1)
                if start_quote != -1:
                    # 提取从开始引号到响应结尾的所有内容
                    truncated_text = response[start_quote + 1:]
                    # 在最后一个完整句子处截断
                    last_sentence_end = max(
                        truncated_text.rfind('。'),
                        truncated_text.rfind('！'),
                        truncated_text.rfind('？'),
                        truncated_text.rfind('.'),
                        truncated_text.rfind('!'),
                        truncated_text.rfind('?')
                    )
                    if last_sentence_end > 50:  # 至少要有50个字符
                        warning_text = truncated_text[:last_sentence_end + 1]
                        # 处理转义字符
                        warning_text = warning_text.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
                        result['risk_warning'] = warning_text
                        print(f"✅ 从被截断的响应中提取risk_warning（{len(warning_text)}字符，在句子边界截断）")
                    else:
                        print(f"⚠️ 被截断的内容太短（{last_sentence_end}字符），无法提取")
                else:
                    print(f"⚠️ 未找到risk_warning的起始引号")
            else:
                print(f"[DEBUG] 响应中不包含risk_warning字段")

        # 提取risk_score字段
        score_match = re.search(r'"risk_score"\s*:\s*(\d+)', response)
        if score_match:
            result['risk_score'] = int(score_match.group(1))
        else:
            result['risk_score'] = 50  # 默认值

        # 提取risk_level字段
        level_match = re.search(r'"risk_level"\s*:\s*"([^"]+)"', response)
        if level_match:
            result['risk_level'] = level_match.group(1)
        else:
            # 根据risk_score自动判定
            score = result.get('risk_score', 50)
            if score <= 30:
                result['risk_level'] = '低危'
            elif score <= 60:
                result['risk_level'] = '中危'
            else:
                result['risk_level'] = '高危'

        # 如果至少提取到了conclusion，就返回结果
        if 'conclusion' in result:
            # 确保所有必需字段都有值
            if 'risk_warning' not in result:
                result['risk_warning'] = "数据解析不完整，建议联系医生进行人工评估。"
            return result

        # 所有方法都失败了
        print(f"❌ JSON解析失败，无法提取字段")
        print(f"原始响应前500字符: {original_response[:500]}")
        raise Exception(f"JSON解析失败")

    except Exception as e:
        if 'JSON解析失败' in str(e):
            raise
        print(f"❌ JSON解析失败: {e}")
        print(f"原始响应前500字符: {original_response[:500]}")
        raise Exception(f"JSON解析失败: {e}")


def format_text_with_line_breaks(text: str) -> str:
    """
    格式化文本，确保"首先"、"其次"、"最后"等关键词前面有空行和编号
    说明：
    - 保留换行与编号
    - 去除行首缩进字符（避免在 HTML 模板使用 white-space: pre-* 时出现“多个空格/大缩进”视觉问题）
    """
    if not text:
        return text
    
    # ========== 第一步：彻底清理"尊敬的"前面的所有空格 ==========
    # 移除开头的所有空格（包括全角空格、半角空格、制表符等）
    text = text.lstrip()
    # 移除所有类型的空格（全角空格\u3000、半角空格、制表符\t、换行符\n、不间断空格\u00A0等）
    text = re.sub(r'^[\s\u3000\u00A0\t\n]*尊敬的', '尊敬的', text)
    # 再次确保"尊敬的"前面没有任何空格（包括多个连续空格）
    text = re.sub(r'^\s+尊敬的', '尊敬的', text)
    # 如果文本不是以"尊敬的"开头，再次清理开头空格
    if not text.startswith('尊敬的'):
        text = text.lstrip()
        text = re.sub(r'^[\s\u3000\u00A0\t\n]*尊敬的', '尊敬的', text)
    
    # 处理"首先"、"其次"、"最后"等关键词，确保它们前面有空行，并添加编号
    # 如果它们前面是句号、感叹号或问号，在标点后添加两个换行（空一行）
    text = re.sub(r'([。！？])\s*首先', r'\1\n\n1. 首先', text)
    text = re.sub(r'([。！？])\s*其次', r'\1\n\n2. 其次', text)
    text = re.sub(r'([。！？])\s*最后', r'\1\n\n3. 最后', text)
    
    # 如果"首先"、"其次"、"最后"在文本开头或行首，确保前面有空行并添加编号
    if text.startswith('首先'):
        text = '1. ' + text[2:]  # 替换"首先"为"1. 首先"
    elif text.startswith('其次'):
        text = '\n2. ' + text[2:]  # 替换"其次"为"2. 其次"，前面加空行
    elif text.startswith('最后'):
        text = '\n3. ' + text[2:]  # 替换"最后"为"3. 最后"，前面加空行
    
    # 按行处理，为"首先"、"其次"、"最后"开头的段落添加两个字符缩进
    # 同时处理风险提示中的【器官名称】标记，为其添加编号和缩进
    lines = text.split('\n')
    formatted_lines = []
    risk_item_counter = 0  # 风险提示项目计数器
    found_risk_marker = False  # 标记是否已经遇到【器官名称】标记
    in_conclusion_section = False  # 标记是否在结论部分（"首先"、"其次"、"最后"）
    
    for i, line in enumerate(lines):
        stripped = line.lstrip()  # 移除行首所有空格
        if not stripped:  # 空行，保持原样
            formatted_lines.append('')
            # 空行后重置标记，因为可能开始新的段落（结尾段落）
            found_risk_marker = False  # 重置，允许新的风险提示段落（结尾段落应该顶格）
        elif re.match(r'^[123]\.\s*(首先|其次|最后)', stripped):
            # "1. 首先"、"2. 其次"、"3. 最后"开头的行：不再插入全角空格缩进，交给模板/样式控制
            formatted_lines.append(stripped)
            in_conclusion_section = True  # 标记在结论部分
            found_risk_marker = False  # 结论部分，不是风险提示
            risk_item_counter = 0  # 重置计数器
        elif re.search(r'【[^】]+】', stripped):  # 改为search而不是match，允许【器官名称】在行中任何位置
            # 风险提示中的【器官名称】标记，添加编号和缩进
            # 检查是否已经有编号
            if not re.match(r'^\d+\.\s*', stripped):
                # 如果没有编号，添加编号
                found_risk_marker = True
                risk_item_counter += 1
                formatted_lines.append(str(risk_item_counter) + '. ' + stripped)
            else:
                # 如果已经有编号，只添加缩进
                found_risk_marker = True
                formatted_lines.append(stripped)
        else:
            # 其他行（如开头段落，包括"尊敬的"）不添加缩进，确保前面没有任何空格
            # 特别处理：如果是以"尊敬的"开头，确保前面绝对没有任何空格
            if stripped.startswith('尊敬的'):
                formatted_lines.append('尊敬的' + stripped[3:])  # 确保"尊敬的"前面没有任何空格
                in_conclusion_section = False
                found_risk_marker = False  # 开头段落，不是风险提示
                risk_item_counter = 0  # 重置计数器
            else:
                # 判断是否应该添加缩进：
                # 1. 如果在结论部分（"首先"、"其次"、"最后"之后），不添加缩进（除非是这些关键词本身）
                # 2. 如果已经遇到【器官名称】标记，且当前行是【器官名称】的后续行（不是新的段落），添加缩进
                # 3. 风险提示的开头段落（在【器官名称】之前）和结尾段落（空行之后）应该顶格显示
                if in_conclusion_section:
                    # 结论部分的其他行，不添加缩进（只有"首先"、"其次"、"最后"有缩进）
                    formatted_lines.append(stripped)
                elif found_risk_marker and risk_item_counter > 0:
                    # 检查上一行是否是【器官名称】行或【器官名称】的后续行
                    # 如果是，说明这是【器官名称】的后续行，应该添加缩进
                    # 如果上一行是空行，说明这是新的段落（结尾段落），应该顶格显示
                    if i > 0 and formatted_lines and formatted_lines[-1] and not formatted_lines[-1].strip() == '':
                        # 上一行不是空行，说明是【器官名称】的后续行，添加缩进
                        formatted_lines.append(stripped)
                    else:
                        # 上一行是空行，说明是新的段落（结尾段落），顶格显示
                        formatted_lines.append(stripped)
                        found_risk_marker = False  # 重置标记，因为已经进入结尾段落
                else:
                    # 风险提示的开头段落（在【器官名称】之前）或其他内容，顶格显示
                    formatted_lines.append(stripped)  # 其他行也确保没有行首空格
    
    text = '\n'.join(formatted_lines)
    
    # 清理多余的连续换行（最多保留两个换行，即一个空行）
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # 最后再次确保"尊敬的"前面绝对没有任何空格（顶格显示）
    # 移除所有类型的空格（全角空格、半角空格、制表符等）
    text = re.sub(r'^[\s\u3000\u00A0]*尊敬的', '尊敬的', text, flags=re.MULTILINE)  # \u3000是全角空格，\u00A0是不间断空格
    text = re.sub(r'^\s*尊敬的', '尊敬的', text, flags=re.MULTILINE)
    # 确保每一行以"尊敬的"开头的都没有行首空格
    lines = text.split('\n')
    final_lines = []
    for line in lines:
        stripped = line.lstrip()  # 移除所有类型的空格
        if stripped.startswith('尊敬的'):
            # 如果这行以"尊敬的"开头，确保顶格（没有任何空格，包括全角空格）
            # 移除"尊敬的"前面的所有字符（包括全角空格\u3000）
            clean_line = '尊敬的' + stripped[3:]
            final_lines.append(clean_line)
        else:
            final_lines.append(line)
    text = '\n'.join(final_lines)
    
    # 最终检查：确保文本开头的"尊敬的"前面绝对没有任何空格
    if text.startswith('尊敬的'):
        pass  # 已经是顶格，不需要处理
    else:
        # 如果开头不是"尊敬的"，检查是否有空格
        text = text.lstrip()
        if not text.startswith('尊敬的'):
            # 如果清理空格后还不是"尊敬的"开头，可能是其他内容，保持原样
            pass
    
    return text


def clean_markdown_formatting(text: str) -> str:
    """
    清理文本中的markdown格式标记和多余字符
    - 去除加粗标记 **text** 或 __text__
    - 去除斜体标记 *text* 或 _text_
    - 去除代码块标记 ``` 和 ```
    - 保留换行符（后续会转换为HTML）
    - 保留文本内容
    """
    if not text:
        return text

    # 去除markdown代码块标记
    text = re.sub(r'```[a-z]*\n?', '', text)
    text = re.sub(r'```', '', text)
    
    # 去除加粗标记 **text** 或 __text__
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)

    # 去除斜体标记 *text* 或 _text_ (但不要误删单个星号)
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)

    # 去除多余的星号、下划线
    text = text.replace('***', '').replace('**', '').replace('*', '')
    text = text.replace('___', '').replace('__', '').replace('_', '')
    
    # 去除多余的空白字符（保留单个空格）
    text = re.sub(r'[ \t]+', ' ', text)
    
    # 去除多余的空行（保留最多一个空行）
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # 去除行首行尾的空白
    lines = text.split('\n')
    lines = [line.strip() for line in lines]
    text = '\n'.join(lines)
    
    # 去除整个文本首尾的空白
    text = text.strip()

    return text


def generate_comprehensive_conclusion_with_llm(patient_data: dict, decision_result: dict, matched_knowledge: list, nodule_type: str = 'breast') -> str:
    """
    使用LLM生成包含决策树8层结果的综合分析结论（支持七种结节类型）

    Args:
        patient_data: 患者数据字典
        decision_result: 决策树处理结果
        matched_knowledge: 匹配的知识库条目
        nodule_type: 结节类型 (breast/lung/thyroid/breast_lung/breast_thyroid/lung_thyroid/triple)

    Returns:
        str: 综合分析结论
    """
    try:
        # ========== 只上传前端填写的字段（不填充默认值） ==========
        EXCLUDED_FIELDS = {'phone', 'id_card', 'patient_id', 'id', 'record_code'}

        # 构建prompt_vars：只添加有值的字段
        prompt_vars = {}

        # ⚠️ 强制添加gender字段（必需字段，不能被过滤）
        if 'gender' in patient_data:
            gender_value = patient_data['gender'] if patient_data['gender'] else '未知'
            prompt_vars['gender'] = gender_value

        for key, value in patient_data.items():
            # 跳过gender（已单独处理）
            if key == 'gender':
                continue
            # 跳过隐私字段
            if key in EXCLUDED_FIELDS:
                continue
            # 只上传有值的字段
            if value is not None and value != '' and value != []:
                prompt_vars[key] = value

        # 添加决策树结果
        prompt_vars.update({
            'risk_level': decision_result.get('风险评估', {}).get('risk_level', '未知'),
            'risk_score': decision_result.get('风险评估', {}).get('risk_score', 0),
            'imaging_category': decision_result.get('影像学评估', {}).get('category', '常规影像'),
            'symptom_count': len(decision_result.get('症状管理', {}).get('recommendations', [])),
            'rhythm_count': len(decision_result.get('节律调节', {}).get('recommendations', [])),
            'lifestyle_count': len(decision_result.get('生活方式干预', {}).get('recommendations', [])),
            'family_management': '有' if decision_result.get('家族史管理') else '无',
            'followup_frequency': decision_result.get('随访规划', {}).get('frequency', '待定'),
            'knowledge_count': min(len(matched_knowledge), 30),
            'knowledge_items': format_knowledge_for_prompt(matched_knowledge[:30])
        })

        # 获取对应结节类型的提示词模板（使用 western_medical 类型，因为 comprehensive 类型不存在）
        try:
            template = get_prompt_template(nodule_type, 'comprehensive')
        except ValueError:
            # 如果 comprehensive 类型不存在，使用 western_medical 类型
            template = get_prompt_template(nodule_type, 'western_medical')
        prompt = format_prompt(template, **prompt_vars)

        # 调用LLM
        print(f"🤖 调用LLM生成{nodule_type}类型的综合分析结论...")
        conclusion = llm_generator._call_llm_api(prompt)

        if conclusion and isinstance(conclusion, str):
            conclusion = conclusion.strip()
            # 清理markdown格式标记
            conclusion = clean_markdown_formatting(conclusion)
            print(f"✅ 综合分析结论生成成功: {conclusion[:50]}...")
            return conclusion
        else:
            raise Exception("LLM未能生成有效的综合分析结论")

    except Exception as e:
        print(f"生成综合结论失败: {str(e)}")
        # 返回基于决策树的默认结论
        return generate_fallback_conclusion(patient_data, decision_result, matched_knowledge)


def generate_imaging_conclusion_with_llm(patient_data: dict, decision_result: dict, matched_knowledge: list, nodule_type: str = 'breast') -> dict:
    """
    使用LLM生成包含决策树8层结果的影像学分析结论（支持七种结节类型）

    Args:
        patient_data: 患者数据字典
        decision_result: 决策树处理结果
        matched_knowledge: 匹配的知识库条目
        nodule_type: 结节类型 (breast/lung/thyroid/breast_lung/breast_thyroid/lung_thyroid/triple)

    Returns:
        dict: {"conclusion": str (400-500字), "risk_warning": str (300字)}
    """
    try:
        # ========== 只上传前端填写的字段（不填充默认值） ==========
        # 排除的隐私字段
        EXCLUDED_FIELDS = {'phone', 'id_card', 'patient_id', 'id', 'record_code'}

        # 构建prompt_vars：只添加有值的字段
        prompt_vars = {}

        print(f"\n[LLM数据] ========== 上传到LLM的字段（只包含有值字段） ==========")
        uploaded_count = 0

        # ⚠️ 强制添加gender字段（必需字段，不能被过滤）
        if 'gender' in patient_data:
            gender_value = patient_data['gender'] if patient_data['gender'] else '未知'
            prompt_vars['gender'] = gender_value
            print(f"  🔴 gender: {gender_value} （必需字段）")
            uploaded_count += 1

        for key, value in patient_data.items():
            # 跳过gender（已单独处理）
            if key == 'gender':
                continue

            # 跳过隐私字段
            if key in EXCLUDED_FIELDS:
                continue

            # 只上传有值的字段（不为None、不为空字符串、不为空列表）
            # 特殊处理：
            # 1. age字段：即使为0也应该传递（0是有效值）
            # 2. 字符串'无'也应该传递（表示明确的无，不是缺失）
            if value is not None and value != '' and value != []:
                prompt_vars[key] = value
                uploaded_count += 1
                # 打印上传的字段（限制打印前30个字符）
                value_str = str(value)[:30] + ('...' if len(str(value)) > 30 else '')
                print(f"  ✅ {key}: {value_str}")

        # 添加知识库（始终需要）
        prompt_vars['knowledge_items'] = format_knowledge_for_prompt(matched_knowledge[:20], focus='imaging')

        print(f"[LLM数据] 共上传 {uploaded_count} 个有值字段")
        print(f"[LLM数据] ==========================================\n")

        # 获取对应结节类型的提示词模板
        template = get_prompt_template(nodule_type, 'imaging')
        prompt = format_prompt(template, **prompt_vars)
        
        # 调试：打印完整数据（可选，通过环境变量控制）
        if os.getenv('DEBUG_LLM_DATA', 'False').lower() == 'true':
            from utils.llm_data_debugger import print_full_llm_data, save_llm_prompt_to_file
            print_full_llm_data(patient_data, prompt_vars, nodule_type, 'imaging')
            save_llm_prompt_to_file(prompt, f"imaging_{nodule_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

        # 调用LLM
        print(f"🤖 调用LLM生成{nodule_type}类型的影像学分析结论...")
        response = llm_generator._call_llm_api(prompt)

        if response and isinstance(response, str):
            # 解析JSON响应
            result = parse_json_response(response)

            # 验证必需字段
            if 'conclusion' not in result or 'risk_warning' not in result:
                raise Exception("LLM响应缺少必需字段")

            # 清理LLM返回的内容，确保"尊敬的"前面没有任何空格
            if 'conclusion' in result and result['conclusion']:
                # 移除"尊敬的"前面的所有空格（包括全角空格、半角空格等）
                result['conclusion'] = re.sub(r'^[\s\u3000\u00A0]*尊敬的', '尊敬的', result['conclusion'])
                result['conclusion'] = result['conclusion'].lstrip()  # 移除开头所有空格
                # 再次确保"尊敬的"前面没有空格
                result['conclusion'] = re.sub(r'^\s*尊敬的', '尊敬的', result['conclusion'])
            
            if 'risk_warning' in result and result['risk_warning']:
                # 同样清理risk_warning
                result['risk_warning'] = result['risk_warning'].lstrip()

            print(f"✅ 影像学分析结论生成成功: conclusion={len(result['conclusion'])}字, risk_warning={len(result['risk_warning'])}字")
            return result
        else:
            raise Exception("LLM未能生成有效的影像学分析结论")

    except Exception as e:
        print(f"❌ 生成影像学结论失败: {str(e)}")
        # 不再使用降级方案，直接抛出异常
        raise Exception(f"LLM 影像学评估失败: {str(e)}")


def format_knowledge_for_prompt(knowledge_items: list, focus: str = None) -> str:
    """
    格式化知识库条目用于LLM提示词（兼容对象和字典）
    
    Args:
        knowledge_items: 知识库条目列表
        focus: 聚焦领域 ('imaging' 表示只关注影像学相关)
    """
    if not knowledge_items:
        return "无相关医学知识"
    
    def get_attr(obj, attr_name, default=None):
        """兼容获取属性值"""
        if isinstance(obj, dict):
            return obj.get(attr_name, default)
        return getattr(obj, attr_name, default)
    
    formatted = []
    for idx, item in enumerate(knowledge_items, 1):
        # 如果指定了聚焦领域，筛选相关知识
        if focus == 'imaging':
            title = get_attr(item, 'title', '')
            if not any(keyword in title for keyword in ['影像', 'BI-RADS', '超声', '弹性', '血流']):
                continue
        
        # 格式化知识库条目
        title = get_attr(item, 'title') or '未命名知识'
        content = get_attr(item, 'content') or ''  # 使用完整内容，不截断
        
        # 添加更多上下文信息
        extra_info = []
        recommendation_level = get_attr(item, 'recommendation_level')
        if recommendation_level:
            extra_info.append(f"推荐等级:{recommendation_level}")
        interventions = get_attr(item, 'interventions')
        if interventions:
            extra_info.append(f"干预措施:{interventions[:50]}")
        
        extra_text = f" [{', '.join(extra_info)}]" if extra_info else ""
        formatted.append(f"{idx}. {title}: {content}{extra_text}")
    
    return '\n'.join(formatted) if formatted else "无相关医学知识"


def generate_fallback_conclusion(patient_data: dict, decision_result: dict, matched_knowledge: list) -> str:
    """生成降级方案的综合分析结论"""
    risk_level = decision_result.get('风险评估', {}).get('risk_level', '未知')
    birads = patient_data.get('birads_level', '未知')
    
    conclusion = f"""根据患者的健康档案和决策树分析，综合评估如下：

患者年龄{patient_data.get('age', '未知')}岁，BI-RADS分级为{birads}类，综合风险评估为{risk_level}。基于决策树8层分析系统的全面评估，包括风险评估、影像学评估、症状管理、节律调节、生活方式干预、家族史管理、检查历史分析和随访规划，匹配了{len(matched_knowledge)}条专业医学知识。

建议定期随访观察，保持健康的生活方式，注意情绪管理和规律作息。如有任何症状变化，请及时就医。"""
    
    return conclusion


def generate_fallback_imaging_conclusion(patient_data: dict, decision_result: dict) -> str:
    """生成降级方案的影像学分析结论"""
    birads = patient_data.get('birads_level', '未知')
    location = patient_data.get('nodule_location', '未知')
    size = patient_data.get('nodule_size', '未知')
    
    conclusion = f"""影像学特征显示：结节位于{location}，大小约{size}，BI-RADS分级为{birads}类。

边界特征{patient_data.get('boundary_features', '未明确')}，内部回声{patient_data.get('internal_echo', '未记录')}，{patient_data.get('blood_flow_signal', 'CDFI未见明显异常血流信号')}。弹性评分{patient_data.get('elasticity_score', '未评估')}分。

建议定期超声随访，监测结节大小和特征变化。根据BI-RADS分级和综合评估，建议3-6个月后复查。"""
    
    return conclusion


def match_knowledge(patient_data: dict) -> list:
    """
    智能匹配知识库（重构版）
    按 source_type 分类精确匹配，避免重复累加
    
    Args:
        patient_data: 患者数据字典，包含年龄、BI-RADS、症状、家族史等信息
        
    Returns:
        匹配的知识库条目列表（已去重）
    """
    matched_items = []
    matched_ids = set()  # 用于去重
    
    # ============================================
    # 1. 年龄匹配（source_type='age_general'）
    # ============================================
    if 'age' in patient_data and patient_data['age']:
        age = patient_data['age']
        age_items = KnowledgeItem.query.filter(
            KnowledgeItem.source_type == 'age_general',
            KnowledgeItem.age_min <= age,
            KnowledgeItem.age_max >= age
        ).all()
        
        for item in age_items:
            if item.id not in matched_ids:
                matched_items.append(item)
                matched_ids.add(item.id)
    
    # 2. BI-RADS分级匹配
    if 'birads_level' in patient_data and patient_data['birads_level']:
        birads = int(patient_data['birads_level'])
        birads_items = KnowledgeItem.query.filter(
            (KnowledgeItem.birads_min.is_(None) | (KnowledgeItem.birads_min <= birads)) &
            (KnowledgeItem.birads_max.is_(None) | (KnowledgeItem.birads_max >= birads))
        ).all()
        matched_items.extend(birads_items)
    
    # 2.1 影像学特征匹配（新增：结节位置）
    if 'nodule_location' in patient_data and patient_data['nodule_location']:
        location = patient_data['nodule_location']
        location_items = KnowledgeItem.query.filter(
            (KnowledgeItem.nodule_location == location) |
            (KnowledgeItem.nodule_location.is_(None))  # NULL表示通用建议
        ).all()
        matched_items.extend(location_items)
    
    # 2.2 影像学特征匹配（新增：结节大小）
    if 'nodule_size' in patient_data and patient_data['nodule_size']:
        size = patient_data['nodule_size']
        size_items = KnowledgeItem.query.filter(
            (KnowledgeItem.nodule_size == size) |
            (KnowledgeItem.nodule_size.is_(None))
        ).all()
        matched_items.extend(size_items)
    
    # 2.3 影像学特征匹配（新增：边界特征）
    if 'boundary_features' in patient_data and patient_data['boundary_features']:
        boundary = patient_data['boundary_features']
        boundary_items = KnowledgeItem.query.filter(
            (KnowledgeItem.boundary_features == boundary) |
            (KnowledgeItem.boundary_features.is_(None))
        ).all()
        matched_items.extend(boundary_items)
    
    # 2.4 影像学特征匹配（新增：内部回声）
    if 'internal_echo' in patient_data and patient_data['internal_echo']:
        echo = patient_data['internal_echo']
        echo_items = KnowledgeItem.query.filter(
            (KnowledgeItem.internal_echo == echo) |
            (KnowledgeItem.internal_echo.is_(None))
        ).all()
        matched_items.extend(echo_items)
    
    # 2.5 影像学特征匹配（新增：血流信号）
    if 'blood_flow_signal' in patient_data and patient_data['blood_flow_signal']:
        blood_flow = patient_data['blood_flow_signal']
        blood_flow_items = KnowledgeItem.query.filter(
            (KnowledgeItem.blood_flow_signal == blood_flow) |
            (KnowledgeItem.blood_flow_signal.is_(None))
        ).all()
        matched_items.extend(blood_flow_items)
    
    # 2.6 影像学特征匹配（新增：弹性评分）
    if 'elasticity_score' in patient_data and patient_data['elasticity_score']:
        elasticity = patient_data['elasticity_score']
        elasticity_items = KnowledgeItem.query.filter(
            (KnowledgeItem.elasticity_score == elasticity) |
            (KnowledgeItem.elasticity_score.is_(None))
        ).all()
        matched_items.extend(elasticity_items)
    
    # 3. 症状匹配（优化版：主症状 + 子类型联合匹配）
    if 'symptoms' in patient_data and patient_data['symptoms']:
        symptoms_list = patient_data['symptoms']
        # 如果是字符串，转为列表
        if isinstance(symptoms_list, str):
            symptoms_list = [s.strip() for s in symptoms_list.split(',')]
        
        # 遍历每个症状，匹配主症状
        for symptom in symptoms_list:
            if symptom and symptom != '无症状':
                # 匹配主症状
                symptom_items = KnowledgeItem.query.filter(KnowledgeItem.symptoms.ilike(f'%{symptom}%')).all()
                matched_items.extend(symptom_items)
                
                # 子类型匹配（根据主症状类型匹配对应的子类型）
                if symptom == '疼痛' and 'pain_type' in patient_data and patient_data['pain_type']:
                    # 疼痛子类型匹配
                    subtype_items = KnowledgeItem.query.filter(
                        (KnowledgeItem.symptoms == symptom) &
                        (KnowledgeItem.symptom_subtype == patient_data['pain_type'])
                    ).all()
                    matched_items.extend(subtype_items)
                
                elif symptom == '乳头溢液' and 'nipple_discharge_type' in patient_data and patient_data['nipple_discharge_type']:
                    # 乳头溢液子类型匹配
                    subtype_items = KnowledgeItem.query.filter(
                        (KnowledgeItem.symptoms == symptom) &
                        (KnowledgeItem.symptom_subtype == patient_data['nipple_discharge_type'])
                    ).all()
                    matched_items.extend(subtype_items)
                
                elif symptom == '皮肤变化' and 'skin_change_type' in patient_data and patient_data['skin_change_type']:
                    # 皮肤变化子类型匹配
                    subtype_items = KnowledgeItem.query.filter(
                        (KnowledgeItem.symptoms == symptom) &
                        (KnowledgeItem.symptom_subtype == patient_data['skin_change_type'])
                    ).all()
                    matched_items.extend(subtype_items)
    
    # 4. 家族史匹配（优化版：精确匹配风险等级）
    if 'family_history' in patient_data and patient_data['family_history']:
        family = patient_data['family_history']
        
        # 提取家族史风险等级
        risk_level = None
        if '无家族史' in family:
            risk_level = '低危'  # 无家族史按低危处理
        elif '低危家族史' in family:
            risk_level = '低危'
        elif '中危家族史' in family:
            risk_level = '中危'
        elif '高危家族史' in family:
            risk_level = '高危'
        
        if risk_level:
            # 同时匹配 risk_level 和 family_history 字段（提高匹配准确性）
            from sqlalchemy import or_
            family_items = KnowledgeItem.query.filter(
                or_(
                    KnowledgeItem.risk_level == risk_level,
                    KnowledgeItem.family_history.ilike(f'%{risk_level}%')
                )
            ).all()
            matched_items.extend(family_items)
    
    # 5. 病程阶段匹配（改进版：同时匹配 course_stage 和 tnm_stage）
    if 'course_stage' in patient_data and patient_data['course_stage']:
        course_stage = patient_data['course_stage']
        tnm_stage = patient_data.get('tnm_stage')
        
        if tnm_stage:
            # 同时匹配病程阶段和TNM分期（精确匹配）
            tnm_stage_int = int(tnm_stage)  # 转为整数
            stage_items = KnowledgeItem.query.filter(
                (KnowledgeItem.course_stage == course_stage) &
                (KnowledgeItem.tnm_stage == tnm_stage_int)
            ).all()
        else:
            # 如果没有TNM分期，只匹配病程阶段
            stage_items = KnowledgeItem.query.filter(KnowledgeItem.course_stage == course_stage).all()
        
        matched_items.extend(stage_items)
    
    # 6. 生物节律匹配（优化版：rhythm_type + cycle_phase 联合匹配）
    if 'rhythm_type' in patient_data and patient_data['rhythm_type']:
        rhythm_type = patient_data['rhythm_type']
        cycle_phase = patient_data.get('cycle_phase')
        
        if cycle_phase:
            # 同时匹配节律类型和周期阶段（精确匹配）
            rhythm_items = KnowledgeItem.query.filter(
                (KnowledgeItem.rhythm_type == rhythm_type) &
                (KnowledgeItem.cycle_phase == cycle_phase)
            ).all()
        else:
            # 如果没有周期阶段，只匹配节律类型
            rhythm_items = KnowledgeItem.query.filter(KnowledgeItem.rhythm_type == rhythm_type).all()
        
        matched_items.extend(rhythm_items)
    
    # 7. 睡眠管理匹配（优化版：sleep_quality + sleep_condition 联合匹配）
    if 'sleep_quality' in patient_data and patient_data['sleep_quality']:
        sleep_quality = patient_data['sleep_quality']
        sleep_condition = patient_data.get('sleep_condition')
        
        if sleep_condition:
            # 同时匹配睡眠质量和睡眠状况（精确匹配）
            sleep_items = KnowledgeItem.query.filter(
                (KnowledgeItem.sleep_quality == sleep_quality) &
                (KnowledgeItem.sleep_condition == sleep_condition)
            ).all()
        else:
            # 如果没有特殊状况，只匹配睡眠质量
            sleep_items = KnowledgeItem.query.filter(KnowledgeItem.sleep_quality == sleep_quality).all()
        
        matched_items.extend(sleep_items)
    
    # 8. 检查历史匹配（优化版：exam_history_type + exam_special_situation + exam_subcategory）
    if 'exam_history_type' in patient_data and patient_data['exam_history_type']:
        exam_type = patient_data['exam_history_type']
        exam_special = patient_data.get('exam_special_situation')
        exam_sub = patient_data.get('exam_subcategory')
        
        # 优先级1：如果有特殊情况和子分类，进行精确匹配
        if exam_special and exam_sub:
            exam_items = KnowledgeItem.query.filter(
                (KnowledgeItem.exam_history_type == exam_special) &
                (KnowledgeItem.exam_subcategory == exam_sub)
            ).all()
        # 优先级2：如果只有特殊情况，匹配该类型的所有建议
        elif exam_special:
            exam_items = KnowledgeItem.query.filter(KnowledgeItem.exam_history_type == exam_special).all()
        # 优先级3：只匹配基础检查类型（通用管理建议）
        else:
            exam_items = KnowledgeItem.query.filter(KnowledgeItem.exam_history_type == exam_type).all()
        
        matched_items.extend(exam_items)
    
    # 9. 乳腺疾病史匹配（disease_history）
    # 患者表字段：breast_disease_history（逗号分隔的字符串，如："乳腺增生-普通增生,乳腺囊肿-单发囊肿"）
    if 'breast_disease_history' in patient_data and patient_data['breast_disease_history']:
        breast_history = patient_data['breast_disease_history']
        
        # 解析逗号分隔的疾病史
        if isinstance(breast_history, str):
            disease_entries = [entry.strip() for entry in breast_history.split(',')]
        else:
            disease_entries = []
        
        # 遍历每个疾病条目，解析"疾病类型-子类型"格式
        for entry in disease_entries:
            if '-' in entry:
                parts = entry.split('-', 1)  # 分割成两部分：疾病类型和子类型
                disease_type = parts[0].strip()
                disease_subtype = parts[1].strip() if len(parts) > 1 else None
                
                # 精确匹配：疾病类型 + 子类型
                if disease_type and disease_subtype:
                    disease_items = KnowledgeItem.query.filter(
                        (KnowledgeItem.source_type == 'disease_history') &
                        (KnowledgeItem.disease_type == disease_type) &
                        (KnowledgeItem.disease_subtype == disease_subtype)
                    ).all()
                    matched_items.extend(disease_items)
            else:
                # 没有子类型，只匹配疾病类型
                disease_type = entry.strip()
                if disease_type:
                    disease_items = KnowledgeItem.query.filter(
                        (KnowledgeItem.source_type == 'disease_history') &
                        (KnowledgeItem.disease_type == disease_type)
                    ).all()
                    matched_items.extend(disease_items)
    
    # 10. 家族遗传史匹配（family_genetic_history）
    # 患者表字段：family_genetic_history（单选字符串，如："一级亲属-BRCA1突变" 或 "二级亲属"）
    if 'family_genetic_history' in patient_data and patient_data['family_genetic_history']:
        family_history = patient_data['family_genetic_history']
        
        # 解析家族史格式："亲属类型" 或 "亲属类型-基因突变"
        if '-' in family_history:
            parts = family_history.split('-', 1)
            relative_type = parts[0].strip()
            genetic_mutation = parts[1].strip() if len(parts) > 1 else None
            
            # 优先匹配基因突变信息
            if genetic_mutation:
                mutation_items = KnowledgeItem.query.filter(
                    (KnowledgeItem.source_type == 'family_genetic_history') &
                    (KnowledgeItem.genetic_mutation.ilike(f'%{genetic_mutation}%'))
                ).all()
                matched_items.extend(mutation_items)
            
            # 同时匹配亲属类型
            relative_items = KnowledgeItem.query.filter(
                (KnowledgeItem.source_type == 'family_genetic_history') &
                (KnowledgeItem.family_relative_type.ilike(f'%{relative_type}%'))
            ).all()
            matched_items.extend(relative_items)
        else:
            # 只有亲属类型，直接匹配
            relative_type = family_history.strip()
            family_items = KnowledgeItem.query.filter(
                (KnowledgeItem.source_type == 'family_genetic_history') &
                (KnowledgeItem.family_relative_type.ilike(f'%{relative_type}%'))
            ).all()
            matched_items.extend(family_items)
    
    # 11. 现病史与检查史匹配（current_medical_history）
    # 11.1 症状匹配
    if 'symptoms' in patient_data and patient_data['symptoms']:
        symptoms_list = patient_data['symptoms']
        if isinstance(symptoms_list, str):
            symptoms_list = [s.strip() for s in symptoms_list.split(',')]
        
        for symptom in symptoms_list:
            if symptom and symptom != '无症状':
                current_items = KnowledgeItem.query.filter(
                    (KnowledgeItem.source_type == 'current_medical_history') &
                    (KnowledgeItem.symptoms.ilike(f'%{symptom}%'))
                ).all()
                matched_items.extend(current_items)
    
    # 11.2 既往活检史匹配
    if 'previous_biopsy_history' in patient_data and patient_data['previous_biopsy_history']:
        biopsy_history = patient_data['previous_biopsy_history']
        
        # 解析逗号分隔的活检史
        if isinstance(biopsy_history, str):
            biopsy_entries = [entry.strip() for entry in biopsy_history.split(',') if entry.strip()]
        else:
            biopsy_entries = []
        
        # 遍历每个活检史条目，匹配知识库
        for biopsy_type in biopsy_entries:
            if biopsy_type:
                biopsy_items = KnowledgeItem.query.filter(
                    (KnowledgeItem.source_type == 'current_medical_history') &
                    (KnowledgeItem.previous_biopsy_result.ilike(f'%{biopsy_type}%'))
                ).all()
                matched_items.extend(biopsy_items)
    
    # 12. 其他风险因素匹配（risk_factors）改为档位匹配
    # 12.1 避孕药风险档位
    if 'contraceptive_risk_level' in patient_data and patient_data['contraceptive_risk_level']:
        contraceptive_level = patient_data['contraceptive_risk_level']
        
        # 匹配对应档位的知识库条目
        contraceptive_items = KnowledgeItem.query.filter(
            (KnowledgeItem.source_type == 'risk_factors') &
            (KnowledgeItem.disease_type == '长期避孕药使用') &
            (KnowledgeItem.disease_subtype.ilike(f'%{contraceptive_level}%'))
        ).all()
        matched_items.extend(contraceptive_items)
    
    # 12.2 吸烟风险档位
    if 'smoking_risk_level' in patient_data and patient_data['smoking_risk_level']:
        smoking_level = patient_data['smoking_risk_level']
        
        # 匹配对应档位的知识库条目
        smoking_items = KnowledgeItem.query.filter(
            (KnowledgeItem.source_type == 'risk_factors') &
            (KnowledgeItem.disease_type == '吸烟史') &
            (KnowledgeItem.disease_subtype.ilike(f'%{smoking_level}%'))
        ).all()
        matched_items.extend(smoking_items)
    
    # 12.3 糖尿病控制档位
    if 'diabetes_control_level' in patient_data and patient_data['diabetes_control_level']:
        diabetes_level = patient_data['diabetes_control_level']
        
        # 匹配对应档位的知识库条目
        diabetes_items = KnowledgeItem.query.filter(
            (KnowledgeItem.source_type == 'risk_factors') &
            (KnowledgeItem.disease_type == '糖尿病') &
            (KnowledgeItem.disease_subtype.ilike(f'%{diabetes_level}%'))
        ).all()
        matched_items.extend(diabetes_items)
    
    # 去重并按优先级排序
    unique_items = list({item.id: item for item in matched_items}.values())
    unique_items.sort(key=lambda x: (x.priority if x.priority else 0, x.id), reverse=True)
    
    print(f"\n📊 总匹配知识库: {len(unique_items)} 条（已去重）")
    
    # 返回字典格式，便于使用
    return [item.to_dict() for item in unique_items]


def match_knowledge_v2_by_source_type(patient_data: dict) -> list:
    """
    智能匹配知识库（重构版）- 按 source_type 分类精确匹配
    避免重复累加，每个类别独立查询
    
    Args:
        patient_data: 患者数据字典
        
    Returns:
        匹配的知识库条目列表（字典格式，已去重）
    """
    from sqlalchemy import or_, and_
    
    matched_items = []
    matched_ids = set()  # 用于去重
    
    def add_items(items, category_name=""):
        """添加知识库条目（自动去重）"""
        count = 0
        for item in items:
            if item.id not in matched_ids:
                matched_items.append(item)
                matched_ids.add(item.id)
                count += 1
        if count > 0:
            print(f"  ✅ {category_name}: {count} 条")
    
    print("\n" + "="*60)
    print("📝 开始按类别匹配知识库...")
    print("="*60)
    
    # ============================================
    # 1. 年龄相关建议（source_type='age_general'）
    # ============================================
    if 'age' in patient_data and patient_data['age']:
        age = patient_data['age']
        age_items = KnowledgeItem.query.filter(
            KnowledgeItem.source_type == 'age_general',
            KnowledgeItem.age_min <= age,
            KnowledgeItem.age_max >= age
        ).all()
        add_items(age_items, f"年龄匹配（{age}岁）")
    
    # ============================================
    # 2. 病程时间轴（source_type='timeline'）
    # 优先精确匹配（年龄+病程+TNM），匹配不到则降级（年龄+病程）
    # ============================================
    if 'course_stage' in patient_data and patient_data['course_stage']:
        age = patient_data.get('age')
        tnm_stage = patient_data.get('tnm_stage')
        course_stage = patient_data['course_stage']
        
        if age and tnm_stage:
            # 策略1：优先精确匹配（年龄 + 病程 + TNM分期）
            timeline_items = KnowledgeItem.query.filter(
                KnowledgeItem.source_type == 'timeline',
                KnowledgeItem.course_stage == course_stage,
                KnowledgeItem.age_min <= age,
                KnowledgeItem.age_max >= age,
                KnowledgeItem.tnm_stage == tnm_stage
            ).all()
            
            if timeline_items:
                # 找到精确匹配（知识库完整）
                add_items(timeline_items, f"时间轴精确匹配（{course_stage} + {age}岁 + TNM{tnm_stage}期）")
            else:
                # 知识库不完整，降级到通用匹配（年龄 + 病程）
                timeline_items = KnowledgeItem.query.filter(
                    KnowledgeItem.source_type == 'timeline',
                    KnowledgeItem.course_stage == course_stage,
                    KnowledgeItem.age_min <= age,
                    KnowledgeItem.age_max >= age
                ).all()
                add_items(timeline_items, f"时间轴通用匹配（{course_stage} + {age}岁，无TNM{tnm_stage}期精确记录）")
        
        elif age:
            # 策略2：患者没有TNM分期，只用年龄+病程匹配
            timeline_items = KnowledgeItem.query.filter(
                KnowledgeItem.source_type == 'timeline',
                KnowledgeItem.course_stage == course_stage,
                KnowledgeItem.age_min <= age,
                KnowledgeItem.age_max >= age
            ).all()
            add_items(timeline_items, f"时间轴通用匹配（{course_stage} + {age}岁）")
        
        else:
            # 策略3：只按病程阶段匹配（无年龄）
            timeline_items = KnowledgeItem.query.filter(
                KnowledgeItem.source_type == 'timeline',
                KnowledgeItem.course_stage == course_stage
            ).all()
            add_items(timeline_items, f"时间轴匹配（{course_stage}）")
    
    # ============================================
    # 3. 症状管理（source_type='symptoms'）
    # ============================================
    if 'symptoms' in patient_data and patient_data['symptoms']:
        symptoms_data = patient_data['symptoms']
        
        # 兼容字符串和列表两种格式
        if isinstance(symptoms_data, str):
            if symptoms_data and symptoms_data != '无症状':
                symptoms_list = [s.strip() for s in symptoms_data.split(',')]
            else:
                symptoms_list = []
        elif isinstance(symptoms_data, list):
            symptoms_list = [s for s in symptoms_data if s and s != '无症状']
        else:
            symptoms_list = []
        
        for symptom in symptoms_list:
            symptom_items = KnowledgeItem.query.filter(
                KnowledgeItem.source_type == 'symptoms',
                KnowledgeItem.symptoms.like(f'%{symptom}%')
            ).all()
            add_items(symptom_items, f"症状匹配（{symptom}）")
    
    # ============================================
    # 4. 影像学特征（source_type='medical_imaging'）
    # ============================================
    imaging_conditions = []
    
    # BI-RADS
    if 'birads_level' in patient_data and patient_data['birads_level']:
        birads = int(patient_data['birads_level'])
        imaging_conditions.append(
            and_(
                KnowledgeItem.birads_min <= birads,
                KnowledgeItem.birads_max >= birads
            )
        )
    
    # 结节位置
    if 'nodule_location' in patient_data and patient_data['nodule_location']:
        imaging_conditions.append(
            KnowledgeItem.nodule_location == patient_data['nodule_location']
        )
    
    # 结节大小
    if 'nodule_size' in patient_data and patient_data['nodule_size']:
        imaging_conditions.append(
            KnowledgeItem.nodule_size == patient_data['nodule_size']
        )
    
    # 边界特征
    if 'boundary_features' in patient_data and patient_data['boundary_features']:
        imaging_conditions.append(
            KnowledgeItem.boundary_features == patient_data['boundary_features']
        )
    
    # 内部回声
    if 'internal_echo' in patient_data and patient_data['internal_echo']:
        imaging_conditions.append(
            KnowledgeItem.internal_echo == patient_data['internal_echo']
        )
    
    # 血流信号
    if 'blood_flow_signal' in patient_data and patient_data['blood_flow_signal']:
        imaging_conditions.append(
            KnowledgeItem.blood_flow_signal == patient_data['blood_flow_signal']
        )
    
    # 弹性评分
    if 'elasticity_score' in patient_data and patient_data['elasticity_score']:
        imaging_conditions.append(
            KnowledgeItem.elasticity_score == patient_data['elasticity_score']
        )
    
    if imaging_conditions:
        imaging_items = KnowledgeItem.query.filter(
            KnowledgeItem.source_type == 'medical_imaging',
            or_(*imaging_conditions)
        ).all()
        add_items(imaging_items, "影像学特征")
    
    # ============================================
    # 5. 家族史管理（source_type='family_history'）
    # 根据风险等级关键词匹配
    # ============================================
    if 'family_history' in patient_data and patient_data['family_history']:
        family = patient_data['family_history']
        
        # 提取风险等级关键词
        if '无家族史' in family:
            # 无家族史：只匹配"无家族史"相关
            family_items = KnowledgeItem.query.filter(
                KnowledgeItem.source_type == 'family_history',
                KnowledgeItem.title.like('%无家族史%')
            ).all()
            add_items(family_items, f"家族史（无家族史）")
        
        elif '高危家族史' in family or 'BRCA' in family:
            # 高危家族史：匹配所有"高危"相关（包括基因检测、干预、卵巢防控等）
            family_items = KnowledgeItem.query.filter(
                KnowledgeItem.source_type == 'family_history',
                or_(
                    KnowledgeItem.title.like('%高危%'),
                    KnowledgeItem.title.like('%BRCA%'),
                    KnowledgeItem.title.like('%PALB2%'),
                    KnowledgeItem.title.like('%TP53%'),
                    KnowledgeItem.title.like('%卵巢癌%'),
                    KnowledgeItem.title.like('%红色警报%')
                )
            ).all()
            add_items(family_items, f"家族史（高危）")
        
        elif '中危家族史' in family:
            # 中危家族史：匹配"中危"相关
            family_items = KnowledgeItem.query.filter(
                KnowledgeItem.source_type == 'family_history',
                or_(
                    KnowledgeItem.title.like('%中危%'),
                    KnowledgeItem.title.like('%基因检测%')  # 中危也需要基因检测建议
                )
            ).all()
            add_items(family_items, f"家族史（中危）")
        
        elif '低危家族史' in family:
            # 低危家族史：匹配"低危"相关
            family_items = KnowledgeItem.query.filter(
                KnowledgeItem.source_type == 'family_history',
                KnowledgeItem.title.like('%低危%')
            ).all()
            add_items(family_items, f"家族史（低危）")
        
        else:
            # 无法识别风险等级，匹配所有（兜底策略）
            family_items = KnowledgeItem.query.filter(
                KnowledgeItem.source_type == 'family_history'
            ).all()
            add_items(family_items, f"家族史（通用匹配）")
    
    # ============================================
    # 6. 生物节律调节（source_type='rhythm'）
    # 按 rhythm_type + cycle_phase + age 匹配（含"通用"）
    # ============================================
    if 'rhythm_type' in patient_data and patient_data['rhythm_type']:
        age = patient_data.get('age')
        rhythm_type = patient_data['rhythm_type']
        cycle_phase = patient_data.get('cycle_phase')
        
        if age and cycle_phase:
            # 策略：匹配年龄段+周期阶段，同时包含"通用"建议
            rhythm_items = KnowledgeItem.query.filter(
                KnowledgeItem.source_type == 'rhythm',
                KnowledgeItem.rhythm_type == rhythm_type,
                KnowledgeItem.cycle_phase == cycle_phase,
                or_(
                    and_(
                        KnowledgeItem.age_min <= age,
                        KnowledgeItem.age_max >= age
                    ),
                    KnowledgeItem.title.like('%通用%')  # 同时匹配"通用"建议
                )
            ).all()
            add_items(rhythm_items, f"生物节律（{rhythm_type}-{cycle_phase}，{age}岁）")
        
        elif cycle_phase:
            # 没有年龄，只按周期阶段匹配
            rhythm_items = KnowledgeItem.query.filter(
                KnowledgeItem.source_type == 'rhythm',
                KnowledgeItem.rhythm_type == rhythm_type,
                KnowledgeItem.cycle_phase == cycle_phase
            ).all()
            add_items(rhythm_items, f"生物节律（{rhythm_type}-{cycle_phase}）")
        
        else:
            # 只有rhythm_type，匹配所有该类型
            rhythm_items = KnowledgeItem.query.filter(
                KnowledgeItem.source_type == 'rhythm',
                KnowledgeItem.rhythm_type == rhythm_type
            ).all()
            add_items(rhythm_items, f"生物节律（{rhythm_type}）")
    
    # ============================================
    # 7. 睡眠管理（source_type='sleep'）
    # 按 age + sleep_condition 精确匹配，LIMIT 1
    # ============================================
    if 'sleep_condition' in patient_data and patient_data['sleep_condition']:
        age = patient_data.get('age')
        sleep_condition = patient_data['sleep_condition']
        
        if age:
            # 精确匹配年龄段+睡眠状况，只取1条
            sleep_items = KnowledgeItem.query.filter(
                KnowledgeItem.source_type == 'sleep',
                KnowledgeItem.age_min <= age,
                KnowledgeItem.age_max >= age,
                KnowledgeItem.sleep_condition == sleep_condition
            ).limit(1).all()
            add_items(sleep_items, f"睡眠管理（{age}岁-{sleep_condition}）")
        else:
            # 只有睡眠状况，没有年龄
            sleep_items = KnowledgeItem.query.filter(
                KnowledgeItem.source_type == 'sleep',
                KnowledgeItem.sleep_condition == sleep_condition
            ).limit(1).all()
            add_items(sleep_items, f"睡眠管理（{sleep_condition}）")
    
    # ============================================
    # 8. 检查历史管理（source_type='exam_history'）
    # 优先匹配特殊情况，否则匹配基础检查类型
    # ============================================
    exam_special = patient_data.get('exam_special_situation')
    exam_subcategory = patient_data.get('exam_subcategory')
    exam_type = patient_data.get('exam_history_type')
    
    if exam_special and exam_subcategory:
        # 策略1：优先匹配特殊情况+子分类
        # 提取关键词（去除括号内容）
        subcategory_keyword = exam_subcategory.split('（')[0].strip()
        
        exam_items = KnowledgeItem.query.filter(
            KnowledgeItem.source_type == 'exam_history',
            KnowledgeItem.title.like(f'%{exam_special}%'),
            KnowledgeItem.title.like(f'%{subcategory_keyword}%')
        ).all()
        add_items(exam_items, f"检查历史（{exam_special}-{subcategory_keyword}）")
    
    elif exam_type:
        # 策略2：匹配基础检查类型
        exam_items = KnowledgeItem.query.filter(
            KnowledgeItem.source_type == 'exam_history',
            KnowledgeItem.title.like(f'%{exam_type}%')
        ).all()
        add_items(exam_items, f"检查历史（{exam_type}）")
    
    # ============================================
    # 9. 疾病史管理（source_type='disease_history'）
    # 按疾病类型和子类型精确匹配
    # ============================================
    if 'breast_disease_history' in patient_data and patient_data['breast_disease_history']:
        disease_history = patient_data['breast_disease_history']
        
        # 支持字符串或列表格式
        if isinstance(disease_history, str):
            disease_list = [disease_history.strip()]
        else:
            disease_list = disease_history if isinstance(disease_history, list) else []
        
        for disease in disease_list:
            if not disease or disease == '无':
                continue
            
            # 方法1：尝试从标题中匹配疾病类型和子类型
            # 标题格式："乳腺疾病史-增生-普通增生"
            disease_items = KnowledgeItem.query.filter(
                KnowledgeItem.source_type == 'disease_history',
                KnowledgeItem.title.like(f'%{disease}%')
            ).all()
            add_items(disease_items, f"疾病史匹配（{disease}）")
    
    # ============================================
    # 10. 家族遗传史（source_type='family_genetic_history'）
    # 按亲属类型和基因突变类型匹配
    # ============================================
    family_genetic = patient_data.get('family_genetic_history', '')
    genetic_mutation = patient_data.get('genetic_mutation', '')
    
    if family_genetic:
        # 优先匹配基因突变
        if genetic_mutation and genetic_mutation != '无' and genetic_mutation != '未检测':
            mutation_items = KnowledgeItem.query.filter(
                KnowledgeItem.source_type == 'family_genetic_history',
                KnowledgeItem.title.like(f'%{genetic_mutation}%')
            ).all()
            add_items(mutation_items, f"家族遗传史-基因突变（{genetic_mutation}）")
        
        # 按亲属类型匹配（一级/二级亲属）
        if '一级' in family_genetic or '母亲' in family_genetic or '姐妹' in family_genetic or '女儿' in family_genetic:
            relative_items = KnowledgeItem.query.filter(
                KnowledgeItem.source_type == 'family_genetic_history',
                KnowledgeItem.title.like('%一级亲属%')
            ).all()
            add_items(relative_items, "家族遗传史（一级亲属）")
        elif '二级' in family_genetic or '姑姑' in family_genetic or '姨妈' in family_genetic or '祖母' in family_genetic:
            relative_items = KnowledgeItem.query.filter(
                KnowledgeItem.source_type == 'family_genetic_history',
                KnowledgeItem.title.like('%二级亲属%')
            ).all()
            add_items(relative_items, "家族遗传史（二级亲属）")
        else:
            # 通用匹配
            genetic_items = KnowledgeItem.query.filter(
                KnowledgeItem.source_type == 'family_genetic_history',
                KnowledgeItem.title.like(f'%{family_genetic}%')
            ).all()
            add_items(genetic_items, f"家族遗传史（{family_genetic}）")
    
    # ============================================
    # 11. 现病史管理（source_type='current_medical_history'）
    # 按症状和活检结果匹配
    # ============================================
    current_symptoms = patient_data.get('current_symptoms', '')
    biopsy_result = patient_data.get('previous_biopsy_result', '')
    
    if current_symptoms:
        # 支持字符串或列表格式
        if isinstance(current_symptoms, str):
            symptoms_list = [s.strip() for s in current_symptoms.split(',') if s.strip()]
        else:
            symptoms_list = current_symptoms if isinstance(current_symptoms, list) else []
        
        for symptom in symptoms_list:
            if symptom and symptom != '无症状':
                current_items = KnowledgeItem.query.filter(
                    KnowledgeItem.source_type == 'current_medical_history',
                    KnowledgeItem.symptoms.like(f'%{symptom}%')
                ).all()
                add_items(current_items, f"现病史-症状（{symptom}）")
    
    # 匹配活检结果
    if biopsy_result and biopsy_result != '无' and biopsy_result != '未做':
        biopsy_items = KnowledgeItem.query.filter(
            KnowledgeItem.source_type == 'current_medical_history',
            KnowledgeItem.title.like(f'%{biopsy_result}%')
        ).all()
        add_items(biopsy_items, f"现病史-活检（{biopsy_result}）")
    
    # ============================================
    # 12. 风险因素评估（source_type='risk_factors'）
    # 按避孕药、吸烟、糖尿病等风险因素匹配
    # ============================================
    contraceptive_years = patient_data.get('contraceptive_years', 0)
    smoking_years = patient_data.get('smoking_years', 0)
    smoking_daily = patient_data.get('smoking_daily_amount', 0)
    hba1c = patient_data.get('hba1c', 0)
    diabetes = patient_data.get('diabetes', '')
    
    # 匹配长期避孕药使用
    if contraceptive_years and contraceptive_years > 0:
        if contraceptive_years >= 10:
            contraceptive_level = '>10年'
        elif contraceptive_years >= 5:
            contraceptive_level = '5-10年'
        else:
            contraceptive_level = '<5年'
        
        contraceptive_items = KnowledgeItem.query.filter(
            KnowledgeItem.source_type == 'risk_factors',
            KnowledgeItem.title.like(f'%避孕药%{contraceptive_level}%')
        ).all()
        add_items(contraceptive_items, f"风险因素-避孕药（{contraceptive_level}）")
    
    # 匹配吸烟史（计算包年数：每日包数×吸烟年数）
    if smoking_years and smoking_years > 0:
        pack_years = (smoking_daily / 20) * smoking_years  # 20支/包
        
        if pack_years >= 20:
            smoking_level = '重度'
        elif pack_years >= 10:
            smoking_level = '中度'
        else:
            smoking_level = '轻度'
        
        smoking_items = KnowledgeItem.query.filter(
            KnowledgeItem.source_type == 'risk_factors',
            KnowledgeItem.title.like(f'%吸烟%{smoking_level}%')
        ).all()
        add_items(smoking_items, f"风险因素-吸烟（{smoking_level}，{pack_years:.1f}包年）")
    
    # 匹配糖尿病
    if diabetes and diabetes != '无':
        if hba1c:
            if hba1c <= 7.0:
                diabetes_level = '控制良好'
            elif hba1c <= 9.0:
                diabetes_level = '控制欠佳'
            else:
                diabetes_level = '控制不良'
        else:
            diabetes_level = '控制良好'  # 默认
        
        diabetes_items = KnowledgeItem.query.filter(
            KnowledgeItem.source_type == 'risk_factors',
            KnowledgeItem.title.like(f'%糖尿病%{diabetes_level}%')
        ).all()
        add_items(diabetes_items, f"风险因素-糖尿病（{diabetes_level}）")
    
    # ============================================
    # 13. 结论与预警（source_type='conclusion_and_warning'）
    # 按综合风险等级匹配（低危/中危/高危）
    # ============================================
    comprehensive_risk = patient_data.get('comprehensive_risk_level', '')
    
    if comprehensive_risk:
        # 按风险等级精确匹配
        conclusion_items = KnowledgeItem.query.filter(
            KnowledgeItem.source_type == 'conclusion_and_warning',
            KnowledgeItem.risk_level == comprehensive_risk
        ).all()
        add_items(conclusion_items, f"结论与预警（{comprehensive_risk}）")
    else:
        # 如果没有明确风险等级，尝试通过其他信息推断
        # 根据BI-RADS分级推断
        birads = patient_data.get('birads_category', 0)
        
        if birads >= 4:
            risk_level = '高危'
        elif birads == 3:
            risk_level = '中危'
        else:
            risk_level = '低危'
        
        conclusion_items = KnowledgeItem.query.filter(
            KnowledgeItem.source_type == 'conclusion_and_warning',
            KnowledgeItem.risk_level == risk_level
        ).all()
        add_items(conclusion_items, f"结论与预警（推断：{risk_level}）")
    
    # 按优先级排序
    matched_items.sort(key=lambda x: (x.priority if x.priority else 0, x.id), reverse=True)
    
    print("="*60)
    print(f"📊 总匹配知识库: {len(matched_items)} 条（已去重）")
    print("="*60 + "\n")
    
    # 返回字典格式
    return [item.to_dict() for item in matched_items]


def group_knowledge_by_source_type(matched_knowledge: list) -> dict:
    """
    按source_type分组知识库
    
    Args:
        matched_knowledge: 匹配到的知识库列表（dict格式）
        
    Returns:
        按source_type分组的字典 {source_type: [knowledge_items]}
    """
    grouped = {}
    for item in matched_knowledge:
        source_type = item.get('source_type', 'other')
        if source_type not in grouped:
            grouped[source_type] = []
        grouped[source_type].append(item)
    
    return grouped


def generate_recommendation_for_category(source_type: str, knowledge_list: list, patient_data: dict, nodule_type: str = None) -> str:
    """
    为单个类别生成建议
    
    Args:
        source_type: 知识库类型（age_general, symptoms等）
        knowledge_list: 该类别的知识库列表
        patient_data: 患者数据
        
    Returns:
        生成的建议文本
    """
    # 类别名称映射
    category_names = {
        'age_general': '年龄相关建议',
        'timeline': '病程时间轴建议',
        'symptoms': '症状管理',
        'medical_imaging': '影像学建议',
        'family_history': '家族史管理',
        'rhythm': '生物节律调节',
        'exam_history': '检查史管理',
        'sleep': '睡眠管理',
        'disease_history': '疾病史管理',
        'family_genetic_history': '遗传史管理',
        'current_medical_history': '当前病史管理',
        'risk_factors': '风险因素评估',
        'conclusion_and_warning': '结论与预警'
    }
    
    category_name = category_names.get(source_type, '健康管理')
    
    try:
        # 根据结节类型确定角色和分级系统
        nodule_type = nodule_type or patient_data.get('nodule_type', 'breast')
        type_config = {
            'breast': {'role': '乳腺健康管理师', 'rads_name': 'BI-RADS', 'rads_field': 'birads_level'},
            'lung': {'role': '肺部健康管理师', 'rads_name': 'Lung-RADS', 'rads_field': 'lung_rads_level'},
            'thyroid': {'role': '甲状腺健康管理师', 'rads_name': 'TI-RADS', 'rads_field': 'tirads_level'},
            'breast_lung': {'role': '多器官健康管理师', 'rads_name': 'BI-RADS/Lung-RADS', 'rads_field': 'birads_level'},
            'breast_thyroid': {'role': '多器官健康管理师', 'rads_name': 'BI-RADS/TI-RADS', 'rads_field': 'birads_level'},
            'lung_thyroid': {'role': '多器官健康管理师', 'rads_name': 'Lung-RADS/TI-RADS', 'rads_field': 'lung_rads_level'},
            'triple': {'role': '全科健康管理师', 'rads_name': 'BI-RADS/Lung-RADS/TI-RADS', 'rads_field': 'birads_level'}
        }
        config = type_config.get(nodule_type, type_config['breast'])
        role_name = config['role']
        rads_name = config['rads_name']
        rads_field = config['rads_field']
        
        # 获取RADS分级
        rads_level = patient_data.get(rads_field, '未知') or patient_data.get('birads_level', '未知') or patient_data.get('lung_rads_level', '未知') or patient_data.get('tirads_level', '未知')
        
        # 判断是否为高优先级类别（需要突出重点）
        high_priority_categories = ['conclusion_and_warning', 'risk_factors', 'medical_imaging', 'symptoms']
        is_high_priority = source_type in high_priority_categories
        
        # 判断是否为高风险情况（需要特别强调）
        is_high_risk = False
        if rads_level:
            # 检查是否为高风险分级
            high_risk_patterns = ['4', '4A', '4B', '4C', '4X', '5', '6']
            if any(pattern in str(rads_level) for pattern in high_risk_patterns):
                is_high_risk = True
        
        priority_instruction = ""
        if is_high_priority:
            risk_emphasis = ""
            if is_high_risk:
                risk_emphasis = f"\n   - **特别强调**：患者当前{rads_name}分级为{rads_level}，属于高风险情况，必须明确强调复查的紧迫性和重要性"
            priority_instruction = f"""
7. **突出重点**（重要！）：
   - 使用"特别重要"、"首要"、"必须"、"务必"等强调词汇突出最关键的建议
   - 将最紧急、最重要的建议放在开头{risk_emphasis}
   - 对于高风险情况（如{rads_name} 4级及以上），要明确强调复查的紧迫性
   - 使用"⚠️"或"重要提醒"等标记突出关键信息
"""
        
        # 构建患者信息部分（根据结节类型调整字段）
        patient_info_lines = [
            f"- 年龄：{patient_data.get('age', '未知')}岁",
            f"- {rads_name}分级：{rads_level}级" if rads_level != '未知' else f"- {rads_name}分级：未知",
            f"- 症状：{patient_data.get('symptoms', '无')}",
            f"- 家族史：{patient_data.get('family_history', '无')}",
        ]
        # 根据结节类型添加结节大小
        if nodule_type == 'breast':
            patient_info_lines.append(f"- 结节大小：{patient_data.get('nodule_size', '未知')}")
        elif nodule_type == 'lung':
            patient_info_lines.append(f"- 结节大小：{patient_data.get('lung_nodule_size', patient_data.get('nodule_size', '未知'))}")
        elif nodule_type == 'thyroid':
            patient_info_lines.append(f"- 结节大小：{patient_data.get('thyroid_nodule_size', patient_data.get('nodule_size', '未知'))}")
        
        patient_info = "\n".join(patient_info_lines)
        
        # 构建示例（根据优先级和风险调整）
        if is_high_priority and is_high_risk:
            example = f"⚠️ 特别重要：根据您{patient_data.get('age', '46')}岁的年龄和{rads_name} {rads_level}级分级，建议每3个月复查，这是当前最优先的健康管理任务。"
        elif is_high_priority:
            example = f"根据您{patient_data.get('age', '46')}岁的年龄和{rads_name}分级，建议定期复查，这是当前重要的健康管理任务。"
        else:
            example = f"根据您{patient_data.get('age', '46')}岁的年龄，建议定期复查，保持健康生活方式。"
        
        prompt = f"""你是一位专业的{role_name}，请基于以下知识库为患者生成{category_name}建议：

患者信息：
{patient_info}

知识库内容（{len(knowledge_list)}条）：
{format_knowledge_for_prompt(knowledge_list)}

要求：
1. **智能去重整合**：综合上述{len(knowledge_list)}条知识库，去除重复内容，提取核心建议
2. **优先保留关键信息**：
   - 具体数值（如"400g蔬菜"、"1000mg"、"每6个月"）
   - 时间频率（如"每日"、"每周3次"）
   - 检查方式（如"超声+钼靶"、"高频超声"、"LDCT"等）
3. **合并同类建议**：如果多条知识库说的是同一件事，合并成一句话
4. **语言温暖专业**：像朋友般关心，又不失专业性
5. **精简表达**：控制在100-200字
6. **直接输出建议内容**：不要标题、不要列表符号、不要"建议如下"等开场白{priority_instruction}

示例格式（仅供参考，不要照抄）：
"{example}"
"""
        
        # 调用LLM
        recommendation = llm_generator._call_llm_api(prompt)
        
        if recommendation and isinstance(recommendation, str):
            recommendation = recommendation.strip()
            # 清理markdown格式标记
            recommendation = clean_markdown_formatting(recommendation)
            return recommendation
        else:
            # 如果LLM失败，返回简化的知识库内容
            return _fallback_recommendation(knowledge_list)
            
    except Exception as e:
        print(f"为类别 {source_type} 生成建议失败: {str(e)}")
        return _fallback_recommendation(knowledge_list)


def _fallback_recommendation(knowledge_list: list) -> str:
    """LLM失败时的备选方案：简单拼接知识库内容"""
    if not knowledge_list:
        return "暂无相关建议"
    
    # 取前3条知识库的内容，简单拼接
    contents = []
    for item in knowledge_list[:3]:
        content = item.get('content', '')
        if content:
            # 截取前100字
            contents.append(content[:100])
    
    return '；'.join(contents) if contents else "暂无相关建议"


def generate_recommendations_by_category(patient_data: dict, matched_knowledge: list) -> dict:
    """
    生成按类别分组的建议草稿
    
    Args:
        patient_data: 患者数据
        matched_knowledge: 匹配到的知识库列表
        
    Returns:
        包含所有分类建议的字典，格式：
        {
            "recommendations": [
                {
                    "category": "年龄相关建议",
                    "source_type": "age_general",
                    "subcategory": "46-60岁",
                    "recommendation": "建议每3个月复查...",
                    "priority": 2,
                    "is_approved": False,
                    "knowledge_sources": [{"id": 120, "title": "...", "content": "..."}]
                },
                ...
            ]
        }
    """
    # 1. 按类别分组
    grouped_knowledge = group_knowledge_by_source_type(matched_knowledge)
    
    # 2. 优先级映射（数字越小优先级越高）
    priority_map = {
        'conclusion_and_warning': 1,  # 结论与预警（最高优先级）
        'risk_factors': 2,  # 风险因素
        'medical_imaging': 3,  # 影像学建议
        'symptoms': 4,  # 症状管理
        'family_history': 5,  # 家族史
        'age_general': 6,  # 年龄建议
        'timeline': 7,  # 病程时间轴
        'exam_history': 8,  # 检查史
        'rhythm': 9,  # 生物节律
        'sleep': 10,  # 睡眠
        'disease_history': 11,  # 疾病史
        'family_genetic_history': 12,  # 遗传史
        'current_medical_history': 13  # 当前病史
    }
    
    recommendations = []
    
    # 3. 为每个类别生成建议
    for source_type, knowledge_list in grouped_knowledge.items():
        if not knowledge_list:
            continue
            
        print(f"📝 为类别 {source_type} 生成建议（基于{len(knowledge_list)}条知识库）...")
        
        # 生成该类别的建议
        nodule_type = patient_data.get('nodule_type', 'breast')
        recommendation_text = generate_recommendation_for_category(
            source_type, knowledge_list, patient_data, nodule_type
        )
        
        # 提取子分类（从第一条知识库中获取）
        subcategory = knowledge_list[0].get('category', '') or knowledge_list[0].get('title', '')
        
        # 构建建议对象
        recommendation_obj = {
            "category": _get_category_display_name(source_type),
            "source_type": source_type,
            "subcategory": subcategory,
            "recommendation": recommendation_text,
            "priority": priority_map.get(source_type, 99),
            "is_approved": False,  # 默认未审核
            "knowledge_sources": [
                {
                    "id": item.get('id'),
                    "title": item.get('title', ''),
                    "content": item.get('content', ''),
                    "priority": item.get('priority', 5)
                }
                for item in knowledge_list[:5]  # 只保存前5条知识库作为来源
            ]
        }
        
        recommendations.append(recommendation_obj)
    
    # 4. 如果没有匹配到知识库，生成基础建议
    if not recommendations and patient_data:
        print("⚠️ [rule_based] 未匹配到知识库，走规则模板生成基础建议（非 LLM 生成）...")
        recommendations = _generate_basic_recommendations(patient_data, priority_map)
        # 标记每条建议为 rule_based，便于前端/日志区分
        for rec in recommendations:
            rec['generation_method'] = 'rule_based'
    
    # 5. 按优先级排序
    recommendations.sort(key=lambda x: x['priority'])
    
    print(f"✅ 共生成 {len(recommendations)} 条分类建议")
    
    return {
        "recommendations": recommendations
    }


def _generate_basic_recommendations(patient_data: dict, priority_map: dict) -> list:
    """
    当没有知识库匹配时，基于患者数据生成基础建议
    
    Args:
        patient_data: 患者数据
        priority_map: 优先级映射
        
    Returns:
        基础建议列表
    """
    recommendations = []
    
    # 1. 影像学建议（基于BI-RADS/TI-RADS/Lung-RADS分级）
    nodule_type = patient_data.get('nodule_type', 'breast')
    
    if nodule_type == 'breast':
        birads = patient_data.get('birads_level', '')
        if birads:
            if birads in ['4A', '4B', '4C', '4']:
                recommendations.append({
                    "category": "影像学建议",
                    "source_type": "medical_imaging",
                    "subcategory": f"BI-RADS {birads}级",
                    "recommendation": f"您的结节评级为BI-RADS {birads}级，属于可疑病变。建议进行穿刺活检以明确诊断，或每3-6个月密切随访观察结节变化。",
                    "priority": priority_map.get('medical_imaging', 3),
                    "is_approved": False,
                    "knowledge_sources": []
                })
            elif birads in ['3', '3类']:
                recommendations.append({
                    "category": "影像学建议",
                    "source_type": "medical_imaging",
                    "subcategory": f"BI-RADS {birads}级",
                    "recommendation": f"您的结节评级为BI-RADS {birads}级，良性可能性大。建议每6个月复查超声，密切观察结节大小和形态变化。",
                    "priority": priority_map.get('medical_imaging', 3),
                    "is_approved": False,
                    "knowledge_sources": []
                })
    
    elif nodule_type == 'thyroid':
        tirads = patient_data.get('tirads_level', '')
        if tirads:
            recommendations.append({
                "category": "影像学建议",
                "source_type": "medical_imaging",
                "subcategory": f"TI-RADS {tirads}级",
                "recommendation": f"您的甲状腺结节评级为TI-RADS {tirads}级。建议根据分级进行相应的随访或进一步检查，具体方案请咨询专科医生。",
                "priority": priority_map.get('medical_imaging', 3),
                "is_approved": False,
                "knowledge_sources": []
            })
    
    elif nodule_type == 'lung':
        lung_rads = patient_data.get('lung_rads_level', '')
        if lung_rads:
            recommendations.append({
                "category": "影像学建议",
                "source_type": "medical_imaging",
                "subcategory": f"Lung-RADS {lung_rads}级",
                "recommendation": f"您的肺结节评级为Lung-RADS {lung_rads}级。建议根据分级进行相应的随访或进一步检查，具体方案请咨询专科医生。",
                "priority": priority_map.get('medical_imaging', 3),
                "is_approved": False,
                "knowledge_sources": []
            })
    
    # 2. 年龄相关建议
    age = patient_data.get('age')
    if age:
        if age >= 40:
            recommendations.append({
                "category": "年龄相关建议",
                "source_type": "age_general",
                "subcategory": f"{age}岁",
                "recommendation": f"您已进入{age}岁，是结节性疾病的高发年龄段。建议每年进行一次全面体检，包括影像学检查，以便及早发现和处理异常情况。",
                "priority": priority_map.get('age_general', 6),
                "is_approved": False,
                "knowledge_sources": []
            })
    
    # 3. 症状管理建议
    symptoms = patient_data.get('symptoms', '')
    if symptoms and symptoms != '无' and symptoms.strip():
        recommendations.append({
            "category": "症状管理",
            "source_type": "symptoms",
            "subcategory": "症状观察",
            "recommendation": f"您目前有{symptoms}等症状。建议密切观察症状变化，如症状加重或出现新症状，请及时就医。同时注意休息，避免过度劳累。",
            "priority": priority_map.get('symptoms', 4),
            "is_approved": False,
            "knowledge_sources": []
        })
    
    # 4. 家族史管理建议
    family_history = patient_data.get('family_history', '')
    if family_history and family_history != '无' and family_history.strip():
        recommendations.append({
            "category": "家族史管理",
            "source_type": "family_history",
            "subcategory": "家族史",
            "recommendation": f"您有{family_history}家族史，这是重要的风险因素。建议加强定期检查频率，建议每6个月进行一次影像学检查，并告知医生您的家族史情况。",
            "priority": priority_map.get('family_history', 5),
            "is_approved": False,
            "knowledge_sources": []
        })
    
    return recommendations


def _get_category_display_name(source_type: str) -> str:
    """获取类别显示名称"""
    category_names = {
        'age_general': '年龄相关建议',
        'timeline': '病程时间轴建议',
        'symptoms': '症状管理',
        'medical_imaging': '影像学建议',
        'family_history': '家族史管理',
        'rhythm': '生物节律调节',
        'exam_history': '检查史管理',
        'sleep': '睡眠管理',
        'disease_history': '疾病史管理',
        'family_genetic_history': '遗传史管理',
        'current_medical_history': '当前病史管理',
        'risk_factors': '风险因素评估',
        'conclusion_and_warning': '结论与预警'
    }
    return category_names.get(source_type, source_type)


# ========================================
# 风险评估相关函数（从 llm_helpers_supplement.py 合并）
# ========================================

def match_disease_history(patient_data):
    """
    匹配乳腺疾病史知识库
    
    Args:
        patient_data: 包含 breast_disease_history 字段的患者数据字典
    
    Returns:
        List[KnowledgeItem]: 匹配到的知识库条目
    """
    from models import db
    
    matched_items = []
    
    if 'breast_disease_history' in patient_data and patient_data['breast_disease_history']:
        diseases = patient_data['breast_disease_history']
        
        # 确保 diseases 是列表
        if not isinstance(diseases, list):
            diseases = [diseases]
        
        for disease in diseases:
            # 模糊匹配疾病子类型
            items = KnowledgeItem.query.filter(
                KnowledgeItem.source_type == 'disease_history',
                db.or_(
                    KnowledgeItem.disease_subtype.like(f'%{disease}%'),
                    KnowledgeItem.title.like(f'%{disease}%')
                )
            ).all()
            matched_items.extend(items)
        
        # 检查高危组合
        high_risk_combinations = check_high_risk_combinations(diseases, patient_data)
        matched_items.extend(high_risk_combinations)
    
    return matched_items


def check_high_risk_combinations(diseases, patient_data):
    """
    检查高危疾病组合
    
    Args:
        diseases: 疾病史列表
        patient_data: 患者数据（包含症状等其他信息）
    
    Returns:
        List[KnowledgeItem]: 匹配到的高危组合知识库条目
    """
    matched_items = []
    
    # 组合1：不典型增生 + 多发纤维瘤
    if '不典型增生' in str(diseases) and '多发纤维瘤' in str(diseases):
        items = KnowledgeItem.query.filter(
            KnowledgeItem.source_type == 'disease_history',
            KnowledgeItem.disease_type == '高危组合',
            KnowledgeItem.disease_subtype.like('%不典型增生%')
        ).all()
        matched_items.extend(items)
    
    # 组合2：浸润癌史 + 新发囊肿
    if '浸润癌史' in str(diseases) and '囊肿' in str(diseases):
        items = KnowledgeItem.query.filter(
            KnowledgeItem.source_type == 'disease_history',
            KnowledgeItem.disease_type == '高危组合',
            KnowledgeItem.disease_subtype.like('%浸润癌史%')
        ).all()
        matched_items.extend(items)
    
    # 组合3：慢性乳腺炎 + 皮肤变化
    symptoms = patient_data.get('symptoms', [])
    if '非哺乳期乳腺炎（慢性）' in str(diseases) and '皮肤变化' in str(symptoms):
        items = KnowledgeItem.query.filter(
            KnowledgeItem.source_type == 'disease_history',
            KnowledgeItem.disease_type == '高危组合',
            KnowledgeItem.disease_subtype.like('%慢性乳腺炎%')
        ).all()
        matched_items.extend(items)
    
    return matched_items


def match_risk_factors(patient_data):
    """
    匹配其他风险因素知识库
    
    Args:
        patient_data: 患者数据字典
    
    Returns:
        List[KnowledgeItem]: 匹配到的知识库条目
    """
    matched_items = []
    
    # 1. 避孕药使用史（≥5年）
    contraceptive_years = patient_data.get('contraceptive_years', 0)
    if contraceptive_years and contraceptive_years >= 5:
        items = KnowledgeItem.query.filter(
            KnowledgeItem.source_type == 'risk_factors',
            KnowledgeItem.risk_factor_type == '激素暴露'
        ).all()
        matched_items.extend(items)
    
    # 2. 糖尿病
    has_diabetes = patient_data.get('has_diabetes', False)
    if has_diabetes:
        items = KnowledgeItem.query.filter(
            KnowledgeItem.source_type == 'risk_factors',
            KnowledgeItem.risk_factor_type == '代谢疾病'
        ).all()
        matched_items.extend(items)
    
    # 3. 吸烟史
    smoking_pack_years = patient_data.get('smoking_pack_years', 0)
    if smoking_pack_years and smoking_pack_years > 0:
        items = KnowledgeItem.query.filter(
            KnowledgeItem.source_type == 'risk_factors',
            KnowledgeItem.risk_factor_type == '毒物暴露'
        ).all()
        matched_items.extend(items)
    
    return matched_items


def calculate_comprehensive_risk(patient_data):
    """
    计算综合风险等级（基于多个维度）- 从数据库规则表读取
    
    Args:
        patient_data: 患者完整数据字典
    
    Returns:
        tuple: (综合风险等级, 各维度评分字典, 各维度详情)
    """
    from models import db, RiskAssessmentRule
    
    risk_scores = {
        'family_history': 1,  # 默认低危
        'disease_history': 1,
        'imaging': 1,
        'biomarker': 1
    }
    
    risk_details = {
        'family_history': {},
        'disease_history': {},
        'imaging': {},
        'biomarker': {}
    }
    
    # 从数据库加载所有规则
    try:
        all_rules = RiskAssessmentRule.query.all()
        rules_by_dimension = {}
        weights_by_dimension = {}
        
        for rule in all_rules:
            if rule.dimension not in rules_by_dimension:
                rules_by_dimension[rule.dimension] = {}
                weights_by_dimension[rule.dimension] = {}
            
            rules_by_dimension[rule.dimension][rule.risk_level] = rule
            weights_by_dimension[rule.dimension][rule.risk_level] = rule.weight_percentage / 100.0
    except Exception as e:
        print(f"⚠️ 无法加载风险评估规则表，使用默认逻辑: {e}")
        # 如果表不存在，使用硬编码逻辑（向后兼容）
        return _calculate_risk_legacy(patient_data)
    
    # 1. 家族史维度评分
    family_history = patient_data.get('family_history', '无家族史')
    genetic_mutation = patient_data.get('genetic_mutation', '')
    
    if 'BRCA' in family_history or 'BRCA' in genetic_mutation or '一级亲属' in family_history:
        risk_scores['family_history'] = 3  # 高危
        risk_level_key = '高危'
    elif '二级亲属' in family_history or '中危' in family_history:
        risk_scores['family_history'] = 2  # 中危
        risk_level_key = '中危'
    else:
        risk_scores['family_history'] = 1  # 低危
        risk_level_key = '低危'
    
    if '家族史' in rules_by_dimension and risk_level_key in rules_by_dimension['家族史']:
        rule = rules_by_dimension['家族史'][risk_level_key]
        risk_details['family_history'] = {
            'score': risk_scores['family_history'],
            'level': risk_level_key,
            'criteria': rule.criteria,
            'monitoring': rule.monitoring_frequency,
            'upgrade': rule.upgrade_conditions
        }
    
    # 2. 疾病史维度评分
    diseases = patient_data.get('breast_disease_history', [])
    if not isinstance(diseases, list):
        diseases = [diseases] if diseases else []
    
    if any('浸润癌' in d or '不典型增生' in d for d in diseases):
        risk_scores['disease_history'] = 3  # 高危
        risk_level_key = '高危'
    elif any('纤维瘤' in d or '囊肿' in d or '炎' in d for d in diseases):
        risk_scores['disease_history'] = 2  # 中危
        risk_level_key = '中危'
    else:
        risk_scores['disease_history'] = 1  # 低危
        risk_level_key = '低危'
    
    if '疾病史' in rules_by_dimension and risk_level_key in rules_by_dimension['疾病史']:
        rule = rules_by_dimension['疾病史'][risk_level_key]
        risk_details['disease_history'] = {
            'score': risk_scores['disease_history'],
            'level': risk_level_key,
            'criteria': rule.criteria,
            'monitoring': rule.monitoring_frequency,
            'upgrade': rule.upgrade_conditions
        }
    
    # 3. 影像学维度评分
    birads = patient_data.get('birads_level', 0)
    tnm_stage = patient_data.get('tnm_stage', 1)
    
    try:
        birads = int(birads) if birads else 0
        tnm_stage = int(tnm_stage) if tnm_stage else 1
    except:
        birads = 0
        tnm_stage = 1
    
    if birads >= 4 or tnm_stage >= 4:
        risk_scores['imaging'] = 3  # 高危
        risk_level_key = '高危'
    elif birads == 3 or tnm_stage == 3:
        risk_scores['imaging'] = 2  # 中危
        risk_level_key = '中危'
    else:
        risk_scores['imaging'] = 1  # 低危
        risk_level_key = '低危'
    
    if '影像学' in rules_by_dimension and risk_level_key in rules_by_dimension['影像学']:
        rule = rules_by_dimension['影像学'][risk_level_key]
        risk_details['imaging'] = {
            'score': risk_scores['imaging'],
            'level': risk_level_key,
            'criteria': rule.criteria,
            'monitoring': rule.monitoring_frequency,
            'upgrade': rule.upgrade_conditions
        }
    
    # 4. 分子标志物维度评分
    ca153 = patient_data.get('ca153_value', 0) or 0
    
    if ca153 > 30:
        risk_scores['biomarker'] = 3  # 高危
        risk_level_key = '高危'
    elif ca153 > 25:
        risk_scores['biomarker'] = 2  # 中危
        risk_level_key = '中危'
    else:
        risk_scores['biomarker'] = 1  # 低危
        risk_level_key = '低危'
    
    if '分子标志物' in rules_by_dimension and risk_level_key in rules_by_dimension['分子标志物']:
        rule = rules_by_dimension['分子标志物'][risk_level_key]
        risk_details['biomarker'] = {
            'score': risk_scores['biomarker'],
            'level': risk_level_key,
            'criteria': rule.criteria,
            'monitoring': rule.monitoring_frequency,
            'upgrade': rule.upgrade_conditions
        }
    
    # 计算加权综合评分（从规则表获取权重）
    total_score = (
        risk_scores['family_history'] * 0.30 +
        risk_scores['disease_history'] * 0.30 +
        risk_scores['imaging'] * 0.25 +
        risk_scores['biomarker'] * 0.15
    )
    
    # 判定综合风险等级
    if total_score >= 2.5:
        comprehensive_risk = '高危'
    elif total_score >= 1.8:
        comprehensive_risk = '中危'
    else:
        comprehensive_risk = '低危'
    
    return comprehensive_risk, risk_scores, risk_details


def _calculate_risk_legacy(patient_data):
    """
    旧版风险评估逻辑（向后兼容）
    """
    risk_scores = {
        'family_history': 1,
        'disease_history': 1,
        'imaging': 1,
        'biomarker': 1
    }
    
    # 简化的评分逻辑
    family_history = patient_data.get('family_history', '无')
    if 'BRCA' in family_history or '一级亲属' in family_history:
        risk_scores['family_history'] = 3
    elif '二级亲属' in family_history:
        risk_scores['family_history'] = 2
    
    diseases = patient_data.get('breast_disease_history', [])
    if not isinstance(diseases, list):
        diseases = [diseases] if diseases else []
    
    if any('浸润癌' in d or '不典型增生' in d for d in diseases):
        risk_scores['disease_history'] = 3
    elif any('纤维瘤' in d or '囊肿' in d for d in diseases):
        risk_scores['disease_history'] = 2
    
    tnm_stage = patient_data.get('tnm_stage', 1)
    try:
        tnm_stage = int(tnm_stage)
    except:
        tnm_stage = 1
    
    if tnm_stage >= 4:
        risk_scores['imaging'] = 3
    elif tnm_stage == 3:
        risk_scores['imaging'] = 2
    
    ca153 = patient_data.get('ca153_value', 0) or 0
    if ca153 > 30:
        risk_scores['biomarker'] = 3
    elif ca153 > 25:
        risk_scores['biomarker'] = 2
    
    total_score = (
        risk_scores['family_history'] * 0.30 +
        risk_scores['disease_history'] * 0.30 +
        risk_scores['imaging'] * 0.25 +
        risk_scores['biomarker'] * 0.15
    )
    
    if total_score >= 2.5:
        comprehensive_risk = '高危'
    elif total_score >= 1.8:
        comprehensive_risk = '中危'
    else:
        comprehensive_risk = '低危'
    
    return comprehensive_risk, risk_scores, {}


def get_monitoring_recommendation(comprehensive_risk, risk_scores):
    """
    根据综合风险等级和各维度评分，给出监测频率建议
    
    Args:
        comprehensive_risk: 综合风险等级（低危/中危/高危）
        risk_scores: 各维度评分字典
    
    Returns:
        dict: 监测建议字典
    """
    recommendations = {
        'monitoring_frequency': '',
        'intervention_priority': '',
        'upgrade_conditions': []
    }
    
    if comprehensive_risk == '高危':
        recommendations['monitoring_frequency'] = '每3个月MRI+超声联合监测'
        recommendations['intervention_priority'] = '立即多学科会诊（乳腺外科+肿瘤科+遗传咨询）'
        recommendations['upgrade_conditions'] = [
            'CA15-3连续2次升高>25% → 每月超声+季度PET-CT',
            '新发BI-RADS 4级病变 → 72小时内穿刺活检',
            '影像学显示进展 → 立即启动新辅助治疗'
        ]
    elif comprehensive_risk == '中危':
        recommendations['monitoring_frequency'] = '每6个月ABUS+钼靶交替检查'
        recommendations['intervention_priority'] = '强化监测，关注新发病变'
        recommendations['upgrade_conditions'] = [
            '弹性评分较前升高>0.3 → 缩短至3个月复查',
            '新增簇状钙化 → 6个月钼靶复查',
            '结节年增长>20% → 立即穿刺活检'
        ]
    else:  # 低危
        recommendations['monitoring_frequency'] = '年度超声检查（40岁起）'
        recommendations['intervention_priority'] = '常规随访即可'
        recommendations['upgrade_conditions'] = [
            '新发纤维瘤 → 升级为中危管理',
            '家族史变化 → 重新评估风险等级',
            '二级亲属患癌年龄≤45岁 → 升级为高危'
        ]
    
    return recommendations

