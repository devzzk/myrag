"""
myrag 配置管理模块
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from pyprojroot import here


@dataclass
class PipelineConfig:
    """
    主流程配置类
    """
    # 基础路径配置
    root_path: Path
    data_dir: Optional[Path] = None
    pdf_dir: Optional[Path] = None
    parsed_dir: Optional[Path] = None
    merged_dir: Optional[Path] = None
    markdown_dir: Optional[Path] = None
    chunked_dir: Optional[Path] = None
    vector_db_dir: Optional[Path] = None
    
    # LLM 配置
    api_provider: str = "dashscope"
    answering_model: str = "qwen-turbo-latest"
    embedding_model: str = "text-embedding-v1"
    
    def __post_init__(self):
        """
        初始化默认路径
        """
        if self.data_dir is None:
            self.data_dir = self.root_path / "data" / "stock_data"
        
        if self.pdf_dir is None:
            self.pdf_dir = self.data_dir / "pdf_reports"
        
        if self.parsed_dir is None:
            self.parsed_dir = self.data_dir / "debug_data" / "01_parsed_reports"
        
        if self.merged_dir is None:
            self.merged_dir = self.data_dir / "debug_data" / "02_merged_reports"
        
        if self.markdown_dir is None:
            self.markdown_dir = self.data_dir / "debug_data" / "03_reports_markdown"
        
        if self.chunked_dir is None:
            self.chunked_dir = self.data_dir / "databases" / "chunked_reports"
        
        if self.vector_db_dir is None:
            self.vector_db_dir = self.data_dir / "databases" / "vector_dbs"
        
        # 确保所有目录存在
        for dir_path in [
            self.data_dir, self.pdf_dir, self.parsed_dir, 
            self.merged_dir, self.markdown_dir, self.chunked_dir, 
            self.vector_db_dir
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)


@dataclass
class RunConfig:
    """
    运行时配置
    """
    # 分块配置
    chunk_size: int = 500
    chunk_overlap: int = 100
    
    # 检索配置
    top_n_retrieval: int = 5
    parent_document_retrieval: bool = False
    use_bm25: bool = False
    llm_reranking: bool = False
    
    # API 配置
    parallel_requests: int = 1
    temperature: float = 0.1
