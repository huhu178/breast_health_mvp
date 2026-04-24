"""
将comprehensive_report.html拆分为组件化模板
"""
import os
import re

def split_template():
    """拆分模板为多个组件"""

    # 读取原模板
    template_path = r'D:\1work\20251016\breast_health_mvp\frontend\templates\reports\comprehensive_report.html'
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 输出目录
    sections_dir = r'D:\1work\20251016\breast_health_mvp\frontend\templates\reports\sections'
    os.makedirs(sections_dir, exist_ok=True)

    # ==========================================
    # 1. 提取CSS样式（单独文件）
    # ==========================================
    styles_start = content.find('<style>')
    styles_end = content.find('</style>') + len('</style>')
    styles = content[styles_start:styles_end]

    # ==========================================
    # 2. 创建公共头部（封面+寄语）
    # ==========================================
    header_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{{{ nodule_type_name }}}}结节健康管理方案</title>
    {styles}
</head>
<body>
    <div class="container">
        <!-- 封面页 -->
        <div class="cover-page">
            <h1>{{{{ patient_name }}}}女士/先生</h1>
            <h2>结节健康管理方案</h2>
            <p style="margin-top: 40px; font-size: 16px;">报告编号: {{{{ report_code }}}}</p>
            <p style="font-size: 14px;">生成日期: {{{{ report_date }}}}</p>
        </div>

        <div class="page-break"></div>

        <!-- 寄语页 -->
        <div class="greeting-page">
            <h2>结节健康管理团队给您的寄语</h2>
            <h3>尊敬的{{{{ patient_name }}}}女士/先生：</h3>
            <p><strong>感谢您对我们的信任！</strong>我们将竭诚为您提供科学、专业的结节健康管理指导及全程管家服务。我们坚持以新医学模式（生理—心理—社会）为核心，通过多维度干预有效管控结节风险、改善体质基础。目前，我们已形成<strong>结节风险评估、生活方式干预、中医体质调理、影像复查跟踪、情绪与压力管理、长期随访计划</strong>等服务板块，为您提供全方位守护。</p>

            <h3>结节健康管理团队郑重承诺：</h3>
            <ul>
                <li>健康管理师严格遵守公司的服务标准流程；</li>
                <li>认真执行、落实每一项服务内容，同时也接受您的监督；</li>
                <li>承担信息保密责任，未经您的许可，不向第三方泄漏个人信息。</li>
            </ul>

            <p>下列结节健康管理方案是基于您的基础信息、遗传史、疾病史、饮食生活习惯及各项检查报告经综合分析评估后而制定的。我们秉承"结节可防可控，体质调理是根本"的理念，重点从饮食、运动、情绪三大维度入手，帮助您改善内环境、降低结节进展风险。若您有更多信息补充（如近期复查结果、症状变化等），欢迎随时联系专属健康管理师，我们将及时更新您的健康档案与管理策略。</p>

            <p>为了您的健康，希望您配合健康管理师的工作；如您有关于健康的任何需求，均可与您的专属健康管理师联系，您的健康是我们最大的追求和成就！</p>

            <p style="text-align: right; margin-top: 30px;"><strong>结节健康管理团队</strong></p>
        </div>

        <div class="page-break"></div>
'''

    with open(os.path.join(sections_dir, '_common_header.html'), 'w', encoding='utf-8') as f:
        f.write(header_content)
    print('Created: _common_header.html')

    # ==========================================
    # 3. 创建公共尾部（健康建议+免责声明+footer）
    # ==========================================
    # 从原文件中提取"二、乳腺结节健康管理建议"之后的内容
    advice_start_marker = '<!-- 二、健康管理建议 -->'
    advice_start = content.find(advice_start_marker)

    if advice_start == -1:
        # 如果找不到注释，尝试查找实际标题
        advice_start = content.find('<h1>二、乳腺结节健康管理建议</h1>')

    # 提取到文件末尾前
    footer_start = content.find('</div>\n</body>')

    if advice_start != -1 and footer_start != -1:
        advice_content = content[advice_start:footer_start]
        # 替换"乳腺结节"为通用描述
        advice_content = advice_content.replace('乳腺结节健康管理建议', '结节健康管理建议')
        advice_content = advice_content.replace('乳腺结节', '结节')
    else:
        # 如果找不到，创建一个基本的模板
        advice_content = '''
        <!-- 二、健康管理建议 -->
        <h1>二、结节健康管理建议</h1>
        <p>（健康管理建议将在此处展示）</p>
        '''

    # 添加免责声明和footer
    footer_content = advice_content + '''

        <!-- 免责声明 -->
        <div class="disclaimer">
            <h3>重要声明</h3>
            <p>本报告仅供个人健康管理与自我参考，不能作为疾病诊断和处置唯一依据。如有身体不适或报告异常，请及时到正规医院就诊并由专科医师进一步评估。本服务不代替医生诊疗。</p>
        </div>

        <!-- Footer -->
        <footer>
            <h3>联系我们</h3>
            <p><strong>健康管理热线：</strong>400-XXX-XXXX</p>
            <p><strong>在线咨询：</strong>关注微信公众号"结节健康管理"</p>
            <p style="text-align: center; margin-top: 20px; font-size: 12px;">
                © 2025 结节健康管理平台 | 报告编号: {{ report_code }}
            </p>
        </footer>
    </div>
</body>
</html>
'''

    with open(os.path.join(sections_dir, '_common_footer.html'), 'w', encoding='utf-8') as f:
        f.write(footer_content)
    print('Created: _common_footer.html')

    print('\nTemplate split completed!')
    print(f'Output directory: {sections_dir}')


if __name__ == '__main__':
    split_template()
