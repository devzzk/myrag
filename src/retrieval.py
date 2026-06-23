"""
myrag 检索模块
"""
from typing import List, Dict
from src.ingestion import VectorStore


class Retriever:
    """
    检索器 - 封装向量搜索
    """
    
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
    
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        min_score: float = 0.0
    ) -> List[Dict]:
        """
        检索相关文档
        """
        results = self.vector_store.search(query, top_k)
        
        # 过滤低分结果
        filtered = [r for r in results if r["score"] >= min_score]
        
        return filtered
    
    def format_context(self, results: List[Dict]) -> str:
        """
        格式化检索结果为 RAG 上下文
        """
        if not results:
            return "未找到相关文档"
        
        context_parts = []
        
        for i, result in enumerate(results, 1):
            doc = result
            score = result["score"]
            
            source_info = f"文档: {doc['doc_name']}"
            if doc.get("page_num"):
                source_info += f" | 页码: {doc['page_num']}"
            source_info += f" | 相关度: {score:.2f}"
            
            context_parts.append(f"[{i}] {source_info}\n{doc['content']}")
        
        return "\n\n---\n\n".join(context_parts)
    
    def get_references(self, results: List[Dict]) -> List[str]:
        """
        提取引用信息
        """
        references = []
        
        for result in results:
            doc = result
            ref = f"{doc['doc_name']}"
            if doc.get("page_num"):
                ref += f" (第{doc['page_num']}页)"
            references.append(ref)
        
        return references
