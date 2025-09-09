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
            print(f"DEBUG: Chart generation requested - Type: {chart_type}")
            print(f"DEBUG: Data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            
            # Validate input data structure
            if not isinstance(data, dict):
                raise ValueError(f"Expected dict for data, got {type(data)}")
            
            if 'price_data' not in data:
                raise ValueError("Missing 'price_data' key in chart data")
            
            price_data = data['price_data']
            print(f"DEBUG: Price data type: {type(price_data)}")
            print(f"DEBUG: Price data shape: {getattr(price_data, 'shape', 'No shape')}")
            
            if hasattr(price_data, 'columns'):
                print(f"DEBUG: Price data columns: {list(price_data.columns)}")
                print(f"DEBUG: Price data dtypes: {dict(price_data.dtypes)}")
            
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
            print(f"DEBUG: Chart generation error: {str(e)}")
            import traceback
            traceback.print_exc()
            return ToolResult(
                success=False,
                error=f"Chart generation failed: {str(e)}"
            )
    
    def create_price_chart(self, data: Dict[str, Any], title: str = None, 
                          save_path: str = None, **kwargs) -> str:
        """Create a basic price chart."""
        print("DEBUG: Starting price chart creation")
        
        try:
            fig, ax = plt.subplots(figsize=(12, 8))
            
            price_data = data['price_data']
            
            # Clean the data before plotting
            clean_data = self._clean_data_for_plotting(price_data)
            if clean_data is None or len(clean_data) == 0:
                raise ValueError("No valid data available for plotting")
            
            print("DEBUG: About to plot price data")
            # Force convert index and Close to proper types for matplotlib
            x_data = self._safe_convert_for_plotting(clean_data.index, "index")
            y_data = self._safe_convert_for_plotting(clean_data['Close'], "Close")
            
            print(f"DEBUG: X data type: {type(x_data)}, length: {len(x_data)}")
            print(f"DEBUG: Y data type: {type(y_data)}, length: {len(y_data)}")
            
            ax.plot(x_data, y_data, label='Close Price', linewidth=2)
            print("DEBUG: Successfully plotted Close price")
            
            # Add moving averages if available
            if 'sma_20' in data:
                sma_20_clean = self._clean_indicator_data(data, 'sma_20')
                if sma_20_clean is not None:
                    sma_20_safe = self._safe_convert_for_plotting(sma_20_clean, "SMA_20")
                    ax.plot(x_data[:len(sma_20_safe)], sma_20_safe, label='SMA 20', alpha=0.7)
            
            if 'sma_50' in data:
                sma_50_clean = self._clean_indicator_data(data, 'sma_50')
                if sma_50_clean is not None:
                    sma_50_safe = self._safe_convert_for_plotting(sma_50_clean, "SMA_50")
                    ax.plot(x_data[:len(sma_50_safe)], sma_50_safe, label='SMA 50', alpha=0.7)
            
            ax.set_title(title or f"Price Chart - {data.get('symbol', 'Stock')}")
            ax.set_xlabel('Time Period')
            ax.set_ylabel('Price ($)')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            if save_path is None:
                save_path = os.path.join(self.output_dir, f"price_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return save_path
            
        except Exception as e:
            print(f"DEBUG: Error in create_price_chart: {e}")
            # Create error chart as fallback
            return self._create_error_chart(f"Price chart error: {str(e)}")
    
    def create_technical_chart(self, data: Dict[str, Any], title: str = None, 
                             save_path: str = None, **kwargs) -> str:
        """Create a technical analysis chart with multiple indicators."""
        print("DEBUG: Starting technical chart creation")
        
        try:
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 12), 
                                               gridspec_kw={'height_ratios': [3, 1, 1]})
            
            price_data = data['price_data']
            
            # Clean the data before plotting
            clean_data = self._clean_data_for_plotting(price_data)
            if clean_data is None or len(clean_data) == 0:
                raise ValueError("No valid data available for plotting")
            
            # Safe data conversion
            x_data = self._safe_convert_for_plotting(clean_data.index, "index")
            close_data = self._safe_convert_for_plotting(clean_data['Close'], "Close")
            
            # Main price chart
            ax1.plot(x_data, close_data, label='Close Price', linewidth=2)
            
            # Add Bollinger Bands if available
            if 'bollinger_bands' in data:
                bb_clean = self._clean_indicator_data(data, 'bollinger_bands')
                if bb_clean and all(key in bb_clean for key in ['upper_band', 'middle_band', 'lower_band']):
                    upper_safe = self._safe_convert_for_plotting(bb_clean['upper_band'], "BB_Upper")
                    middle_safe = self._safe_convert_for_plotting(bb_clean['middle_band'], "BB_Middle") 
                    lower_safe = self._safe_convert_for_plotting(bb_clean['lower_band'], "BB_Lower")
                    
                    min_len = min(len(x_data), len(upper_safe), len(middle_safe), len(lower_safe))
                    
                    ax1.plot(x_data[:min_len], upper_safe[:min_len], label='BB Upper', alpha=0.5, linestyle='--')
                    ax1.plot(x_data[:min_len], middle_safe[:min_len], label='BB Middle', alpha=0.7)
                    ax1.plot(x_data[:min_len], lower_safe[:min_len], label='BB Lower', alpha=0.5, linestyle='--')
            
            ax1.set_title(title or f"Technical Analysis - {data.get('symbol', 'Stock')}")
            ax1.set_ylabel('Price ($)')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # RSI chart
            if 'rsi' in data:
                rsi_clean = self._clean_indicator_data(data, 'rsi')
                if rsi_clean is not None:
                    rsi_safe = self._safe_convert_for_plotting(rsi_clean, "RSI")
                    min_len = min(len(x_data), len(rsi_safe))
                    ax2.plot(x_data[:min_len], rsi_safe[:min_len], label='RSI', color='orange')
                    ax2.axhline(y=70, color='r', linestyle='--', alpha=0.5)
                    ax2.axhline(y=30, color='g', linestyle='--', alpha=0.5)
                    ax2.set_ylabel('RSI')
                    ax2.set_ylim(0, 100)
                    ax2.legend()
                    ax2.grid(True, alpha=0.3)
            else:
                ax2.text(0.5, 0.5, 'RSI data not available', ha='center', va='center', transform=ax2.transAxes)
            
            # MACD chart
            if 'macd' in data:
                macd_clean = self._clean_indicator_data(data, 'macd')
                if macd_clean and all(key in macd_clean for key in ['macd_line', 'signal_line', 'histogram']):
                    macd_safe = self._safe_convert_for_plotting(macd_clean['macd_line'], "MACD_Line")
                    signal_safe = self._safe_convert_for_plotting(macd_clean['signal_line'], "Signal_Line")
                    hist_safe = self._safe_convert_for_plotting(macd_clean['histogram'], "MACD_Histogram")
                    
                    min_len = min(len(x_data), len(macd_safe), len(signal_safe), len(hist_safe))
                    
                    ax3.plot(x_data[:min_len], macd_safe[:min_len], label='MACD', color='blue')
                    ax3.plot(x_data[:min_len], signal_safe[:min_len], label='Signal', color='red')
                    ax3.bar(range(min_len), hist_safe[:min_len], label='Histogram', alpha=0.3)
                    ax3.set_ylabel('MACD')
                    ax3.set_xlabel('Time Period')
                    ax3.legend()
                    ax3.grid(True, alpha=0.3)
            else:
                ax3.text(0.5, 0.5, 'MACD data not available', ha='center', va='center', transform=ax3.transAxes)
            
            plt.tight_layout()
            
            if save_path is None:
                save_path = os.path.join(self.output_dir, f"technical_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return save_path
            
        except Exception as e:
            print(f"DEBUG: Error in create_technical_chart: {e}")
            return self._create_error_chart(f"Technical chart error: {str(e)}")
    
    def create_performance_chart(self, data: Dict[str, Any], title: str = None, 
                               save_path: str = None, **kwargs) -> str:
        """Create a performance/backtesting chart."""
        try:
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
            
        except Exception as e:
            print(f"DEBUG: Error in create_performance_chart: {e}")
            return self._create_error_chart(f"Performance chart error: {str(e)}")
    
    def create_comparison_chart(self, data: Dict[str, Any], title: str = None, 
                              save_path: str = None, **kwargs) -> str:
        """Create a strategy comparison chart."""
        try:
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
            
        except Exception as e:
            print(f"DEBUG: Error in create_comparison_chart: {e}")
            return self._create_error_chart(f"Comparison chart error: {str(e)}")
    
    def create_volume_chart(self, data: Dict[str, Any], title: str = None, 
                          save_path: str = None, **kwargs) -> str:
        """Create a price and volume chart."""
        try:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), 
                                          gridspec_kw={'height_ratios': [2, 1]})
            
            price_data = data['price_data']
            
            # Clean the data before plotting
            clean_data = self._clean_data_for_plotting(price_data)
            if clean_data is None or len(clean_data) == 0:
                raise ValueError("No valid data available for plotting")
            
            # Safe data conversion
            x_data = self._safe_convert_for_plotting(clean_data.index, "index")
            close_data = self._safe_convert_for_plotting(clean_data['Close'], "Close")
            volume_data = self._safe_convert_for_plotting(clean_data['Volume'], "Volume")
            
            # Price chart
            ax1.plot(x_data, close_data, label='Close Price', linewidth=2)
            ax1.set_title(title or f"Price and Volume - {data.get('symbol', 'Stock')}")
            ax1.set_ylabel('Price ($)')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Volume chart
            ax2.bar(range(len(volume_data)), volume_data, alpha=0.7)
            ax2.set_ylabel('Volume')
            ax2.set_xlabel('Time Period')
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            if save_path is None:
                save_path = os.path.join(self.output_dir, f"volume_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return save_path
            
        except Exception as e:
            print(f"DEBUG: Error in create_volume_chart: {e}")
            return self._create_error_chart(f"Volume chart error: {str(e)}")
    
    def _create_error_chart(self, error_message: str) -> str:
        """Create a chart showing the error message."""
        try:
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.text(0.5, 0.5, f'Chart Generation Error:\n{error_message}', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_title("Chart Error - Please Check Data")
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_path = os.path.join(self.output_dir, f"error_chart_{timestamp}.png")
            
            plt.tight_layout()
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return save_path
        except:
            # If even error chart fails, return a dummy path
            return "chart_creation_failed"
    
    def _safe_convert_for_plotting(self, data, data_name="data"):
        """Convert data to types safe for matplotlib plotting."""
        print(f"DEBUG: Converting {data_name} for plotting")
        
        if data is None:
            raise ValueError(f"{data_name} is None")
        
        try:
            # Handle pandas Series/Index
            if hasattr(data, 'values'):
                array_data = data.values
            else:
                array_data = np.array(data)
            
            print(f"DEBUG: {data_name} array shape: {array_data.shape}")
            print(f"DEBUG: {data_name} array dtype: {array_data.dtype}")
            
            # Check for object dtype (mixed types)
            if array_data.dtype == 'object':
                print(f"DEBUG: {data_name} has object dtype, converting...")
                
                # Try to convert to float
                try:
                    array_data = pd.to_numeric(array_data, errors='coerce')
                    array_data = np.array(array_data, dtype=np.float64)
                except:
                    # If numeric conversion fails, try datetime for x-axis
                    if data_name in ["index", "Index"]:
                        try:
                            array_data = pd.to_datetime(array_data)
                            return array_data
                        except:
                            pass
                    # Last resort: use range index
                    print(f"DEBUG: Using range index for {data_name}")
                    array_data = np.arange(len(data))
            
            # Handle string/datetime index
            elif data_name in ["index", "Index"] and not np.issubdtype(array_data.dtype, np.number):
                try:
                    array_data = pd.to_datetime(array_data)
                    return array_data
                except:
                    print(f"DEBUG: Using range index for {data_name}")
                    array_data = np.arange(len(data))
            
            # Ensure numeric data is float
            if np.issubdtype(array_data.dtype, np.number):
                array_data = np.array(array_data, dtype=np.float64)
                
                # Replace any remaining inf/nan for plotting
                mask = np.isfinite(array_data)
                if not mask.all():
                    print(f"DEBUG: {data_name} has {(~mask).sum()} non-finite values")
                    if data_name not in ["index", "Index"]:
                        # For y-data, we can interpolate or drop
                        array_data = array_data[mask] if mask.any() else np.array([0])
                    else:
                        # For x-data (index), use range
                        array_data = np.arange(len(array_data))
            
            print(f"DEBUG: {data_name} final dtype: {array_data.dtype}")
            print(f"DEBUG: {data_name} final shape: {array_data.shape}")
            
            return array_data
            
        except Exception as e:
            print(f"DEBUG: Error converting {data_name}: {e}")
            # Fallback: create dummy data
            if data_name in ["index", "Index"]:
                return np.arange(len(data) if hasattr(data, '__len__') else 10)
            else:
                return np.zeros(len(data) if hasattr(data, '__len__') else 10)
    
    def _clean_data_for_plotting(self, data):
        """Clean data to ensure it's safe for matplotlib plotting."""
        if data is None:
            return None
            
        try:
            # Make a copy to avoid modifying original data
            clean_data = data.copy()
            
            # Ensure index is datetime-like for time series plots
            if hasattr(clean_data, 'index'):
                try:
                    clean_data.index = pd.to_datetime(clean_data.index)
                except (ValueError, TypeError):
                    pass
            
            # Clean numeric columns - replace inf and convert to numeric
            numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']
            for col in numeric_columns:
                if hasattr(clean_data, 'columns') and col in clean_data.columns:
                    # Convert to numeric, coercing errors to NaN
                    clean_data[col] = pd.to_numeric(clean_data[col], errors='coerce')
                    # Replace infinite values with NaN
                    clean_data[col] = clean_data[col].replace([np.inf, -np.inf], np.nan)
            
            # Drop rows with all NaN values in essential columns
            essential_cols = [col for col in ['Close', 'Open', 'High', 'Low'] if hasattr(clean_data, 'columns') and col in clean_data.columns]
            if essential_cols:
                clean_data = clean_data.dropna(subset=essential_cols, how='all')
            
            return clean_data
        except Exception as e:
            print(f"DEBUG: Error in data cleaning: {e}")
            return data  # Return original data if cleaning fails
    
    def _clean_indicator_data(self, data, indicator_name):
        """Clean technical indicator data for plotting."""
        if indicator_name not in data or data[indicator_name] is None:
            return None
            
        try:
            indicator_data = data[indicator_name]
            
            # Handle Series data
            if hasattr(indicator_data, 'replace'):
                cleaned = pd.to_numeric(indicator_data, errors='coerce')
                cleaned = cleaned.replace([np.inf, -np.inf], np.nan)
                return cleaned
            
            # Handle dictionary data (like MACD, Bollinger Bands)
            elif isinstance(indicator_data, dict):
                cleaned_dict = {}
                for key, values in indicator_data.items():
                    if hasattr(values, 'replace'):
                        cleaned_values = pd.to_numeric(values, errors='coerce')
                        cleaned_values = cleaned_values.replace([np.inf, -np.inf], np.nan)
                        cleaned_dict[key] = cleaned_values
                    else:
                        cleaned_dict[key] = values
                return cleaned_dict
            
            return indicator_data
        except Exception as e:
            print(f"DEBUG: Error cleaning indicator {indicator_name}: {e}")
            return None
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            'chart_type': {'type': 'str', 'required': True, 
                          'description': 'Type of chart (price_chart, technical_chart, performance_chart, comparison_chart, volume_chart)'},
            'data': {'type': 'dict', 'required': True, 'description': 'Chart data'},
            'title': {'type': 'str', 'required': False, 'description': 'Chart title'},
            'save_path': {'type': 'str', 'required': False, 'description': 'Path to save the chart'}
        }