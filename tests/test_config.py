"""
Tests for config module
"""
import sys
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import PipelineConfig, RunConfig


class TestPipelineConfig:
    """Test PipelineConfig class"""
    
    def test_initialization_default(self, temp_dir):
        """Test default initialization"""
        config = PipelineConfig(root_path=temp_dir)
        
        assert config.root_path == temp_dir
        assert config.data_dir == temp_dir / "data" / "stock_data"
        assert config.pdf_dir == config.data_dir / "pdf_reports"
        assert config.api_provider == "dashscope"
        assert config.answering_model == "qwen-turbo-latest"
    
    def test_directories_creation(self, temp_dir):
        """Test that directories are created"""
        config = PipelineConfig(root_path=temp_dir)
        
        assert config.data_dir.exists()
        assert config.pdf_dir.exists()
        assert config.parsed_dir.exists()
        assert config.chunked_dir.exists()
        assert config.vector_db_dir.exists()
    
    def test_custom_paths(self, temp_dir):
        """Test custom path configuration"""
        custom_data = temp_dir / "mydata"
        custom_pdf = temp_dir / "mypdfs"
        
        config = PipelineConfig(
            root_path=temp_dir,
            data_dir=custom_data,
            pdf_dir=custom_pdf
        )
        
        assert config.data_dir == custom_data
        assert config.pdf_dir == custom_pdf
    
    def test_model_configuration(self, temp_dir):
        """Test model configuration"""
        config = PipelineConfig(
            root_path=temp_dir,
            api_provider="openai",
            answering_model="gpt-4"
        )
        
        assert config.api_provider == "openai"
        assert config.answering_model == "gpt-4"


class TestRunConfig:
    """Test RunConfig class"""
    
    def test_default_values(self):
        """Test default values"""
        config = RunConfig()
        
        assert config.chunk_size == 500
        assert config.chunk_overlap == 100
        assert config.top_n_retrieval == 5
        assert config.parent_document_retrieval is False
        assert config.temperature == 0.1
    
    def test_custom_values(self):
        """Test custom values"""
        config = RunConfig(
            chunk_size=1000,
            chunk_overlap=200,
            top_n_retrieval=10,
            temperature=0.7
        )
        
        assert config.chunk_size == 1000
        assert config.chunk_overlap == 200
        assert config.top_n_retrieval == 10
        assert config.temperature == 0.7


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
