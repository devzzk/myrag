"""
Test utilities and helper functions
"""
import sys
import json
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any


def create_test_pdf(output_path: Path, content: str = "Test PDF content"):
    """
    Create a minimal test PDF file for testing
    
    Note: This creates a dummy file, not a real PDF.
    For real PDF testing, use actual PDF files.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create a minimal file (not a real PDF but enough for some tests)
    with output_path.open("w") as f:
        f.write(f"%PDF-1.4\n{content}")
    
    return output_path


def create_test_chunked_data(output_dir: Path, num_docs: int = 3, num_chunks: int = 5):
    """
    Create test chunked data in JSON format
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for doc_idx in range(num_docs):
        doc_data = {
            "doc_name": f"test_doc_{doc_idx}",
            "chunk_count": num_chunks,
            "chunks": [
                {
                    "chunk_id": f"chunk_{doc_idx}_{i}",
                    "doc_name": f"test_doc_{doc_idx}",
                    "page_num": (i // 2) + 1,
                    "content": f"这是测试文档 {doc_idx} 的第 {i} 个分块内容。关于AI和RAG的讨论。",
                    "metadata": {"token_count": 20},
                    "chunk_index": i
                }
                for i in range(num_chunks)
            ]
        }
        
        output_file = output_dir / f"test_doc_{doc_idx}.json"
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(doc_data, f, ensure_ascii=False, indent=2)
    
    return output_dir


def get_test_data_path() -> Path:
    """Get path to test data directory"""
    return Path(__file__).parent / "test_data"


def load_sample_parsed_doc() -> Dict[str, Any]:
    """Load sample parsed document from test data"""
    sample_path = get_test_data_path() / "sample_parsed_doc.json"
    with sample_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def run_tests_quiet():
    """Run pytest quietly"""
    import pytest
    result = pytest.main(["-xvs", "tests/"])
    return result


if __name__ == "__main__":
    print("Test utilities loaded!")
    print(f"Test data path: {get_test_data_path()}")
    
    sample_doc = load_sample_parsed_doc()
    print(f"Loaded sample doc: {sample_doc['doc_name']}")
    print(f"Number of pages: {len(sample_doc['pages'])}")
