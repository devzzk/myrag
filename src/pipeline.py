"""
myrag 主流程模块
"""
from pathlib import Path
from typing import Optional, Dict, List
from pyprojroot import here
import logging
import time

from src.config import PipelineConfig, RunConfig
from src.pdf_parsing import MinerUParser, SimplePDFParser
from src.text_splitter import TextSplitter
from src.ingestion import VectorStore, IngestionPipeline
from src.retrieval import Retriever
from src.api_requests import APIProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    RAG 主流程 - 优化版，支持延迟加载
    """
    
    def __init__(
        self,
        config: Optional[PipelineConfig] = None,
        run_config: Optional[RunConfig] = None,
        lazy_load: bool = True,
        demo_mode: bool = False
    ):
        """
        初始化 RAG 流水线
        
        Args:
            config: 配置对象
            run_config: 运行配置
            lazy_load: 是否延迟加载组件（推荐 True，初始化更快）
            demo_mode: 演示模式（不依赖 API）
        """
        start_time = time.time()
        
        if config is None:
            config = PipelineConfig(root_path=here())
        
        if run_config is None:
            run_config = RunConfig()
        
        self.config = config
        self.run_config = run_config
        self.demo_mode = demo_mode
        
        # 延迟加载的组件，使用时才初始化
        self._pdf_parser = None
        self._text_splitter = None
        self._vector_store = None
        self._api = None
        
        # 快速初始化 - 只做必要的检查
        self._vector_store_loaded = False
        
        if not lazy_load:
            # 完全初始化所有组件（不推荐用于启动）
            self._init_all_components()
        else:
            # 只尝试轻量级地加载向量库（如果存在）
            self._try_load_vector_store_quick()
        
        elapsed = time.time() - start_time
        logger.info(f"RAG 流水线初始化完成，耗时: {elapsed:.2f}秒")
    
    def _init_all_components(self):
        """初始化所有组件（仅在需要时调用）"""
        self.pdf_parser
        self.text_splitter
        self.vector_store
        self.api
    
    @property
    def pdf_parser(self):
        """延迟初始化 PDF 解析器"""
        if self._pdf_parser is None:
            logger.info("正在初始化 PDF 解析器...")
            self._pdf_parser = MinerUParser(output_dir=self.config.parsed_dir)
        return self._pdf_parser
    
    @property
    def text_splitter(self):
        """延迟初始化文本分块器"""
        if self._text_splitter is None:
            logger.info("正在初始化文本分块器...")
            self._text_splitter = TextSplitter(
                chunk_size=self.run_config.chunk_size,
                chunk_overlap=self.run_config.chunk_overlap
            )
        return self._text_splitter
    
    @property
    def vector_store(self):
        """延迟初始化向量存储"""
        if self._vector_store is None:
            logger.info("正在初始化向量存储...")
            self._vector_store = VectorStore(demo_mode=self.demo_mode)
            # 设置锁定标志
            self._vector_store._demo_mode_locked = self.demo_mode
            if not self._vector_store_loaded:
                self._try_load_vector_store()
        return self._vector_store
    
    @property
    def api(self):
        """延迟初始化 API 处理器"""
        if self._api is None:
            logger.info("正在初始化 API 处理器...")
            self._api = APIProcessor()
        return self._api
    
    def _try_load_vector_store_quick(self):
        """快速尝试加载向量库（仅检查是否存在，不立即加载）"""
        if self.config.vector_db_dir.exists():
            index_file = self.config.vector_db_dir / "index.faiss"
            docs_file = self.config.vector_db_dir / "documents.pkl"
            if index_file.exists() or docs_file.exists():
                logger.info("检测到存在向量库，将在首次使用时加载")
                self._vector_store_loaded = False
                return True
        return False
    
    def _try_load_vector_store(self):
        """
        尝试加载已有的向量库
        """
        if self.config.vector_db_dir.exists():
            try:
                logger.info("正在加载向量库...")
                if self._vector_store is None:
                    self._vector_store = VectorStore()
                self._vector_store.load(self.config.vector_db_dir)
                self._vector_store_loaded = True
                logger.info(f"向量库加载完成，包含 {len(self._vector_store.documents)} 个文档块")
                return True
            except Exception as e:
                logger.warning(f"加载向量库失败: {e}")
                self._vector_store_loaded = False
        return False
    
    def parse_pdfs(
        self,
        pdf_dir: Optional[Path] = None,
        use_simple_parser: bool = False
    ):
        """
        步骤 1: 解析 PDF 文档
        """
        if pdf_dir is None:
            pdf_dir = self.config.pdf_dir
        
        logger.info(f"开始解析 PDF 目录: {pdf_dir}")
        
        parser = self.pdf_parser
        if use_simple_parser:
            # 使用简单解析器
            parser = SimplePDFParser(output_dir=self.config.parsed_dir)
        
        results = parser.parse_directory(pdf_dir)
        logger.info(f"成功解析 {len(results)} 个 PDF")
        return len(results) > 0
    
    def split_documents(self):
        """
        步骤 2: 分块文档
        """
        logger.info("开始文档分块")
        
        results = self.text_splitter.split_directory(
            input_dir=self.config.parsed_dir,
            output_dir=self.config.chunked_dir
        )
        
        total_chunks = sum(len(chunks) for chunks in results.values())
        logger.info(f"分块完成，共 {total_chunks} 个文档块")
        return total_chunks
    
    def build_vector_store(self):
        """
        步骤 3: 构建向量库
        """
        logger.info("开始构建向量库")
        
        pipeline = IngestionPipeline(self.config, demo_mode=self.demo_mode)
        pipeline.vector_store = self.vector_store
        chunk_count = pipeline.process_chunked_dir(
            chunked_dir=self.config.chunked_dir,
            save_dir=self.config.vector_db_dir
        )
        
        # 更新向量存储引用
        self._vector_store = pipeline.vector_store
        self._vector_store_loaded = True
        
        # 更新 demo_mode（如果 API 失败时切换了）
        if self._vector_store.demo_mode:
            self.demo_mode = True
        
        logger.info(f"向量库构建完成，共 {chunk_count} 个向量")
        return chunk_count
    
    def process_all(
        self,
        pdf_dir: Optional[Path] = None,
        use_simple_parser: bool = False
    ):
        """
        执行完整流程: 解析 -> 分块 -> 向量化
        """
        logger.info("=" * 50)
        logger.info("开始完整 RAG 流程")
        logger.info("=" * 50)
        
        start_time = time.time()
        
        # 步骤 1: 解析 PDF
        parse_success = self.parse_pdfs(pdf_dir, use_simple_parser)
        
        # 步骤 2: 分块
        chunk_count = self.split_documents()
        
        # 步骤 3: 向量化
        vector_count = 0
        if chunk_count > 0:
            vector_count = self.build_vector_store()
        
        elapsed = time.time() - start_time
        logger.info("=" * 50)
        logger.info(f"流程完成！耗时: {elapsed:.2f}秒")
        logger.info(f"  解析: {'成功' if parse_success else '无文档'}")
        logger.info(f"  分块: {chunk_count} 个")
        logger.info(f"  向量化: {vector_count} 个")
        logger.info("=" * 50)
        
        return chunk_count > 0
    
    def query(self, question: str, top_k: int = 5) -> Dict:
        """
        RAG 查询
        """
        # 检查向量库是否为空
        if len(self.vector_store.documents) == 0:
            return {
                "answer": "知识库为空，请先导入文档！",
                "references": [],
                "context": ""
            }
        
        # 检索
        retriever = Retriever(self.vector_store)
        results = retriever.retrieve(question, top_k=top_k)
        
        if not results:
            return {
                "answer": "知识库中没有找到相关信息。",
                "references": [],
                "context": ""
            }
        
        # 构建上下文
        context = retriever.format_context(results)
        references = retriever.get_references(results)
        
        # 根据模式生成回答
        if self.demo_mode or self.vector_store.demo_mode:
            # 演示模式：直接基于检索结果生成简单回答
            answer = self._generate_demo_answer(question, results)
            return {
                "answer": answer,
                "references": references,
                "context": context,
                "confidence": 0.7,
                "retrieval_results": results
            }
        else:
            # 正常模式：调用 LLM 获取答案
            answer_result = self.api.get_answer_from_rag(question, context)
            return {
                "answer": answer_result.get("answer", ""),
                "references": references,
                "context": context,
                "confidence": answer_result.get("confidence", 0.5),
                "retrieval_results": results
            }
    
    def _generate_demo_answer(self, question: str, results: List[Dict]) -> str:
        """
        演示模式：生成简单回答
        """
        if not results:
            return "没有找到相关信息。"
        
        top_doc = results[0]
        content = top_doc.get("content", "")
        
        # 简单截取前 200 字符作为回答
        if len(content) > 200:
            content = content[:200] + "..."
        
        doc_name = top_doc.get("doc_name", "未知文档")
        page_num = top_doc.get("page_num", 1)
        
        answer = f"根据文档《{doc_name}》（第{page_num}页），相关内容如下：\n\n{content}"
        return answer
    
    def get_knowledge_stats(self) -> Dict:
        """
        获取知识库统计信息
        """
        doc_count = 0
        chunk_count = 0
        
        if self._vector_store is not None or self._vector_store_loaded:
            doc_count = len(set(d["doc_name"] for d in self.vector_store.documents))
            chunk_count = len(self.vector_store.documents)
        else:
            # 尝试快速检查分块目录
            chunked_dir = self.config.chunked_dir
            if chunked_dir.exists():
                chunk_files = list(chunked_dir.glob("*.json"))
                doc_count = len(chunk_files)
                # 这里不实际加载文件，只返回文档数量
        
        return {
            "document_count": doc_count,
            "chunk_count": chunk_count,
            "vector_db_path": str(self.config.vector_db_dir)
        }


# 便捷函数
def create_pipeline(
    root_path: Optional[Path] = None,
    lazy_load: bool = True,
    demo_mode: bool = False,
    **kwargs
) -> RAGPipeline:
    """
    创建 RAG 流水线实例（推荐使用延迟加载）
    
    Args:
        root_path: 根目录路径
        lazy_load: 是否延迟加载（默认 True，启动更快）
        demo_mode: 演示模式（默认 False）
        **kwargs: 其他配置参数
    """
    return RAGPipeline(
        config=PipelineConfig(root_path=root_path) if root_path else None,
        run_config=RunConfig(**kwargs),
        lazy_load=lazy_load,
        demo_mode=demo_mode
    )


if __name__ == "__main__":
    print("=" * 50)
    print("myrag RAG 系统")
    print("=" * 50)
    
    # 快速初始化
    pipeline = create_pipeline(lazy_load=True)
    
    # 打印统计信息
    stats = pipeline.get_knowledge_stats()
    print(f"\n知识库状态:")
    print(f"  文档数: {stats['document_count']}")
    print(f"  块数: {stats['chunk_count']}")
