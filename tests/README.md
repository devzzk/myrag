# Tests for myrag

This directory contains unit tests and integration tests for the myrag project.

## Test Structure

```
tests/
├── __init__.py           # Test package init
├── conftest.py           # Pytest fixtures and configuration
├── pytest.ini            # Pytest configuration (in root directory)
├── test_config.py        # Tests for config module
├── test_text_splitter.py # Tests for text_splitter module
├── test_pdf_parsing.py   # Tests for pdf_parsing module
├── test_ingestion_retrieval.py # Tests for ingestion and retrieval
├── test_integration.py   # Integration tests
├── test_utils.py         # Test utilities
├── test_data/            # Test data files
│   └── sample_parsed_doc.json
└── README.md             # This file
```

## Running Tests

### Prerequisites

First, make sure you have installed the test dependencies:

```bash
pip install pytest pytest-cov
```

### Quick Start

Run all tests:

```bash
# Using the test runner script
python run_tests.py

# Or directly with pytest
pytest tests/ -v
```

### Test Options

Run only unit tests:
```bash
python run_tests.py --type unit
```

Run only integration tests:
```bash
python run_tests.py --type integration
```

Show test coverage:
```bash
python run_tests.py --coverage
```

Quick test (skip integration tests):
```bash
python run_tests.py --quick
```

### Using pytest Directly

```bash
# Run specific test file
pytest tests/test_config.py -v

# Run specific test class
pytest tests/test_text_splitter.py::TestTextSplitter -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing

# Generate HTML coverage report
pytest tests/ --cov=src --cov-report=html
```

## Test Categories

### Unit Tests (`test_*.py`)
- Test individual modules and functions in isolation
- Use mocks where external dependencies are involved
- Fast execution

### Integration Tests (`test_integration.py`)
- Test the interaction between multiple components
- Test the complete pipeline flow
- Marked with `@pytest.mark.integration`

## Writing New Tests

1. Create a new test file: `tests/test_<module_name>.py`
2. Follow the existing patterns
3. Use fixtures from `conftest.py`
4. Use utilities from `test_utils.py`
5. Add appropriate markers: `@pytest.mark.unit` or `@pytest.mark.integration`

## Test Data

Test data is located in `tests/test_data/`:

- `sample_parsed_doc.json`: A sample parsed document for testing

## Mocking External Dependencies

Some tests require mocking external services like:
- DashScope API
- PDF parsing with MinerU
- FAISS vector operations

These are mocked using `unittest.mock.patch` to avoid external calls during testing.

## Troubleshooting

If tests fail:
1. Check that you are in the project root directory
2. Make sure all dependencies are installed: `pip install -r requirements.txt`
3. Try running with `--tb=short` for shorter tracebacks
4. For specific failing tests, try running just that test file
