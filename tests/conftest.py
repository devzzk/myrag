"""
Pytest configuration and fixtures
"""
import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_text():
    """Sample Chinese text for testing"""
    return """这是一段测试文本。
    这是第二句话。
    RAG（检索增强生成）是一种结合检索和生成的技术。
    它可以用于构建知识库问答系统。
    个人知识库可以帮助我们整理和查询信息。"""


@pytest.fixture
def sample_parsed_doc():
    """Sample parsed document structure"""
    return {
        "doc_name": "test_doc",
        "metadata": {"source": "test"},
        "pages": [
            {
                "page_num": 1,
                "content": "这是第一页的内容。包含了一些测试信息。",
                "metadata": {}
            },
            {
                "page_num": 2,
                "content": "这是第二页的内容。继续测试。",
                "metadata": {}
            }
        ]
    }
