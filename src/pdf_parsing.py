"""
myrag PDF 解析模块 - 使用 MinerU
"""
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ParsedPage:
    page_num: int
    content: str
    metadata: dict


@dataclass
class ParsedDocument:
    doc_name: str
    pages: List[ParsedPage]
    metadata: dict


class MinerUParser:
    """
    MinerU PDF 解析器封装
    """
    
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
    
    def parse_pdf(self, pdf_path: Path) -> Optional[ParsedDocument]:
        """
        使用 MinerU 解析单个 PDF 文件
        """
        logger.info(f"正在解析 PDF: {pdf_path}")
        
        try:
            # 创建临时输出目录
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_output = Path(temp_dir)
                
                # 调用 MinerU 命令行
                # MinerU 命令: pdf-extract --input input.pdf --output output_dir --formula
                cmd = [
                    "pdf-extract",
                    "--input", str(pdf_path),
                    "--output", str(temp_output),
                    "--formula"
                ]
                
                logger.info(f"执行命令: {' '.join(cmd)}")
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result.returncode != 0:
                    logger.error(f"MinerU 执行失败: {result.stderr}")
                    return None
                
                # 查找输出文件 - MinerU 会生成多个文件
                # 通常会有 .md 文件和 .json 文件
                md_files = list(temp_output.glob("*.md"))
                json_files = list(temp_output.glob("*.json"))
                
                if not md_files and not json_files:
                    logger.error(f"未找到 MinerU 输出文件")
                    return None
                
                # 优先读取 JSON 格式，其次是 Markdown
                doc_data = self._parse_mineru_output(temp_output, pdf_path.stem)
                
                if doc_data:
                    if self.output_dir:
                        self._save_parsed_result(doc_data)
                    return doc_data
                
                return None
                
        except Exception as e:
            logger.error(f"解析 PDF 失败 {pdf_path}: {e}")
            return None
    
    def _parse_mineru_output(self, output_dir: Path, doc_name: str) -> Optional[ParsedDocument]:
        """
        解析 MinerU 的输出结果
        """
        pages = []
        
        # 尝试读取 Markdown 文件
        md_files = list(output_dir.glob("*.md"))
        if md_files:
            md_file = md_files[0]
            content = md_file.read_text(encoding="utf-8")
            
            # 简单按页面分割（MinerU 的输出可能包含页码标记）
            # 这里做简化处理，整个文档作为一个页面，或者尝试提取页码
            page_content = ParsedPage(
                page_num=1,
                content=content,
                metadata={"source": "markdown"}
            )
            pages.append(page_content)
        
        # 如果有 JSON 文件，尝试获取更详细的结构
        json_files = list(output_dir.glob("*.json"))
        for json_file in json_files:
            try:
                data = json.loads(json_file.read_text(encoding="utf-8"))
                # 根据 MinerU 的 JSON 结构解析页面
                if "pages" in data:
                    for i, page_data in enumerate(data["pages"]):
                        page_text = page_data.get("text", "")
                        if page_text.strip():
                            pages.append(ParsedPage(
                                page_num=i+1,
                                content=page_text,
                                metadata=page_data.get("metadata", {})
                            ))
            except Exception as e:
                logger.warning(f"解析 JSON 文件失败 {json_file}: {e}")
        
        if not pages:
            return None
        
        return ParsedDocument(
            doc_name=doc_name,
            pages=pages,
            metadata={"source": "mineru"}
        )
    
    def _save_parsed_result(self, doc: ParsedDocument):
        """
        保存解析结果
        """
        if not self.output_dir:
            return
        
        output_file = self.output_dir / f"{doc.doc_name}.json"
        result = {
            "doc_name": doc.doc_name,
            "metadata": doc.metadata,
            "pages": [
                {
                    "page_num": p.page_num,
                    "content": p.content,
                    "metadata": p.metadata
                }
                for p in doc.pages
            ]
        }
        
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"解析结果已保存: {output_file}")
    
    def parse_directory(self, pdf_dir: Path) -> List[ParsedDocument]:
        """
        批量解析目录下的所有 PDF
        """
        pdf_files = list(pdf_dir.glob("*.pdf"))
        results = []
        
        for pdf_file in pdf_files:
            doc = self.parse_pdf(pdf_file)
            if doc:
                results.append(doc)
        
        logger.info(f"成功解析 {len(results)}/{len(pdf_files)} 个 PDF")
        return results


# 备用方案：如果 MinerU 不可用，使用简单的文本提取
class SimplePDFParser:
    """
    简单 PDF 解析器（备用方案）
    """
    
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
    
    def parse_pdf(self, pdf_path: Path) -> Optional[ParsedDocument]:
        """
        使用 PyPDF2 简单解析 PDF
        """
        try:
            import PyPDF2
            
            pages = []
            with pdf_path.open("rb") as f:
                reader = PyPDF2.PdfReader(f)
                for i, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text.strip():
                        pages.append(ParsedPage(
                            page_num=i+1,
                            content=text,
                            metadata={}
                        ))
            
            if pages:
                doc = ParsedDocument(
                    doc_name=pdf_path.stem,
                    pages=pages,
                    metadata={"source": "simple"}
                )
                if self.output_dir:
                    self._save_parsed_result(doc)
                return doc
            
            return None
            
        except ImportError:
            logger.error("PyPDF2 未安装，无法使用简单解析器")
            # 提供替代方案：创建简单的占位文档
            return self._create_fallback_doc(pdf_path)
        except Exception as e:
            logger.error(f"简单解析失败 {pdf_path}: {e}")
            # 提供替代方案
            return self._create_fallback_doc(pdf_path)
    
    def _create_fallback_doc(self, pdf_path: Path) -> ParsedDocument:
        """
        创建一个简单的占位文档，确保流程不会中断
        """
        logger.info(f"创建占位文档: {pdf_path.stem}")
        return ParsedDocument(
            doc_name=pdf_path.stem,
            pages=[
                ParsedPage(
                    page_num=1,
                    content=f"文档: {pdf_path.name}\n\n(注：解析器未完全解析此文档的内容)",
                    metadata={"source": "fallback"}
                )
            ],
            metadata={"source": "fallback"}
        )
    
    def _save_parsed_result(self, doc: ParsedDocument):
        if not self.output_dir:
            return
        
        output_file = self.output_dir / f"{doc.doc_name}.json"
        result = {
            "doc_name": doc.doc_name,
            "metadata": doc.metadata,
            "pages": [
                {
                    "page_num": p.page_num,
                    "content": p.content,
                    "metadata": p.metadata
                }
                for p in doc.pages
            ]
        }
        
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    
    def parse_directory(self, pdf_dir: Path) -> list:
        """
        解析目录中的所有 PDF 文件
        """
        pdf_files = list(pdf_dir.glob("*.pdf"))
        results = []
        
        for pdf_file in pdf_files:
            doc = self.parse_pdf(pdf_file)
            if doc:
                results.append(doc)
                if self.output_dir:
                    self._save_parsed_result(doc)
        
        logger.info(f"Successfully parsed {len(results)}/{len(pdf_files)} PDFs")
        return results
