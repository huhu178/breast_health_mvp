#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
将 Word 文档转换为干净的 HTML 网页
使用 mammoth 库进行转换，生成带表格边框的标准 HTML
"""

from pathlib import Path
import re

try:
    import mammoth
except ImportError:
    print("需要安装 mammoth 库，正在安装...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'mammoth'])
    import mammoth


INPUT_DOCX = Path(r'd:\1work\20251016\breast_health_mvp\模板\乳腺结节健康管理方案模板.docx')
OUTPUT_HTML = Path(r'd:\1work\20251016\breast_health_mvp\模板\乳腺结节健康管理方案模板_clean.html')


def convert_docx_to_html(docx_path: Path, html_path: Path):
    """
    将 docx 转换为带样式的 HTML
    """
    print(f'正在转换: {docx_path.name}')
    
    with open(docx_path, 'rb') as docx_file:
        result = mammoth.convert_to_html(
            docx_file,
            style_map="""
                p[style-name='Heading 1'] => h1:fresh
                p[style-name='Heading 2'] => h2:fresh
                p[style-name='Heading 3'] => h3:fresh
                p[style-name='标题 1'] => h1:fresh
                p[style-name='标题 2'] => h2:fresh
                p[style-name='标题 3'] => h3:fresh
            """
        )
        
        html_content = result.value
        
        # 如果有警告信息，打印出来
        if result.messages:
            print('\n转换警告信息:')
            for msg in result.messages:
                print(f'  - {msg}')
    
    # 包装成完整的 HTML 文档
    full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>乳腺结节健康管理方案模板</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: "Microsoft YaHei", "微软雅黑", Arial, sans-serif;
            line-height: 1.8;
            color: #333;
            background-color: #f5f5f5;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        h1 {{
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin: 30px 0 20px 0;
            padding-bottom: 10px;
            border-bottom: 3px solid #3498db;
        }}
        
        h2 {{
            font-size: 20px;
            font-weight: bold;
            color: #34495e;
            margin: 25px 0 15px 0;
            padding-left: 10px;
            border-left: 4px solid #3498db;
        }}
        
        h3 {{
            font-size: 18px;
            font-weight: bold;
            color: #555;
            margin: 20px 0 10px 0;
        }}
        
        p {{
            margin: 10px 0;
            text-indent: 2em;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
        }}
        
        table, th, td {{
            border: 1px solid #444;
        }}
        
        th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
            padding: 12px 8px;
            text-align: left;
        }}
        
        td {{
            padding: 10px 8px;
            vertical-align: top;
        }}
        
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        
        tr:hover {{
            background-color: #e8f4f8;
        }}
        
        strong, b {{
            font-weight: bold;
            color: #2c3e50;
        }}
        
        ul, ol {{
            margin: 10px 0 10px 30px;
        }}
        
        li {{
            margin: 5px 0;
        }}
        
        .highlight {{
            background-color: #fff3cd;
            padding: 2px 4px;
        }}
        
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            
            .container {{
                box-shadow: none;
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
{html_content}
    </div>
</body>
</html>"""
    
    # 写入文件
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(full_html, encoding='utf-8')
    
    print(f'\n✓ 转换完成！')
    print(f'  输出文件: {html_path}')
    print(f'  文件大小: {html_path.stat().st_size / 1024:.1f} KB')


def main():
    if not INPUT_DOCX.exists():
        print(f'错误: 找不到输入文件 {INPUT_DOCX}')
        return
    
    try:
        convert_docx_to_html(INPUT_DOCX, OUTPUT_HTML)
        print(f'\n可以在浏览器中打开查看:\n  {OUTPUT_HTML}')
    except Exception as e:
        print(f'转换失败: {e}')
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

