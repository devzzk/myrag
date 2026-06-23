"""
myrag 文本分块模块
"""
import json
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

# Optional imports with fallback
try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    HAS_LANGCHAIN = True
except ImportError:
    HAS_LANGCHAIN = False

try:
    import tiktoken
    HAS_TIKTOKEN = True
except ImportError:
    HAS_TIKTOKEN = False


@dataclass
class DocumentChunk:
    chunk_id: str
    doc_name: str
    page_num: Optional[int]
    content: str
    metadata: Dict
    chunk_index: int


class TextSplitter:
    """
    文本分块器
    """
    
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 100,
        encoding_name: str = "cl100k_base"
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding_name = encoding_name
        
        # Initialize text splitter if langchain is available
        if HAS_LANGCHAIN:
            self.splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                separators=["\n\n", "\n", "。", "！", "？", "!", "?", " ", ""],
            )
        else:
            self.splitter = None
    
    def count_tokens(self, text: str) -> int:
        """
        统计文本 token 数
        """
        if HAS_TIKTOKEN:
            try:
                enc = tiktoken.get_encoding(self.encoding_name)
                return len(enc.encode(text))
            except Exception:
                pass
        # Fallback: estimate by characters
        return len(text) // 4  # Rough estimate for Chinese
    
    def split_text(
        self,
        text: str,
        doc_name: str,
        page_num: Optional[int] = None,
        metadata: Optional[Dict] = None
    ) -> List[DocumentChunk]:
        """
        分割单段文本
        """
        if metadata is None:
            metadata = {}
        
        chunks = []
        
        if self.splitter:
            # Use langchain splitter
            split_texts = self.splitter.split_text(text)
        else:
            # Fallback: simple splitting
            split_texts = self._simple_split(text)
        
        for i, chunk_content in enumerate(split_texts):
            chunk_id = f"{doc_name}_{page_num if page_num else 'all'}_{i}"
            chunks.append(DocumentChunk(
                chunk_id=chunk_id,
                doc_name=doc_name,
                page_num=page_num,
                content=chunk_content,
                metadata={
                    **metadata,
                    "token_count": self.count_tokens(chunk_content)
                },
                chunk_index=i
            ))
        
        return chunks
    
    def _simple_split(self, text: str) -> List[str]:
        """
        Simple fallback splitting method
        """
        chunks = []
        current = ""
        sentences = text.split("。")
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            sentence += "。"
            
            if len(current) + len(sentence) <= self.chunk_size:
                current += sentence
            else:
                if current:
                    chunks.append(current)
                current = sentence
        
        if current:
            chunks.append(current)
        
        return chunks
    
    def split_parsed_document(self, parsed_doc: Dict) -> List[DocumentChunk]:
        """
        分割已解析的文档（从 JSON 读取）
        """
        doc_name = parsed_doc.get("doc_name", "unknown")
        all_chunks = []
        
        for page_data in parsed_doc.get("pages", []):
            page_num = page_data.get("page_num")
            content = page_data.get("content", "")
            
            if content.strip():
                page_chunks = self.split_text(
                    content,
                    doc_name=doc_name,
                    page_num=page_num,
                    metadata=page_data.get("metadata", {})
                )
                all_chunks.extend(page_chunks)
        
        return all_chunks
    
    def split_directory(self, input_dir: Path, output_dir: Optional[Path] = None) -> Dict[str, List[DocumentChunk]]:
        """
        批量处理目录下的已解析文档
        """
        all_results = {}
        
        json_files = list(input_dir.glob("*.json"))
        
        for json_file in json_files:
            try:
                with json_file.open("r", encoding="utf-8") as f:
                    parsed_doc = json.load(f)
                
                chunks = self.split_parsed_document(parsed_doc)
                all_results[json_file.stem] = chunks
                
                if output_dir:
                    self._save_chunks(chunks, output_dir, json_file.stem)
                
            except Exception as e:
                print(f"处理文件失败 {json_file}: {e}")
        
        return all_results
    
    def _save_chunks(self, chunks: List[DocumentChunk], output_dir: Path, doc_name: str):
        """
        保存分块结果
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        result = {
            "doc_name": doc_name,
            "chunk_count": len(chunks),
            "chunks": [
                {
                    "chunk_id": c.chunk_id,
                    "doc_name": c.doc_name,
                    "page_num": c.page_num,
                    "content": c.content,
                    "metadata": c.metadata,
                    "chunk_index": c.chunk_index
                }
                for c in chunks
            ]
        }
        
        output_file = output_dir / f"{doc_name}.json"
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
