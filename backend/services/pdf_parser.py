"""
PDF解析服务
用于从PDF文件中提取文本内容
支持文本PDF和扫描件PDF（OCR）
"""
import os
import pdfplumber
from typing import Optional

# OCR相关库（可选，如果未安装则跳过OCR功能）
try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False
    # print("⚠️ pdf2image未安装，OCR功能将不可用。安装命令: pip install pdf2image")

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False
    # print("⚠️ pytesseract未安装，OCR功能将不可用。安装命令: pip install pytesseract")


class PDFParser:
    """PDF解析器"""
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> Optional[str]:
        """
        从PDF文件中提取文本内容
        
        Args:
            file_path: PDF文件路径
            
        Returns:
            str: 提取的文本内容，如果解析失败返回None
        """
        try:
            if not os.path.exists(file_path):
                print(f"❌ PDF文件不存在: {file_path}")
                return None
            
            print(f"📄 开始解析PDF: {file_path}")
            text_content = []
            
            with pdfplumber.open(file_path) as pdf:
                total_pages = len(pdf.pages)
                print(f"📄 PDF总页数: {total_pages}")
                
                for page_num, page in enumerate(pdf.pages, 1):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_content.append(f"--- 第{page_num}页 ---\n{page_text}\n")
                            print(f"✅ 第{page_num}页提取成功，文本长度: {len(page_text)}")
                        else:
                            print(f"⚠️ 第{page_num}页未提取到文本（可能是扫描件）")
                    except Exception as e:
                        print(f"⚠️ 第{page_num}页提取失败: {str(e)}")
                        continue
            
            full_text = "\n".join(text_content)
            
            if not full_text.strip():
                # 尝试使用OCR识别扫描件
                print(f"⚠️ PDF未提取到文本内容，尝试使用OCR识别扫描件...")
                ocr_text = PDFParser._extract_text_with_ocr(file_path)
                if ocr_text:
                    print(f"✅ OCR识别成功，总文本长度: {len(ocr_text)} 字符")
                    return ocr_text
                else:
                    print(f"❌ OCR识别失败，无法提取文本内容")
                    return None
            
            print(f"✅ PDF解析成功，总文本长度: {len(full_text)} 字符")
            return full_text.strip()
            
        except Exception as e:
            print(f"❌ PDF解析失败: {str(e)}")
            return None
    
    @staticmethod
    def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> Optional[str]:
        """
        从PDF字节流中提取文本内容
        
        Args:
            pdf_bytes: PDF文件的字节流
            
        Returns:
            str: 提取的文本内容，如果解析失败返回None
        """
        import tempfile
        
        try:
            # 创建临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(pdf_bytes)
                temp_path = temp_file.name
            
            try:
                # 解析临时文件
                text = PDFParser.extract_text_from_pdf(temp_path)
                return text
            finally:
                # 清理临时文件
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            print(f"❌ PDF字节流解析失败: {str(e)}")
            return None
    
    @staticmethod
    def _extract_text_with_ocr(file_path: str) -> Optional[str]:
        """
        使用OCR识别扫描件PDF的文本内容
        
        Args:
            file_path: PDF文件路径
            
        Returns:
            str: OCR识别的文本内容，如果失败返回None
        """
        if not PDF2IMAGE_AVAILABLE or not PYTESSERACT_AVAILABLE:
            print("⚠️ OCR功能不可用，请安装pdf2image和pytesseract")
            print("   安装命令: pip install pdf2image pytesseract")
            return None
        
        try:
            print(f"🔍 开始OCR识别: {file_path}")
            
            # 将PDF转换为图片
            print("📸 正在将PDF转换为图片...")
            # 尝试自动检测poppler路径（Windows）
            poppler_path = None
            if os.name == 'nt':  # Windows系统
                # 常见的poppler安装路径
                possible_paths = [
                    r'C:\poppler\Library\bin',
                    r'C:\Program Files\poppler\bin',
                    r'C:\poppler\bin',
                ]
                for path in possible_paths:
                    if os.path.exists(path):
                        poppler_path = path
                        print(f"✅ 找到poppler路径: {poppler_path}")
                        break
                if not poppler_path:
                    print("⚠️ 未找到poppler路径，尝试使用系统PATH中的poppler")
            
            try:
                if poppler_path:
                    images = convert_from_path(file_path, dpi=300, poppler_path=poppler_path)
                else:
                    images = convert_from_path(file_path, dpi=300)
            except Exception as e:
                if 'poppler' in str(e).lower() or 'pdftoppm' in str(e).lower():
                    print("❌ poppler未安装或未在PATH中")
                    print("   Windows: 下载 https://github.com/oschwartz10612/poppler-windows/releases")
                    print("   Linux: sudo apt-get install poppler-utils")
                    print("   macOS: brew install poppler")
                raise
            
            print(f"✅ 成功转换 {len(images)} 页为图片")
            
            # 对每页进行OCR识别
            ocr_texts = []
            for i, image in enumerate(images, 1):
                try:
                    print(f"🔍 正在识别第 {i}/{len(images)} 页...")
                    # 使用中文+英文语言包进行识别
                    text = pytesseract.image_to_string(image, lang='chi_sim+eng')
                    if text.strip():
                        ocr_texts.append(f"--- 第{i}页 ---\n{text.strip()}\n")
                        print(f"✅ 第{i}页识别成功，文本长度: {len(text)} 字符")
                    else:
                        print(f"⚠️ 第{i}页未识别到文本")
                except Exception as e:
                    print(f"⚠️ 第{i}页OCR识别失败: {str(e)}")
                    continue
            
            if not ocr_texts:
                print("❌ OCR未识别到任何文本")
                return None
            
            full_text = "\n".join(ocr_texts)
            print(f"✅ OCR识别完成，总文本长度: {len(full_text)} 字符")
            return full_text.strip()
            
        except Exception as e:
            print(f"❌ OCR识别失败: {str(e)}")
            print("💡 提示：请确保已安装Tesseract OCR")
            print("   Windows: 下载安装 https://github.com/UB-Mannheim/tesseract/wiki")
            print("   或使用云OCR服务（百度OCR、腾讯OCR等）")
            return None


# 创建单例
pdf_parser = PDFParser()

