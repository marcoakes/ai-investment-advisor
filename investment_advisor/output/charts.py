"""
Chart generation tools for financial data visualization.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
import os
from datetime import datetime
import seaborn as sns
from ..core.base import BaseTool, ToolResult, ToolType


plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


class ChartGenerator(BaseTool):
    """Generate various types of financial charts."""
    
    def __init__(self, output_dir: str = "charts"):
        super().__init__("chart_generator", ToolType.OUTPUT)
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def execute(self, chart_type: str, data: Dict[str, Any], 
                title: str = None, save_path: str = None, **kwargs) -> ToolResult:
        """Generate charts based on type and data."""
        try:
            if chart_type == "price_chart":
                chart_path = self.create_price_chart(data, title, save_path, **kwargs)
            elif chart_type == "technical_chart":
                chart_path = self.create_technical_chart(data, title, save_path, **kwargs)
            elif chart_type == "performance_chart":
                chart_path = self.create_performance_chart(data, title, save_path, **kwargs)
            elif chart_type == "comparison_chart":
                chart_path = self.create_comparison_chart(data, title, save_path, **kwargs)
            elif chart_type == "volume_chart":
                chart_path = self.create_volume_chart(data, title, save_path, **kwargs)
            else:
                return ToolResult(
                    success=False,
                    error=f"Unsupported chart type: {chart_type}"
                )
            
            return ToolResult(
                success=True,
                data={'chart_path': chart_path},
                metadata={'chart_type': chart_type, 'title': title}
            )
        
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Chart generation failed: {str(e)}"
            )
    
    def create_price_chart(self, data: Dict[str, Any], title: str = None, 
                          save_path: str = None, **kwargs) -> str:
        """Create a basic price chart."""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        price_data = data['price_data']
        ax.plot(price_data.index, price_data['Close'], label='Close Price', linewidth=2)
        
        if 'sma_20' in data:
            ax.plot(price_data.index, data['sma_20'], label='SMA 20', alpha=0.7)
        if 'sma_50' in data:
            ax.plot(price_data.index, data['sma_50'], label='SMA 50', alpha=0.7)
        
        ax.set_title(title or f"Price Chart - {data.get('symbol', 'Stock')}")
        ax.set_xlabel('Date')
        ax.set_ylabel('Price ($)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        if save_path is None:
            save_path = os.path.join(self.output_dir, f"price_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return save_path
    
    def create_technical_chart(self, data: Dict[str, Any], title: str = None, 
                             save_path: str = None, **kwargs) -> str:
        """Create a technical analysis chart with multiple indicators."""
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 12), 
                                           gridspec_kw={'height_ratios': [3, 1, 1]})
        
        price_data = data['price_data']
        
        # Main price chart with Bollinger Bands
        ax1.plot(price_data.index, price_data['Close'], label='Close Price', linewidth=2)
        
        if 'bollinger_bands' in data:
            bb = data['bollinger_bands']
            ax1.plot(price_data.index, bb['upper_band'], label='BB Upper', alpha=0.5, linestyle='--')
            ax1.plot(price_data.index, bb['middle_band'], label='BB Middle', alpha=0.7)
            ax1.plot(price_data.index, bb['lower_band'], label='BB Lower', alpha=0.5, linestyle='--')
            ax1.fill_between(price_data.index, bb['upper_band'], bb['lower_band'], alpha=0.1)
        
        ax1.set_title(title or f"Technical Analysis - {data.get('symbol', 'Stock')}")
        ax1.set_ylabel('Price ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # RSI chart
        if 'rsi' in data:
            ax2.plot(price_data.index, data['rsi'], label='RSI', color='orange')
            ax2.axhline(y=70, color='r', linestyle='--', alpha=0.5)
            ax2.axhline(y=30, color='g', linestyle='--', alpha=0.5)
            ax2.set_ylabel('RSI')
            ax2.set_ylim(0, 100)
            ax2.legend()
            ax2.grid(True, alpha=0.3)
        
        # MACD chart
        if 'macd' in data:
            macd = data['macd']
            ax3.plot(price_data.index, macd['macd_line'], label='MACD', color='blue')
            ax3.plot(price_data.index, macd['signal_line'], label='Signal', color='red')
            ax3.bar(price_data.index, macd['histogram'], label='Histogram', alpha=0.3)
            ax3.set_ylabel('MACD')
            ax3.set_xlabel('Date')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
        
        # Format x-axis for all subplots
        for ax in [ax1, ax2, ax3]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save_path is None:
            save_path = os.path.join(self.output_dir, f"technical_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return save_path
    
    def create_performance_chart(self, data: Dict[str, Any], title: str = None, 
                               save_path: str = None, **kwargs) -> str:
        """Create a performance/backtesting chart."""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        portfolio = data['portfolio']
        
        # Portfolio value over time
        ax1.plot(portfolio.index, portfolio['total'], label='Portfolio Value', linewidth=2)
        ax1.plot(portfolio.index, portfolio['price'] * (data.get('initial_capital', 10000) / portfolio['price'].iloc[0]), 
                 label='Buy & Hold', alpha=0.7)
        ax1.set_title(title or "Portfolio Performance")
        ax1.set_ylabel('Value ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Drawdown chart
        rolling_max = portfolio['total'].expanding().max()
        drawdown = (portfolio['total'] - rolling_max) / rolling_max * 100
        ax2.fill_between(portfolio.index, drawdown, 0, alpha=0.5, color='red')
        ax2.set_title('Drawdown')
        ax2.set_ylabel('Drawdown (%)')
        ax2.set_xlabel('Date')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path is None:
            save_path = os.path.join(self.output_dir, f"performance_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return save_path
    
    def create_comparison_chart(self, data: Dict[str, Any], title: str = None, 
                              save_path: str = None, **kwargs) -> str:
        """Create a strategy comparison chart."""
        strategies = data['strategies']
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Performance comparison
        strategy_names = list(strategies.keys())
        returns = [strategies[name]['performance_metrics']['total_return'] for name in strategy_names]
        sharpe_ratios = [strategies[name]['performance_metrics']['sharpe_ratio'] for name in strategy_names]
        
        ax1.bar(strategy_names, returns)
        ax1.set_title('Total Returns Comparison')
        ax1.set_ylabel('Total Return (%)')
        ax1.tick_params(axis='x', rotation=45)
        
        ax2.bar(strategy_names, sharpe_ratios)
        ax2.set_title('Sharpe Ratio Comparison')
        ax2.set_ylabel('Sharpe Ratio')
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        if save_path is None:
            save_path = os.path.join(self.output_dir, f"comparison_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return save_path
    
    def create_volume_chart(self, data: Dict[str, Any], title: str = None, 
                          save_path: str = None, **kwargs) -> str:
        """Create a price and volume chart."""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), 
                                      gridspec_kw={'height_ratios': [2, 1]})
        
        price_data = data['price_data']
        
        # Price chart
        ax1.plot(price_data.index, price_data['Close'], label='Close Price', linewidth=2)
        if 'volume_sma' in data:
            ax1_vol = ax1.twinx()
            ax1_vol.plot(price_data.index, data['volume_sma'], 
                        label='Volume SMA', color='orange', alpha=0.7)
            ax1_vol.set_ylabel('Volume SMA')
        
        ax1.set_title(title or f"Price and Volume - {data.get('symbol', 'Stock')}")
        ax1.set_ylabel('Price ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Volume chart
        ax2.bar(price_data.index, price_data['Volume'], alpha=0.7)
        ax2.set_ylabel('Volume')
        ax2.set_xlabel('Date')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path is None:
            save_path = os.path.join(self.output_dir, f"volume_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return save_path
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            'chart_type': {'type': 'str', 'required': True, 
                          'description': 'Type of chart (price_chart, technical_chart, performance_chart, comparison_chart, volume_chart)'},
            'data': {'type': 'dict', 'required': True, 'description': 'Chart data'},
            'title': {'type': 'str', 'required': False, 'description': 'Chart title'},
            'save_path': {'type': 'str', 'required': False, 'description': 'Path to save the chart'}
        }