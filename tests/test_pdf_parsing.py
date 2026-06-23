"""
Tests for pdf_parsing module
"""
import sys
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pdf_parsing import (
    ParsedPage,
    ParsedDocument,
    MinerUParser,
    SimplePDFParser
)


class TestParsedPage:
    """Test ParsedPage dataclass"""
    
    def test_parsed_page_creation(self):
        """Test creating a ParsedPage"""
        page = ParsedPage(
            page_num=1,
            content="This is page content",
            metadata={"key": "value"}
        )
        
        assert page.page_num == 1
        assert page.content == "This is page content"
        assert page.metadata == {"key": "value"}


class TestParsedDocument:
    """Test ParsedDocument dataclass"""
    
    def test_parsed_document_creation(self):
        """Test creating a ParsedDocument"""
        pages = [
            ParsedPage(1, "Page 1", {}),
            ParsedPage(2, "Page 2", {})
        ]
        
        doc = ParsedDocument(
            doc_name="test_doc",
            pages=pages,
            metadata={"source": "test"}
        )
        
        assert doc.doc_name == "test_doc"
        assert len(doc.pages) == 2
        assert doc.pages[0].page_num == 1


class TestSimplePDFParser:
    """Test SimplePDFParser class"""
    
    def test_initialization(self, temp_dir):
        """Test parser initialization"""
        parser = SimplePDFParser(output_dir=temp_dir)
        
        assert parser.output_dir == temp_dir
    
    def test_initialization_without_output_dir(self):
        """Test initialization without output_dir"""
        parser = SimplePDFParser()
        
        assert parser.output_dir is None
    
    @pytest.mark.skipif(
        not sys.modules.get('PyPDF2'),
        reason="PyPDF2 not installed"
    )
    def test_parse_non_existent_pdf(self, temp_dir):
        """Test parsing a non-existent PDF"""
        parser = SimplePDFParser(output_dir=temp_dir)
        non_existent_pdf = temp_dir / "does_not_exist.pdf"
        
        result = parser.parse_pdf(non_existent_pdf)
        
        assert result is None
    
    def test_parse_empty_dir(self, temp_dir):
        """Test parsing an empty directory"""
        parser = SimplePDFParser(output_dir=temp_dir)
        empty_dir = temp_dir / "empty"
        empty_dir.mkdir()
        
        results = parser.parse_directory(empty_dir)
        
        assert len(results) == 0


class TestMinerUParser:
    """Test MinerUParser class"""
    
    def test_initialization(self, temp_dir):
        """Test parser initialization"""
        parser = MinerUParser(output_dir=temp_dir)
        
        assert parser.output_dir == temp_dir
    
    def test_initialization_without_output_dir(self):
        """Test initialization without output_dir"""
        parser = MinerUParser()
        
        assert parser.output_dir is None
    
    @patch('subprocess.run')
    def test_parse_pdf_failure(self, mock_subprocess, temp_dir):
        """Test PDF parsing failure handling"""
        parser = MinerUParser(output_dir=temp_dir)
        
        # Mock subprocess to return failure
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "Error message"
        mock_subprocess.return_value = mock_result
        
        test_pdf = temp_dir / "test.pdf"
        test_pdf.touch()
        
        result = parser.parse_pdf(test_pdf)
        
        assert result is None
    
    @patch('subprocess.run')
    def test_parse_directory(self, mock_subprocess, temp_dir):
        """Test parsing a directory"""
        parser = MinerUParser(output_dir=temp_dir)
        
        # Create test PDF files
        pdf_dir = temp_dir / "pdfs"
        pdf_dir.mkdir()
        (pdf_dir / "test1.pdf").touch()
        (pdf_dir / "test2.pdf").touch()
        
        # Mock subprocess to fail for all
        mock_result = Mock()
        mock_result.returncode = 1
        mock_subprocess.return_value = mock_result
        
        results = parser.parse_directory(pdf_dir)
        
        # Should return empty list due to mock failure
        assert isinstance(results, list)


class TestSaveParsedResult:
    """Test saving parsed results"""
    
    def test_save_parsed_document(self, temp_dir):
        """Test saving a parsed document"""
        parser = SimplePDFParser(output_dir=temp_dir)
        
        doc = ParsedDocument(
            doc_name="test_doc",
            pages=[ParsedPage(1, "Test content", {})],
            metadata={"source": "test"}
        )
        
        parser._save_parsed_result(doc)
        
        saved_file = temp_dir / "test_doc.json"
        assert saved_file.exists()
        
        with saved_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        
        assert data["doc_name"] == "test_doc"
        assert len(data["pages"]) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
