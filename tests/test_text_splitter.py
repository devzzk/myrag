"""
Tests for text_splitter module
"""
import sys
import json
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.text_splitter import TextSplitter, DocumentChunk


class TestDocumentChunk:
    """Test DocumentChunk dataclass"""
    
    def test_document_chunk_creation(self):
        """Test creating a DocumentChunk"""
        chunk = DocumentChunk(
            chunk_id="test_1",
            doc_name="test_doc",
            page_num=1,
            content="This is test content",
            metadata={"key": "value"},
            chunk_index=0
        )
        
        assert chunk.chunk_id == "test_1"
        assert chunk.doc_name == "test_doc"
        assert chunk.page_num == 1
        assert chunk.content == "This is test content"
        assert chunk.metadata == {"key": "value"}
        assert chunk.chunk_index == 0


class TestTextSplitter:
    """Test TextSplitter class"""
    
    def test_initialization_default(self):
        """Test default initialization"""
        splitter = TextSplitter()
        
        assert splitter.chunk_size == 500
        assert splitter.chunk_overlap == 100
    
    def test_initialization_custom(self):
        """Test custom initialization"""
        splitter = TextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        assert splitter.chunk_size == 1000
        assert splitter.chunk_overlap == 200
    
    def test_count_tokens(self, sample_text):
        """Test token counting"""
        splitter = TextSplitter()
        
        token_count = splitter.count_tokens(sample_text)
        
        assert isinstance(token_count, int)
        assert token_count > 0
    
    def test_split_text_single_chunk(self):
        """Test splitting a short text into single chunk"""
        splitter = TextSplitter(chunk_size=1000)
        short_text = "这是一段很短的文本。"
        
        chunks = splitter.split_text(
            short_text,
            doc_name="test",
            page_num=1
        )
        
        assert len(chunks) == 1
        assert chunks[0].content == short_text
    
    def test_split_text_multiple_chunks(self, sample_text):
        """Test splitting a longer text into multiple chunks"""
        splitter = TextSplitter(chunk_size=50, chunk_overlap=10)
        
        chunks = splitter.split_text(
            sample_text,
            doc_name="test_doc",
            page_num=1
        )
        
        assert len(chunks) >= 1
        for chunk in chunks:
            assert isinstance(chunk, DocumentChunk)
            assert chunk.doc_name == "test_doc"
            assert chunk.page_num == 1
    
    def test_split_parsed_document(self, sample_parsed_doc):
        """Test splitting a parsed document"""
        splitter = TextSplitter()
        
        chunks = splitter.split_parsed_document(sample_parsed_doc)
        
        assert len(chunks) >= 2
        assert chunks[0].doc_name == "test_doc"
        page_nums = set(chunk.page_num for chunk in chunks)
        assert 1 in page_nums
        assert 2 in page_nums
    
    def test_split_directory(self, temp_dir, sample_parsed_doc):
        """Test splitting documents from a directory"""
        # Create test input directory
        input_dir = temp_dir / "input"
        input_dir.mkdir()
        
        # Save sample document
        with (input_dir / "test_doc.json").open("w", encoding="utf-8") as f:
            json.dump(sample_parsed_doc, f, ensure_ascii=False)
        
        # Create output directory
        output_dir = temp_dir / "output"
        
        splitter = TextSplitter()
        results = splitter.split_directory(input_dir, output_dir)
        
        assert "test_doc" in results
        assert len(results["test_doc"]) > 0
        
        # Check output file
        assert (output_dir / "test_doc.json").exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
