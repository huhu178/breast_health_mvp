"""
影像报告分析服务
使用LLM从影像报告中提取结构化信息
支持直接分析PDF（多模态）和文本分析两种方式
"""
import json
import re
import base64
import os
from typing import Dict, Optional, List
from services.llm_service import llm_generator

# 不再需要pdf2image和PIL，直接发送PDF给大模型


class ImagingReportService:
    """影像报告分析服务"""
    
    @staticmethod
    def extract_structured_data_from_pdf(file_path: str, nodule_type: str = 'breast') -> Optional[Dict]:
        """
        直接使用LLM从PDF中提取结构化信息（最简单方法：直接让大模型看PDF文件）
        
        Args:
            file_path: PDF文件路径
            nodule_type: 结节类型（breast/lung/thyroid等）
            
        Returns:
            dict: 提取的结构化信息
        """
        try:
            print(f"\n🔍 开始使用LLM直接分析PDF文件（结节类型: {nodule_type}）...")
            
            # 先尝试用pdfplumber检查PDF页数和是否能提取文本（用于调试）
            try:
                import pdfplumber
                with pdfplumber.open(file_path) as pdf:
                    total_pages = len(pdf.pages)
                    print(f"📄 PDF总页数: {total_pages}")
                    # 尝试提取第一页文本，看看是否是扫描件
                    first_page_text = pdf.pages[0].extract_text() if pdf.pages else None
                    if first_page_text:
                        print(f"📝 第1页可提取文本长度: {len(first_page_text)} 字符")
                        print(f"📝 第1页文本预览（前200字符）: {first_page_text[:200]}...")
                    else:
                        print(f"⚠️ 第1页无法提取文本（可能是扫描件，需要LLM OCR识别）")
            except Exception as e:
                print(f"⚠️ PDF页数检查失败: {str(e)}")
            
            # 读取PDF文件并编码为base64
            with open(file_path, 'rb') as f:
                pdf_bytes = f.read()
                pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
            
            file_size_mb = len(pdf_bytes) / (1024 * 1024)
            print(f"✅ PDF文件已读取并编码（大小: {len(pdf_bytes)} 字节，约 {file_size_mb:.2f} MB）")
            
            # 构建提示词
            extraction_prompt = ImagingReportService._build_extraction_prompt_with_images(nodule_type)
            
            # 调用LLM（直接发送PDF文件）
            print(f"🤖 正在调用LLM直接分析PDF文件（可能需要较长时间，请耐心等待）...")
            response = llm_generator._call_llm_api_with_pdf(extraction_prompt, pdf_base64, file_path)
            
            if not response:
                print("❌ LLM未返回有效响应")
                return None
            
            # 解析JSON响应
            extracted_data = ImagingReportService._parse_extraction_response(response)
            
            if extracted_data:
                print(f"✅ 成功提取结构化信息: {len(extracted_data)} 个字段")
                print(f"📊 提取的数据: {json.dumps(extracted_data, ensure_ascii=False, indent=2)}")
            else:
                print("⚠️ 未能提取到结构化信息")
            
            return extracted_data
            
        except Exception as e:
            print(f"❌ LLM分析PDF失败: {str(e)}")
            # 降级方案：尝试文本提取
            print("🔄 尝试使用文本提取作为降级方案...")
            from services.pdf_parser import pdf_parser
            text = pdf_parser.extract_text_from_pdf(file_path)
            if text:
                return ImagingReportService.extract_structured_data_from_text(text, nodule_type)
            return None
    
    
    @staticmethod
    def _build_extraction_prompt_with_images(nodule_type: str) -> str:
        """构建包含图片的提取提示词"""
        
        field_definitions = {
            'breast': {
                'birads_level': 'BI-RADS分级（如：3类、4A类、4B类、4C类、5类）',
                'nodule_size': '结节大小（如：8mm、1.2cm）',
                'nodule_location': '结节位置（如：左乳外上象限、右乳内下象限）',
                'nodule_quantity': '结节数量（如：单发、多发）',
                'nodule_count': '结节个数（如果是多发，具体个数）',
                'boundary_features': '边界特征（如：边界清晰、边界模糊、边界不规则）',
                'internal_echo': '内部回声（如：低回声、等回声、高回声、无回声）',
                'blood_flow_signal': '血流信号（如：未见异常血流信号、可见血流信号、丰富血流信号）',
                'elasticity_score': '弹性评分（如：1分、2分、3分、4分、5分）',
                'other_findings': '其他发现或备注信息'
            },
            'lung': {
                'lung_rads_level': 'Lung-RADS分级',
                'lung_nodule_size': '结节大小',
                'lung_nodule_location': '结节位置',
                'lung_nodule_count': '结节个数',
                'lung_boundary_features': '边界特征',
                'lung_internal_echo': '内部特征',
                'lung_blood_flow_signal': '血流信号',
                'other_findings': '其他发现'
            },
            'thyroid': {
                'tirads_level': 'TI-RADS分级',
                'thyroid_nodule_size': '结节大小',
                'thyroid_nodule_location': '结节位置',
                'thyroid_nodule_count': '结节个数',
                'thyroid_boundary_features': '边界特征',
                'thyroid_internal_echo': '内部回声',
                'thyroid_blood_flow_signal': '血流信号',
                'other_findings': '其他发现'
            }
        }
        
        fields = field_definitions.get(nodule_type, field_definitions['breast'])
        
        prompt = f"""你是一位专业的医学影像报告分析专家。请**逐页仔细阅读**以下影像报告PDF文件，提取所有关键的结构化信息。

**⚠️ 重要提示：**
这份PDF可能包含多页内容，包括：
- **文字报告页**：包含检查结果、诊断意见、文字描述等
- **影像图片页**：包含彩超图像、超声图像、检查图像等（**重要：需要识别图像上的文字！**）

你必须：
1. **逐页阅读**：从第一页到最后一页，仔细阅读每一页的所有内容
2. **识别图像文字**：**特别注意彩超图像、超声图像等影像图片上的所有文字**，包括：
   - 图像上的文字标注（如"左乳外上象限"、"8mm"、"4A类"等）
   - 图像中的测量值（如"10×8mm"、"1.2cm"等）
   - 图像下方的文字说明（通常包含关键信息）
   - 图像旁边的文字描述（位置、大小、特征等）
   - 图像标题或图例中的文字
3. **全面提取**：不要遗漏任何页面的信息，包括报告正文、检查结果、诊断意见、**图像上的所有文字**等所有部分
4. **仔细查找**：某些关键信息可能在不同页面，必须全部查找
5. **完整信息**：如果报告中（文字页面或图像上的文字）提到了结节、分级、大小、位置等信息，必须全部提取

**需要提取的字段（{nodule_type}类型）：**
{json.dumps(fields, ensure_ascii=False, indent=2)}

**提取规则（请严格遵守）：**
1. **逐页阅读**：从封面到最后一页，逐页仔细阅读，不要跳过任何页面
2. **识别图像文字**（**特别重要！**）：
   - **彩超图像/超声图像**：仔细识别图像上的所有文字，包括：
     * 图像上的文字标注（位置、大小、测量值等，如"左乳外上象限"、"8mm×6mm"等）
     * 图像中的测量值文字（如"10×8mm"、"1.2cm"等）
     * 图像下方的文字说明（通常包含关键信息，如"低回声"、"边界清晰"等）
     * 图像旁边的文字描述（位置、大小、特征等）
     * 图像标题或图例中的文字（如"BI-RADS 4A"等）
   - **文字识别技巧**：
     * 图像上通常有文字标注，必须全部识别出来
     * 图像下方或旁边可能有文字说明，包含诊断信息
     * 图像中的测量线旁边可能有数值标注
3. **关键词搜索**：在每一页（包括图像页的文字）中搜索以下关键词：
   - BI-RADS、分级、分类、级别
   - 结节、肿块、占位、病灶
   - 大小、直径、尺寸、范围、测量
   - 位置、象限、部位、区域
   - 边界、边缘、形态、形状
   - 回声、密度、信号、血流
   - 弹性、硬度、评分
4. **保持原样**：数值字段保持报告中的原始格式（如"8mm"、"4A类"、"1.2cm"、"8mm×6mm"）
5. **提取完整**：文本字段提取完整描述，但不要过长（一般不超过30字）
6. **缺失处理**：**只有在所有页面（包括图像页的文字）都完全找不到**某个字段时，才设置为 null

**字段提取详细说明：**
- **birads_level**: 
  - 在文字报告中查找"BI-RADS"、"分级"、"分类"等关键词
  - **在图像文字中查找**：图像上的标注文字、图像下方的说明文字中的分级信息
  - 提取如"3类"、"4A"、"4B"、"5类"等
- **nodule_size**: 
  - 在文字报告中查找"大小"、"直径"、"约"等关键词
  - **在图像文字中查找**：图像上的标注文字（如"8mm"、"10×8mm"）、图像下方的说明文字、测量线旁边的数值
  - 提取如"8mm"、"1.2cm"、"8mm×6mm"、"10×8mm"等
- **nodule_location**: 
  - 在文字报告中查找"位于"、"位置"、"象限"等关键词
  - **在图像文字中查找**：图像上的位置标注文字（如"左乳外上象限"）、图像标题或说明中的位置信息
  - 提取如"左乳外上象限"、"右乳内下象限"等
- **nodule_quantity**: 
  - 在文字报告中查找"单发"、"多发"、"多个"等关键词
  - **在图像文字中查找**：图像说明中的"单发"、"多发"等文字
- **nodule_count**: 
  - 如果是多发，在文字或图像文字中查找具体个数，如"2个"、"3个"等
  - **在图像文字中查找**：图像说明中提到的结节数量
- **boundary_features**: 
  - 在文字报告中查找"边界"、"边缘"等关键词
  - **在图像文字中查找**：图像上的标注文字、图像下方的说明文字中的边界描述（如"边界清晰"）
  - 提取如"边界清晰"、"边界模糊"、"边界不规则"等
- **internal_echo**: 
  - 在文字报告中查找"回声"、"密度"等关键词
  - **在图像文字中查找**：图像上的标注文字、图像下方的说明文字中的回声描述（如"低回声"）
  - 提取如"低回声"、"等回声"、"高回声"、"无回声"等
- **blood_flow_signal**: 
  - 在文字报告中查找"血流"、"血供"等关键词
  - **在图像文字中查找**：图像上的标注文字、图像下方的说明文字中的血流描述（如"可见血流信号"）
  - 提取如"未见异常血流信号"、"可见血流信号"、"丰富血流信号"等
- **elasticity_score**: 
  - 在文字报告中查找"弹性"、"硬度"、"评分"等关键词
  - **在图像文字中查找**：弹性成像图像上的评分标注文字（如"2分"）
  - 提取如"1分"、"2分"、"3分"等
- **other_findings**: 
  - 提取报告中（文字页面或图像上的文字）其他重要发现，如"增生"、"钙化"、"囊肿"等
  - **在图像文字中查找**：图像说明中的其他发现描述

**输出格式（必须是严格的JSON格式，不要有任何其他文字）：**
```json
{{
  "birads_level": "4A",
  "nodule_size": "8mm",
  "nodule_location": "左乳外上象限",
  "nodule_quantity": "单发",
  "nodule_count": null,
  "boundary_features": "边界清晰",
  "internal_echo": "低回声",
  "blood_flow_signal": "未见异常血流信号",
  "elasticity_score": "2分",
  "other_findings": "其他发现..."
}}
```

**重要约束：**
1. 输出必须是纯JSON格式，不要有任何markdown标记、解释文字或代码块
2. 字段名必须与上述定义完全一致（区分大小写）
3. **必须逐页仔细阅读，不要遗漏任何信息**
4. 只提取报告中明确提到的信息，不要推测、假设或补充信息
5. 如果字段在所有页面都未找到，必须设置为 null（不是空字符串、不是"无"、不是"未提及"）
6. 数值保持原格式，不要转换单位（如"8mm"不要转换为"0.8cm"）

**现在请开始逐页仔细分析PDF文件，提取所有相关信息。**
"""
        
        return prompt
    
    @staticmethod
    def extract_structured_data_from_text(text: str, nodule_type: str = 'breast') -> Optional[Dict]:
        """
        使用LLM从文本中提取结构化信息（第一步：信息提取）
        
        Args:
            text: 从PDF/Word中提取的文本内容
            nodule_type: 结节类型（breast/lung/thyroid等）
            
        Returns:
            dict: 提取的结构化信息，格式如：
            {
                "birads_level": "4A",
                "nodule_size": "8mm",
                "nodule_location": "左乳外上象限",
                "boundary_features": "边界清晰",
                "internal_echo": "低回声",
                "blood_flow_signal": "未见异常血流信号",
                "elasticity_score": "2分",
                "other_findings": "其他发现..."
            }
        """
        try:
            print(f"\n🔍 开始使用LLM提取影像报告结构化信息（结节类型: {nodule_type}）...")
            
            # 根据结节类型构建不同的提取提示词
            extraction_prompt = ImagingReportService._build_extraction_prompt(text, nodule_type)
            
            # 调用LLM
            response = llm_generator._call_llm_api(extraction_prompt)
            
            if not response:
                print("❌ LLM未返回有效响应")
                return None
            
            # 解析JSON响应
            extracted_data = ImagingReportService._parse_extraction_response(response)
            
            if extracted_data:
                print(f"✅ 成功提取结构化信息: {len(extracted_data)} 个字段")
                print(f"📊 提取的数据: {json.dumps(extracted_data, ensure_ascii=False, indent=2)}")
            else:
                print("⚠️ 未能提取到结构化信息")
            
            return extracted_data
            
        except Exception as e:
            print(f"❌ 提取结构化信息失败: {str(e)}")
            return None
    
    @staticmethod
    def _build_extraction_prompt(text: str, nodule_type: str) -> str:
        """构建信息提取提示词"""
        
        # 根据结节类型定义需要提取的字段
        field_definitions = {
            'breast': {
                'birads_level': 'BI-RADS分级（如：3类、4A类、4B类、4C类、5类）',
                'nodule_size': '结节大小（如：8mm、1.2cm）',
                'nodule_location': '结节位置（如：左乳外上象限、右乳内下象限）',
                'nodule_quantity': '结节数量（如：单发、多发）',
                'nodule_count': '结节个数（如果是多发，具体个数）',
                'boundary_features': '边界特征（如：边界清晰、边界模糊、边界不规则）',
                'internal_echo': '内部回声（如：低回声、等回声、高回声、无回声）',
                'blood_flow_signal': '血流信号（如：未见异常血流信号、可见血流信号、丰富血流信号）',
                'elasticity_score': '弹性评分（如：1分、2分、3分、4分、5分）',
                'other_findings': '其他发现或备注信息'
            },
            'lung': {
                'lung_rads_level': 'Lung-RADS分级（如：1类、2类、3类、4A类、4B类、4X类）',
                'lung_nodule_size': '结节大小（如：5mm、1.2cm）',
                'lung_nodule_location': '结节位置（如：右上叶、左下叶）',
                'lung_nodule_count': '结节个数',
                'lung_boundary_features': '边界特征',
                'lung_internal_echo': '内部特征',
                'lung_blood_flow_signal': '血流信号',
                'other_findings': '其他发现'
            },
            'thyroid': {
                'tirads_level': 'TI-RADS分级（如：2类、3类、4类、5类）',
                'thyroid_nodule_size': '结节大小',
                'thyroid_nodule_location': '结节位置（如：左叶、右叶、峡部）',
                'thyroid_nodule_count': '结节个数',
                'thyroid_boundary_features': '边界特征',
                'thyroid_internal_echo': '内部回声',
                'thyroid_blood_flow_signal': '血流信号',
                'other_findings': '其他发现'
            }
        }
        
        fields = field_definitions.get(nodule_type, field_definitions['breast'])
        
        prompt = f"""你是一位专业的医学影像报告分析专家。请从以下影像报告文本中提取关键的结构化信息。

**报告文本内容：**
```
{text[:5000]}  # 限制文本长度，避免超出token限制
```

**需要提取的字段（{nodule_type}类型）：**
{json.dumps(fields, ensure_ascii=False, indent=2)}

**提取要求：**
1. 仔细阅读报告文本，识别所有相关的影像学特征
2. 如果某个字段在报告中未提及，则设置为 null
3. 如果报告中提到但信息不完整，尽量提取可用信息
4. 数值字段保持原样（如"8mm"、"4A类"）
5. 文本字段提取关键描述（不要过长）

**输出格式（必须是严格的JSON格式）：**
```json
{{
  "birads_level": "4A",
  "nodule_size": "8mm",
  "nodule_location": "左乳外上象限",
  "nodule_quantity": "单发",
  "nodule_count": null,
  "boundary_features": "边界清晰",
  "internal_echo": "低回声",
  "blood_flow_signal": "未见异常血流信号",
  "elasticity_score": "2分",
  "other_findings": "其他发现..."
}}
```

**重要：**
- 输出必须是纯JSON格式，不要有任何其他文字
- 如果某个字段在报告中未找到，设置为 null（不是空字符串）
- 字段名必须与上述定义完全一致
- 只提取报告中明确提到的信息，不要推测或假设
"""
        
        return prompt
    
    @staticmethod
    def _parse_extraction_response(response: str) -> Optional[Dict]:
        """解析LLM返回的JSON响应"""
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
                return json.loads(response)
            except json.JSONDecodeError:
                pass
            
            # 尝试提取JSON对象
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    pass
            
            print(f"⚠️ 无法解析LLM响应为JSON: {response[:200]}")
            return None
            
        except Exception as e:
            print(f"❌ 解析响应失败: {str(e)}")
            return None
    
    @staticmethod
    def analyze_with_llm(extracted_data: Dict, patient_data: Dict, nodule_type: str = 'breast') -> Optional[str]:
        """
        使用LLM基于提取的信息生成分析意见（第二步：综合分析）
        
        Args:
            extracted_data: 从报告中提取的结构化信息
            patient_data: 患者表单数据
            nodule_type: 结节类型
            
        Returns:
            str: LLM生成的分析意见
        """
        # 这个功能可以整合到现有的 generate_imaging_conclusion_with_llm 中
        # 暂时返回None，后续在报告生成流程中处理
        return None


# 创建单例
imaging_report_service = ImagingReportService()

