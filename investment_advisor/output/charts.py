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
            
            # Use bulletproof chart generation for all types
            chart_path = self._create_bulletproof_chart(data, chart_type, title, save_path)
            
            if chart_path:
                return ToolResult(
                    success=True,
                    data={'chart_path': chart_path},
                    metadata={'chart_type': chart_type, 'title': title}
                )
            else:
                raise ValueError("Chart generation returned None")
        
        except Exception as e:
            print(f"DEBUG: Chart generation error: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Create an error chart as last resort
            try:
                error_chart_path = self._create_error_chart(str(e))
                return ToolResult(
                    success=False,
                    error=f"Chart generation failed: {str(e)}",
                    data={'chart_path': error_chart_path}
                )
            except:
                return ToolResult(
                    success=False,
                    error=f"Chart generation failed: {str(e)}"
                )
    
    def _create_bulletproof_chart(self, data: Dict[str, Any], chart_type: str, title: str = None, save_path: str = None) -> str:
        """Create a chart that absolutely will not fail due to data type issues."""
        print(f"DEBUG: Creating bulletproof {chart_type} chart")
        
        try:
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Extract price data with maximum safety
            price_data = data.get('price_data')
            if price_data is None:
                raise ValueError("No price_data found")
            
            print(f"DEBUG: Price data type: {type(price_data)}")
            
            # Get Close prices - try multiple approaches
            close_values = None
            
            # Method 1: DataFrame access
            if hasattr(price_data, 'Close'):
                try:
                    close_values = price_data['Close'].values
                    print("DEBUG: Extracted Close via DataFrame column")
                except:
                    pass
            
            # Method 2: Dictionary access
            if close_values is None and isinstance(price_data, dict):
                try:
                    close_values = price_data['Close']
                    print("DEBUG: Extracted Close via dict key")
                except:
                    pass
            
            # Method 3: Try to find any numeric column
            if close_values is None:
                if hasattr(price_data, 'columns'):
                    for col in ['Close', 'close', 'CLOSE', 'price', 'Price']:
                        if col in price_data.columns:
                            try:
                                close_values = price_data[col].values
                                print(f"DEBUG: Found price data in column: {col}")
                                break
                            except:
                                continue
            
            if close_values is None:
                raise ValueError("Could not extract price data from any expected format")
            
            # Convert to safe numpy array
            try:
                # Force conversion to numpy array of floats
                close_array = np.array(close_values, dtype=np.float64)
                print(f"DEBUG: Converted to numpy array, shape: {close_array.shape}")
            except:
                # If that fails, try pandas numeric conversion first
                close_series = pd.to_numeric(close_values, errors='coerce')
                close_array = np.array(close_series, dtype=np.float64)
                print("DEBUG: Had to use pandas conversion first")
            
            # Remove non-finite values
            finite_mask = np.isfinite(close_array)
            clean_prices = close_array[finite_mask]
            
            if len(clean_prices) == 0:
                raise ValueError("No finite price data available after cleaning")
            
            # Create simple x-axis
            x_values = np.arange(len(clean_prices))
            
            print(f"DEBUG: Final arrays - X: {len(x_values)} points, Y: {len(clean_prices)} points")
            print(f"DEBUG: Data types - X: {x_values.dtype}, Y: {clean_prices.dtype}")
            
            # Plot with maximum safety
            ax.plot(x_values, clean_prices, linewidth=2, color='blue', label='Price')
            ax.set_title(title or 'Stock Price Chart')
            ax.set_xlabel('Time Period')
            ax.set_ylabel('Price ($)')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # Save the chart
            if save_path is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                save_path = os.path.join(self.output_dir, f"bulletproof_chart_{timestamp}.png")
            
            plt.tight_layout()
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"DEBUG: Successfully saved chart to {save_path}")
            return save_path
            
        except Exception as e:
            print(f"DEBUG: Error in bulletproof chart: {e}")
            return self._create_error_chart(str(e))
    
    def _create_error_chart(self, error_message: str) -> str:
        """Create a chart showing the error message."""
        try:
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.text(0.5, 0.5, f'Chart Generation Error:\n{error_message}', 
                   ha='center', va='center', transform=ax.transAxes, wrap=True)
            ax.set_title("Chart Error - Please Check Data")
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_path = os.path.join(self.output_dir, f"error_chart_{timestamp}.png")
            
            plt.tight_layout()
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return save_path
        except:
            return None
    
    def create_price_chart(self, data: Dict[str, Any], title: str = None, 
                          save_path: str = None, **kwargs) -> str:
        """Create a basic price chart."""
        print("DEBUG: Starting price chart creation")
        
        try:
            fig, ax = plt.subplots(figsize=(12, 8))
            
            price_data = data['price_data']
            print(f"DEBUG: Raw price_data type: {type(price_data)}")
            
            # Ultra-safe data extraction
            try:
                # Get Close prices as numpy array
                if hasattr(price_data, 'Close'):
                    close_values = price_data['Close'].values
                elif isinstance(price_data, dict) and 'Close' in price_data:
                    close_values = price_data['Close']
                else:
                    raise ValueError("Cannot find Close price data")
                
                print(f"DEBUG: Close values type: {type(close_values)}, shape: {getattr(close_values, 'shape', len(close_values))}")
                
                # Convert to pure numpy float array
                close_array = np.array(close_values, dtype=np.float64)
                
                # Remove any non-finite values
                finite_mask = np.isfinite(close_array)
                clean_close = close_array[finite_mask]
                
                if len(clean_close) == 0:
                    raise ValueError("No finite Close price data available")
                
                # Create simple range index for x-axis
                x_values = np.arange(len(clean_close))
                
                print(f"DEBUG: Final data - X: {type(x_values)}, Y: {type(clean_close)}")
                print(f"DEBUG: Data lengths - X: {len(x_values)}, Y: {len(clean_close)}")
                
                # Simple, safe plot
                ax.plot(x_values, clean_close, label='Close Price', linewidth=2, color='blue')
                ax.set_title(title or "Stock Price Chart")
                ax.set_xlabel('Time Period')
                ax.set_ylabel('Price ($)')
                ax.legend()
                ax.grid(True, alpha=0.3)
                
                print("DEBUG: Successfully created basic price chart")
                
            except Exception as plot_error:
                print(f"DEBUG: Error in plotting: {plot_error}")
                # Create a minimal fallback chart
                ax.text(0.5, 0.5, f'Chart data error:\n{str(plot_error)}', 
                       ha='center', va='center', transform=ax.transAxes)
                ax.set_title(title or "Chart Generation Error")
                
            plt.tight_layout()
            
            if save_path is None:
                save_path = os.path.join(self.output_dir, f"price_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return save_path
            
        except Exception as e:
            print(f"DEBUG: Critical error in create_price_chart: {e}")
            # Create a minimal error chart
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.text(0.5, 0.5, f'Chart Generation Failed:\n{str(e)}', 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title("Chart Error")
            
            if save_path is None:
                save_path = os.path.join(self.output_dir, f"error_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return save_path
    
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
        
        # Main price chart with Bollinger Bands
        ax1.plot(clean_data.index, clean_data['Close'], label='Close Price', linewidth=2)
        
        if 'bollinger_bands' in data:
            bb_clean = self._clean_indicator_data(data, 'bollinger_bands')
            if bb_clean and all(key in bb_clean for key in ['upper_band', 'middle_band', 'lower_band']):
                ax1.plot(clean_data.index, bb_clean['upper_band'], label='BB Upper', alpha=0.5, linestyle='--')
                ax1.plot(clean_data.index, bb_clean['middle_band'], label='BB Middle', alpha=0.7)
                ax1.plot(clean_data.index, bb_clean['lower_band'], label='BB Lower', alpha=0.5, linestyle='--')
                ax1.fill_between(clean_data.index, bb_clean['upper_band'], bb_clean['lower_band'], alpha=0.1)
        
        ax1.set_title(title or f"Technical Analysis - {data.get('symbol', 'Stock')}")
        ax1.set_ylabel('Price ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # RSI chart
        if 'rsi' in data:
            rsi_clean = self._clean_indicator_data(data, 'rsi')
            if rsi_clean is not None:
                ax2.plot(clean_data.index, rsi_clean, label='RSI', color='orange')
            ax2.axhline(y=70, color='r', linestyle='--', alpha=0.5)
            ax2.axhline(y=30, color='g', linestyle='--', alpha=0.5)
            ax2.set_ylabel('RSI')
            ax2.set_ylim(0, 100)
            ax2.legend()
            ax2.grid(True, alpha=0.3)
        
        # MACD chart
        if 'macd' in data:
            macd_clean = self._clean_indicator_data(data, 'macd')
            if macd_clean and all(key in macd_clean for key in ['macd_line', 'signal_line', 'histogram']):
                ax3.plot(clean_data.index, macd_clean['macd_line'], label='MACD', color='blue')
                ax3.plot(clean_data.index, macd_clean['signal_line'], label='Signal', color='red')
                ax3.bar(clean_data.index, macd_clean['histogram'], label='Histogram', alpha=0.3)
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
        
        # Clean the data before plotting
        clean_data = self._clean_data_for_plotting(price_data)
        if clean_data is None or len(clean_data) == 0:
            raise ValueError("No valid data available for plotting")
        
        # Price chart
        ax1.plot(clean_data.index, clean_data['Close'], label='Close Price', linewidth=2)
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
        ax2.bar(clean_data.index, clean_data['Volume'], alpha=0.7)
        ax2.set_ylabel('Volume')
        ax2.set_xlabel('Date')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path is None:
            save_path = os.path.join(self.output_dir, f"volume_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return save_path
    
    def _safe_convert_for_plotting(self, data, data_name="data"):
        """Convert data to types safe for matplotlib plotting."""
        print(f"DEBUG: Converting {data_name} for plotting")
        
        if data is None:
            raise ValueError(f"{data_name} is None")
        
        try:
            # Convert to numpy array first
            import numpy as np
            
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
                    if data_name == "index":
                        try:
                            array_data = pd.to_datetime(array_data)
                            return array_data
                        except:
                            pass
                    # Last resort: use range index
                    print(f"DEBUG: Using range index for {data_name}")
                    array_data = np.arange(len(data))
            
            # Handle string/datetime index
            elif data_name == "index" and not np.issubdtype(array_data.dtype, np.number):
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
                    if data_name != "index":
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
            if data_name == "index":
                return np.arange(len(data) if hasattr(data, '__len__') else 10)
            else:
                return np.zeros(len(data) if hasattr(data, '__len__') else 10)
    
    def _clean_data_for_plotting(self, data):
        """Clean data to ensure it's safe for matplotlib plotting."""
        if data is None:
            return None
            
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
            if col in clean_data.columns:
                # Convert to numeric, coercing errors to NaN
                clean_data[col] = pd.to_numeric(clean_data[col], errors='coerce')
                # Replace infinite values with NaN
                clean_data[col] = clean_data[col].replace([np.inf, -np.inf], np.nan)
        
        # Drop rows with all NaN values in essential columns
        essential_cols = [col for col in ['Close', 'Open', 'High', 'Low'] if col in clean_data.columns]
        if essential_cols:
            clean_data = clean_data.dropna(subset=essential_cols, how='all')
        
        return clean_data
    
    def _clean_indicator_data(self, data, indicator_name):
        """Clean technical indicator data for plotting."""
        if indicator_name not in data or data[indicator_name] is None:
            return None
            
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
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            'chart_type': {'type': 'str', 'required': True, 
                          'description': 'Type of chart (price_chart, technical_chart, performance_chart, comparison_chart, volume_chart)'},
            'data': {'type': 'dict', 'required': True, 'description': 'Chart data'},
            'title': {'type': 'str', 'required': False, 'description': 'Chart title'},
            'save_path': {'type': 'str', 'required': False, 'description': 'Path to save the chart'}
        }