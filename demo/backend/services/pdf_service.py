"""
PDF报告生成服务（多结节系统专用）
使用Playwright将HTML转换为PDF，支持所有多结节类型
"""
import os
import tempfile
import pathlib
from datetime import datetime
from typing import Optional
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


class PDFConfig:
    """PDF生成配置"""
    # 页面设置
    PAGE_FORMAT = 'A4'
    PAGE_WIDTH = 794   # A4宽度（像素，96dpi）
    PAGE_HEIGHT = 1123  # A4高度（像素，96dpi）
    
    # 边距设置（CSS @page 已设置，这里设为0）
    MARGIN_TOP = '0mm'
    MARGIN_BOTTOM = '0mm'
    MARGIN_LEFT = '0mm'
    MARGIN_RIGHT = '0mm'
    
    # 超时设置
    PAGE_LOAD_TIMEOUT = 30000  # 30秒
    WAIT_TIMEOUT = 1000  # 额外等待1秒确保样式应用
    
    # PDF选项
    PRINT_BACKGROUND = True
    PREFER_CSS_PAGE_SIZE = True
    DISPLAY_HEADER_FOOTER = False


class PDFService:
    """PDF生成服务（多结节系统专用）"""
    
    @staticmethod
    def _inject_print_styles(html_content: str) -> str:
        """
        注入PDF打印专用样式（确保所有报告模板都能正确导出）
        
        Args:
            html_content: 原始HTML内容
            
        Returns:
            注入样式后的HTML内容
        """
        pdf_print_styles = """
        <style>
            @media print {
                @page {
                    size: A4;
                    margin: 10mm 12mm;  /* 上下10mm，左右12mm */
                }
                body {
                    margin: 0;
                    padding: 0;
                    background: white;
                    font-size: 11px;
                }
                .container {
                    width: 100% !important;
                    max-width: none !important;
                    box-shadow: none !important;
                    margin: 0 !important;
                    padding: 8px 0 !important;
                    border-radius: 0 !important;
                }
                /* 封面页和寄语页分页 */
                .cover-page {
                    page-break-after: always;
                    min-height: 100vh;
                }
                .greeting-page {
                    page-break-after: always;
                    page-break-inside: avoid;
                }
                /* 分页符 */
                .page-break {
                    display: block !important;
                    page-break-after: always !important;
                    height: 0 !important;
                    margin: 0 !important;
                    padding: 0 !important;
                    visibility: hidden !important;
                }
                .page-break::after {
                    display: none !important;
                }
                /* 表格优化 */
                table {
                    width: 100% !important;
                    table-layout: auto !important;
                    font-size: 10px !important;
                    page-break-inside: auto;
                }
                td, th {
                    word-wrap: break-word !important;
                    word-break: break-word !important;
                    white-space: normal !important;
                    padding: 5px !important;
                }
                tr {
                    page-break-inside: avoid;
                }
                thead {
                    display: table-header-group;
                }
                /* 标题和章节 */
                header {
                    page-break-after: avoid;
                }
                section {
                    page-break-inside: auto;
                }
                h1, h2, h3 {
                    page-break-after: avoid;
                    page-break-inside: avoid;
                }
                h2 + table, h2 + div, h2 + p {
                    page-break-before: avoid;
                }
                /* 免责声明和footer */
                .disclaimer {
                    page-break-before: avoid !important;
                    page-break-inside: avoid !important;
                    page-break-after: avoid !important;
                    background-color: #f5f5f5 !important;
                }
                footer {
                    page-break-before: avoid !important;
                    page-break-inside: avoid !important;
                    -webkit-print-color-adjust: exact !important;
                    print-color-adjust: exact !important;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                    color: white !important;
                    padding: 15px 12px !important;
                    margin-top: 10px !important;
                }
                footer h3, footer strong, footer p {
                    color: white !important;
                }
            }
        </style>
        """
        
        # 将样式注入到HTML的head标签中
        if '</head>' in html_content:
            html_content = html_content.replace('</head>', f'{pdf_print_styles}</head>')
        elif '<body' in html_content:
            html_content = html_content.replace('<body', f'{pdf_print_styles}<body')
        else:
            # 如果没有head或body标签，在开头添加
            html_content = pdf_print_styles + html_content
        
        return html_content
    
    @staticmethod
    def html_to_pdf(
        html_content: str,
        filename: Optional[str] = None,
        timeout: int = PDFConfig.PAGE_LOAD_TIMEOUT
    ) -> bytes:
        """
        将HTML内容转换为PDF（统一入口，支持所有多结节类型）
        
        Args:
            html_content: HTML内容（完整的HTML文档）
            filename: 文件名（可选，仅用于日志）
            timeout: 页面加载超时时间（毫秒）
            
        Returns:
            bytes: PDF文件内容
            
        Raises:
            Exception: PDF生成失败
        """
        if not html_content or not html_content.strip():
            raise ValueError("HTML内容不能为空")
        
        # 注入PDF打印样式
        html_with_styles = PDFService._inject_print_styles(html_content)
        
        # 创建临时HTML文件
        temp_html = None
        try:
            # 使用tempfile创建临时文件，确保自动清理
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.html',
                delete=False,
                encoding='utf-8'
            ) as f:
                f.write(html_with_styles)
                temp_html = f.name
            
            # 转换为绝对路径（Windows兼容）
            temp_html_path = pathlib.Path(temp_html).absolute()
            # 转换为file:// URL格式（Windows使用/分隔符）
            file_url = temp_html_path.as_uri()
            
            print(f"📄 开始生成PDF: {filename or '未命名报告'}")
            print(f"   临时文件: {temp_html}")
            
            # 使用Playwright生成PDF
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                
                try:
                    # 设置A4页面尺寸的viewport
                    page = browser.new_page(
                        viewport={
                            'width': PDFConfig.PAGE_WIDTH,
                            'height': PDFConfig.PAGE_HEIGHT
                        }
                    )
                    
                    # 设置超时
                    page.set_default_timeout(timeout)
                    
                    # 加载HTML文件
                    page.goto(file_url, wait_until='networkidle', timeout=timeout)
                    
                    # 额外等待确保样式完全应用
                    page.wait_for_timeout(PDFConfig.WAIT_TIMEOUT)
                    
                    # 生成PDF
                    pdf_bytes = page.pdf(
                        format=PDFConfig.PAGE_FORMAT,
                        print_background=PDFConfig.PRINT_BACKGROUND,
                        margin={
                            'top': PDFConfig.MARGIN_TOP,
                            'bottom': PDFConfig.MARGIN_BOTTOM,
                            'left': PDFConfig.MARGIN_LEFT,
                            'right': PDFConfig.MARGIN_RIGHT
                        },
                        prefer_css_page_size=PDFConfig.PREFER_CSS_PAGE_SIZE,
                        display_header_footer=PDFConfig.DISPLAY_HEADER_FOOTER
                    )
                    
                    print(f"✅ PDF生成成功，大小: {len(pdf_bytes)} 字节")
                    return pdf_bytes
                    
                except PlaywrightTimeoutError as e:
                    raise Exception(f"PDF生成超时（{timeout}ms）: {str(e)}")
                finally:
                    browser.close()
                    
        except Exception as e:
            print(f"❌ PDF生成失败: {e}")
            import traceback
            traceback.print_exc()
            raise Exception(f"PDF生成失败: {str(e)}")
            
        finally:
            # 确保临时文件被删除
            if temp_html and os.path.exists(temp_html):
                try:
                    os.unlink(temp_html)
                    print(f"🗑️  临时文件已清理: {temp_html}")
                except Exception as cleanup_error:
                    print(f"⚠️  临时文件清理失败: {cleanup_error}")
    
    @staticmethod
    def generate_report_pdf(
        report_html: str,
        report_code: str,
        nodule_type: Optional[str] = None
    ) -> bytes:
        """
        生成多结节报告PDF
        
        Args:
            report_html: 报告HTML内容
            report_code: 报告编号
            nodule_type: 结节类型（可选，用于日志）
            
        Returns:
            bytes: PDF文件内容
        """
        filename = f"健康报告_{report_code}"
        if nodule_type:
            filename += f"_{nodule_type}"
        
        return PDFService.html_to_pdf(report_html, filename)


# 单例实例
pdf_service = PDFService()
