import re
from pathlib import Path

# 配置路径（按需修改）
INPUT_FILE = Path(r'd:\1work\20251016\breast_health_mvp\模板\乳腺结节健康管理方案模板.html')
OUTPUT_FILE = Path(r'd:\1work\20251016\breast_health_mvp\模板\乳腺结节健康管理方案_常规版.html')


def ensure_utf8_meta(html: str) -> str:
    # 移除原有 meta charset，插入 UTF-8
    html = re.sub(r'<meta[^>]*charset=[^>]*>', '', html, flags=re.IGNORECASE)
    if re.search(r'<head[^>]*>', html, flags=re.IGNORECASE):
        html = re.sub(r'(<head[^>]*>)', r'\1\n<meta charset="utf-8">', html, count=1, flags=re.IGNORECASE)
    else:
        html = '<head><meta charset="utf-8"></head>' + html
    return html


def strip_mso_conditional(html: str) -> str:
    # 移除 Word 条件注释块 <!--[if gte mso 9]> ... <![endif]-->
    return re.sub(r'<!--\[if.*?<!\[endif\]-->', '', html, flags=re.IGNORECASE | re.DOTALL)


def remove_word_namespaces(html: str) -> str:
    # 清理根节点上的 Word 命名空间（可选）
    html = html.replace('xmlns:o="urn:schemas-microsoft-com:office:office"', '')
    html = html.replace('xmlns:w="urn:schemas-microsoft-com:office:word"', '')
    html = html.replace('xmlns:dt="uuid:C2F41010-65B3-11d1-A29F-00AA00C14882"', '')
    return html


def remove_heavy_mso_css(html: str) -> str:
    # 移除大段 @list / @font-face（视需要启用）
    html = re.sub(r'@list[\s\S]*?\}', '', html)
    html = re.sub(r'@font-face[\s\S]*?\}', '', html)
    return html


def strip_mso_props_in_style(html: str) -> str:
    def strip_mso_props(css: str) -> str:
        css = re.sub(r'mso-[\w-]+\s*:[^;]+;?', '', css)
        css = re.sub(r';\s*;', ';', css)
        return css

    def clean_style_attr(m):
        style = m.group(1)
        return f'style="{strip_mso_props(style)}"'

    return re.sub(r'style="([^"]*)"', clean_style_attr, html, flags=re.IGNORECASE)


def add_border_for_all_tables(html: str) -> str:
    # 为所有 table 强制添加边框，可见线条
    def add_border_to_table(m):
        tag = m.group(0)
        if re.search(r'border\s*=\s*"', tag):
            # 如已有 border 属性，强制改为 1
            tag = re.sub(r'border\s*=\s*"[^"]*"', 'border="1"', tag)
        else:
            tag = tag[:-1] + ' border="1">'
        return tag

    html = re.sub(r'<table\b[^>]*>', add_border_to_table, html, flags=re.IGNORECASE)

    # 注入全局表格样式，保证边线可见且规整
    table_css = (
        "\n<style>\n"
        "  table { border-collapse: collapse; }\n"
        "  table, th, td { border: 1px solid #444; }\n"
        "</style>\n"
    )
    if re.search(r'<head[^>]*>', html, flags=re.IGNORECASE):
        html = re.sub(r'(<head[^>]*>)', r'\1' + table_css, html, count=1, flags=re.IGNORECASE)
    else:
        html = table_css + html
    return html


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f'输入文件不存在: {INPUT_FILE}')

    html = INPUT_FILE.read_text(encoding='utf-8', errors='ignore')

    html = ensure_utf8_meta(html)
    html = strip_mso_conditional(html)
    html = remove_word_namespaces(html)
    html = remove_heavy_mso_css(html)
    html = strip_mso_props_in_style(html)
    html = add_border_for_all_tables(html)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(html, encoding='utf-8')
    print(f'已生成常规版（含表格边框）：{OUTPUT_FILE}')


if __name__ == '__main__':
    main()
