"""
myrag 向量化与存储模块
"""
import json
import pickle
import random
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

# Optional imports with fallback
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False

from tqdm import tqdm
from src.api_requests import APIProcessor
from src.text_splitter import DocumentChunk


class VectorStore:
    """
    向量存储类 - 支持 FAISS 或简单内存存储
    """
    
    def __init__(
        self,
        dimension: int = 1536,
        index_type: str = "flat",
        demo_mode: bool = False
    ):
        self.dimension = dimension
        self.index_type = index_type
        self.index = None
        self.documents: List[Dict] = []
        self.demo_mode = demo_mode
        self._demo_mode_locked = demo_mode  # 如果初始化时就设置了演示模式，则锁定
        
        if not demo_mode:
            self.api = APIProcessor()
        
        # Initialize FAISS index if available
        if HAS_FAISS and HAS_NUMPY:
            self.index = faiss.IndexFlatIP(dimension)
        else:
            # Use simple in-memory storage as fallback
            self.embeddings: List[List[float]] = []
    
    def _generate_demo_embedding(self, text: str) -> List[float]:
        """
        生成演示用的随机向量（离线模式）
        """
        # 基于文本内容生成伪随机向量，保证相同文本产生相同向量
        seed = sum(ord(c) for c in text) % 10000
        rng = random.Random(seed)
        vec = [rng.uniform(-1, 1) for _ in range(self.dimension)]
        # L2 归一化
        norm = sum(x*x for x in vec) ** 0.5
        vec = [x/norm for x in vec]
        return vec
    
    def add_documents(
        self,
        chunks: List[DocumentChunk],
        batch_size: int = 10
    ):
        """
        添加文档到向量库
        """
        if not chunks:
            return
        
        # Get embeddings
        texts = [c.content for c in chunks]
        embeddings_list = []
        
        if self.demo_mode:
            # 演示模式：使用随机向量
            for text in tqdm(texts, desc="向量化（演示模式）"):
                embeddings_list.append(self._generate_demo_embedding(text))
        else:
            # 真实模式：调用 API
            for i in tqdm(range(0, len(texts), batch_size), desc="向量化"):
                batch = texts[i:i+batch_size]
                try:
                    batch_embeddings = self.api.get_embeddings(batch)
                    embeddings_list.extend(batch_embeddings)
                except Exception as e:
                    print(f"向量化失败: {e}")
                    print("切换到演示模式...")
                    self.demo_mode = True
                    for text in texts[i:]:
                        embeddings_list.append(self._generate_demo_embedding(text))
                    break
        
        # Store documents
        for chunk in chunks:
            self.documents.append({
                "chunk_id": chunk.chunk_id,
                "doc_name": chunk.doc_name,
                "page_num": chunk.page_num,
                "content": chunk.content,
                "metadata": chunk.metadata
            })
        
        # Add to index
        if HAS_FAISS and HAS_NUMPY and self.index is not None:
            if embeddings_list:
                arr = np.array(embeddings_list, dtype=np.float32)
                self.index.add(arr)
        else:
            if not hasattr(self, 'embeddings'):
                self.embeddings = []
            self.embeddings.extend(embeddings_list)
    
    def search(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict]:
        """
        搜索相似文档
        """
        if not self.documents:
            return []
        
        # Get query embedding
        if self.demo_mode:
            query_emb = self._generate_demo_embedding(query)
        else:
            try:
                query_emb = self.api.get_embeddings([query])[0]
            except Exception as e:
                print(f"查询向量化失败: {e}")
                print("切换到演示模式...")
                self.demo_mode = True
                query_emb = self._generate_demo_embedding(query)
        
        # Search
        if HAS_FAISS and HAS_NUMPY and self.index is not None:
            query_arr = np.array([query_emb], dtype=np.float32)
            scores, indices = self.index.search(query_arr, min(top_k, len(self.documents)))
            results = []
            for i, idx in enumerate(indices[0]):
                if idx < len(self.documents):
                    doc = self.documents[idx].copy()
                    doc["score"] = float(scores[0][i])
                    results.append(doc)
            return results
        else:
            # Simple cosine similarity search
            results = []
            for i, doc in enumerate(self.documents):
                if i < len(self.embeddings):
                    emb = self.embeddings[i]
                    # Cosine similarity
                    dot = sum(a*b for a, b in zip(query_emb, emb))
                    doc = doc.copy()
                    doc["score"] = dot
                    results.append(doc)
            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:top_k]
    
    def save(self, save_dir: Path):
        """
        保存向量库
        """
        save_dir.mkdir(parents=True, exist_ok=True)
        
        docs_file = save_dir / "documents.pkl"
        with open(docs_file, 'wb') as f:
            pickle.dump({
                "documents": self.documents,
                "demo_mode": self.demo_mode,
                "dimension": self.dimension
            }, f)
        
        if HAS_FAISS and HAS_NUMPY and self.index is not None:
            faiss_file = save_dir / "index.faiss"
            faiss.write_index(self.index, str(faiss_file))
        else:
            emb_file = save_dir / "embeddings.pkl"
            with open(emb_file, 'wb') as f:
                pickle.dump(self.embeddings if hasattr(self, 'embeddings') else [], f)
    
    def load(self, load_dir: Path):
        """
        加载向量库
        """
        docs_file = load_dir / "documents.pkl"
        if docs_file.exists():
            with open(docs_file, 'rb') as f:
                data = pickle.load(f)
                self.documents = data.get("documents", [])
                # 如果初始化时没有锁定演示模式，则使用保存的模式
                if not self._demo_mode_locked:
                    self.demo_mode = data.get("demo_mode", False)
                self.dimension = data.get("dimension", 1536)
        
        faiss_file = load_dir / "index.faiss"
        if faiss_file.exists() and HAS_FAISS:
            self.index = faiss.read_index(str(faiss_file))
        else:
            emb_file = load_dir / "embeddings.pkl"
            if emb_file.exists():
                with open(emb_file, 'rb') as f:
                    self.embeddings = pickle.load(f)
            else:
                self.embeddings = []
    
    def clear(self):
        """
        清空向量库
        """
        self.documents = []
        if HAS_FAISS and HAS_NUMPY:
            self.index = faiss.IndexFlatIP(self.dimension)
        else:
            self.embeddings = []


