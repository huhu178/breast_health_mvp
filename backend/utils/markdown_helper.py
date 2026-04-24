"""
Markdown 转 HTML 工具函数
用于将 LLM 返回的 Markdown 格式文本转换为 HTML
"""
import re
import html


def markdown_to_html(text):
    """
    将简单的 Markdown 格式转换为 HTML

    支持的格式：
    - **粗体** → <strong>粗体</strong>
    - *斜体* → <em>斜体</em>
    - 换行 → <br>
    - 数字列表 1) 2) 3) → <ol><li>

    Args:
        text: Markdown 格式的文本

    Returns:
        HTML 格式的文本
    """
    if not text:
        return text
    
    # 0. 预处理：去除多余的空白字符和格式标记
    # 去除markdown代码块标记
    text = re.sub(r'```[a-z]*\n?', '', text)
    text = re.sub(r'```', '', text)
    # 去除多余的空白字符（保留单个空格）
    text = re.sub(r'[ \t]+', ' ', text)
    # 去除多余的空行（保留最多一个空行）
    text = re.sub(r'\n{3,}', '\n\n', text)
    # 去除行首行尾的空白
    lines = text.split('\n')
    lines = [line.strip() for line in lines if line.strip()]  # 同时去除空行
    text = '\n'.join(lines)
    # 去除整个文本首尾的空白
    text = text.strip()

    # 1. 先处理粗体 **text**，生成 HTML 标签
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)

    # 2. 处理斜体 *text* (注意：要在粗体之后处理，避免冲突)
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', text)

    # 3. 处理换行符（保留段落结构）
    # 将连续两个换行符视为段落分隔，但不在外层添加 <p> 标签
    # 因为模板中已经有 <p> 标签包裹，这里只处理内联的换行
    paragraphs = text.split('\n\n')
    formatted_paragraphs = []

    for para in paragraphs:
        if para.strip():
            # 段落内的单个换行符替换为 <br>，但不添加外层的 <p> 标签
            para = para.replace('\n', '<br>')
            formatted_paragraphs.append(para)

    text = '<br><br>'.join(formatted_paragraphs)

    # 4. 处理数字列表 1) 2) 3)
    # 匹配 "数字)" 开头的行（需要先按 <br> 分割，因为段落已经转换为 <br>）
    # 先按 <br><br> 分割段落，再在每个段落内处理列表
    paragraphs = text.split('<br><br>')
    processed_paragraphs = []
    
    for para in paragraphs:
        # 在段落内按 <br> 分割行
        lines = para.split('<br>')
        in_list = False
        result_lines = []
        
        for line in lines:
            # 匹配 "1) " 或 "1）" 格式
            if re.match(r'^\s*\d+[)）]\s+', line):
                if not in_list:
                    result_lines.append('<ol>')
                    in_list = True
                # 提取列表项内容
                item_content = re.sub(r'^\s*\d+[)）]\s+', '', line)
                result_lines.append(f'<li>{item_content}</li>')
            else:
                if in_list:
                    result_lines.append('</ol>')
                    in_list = False
                if line.strip():  # 只添加非空行
                    result_lines.append(line)
        
        if in_list:
            result_lines.append('</ol>')
        
        # 将处理后的段落重新组合
        processed_para = '<br>'.join(result_lines)
        if processed_para.strip():
            processed_paragraphs.append(processed_para)
    
    text = '<br><br>'.join(processed_paragraphs)

    # 最后：转义剩余的 < 和 > 字符（但保留我们已经生成的 HTML 标签）
    # 使用正则表达式匹配已知的 HTML 标签，只转义不在这些标签中的 < 和 >
    # 已知的 HTML 标签：<p>, </p>, <br>, <strong>, </strong>, <em>, </em>, <ol>, </ol>, <li>, </li>
    html_tags = ['p', '/p', 'br', 'strong', '/strong', 'em', '/em', 'ol', '/ol', 'li', '/li']
    
    # 保护已知的 HTML 标签
    protected_pattern = r'<(/?(?:' + '|'.join(html_tags) + r'))>'
    
    # 临时替换已知标签为占位符
    placeholders = {}
    placeholder_index = 0
    
    def replace_tag(match):
        nonlocal placeholder_index
        placeholder = f'__HTML_TAG_{placeholder_index}__'
        placeholders[placeholder] = match.group(0)
        placeholder_index += 1
        return placeholder
    
    text = re.sub(protected_pattern, replace_tag, text)
    
    # 转义剩余的 < 和 >
    text = text.replace('<', '&lt;').replace('>', '&gt;')
    
    # 恢复已知的 HTML 标签
    for placeholder, original_tag in placeholders.items():
        text = text.replace(placeholder, original_tag)

    return text


def safe_markdown_to_html(text):
    """
    安全的 Markdown 转 HTML（捕获异常）

    Args:
        text: Markdown 格式的文本

    Returns:
        HTML 格式的文本，如果转换失败则返回原文
    """
    try:
        return markdown_to_html(text)
    except Exception as e:
        print(f"⚠️ Markdown转换失败: {e}")
        return text


# 测试用例
if __name__ == '__main__':
    test_text = """您好，本次影像学检查的综合结果总体令人放心。**乳腺部分**提示为良性改变（BI-RADS 2类），恶性风险极低。

关于您的乳腺结节，影像学评估为**BI-RADS 2类**，这是一个明确的良性诊断结论。

1) 第一点建议
2) 第二点建议
3) 第三点建议

请您*不必为此*感到緊張。"""

    print("原始文本:")
    print(test_text)
    print("\n" + "="*60 + "\n")
    print("转换后的HTML:")
    print(markdown_to_html(test_text))
