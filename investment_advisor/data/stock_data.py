"""
Stock data acquisition tools using various financial APIs.
"""

import requests
import pandas as pd
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import yfinance as yf
from ..core.base import BaseTool, ToolResult, ToolType
import os


class YahooFinanceAPI(BaseTool):
    """Yahoo Finance API for stock data."""
    
    def __init__(self):
        super().__init__("yahoo_finance", ToolType.DATA_ACQUISITION)
    
    def execute(self, symbol: str, period: str = "1y", **kwargs) -> ToolResult:
        """Fetch stock data from Yahoo Finance."""
        try:
            ticker = yf.Ticker(symbol)
            hist_data = ticker.history(period=period)
            info = ticker.info
            
            return ToolResult(
                success=True,
                data={
                    'historical_data': hist_data,
                    'company_info': info,
                    'symbol': symbol
                },
                metadata={'source': 'yahoo_finance', 'period': period}
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Failed to fetch data for {symbol}: {str(e)}"
            )
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            'symbol': {'type': 'str', 'required': True, 'description': 'Stock symbol'},
            'period': {'type': 'str', 'required': False, 'default': '1y', 
                      'description': 'Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)'}
        }


class AlphaVantageAPI(BaseTool):
    """Alpha Vantage API for comprehensive stock data."""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("alpha_vantage", ToolType.DATA_ACQUISITION)
        self.api_key = api_key or os.getenv('ALPHA_VANTAGE_API_KEY')
        self.base_url = "https://www.alphavantage.co/query"
    
    def execute(self, symbol: str, function: str = "TIME_SERIES_DAILY", **kwargs) -> ToolResult:
        """Fetch data from Alpha Vantage API."""
        if not self.api_key:
            return ToolResult(
                success=False,
                error="Alpha Vantage API key not configured"
            )
        
        try:
            params = {
                'function': function,
                'symbol': symbol,
                'apikey': self.api_key,
                **kwargs
            }
            
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            if 'Error Message' in data:
                return ToolResult(
                    success=False,
                    error=data['Error Message']
                )
            
            return ToolResult(
                success=True,
                data=data,
                metadata={'source': 'alpha_vantage', 'function': function}
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Alpha Vantage API error: {str(e)}"
            )
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            'symbol': {'type': 'str', 'required': True, 'description': 'Stock symbol'},
            'function': {'type': 'str', 'required': False, 'default': 'TIME_SERIES_DAILY',
                        'description': 'API function to call'}
        }


class FinnhubAPI(BaseTool):
    """Finnhub API for market data and news."""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("finnhub", ToolType.DATA_ACQUISITION)
        self.api_key = api_key or os.getenv('FINNHUB_API_KEY')
        self.base_url = "https://finnhub.io/api/v1"
    
    def execute(self, symbol: str, data_type: str = "quote", **kwargs) -> ToolResult:
        """Fetch data from Finnhub API."""
        if not self.api_key:
            return ToolResult(
                success=False,
                error="Finnhub API key not configured"
            )
        
        try:
            headers = {'X-Finnhub-Token': self.api_key}
            
            if data_type == "quote":
                url = f"{self.base_url}/quote?symbol={symbol}"
            elif data_type == "news":
                url = f"{self.base_url}/company-news?symbol={symbol}&from={kwargs.get('from_date', (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'))}&to={kwargs.get('to_date', datetime.now().strftime('%Y-%m-%d'))}"
            elif data_type == "profile":
                url = f"{self.base_url}/stock/profile2?symbol={symbol}"
            else:
                return ToolResult(
                    success=False,
                    error=f"Unsupported data type: {data_type}"
                )
            
            response = requests.get(url, headers=headers)
            data = response.json()
            
            return ToolResult(
                success=True,
                data=data,
                metadata={'source': 'finnhub', 'data_type': data_type}
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Finnhub API error: {str(e)}"
            )
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            'symbol': {'type': 'str', 'required': True, 'description': 'Stock symbol'},
            'data_type': {'type': 'str', 'required': False, 'default': 'quote',
                         'description': 'Type of data (quote, news, profile)'},
            'from_date': {'type': 'str', 'required': False, 'description': 'Start date for news (YYYY-MM-DD)'},
            'to_date': {'type': 'str', 'required': False, 'description': 'End date for news (YYYY-MM-DD)'}
        }


class StockDataAggregator(BaseTool):
    """Aggregates data from multiple sources."""
    
    def __init__(self):
        super().__init__("stock_aggregator", ToolType.DATA_ACQUISITION)
        self.yahoo_api = YahooFinanceAPI()
        self.alpha_vantage_api = AlphaVantageAPI()
        self.finnhub_api = FinnhubAPI()
    
    def execute(self, symbol: str, include_fundamentals: bool = True, 
                include_news: bool = True, **kwargs) -> ToolResult:
        """Aggregate stock data from multiple sources."""
        results = {}
        errors = []
        
        # Get basic data from Yahoo Finance
        yahoo_result = self.yahoo_api.execute(symbol, **kwargs)
        if yahoo_result.success:
            results['yahoo_data'] = yahoo_result.data
        else:
            errors.append(f"Yahoo Finance: {yahoo_result.error}")
        
        # Get additional data from Finnhub if available
        if include_fundamentals:
            profile_result = self.finnhub_api.execute(symbol, data_type="profile")
            if profile_result.success:
                results['company_profile'] = profile_result.data
        
        if include_news:
            news_result = self.finnhub_api.execute(symbol, data_type="news")
            if news_result.success:
                results['recent_news'] = news_result.data
        
        if not results:
            return ToolResult(
                success=False,
                error=f"Failed to fetch data from all sources: {'; '.join(errors)}"
            )
        
        return ToolResult(
            success=True,
            data=results,
            metadata={
                'sources_used': list(results.keys()),
                'errors': errors
            }
        )
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            'symbol': {'type': 'str', 'required': True, 'description': 'Stock symbol'},
            'include_fundamentals': {'type': 'bool', 'required': False, 'default': True,
                                   'description': 'Include fundamental data'},
            'include_news': {'type': 'bool', 'required': False, 'default': True,
                           'description': 'Include recent news'}
        }