class IngestionPipeline:
    """
    向量化流水线
    """
    
    def __init__(self, config, demo_mode: bool = False):
        self.config = config
        self.vector_store = VectorStore(demo_mode=demo_mode)
    
    def process_chunked_dir(
        self,
        chunked_dir: Optional[Path] = None,
        save_dir: Optional[Path] = None
    ) -> int:
        """
        处理分块后的文档目录
        """
        if chunked_dir is None:
            chunked_dir = self.config.chunked_dir
        
        if not chunked_dir.exists():
            return 0
        
        all_chunks = []
        
        # Load all chunk files
        for chunk_file in chunked_dir.glob("*.json"):
            with open(chunk_file, 'r', encoding='utf-8') as f:
                chunks_data = json.load(f)
                # 兼容两种数据结构：直接是数组或者有 chunks 字段的对象
                if isinstance(chunks_data, list):
                    chunks_list = chunks_data
                else:
                    chunks_list = chunks_data.get("chunks", [])
                
                for chunk_data in chunks_list:
                    chunk = DocumentChunk(
                        chunk_id=chunk_data["chunk_id"],
                        doc_name=chunk_data["doc_name"],
                        page_num=chunk_data.get("page_num"),
                        content=chunk_data["content"],
                        metadata=chunk_data.get("metadata", {}),
                        chunk_index=chunk_data.get("chunk_index", 0)
                    )
                    all_chunks.append(chunk)
        
        # Add to vector store
        if all_chunks:
            self.vector_store.add_documents(all_chunks)
            
            if save_dir is not None:
                self.vector_store.save(save_dir)
        
        return len(all_chunks)
