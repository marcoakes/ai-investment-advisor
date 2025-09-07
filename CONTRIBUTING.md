# 🤝 Contributing to AI Investment Research Assistant

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## 📋 Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)

## 📜 Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code:

- **Be respectful and inclusive** to all contributors
- **Be constructive** in discussions and feedback
- **Focus on the issue, not the person** when disagreeing
- **Help create a welcoming environment** for new contributors

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Git
- Basic knowledge of financial markets (helpful but not required)

### Development Setup

1. **Fork the repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/ai-investment-advisor.git
   cd ai-investment-advisor
   ```

2. **Set up development environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # Windows:
   venv\\Scripts\\activate
   # macOS/Linux:
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Install development dependencies
   pip install pytest black flake8 mypy
   
   # Install package in editable mode
   pip install -e .
   ```

3. **Verify installation**
   ```bash
   python investment_advisor/cli.py --query "help"
   ```

## 🛠️ How to Contribute

### 🐛 Reporting Bugs

1. **Search existing issues** to avoid duplicates
2. **Use the bug report template** when creating new issues
3. **Provide detailed information**:
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details
   - Error logs and screenshots

### 💡 Suggesting Features

1. **Check existing feature requests** first
2. **Use the feature request template**
3. **Clearly describe the use case** and benefits
4. **Consider implementation complexity** and maintenance

### 🔧 Code Contributions

#### Types of Contributions Welcome:
- **Bug fixes** - Fix existing issues
- **New features** - Add requested functionality  
- **Performance improvements** - Optimize existing code
- **Documentation** - Improve docs and examples
- **Tests** - Add or improve test coverage
- **Refactoring** - Code cleanup and organization

#### Before You Start:
1. **Check existing issues** and PRs to avoid duplicates
2. **Comment on the issue** you want to work on
3. **Fork the repository** and create a feature branch
4. **Discuss major changes** in an issue first

## 📝 Coding Standards

### Python Style Guide
- Follow **PEP 8** style guidelines
- Use **Black** for code formatting: `black investment_advisor/`
- Use **flake8** for linting: `flake8 investment_advisor/`
- Maximum line length: **88 characters**

### Code Quality
- **Type hints** for function parameters and return values
- **Docstrings** for all public functions and classes
- **Clear variable names** and comments for complex logic
- **Error handling** with appropriate exception types

### Example Code Style:
```python
from typing import Dict, Any, Optional
import pandas as pd

class ExampleAnalyzer(BaseTool):
    """Example analyzer tool for demonstration.
    
    This tool demonstrates proper coding style and documentation
    standards for the investment advisor project.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("example_analyzer", ToolType.ANALYSIS)
        self.config = config or {}
    
    def execute(self, data: pd.DataFrame, **kwargs) -> ToolResult:
        """Execute the analysis on provided data.
        
        Args:
            data: Input DataFrame with stock price data
            **kwargs: Additional parameters
            
        Returns:
            ToolResult containing analysis results
            
        Raises:
            ValueError: If input data is invalid
        """
        try:
            if data.empty:
                raise ValueError("Input data cannot be empty")
            
            # Perform analysis logic here
            result = self._analyze_data(data)
            
            return ToolResult(
                success=True,
                data=result,
                metadata={"rows_processed": len(data)}
            )
        
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Analysis failed: {str(e)}"
            )
    
    def _analyze_data(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Private method to perform the actual analysis."""
        # Implementation details...
        return {"analysis_result": "example"}
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=investment_advisor

# Run specific test file
pytest tests/test_technical.py

# Run with verbose output
pytest -v
```

### Writing Tests
- **Write tests for new functionality**
- **Include edge cases and error conditions**
- **Use descriptive test names**
- **Mock external APIs** to avoid rate limits

### Test Structure:
```python
import pytest
from unittest.mock import Mock, patch
from investment_advisor.analysis.technical import TechnicalAnalyzer

class TestTechnicalAnalyzer:
    """Test suite for TechnicalAnalyzer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = TechnicalAnalyzer()
        self.sample_data = self._create_sample_data()
    
    def test_rsi_calculation(self):
        """Test RSI calculation with known values."""
        result = self.analyzer.calculate_rsi(self.sample_data)
        
        assert isinstance(result, pd.Series)
        assert len(result) == len(self.sample_data)
        assert 0 <= result.max() <= 100
        assert 0 <= result.min() <= 100
    
    def test_invalid_data_handling(self):
        """Test handling of invalid input data."""
        empty_data = pd.DataFrame()
        
        with pytest.raises(ValueError):
            self.analyzer.execute(empty_data)
```

## 📚 Documentation

### Documentation Standards
- **Clear and concise** explanations
- **Code examples** for complex features
- **API documentation** for all public methods
- **User guides** for new features

### Documentation Types:
- **README updates** for new features
- **Docstrings** in code
- **API documentation** 
- **Tutorial examples**
- **Configuration guides**

## 🔄 Pull Request Process

### Before Submitting
1. **Create a feature branch**: `git checkout -b feature/your-feature-name`
2. **Make your changes** following coding standards
3. **Add tests** for new functionality
4. **Update documentation** as needed
5. **Run the full test suite**: `pytest`
6. **Check code formatting**: `black investment_advisor/ && flake8`

### PR Guidelines
1. **Use clear, descriptive PR titles**
2. **Fill out the PR template completely**
3. **Link related issues**: "Closes #123"
4. **Keep PRs focused** - one feature/fix per PR
5. **Write clear commit messages**

### PR Review Process
1. **Automated checks** must pass (CI/CD)
2. **Code review** by maintainers
3. **Testing** of new functionality
4. **Documentation review**
5. **Final approval** and merge

### Commit Message Format
```
type(scope): brief description

Detailed explanation of changes if needed.

Closes #123
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Example:
```
feat(analysis): add RSI momentum indicator

Implement Relative Strength Index calculation with configurable
period parameter. Includes comprehensive tests and documentation.

Closes #45
```

## 🏷️ Issue Labels

| Label | Description |
|-------|-------------|
| `bug` | Something isn't working |
| `enhancement` | New feature or request |
| `documentation` | Improvements or additions to docs |
| `good first issue` | Good for newcomers |
| `help wanted` | Extra attention is needed |
| `question` | Further information is requested |
| `duplicate` | This issue or PR already exists |
| `invalid` | This doesn't seem right |
| `wontfix` | This will not be worked on |

## 🎯 Development Priorities

### High Priority
- **Bug fixes** - Critical issues affecting users
- **Performance optimizations** - Speed improvements
- **Documentation** - Missing or unclear docs
- **Test coverage** - Improving reliability

### Medium Priority
- **New analysis tools** - Additional indicators/strategies
- **Data source integrations** - New API connections
- **User experience** - CLI improvements
- **Output formats** - New report types

### Low Priority
- **Code refactoring** - Internal improvements
- **Optional features** - Nice-to-have additions
- **Experimental features** - Research and development

## 🆘 Getting Help

- **GitHub Discussions** - General questions and ideas
- **GitHub Issues** - Bug reports and feature requests
- **Code Reviews** - Feedback on implementation
- **Documentation** - Check existing docs first

## 🙏 Recognition

Contributors will be:
- **Listed in README** acknowledgments
- **Mentioned in release notes** for significant contributions
- **Given credit** in code comments where appropriate

## 📞 Contact

For questions about contributing:
- Open a **GitHub Discussion**
- Create an **issue** with the "question" label
- Review **existing documentation** and issues first

---

Thank you for contributing to the AI Investment Research Assistant! 🚀