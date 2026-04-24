import re
from pathlib import Path

# 保守模式：只做三件事
# 1) 以 GBK/GB2312 读取源文件，避免乱码
# 2) 统一设置 UTF-8 meta 与 http-equiv Content-Type
# 3) 为所有 <table> 添加可见边框（不移除任何 mso/注释，不改动其它内容）

INPUT_FILE = Path(r'd:\1work\20251016\breast_health_mvp\模板\乳腺结节健康管理方案模板.html')
OUTPUT_FILE = Path(r'd:\1work\20251016\breast_health_mvp\模板\乳腺结节健康管理方案_常规版_safe.html')


def ensure_utf8_meta(html: str) -> str:
    # 先移除已有 charset 声明，统一为 utf-8
    html = re.sub(r'<meta[^>]*charset=[^>]*>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<meta[^>]*http-equiv\s*=\s*["\']?Content-Type["\']?[^>]*>', '', html, flags=re.IGNORECASE)

    utf8_meta = '<meta charset="utf-8">\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8">'

    if re.search(r'<head[^>]*>', html, flags=re.IGNORECASE):
        html = re.sub(r'(<head[^>]*>)', r'\1\n' + utf8_meta, html, count=1, flags=re.IGNORECASE)
    else:
        html = '<head>' + utf8_meta + '</head>' + html
    return html


def add_border_for_all_tables(html: str) -> str:
    def add_border_to_table(m):
        tag = m.group(0)
        if re.search(r'border\s*=\s*"', tag):
            return tag  # 已有则保留，避免冲突
        return tag[:-1] + ' border="1">'

    html = re.sub(r'<table\b[^>]*>', add_border_to_table, html, flags=re.IGNORECASE)

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

    # 以 GBK 读取（兼容 GB2312）
    raw = INPUT_FILE.read_text(encoding='gbk', errors='ignore')

    html = ensure_utf8_meta(raw)
    html = add_border_for_all_tables(html)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    # 以 UTF-8 写出
    OUTPUT_FILE.write_text(html, encoding='utf-8')
    print(f'已生成保守常规版（UTF-8，含表格边框）：{OUTPUT_FILE}')


if __name__ == '__main__':
    main()
