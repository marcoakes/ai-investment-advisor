"""
Configuration file for the AI Investment Research Assistant.
"""

import os
from typing import Dict, Any


class Config:
    """Configuration settings for the investment advisor."""
    
    # API Keys (set via environment variables)
    ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
    FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY')
    
    # Output directories
    CHARTS_OUTPUT_DIR = "charts"
    REPORTS_OUTPUT_DIR = "reports" 
    PRESENTATIONS_OUTPUT_DIR = "presentations"
    
    # Default analysis parameters
    DEFAULT_ANALYSIS_PERIOD = "1y"
    DEFAULT_TECHNICAL_INDICATORS = [
        'sma_20', 'sma_50', 'rsi', 'macd', 'bollinger_bands'
    ]
    DEFAULT_BACKTEST_CAPITAL = 10000
    DEFAULT_COMMISSION_RATE = 0.001
    
    # Chart settings
    CHART_FIGSIZE = (12, 8)
    CHART_DPI = 300
    CHART_STYLE = 'seaborn-v0_8'
    
    # Report settings
    PDF_PAGE_SIZE = "A4"
    PDF_MARGIN = 1  # inches
    
    # Session settings
    MAX_CONVERSATION_HISTORY = 100
    MAX_SYMBOLS_TO_REMEMBER = 50
    
    @classmethod
    def get_api_config(cls) -> Dict[str, Any]:
        """Get API configuration."""
        return {
            'alpha_vantage_key': cls.ALPHA_VANTAGE_API_KEY,
            'finnhub_key': cls.FINNHUB_API_KEY,
        }
    
    @classmethod
    def get_output_config(cls) -> Dict[str, str]:
        """Get output directory configuration."""
        return {
            'charts_dir': cls.CHARTS_OUTPUT_DIR,
            'reports_dir': cls.REPORTS_OUTPUT_DIR,
            'presentations_dir': cls.PRESENTATIONS_OUTPUT_DIR
        }
    
    @classmethod
    def get_analysis_config(cls) -> Dict[str, Any]:
        """Get default analysis configuration."""
        return {
            'period': cls.DEFAULT_ANALYSIS_PERIOD,
            'indicators': cls.DEFAULT_TECHNICAL_INDICATORS,
            'backtest_capital': cls.DEFAULT_BACKTEST_CAPITAL,
            'commission_rate': cls.DEFAULT_COMMISSION_RATE
        }
    
    @classmethod
    def setup_directories(cls):
        """Create output directories if they don't exist."""
        for directory in [cls.CHARTS_OUTPUT_DIR, cls.REPORTS_OUTPUT_DIR, cls.PRESENTATIONS_OUTPUT_DIR]:
            os.makedirs(directory, exist_ok=True)


# Tool usage guidelines for AI behavior
AI_TOOL_USAGE_GUIDELINES = """
AI Tool Usage Guidelines for Investment Research Assistant

When a user requests analysis, follow these guidelines:

1. DATA ACQUISITION:
   - Always fetch necessary data using financial data tools before analysis
   - Use StockDataAggregator for comprehensive data (includes fundamentals + news)
   - Use YahooFinanceAPI for basic price data and company info
   - Use AlphaVantage/Finnhub for specialized data if API keys are available

2. ANALYSIS WORKFLOW:
   - For stock analysis: Data → Technical Analysis → Trading Signals → Charts
   - For backtesting: Historical Data → Technical Analysis → Signals → Backtest → Performance Charts
   - For comparison: Individual analysis for each stock → Comparison analysis → Comparison charts

3. CHART GENERATION:
   - When charts are requested, call the chart generator and inform user of saved file path
   - Use appropriate chart types: price_chart, technical_chart, performance_chart, comparison_chart
   - Include relevant technical indicators in technical charts

4. MULTI-STEP QUERIES:
   - For complex queries, explicitly outline the step-by-step plan before executing
   - Break down requests like "analyze and compare stocks" into sequential tasks
   - Execute tasks in dependency order (data → analysis → visualization → reporting)

5. CODE EXECUTION:
   - When generating custom calculations, adhere to PEP 8 standards
   - Use type hints for better code clarity
   - Implement proper error handling for API calls and data processing

6. REPORTING:
   - Compile results from multiple tools into coherent summaries
   - Include key metrics, insights, and visualizations in reports
   - Generate both PDF reports and PowerPoint presentations when requested

7. SESSION MEMORY:
   - Remember analyzed symbols for context in future queries
   - Store analysis results for quick reference
   - Maintain conversation history for better user experience

8. ERROR HANDLING:
   - Gracefully handle API failures and missing data
   - Provide alternative data sources when primary sources fail
   - Give clear error messages and suggest alternative approaches

9. USER COMMUNICATION:
   - Explain what analysis is being performed and why
   - Provide clear summaries of findings and recommendations
   - Indicate when files (charts, reports) have been created and their locations
"""