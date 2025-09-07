"""
Technical analysis tools for stock data.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
from ..core.base import BaseTool, ToolResult, ToolType


class TechnicalAnalyzer(BaseTool):
    """Technical analysis calculations for stock data."""
    
    def __init__(self):
        super().__init__("technical_analyzer", ToolType.ANALYSIS)
    
    def execute(self, data: pd.DataFrame, indicators: List[str] = None, **kwargs) -> ToolResult:
        """Calculate technical indicators."""
        if indicators is None:
            indicators = ['sma_20', 'sma_50', 'rsi', 'macd', 'bollinger_bands']
        
        try:
            results = {}
            
            if 'sma_20' in indicators:
                results['sma_20'] = self.calculate_sma(data, 20)
            
            if 'sma_50' in indicators:
                results['sma_50'] = self.calculate_sma(data, 50)
            
            if 'ema_12' in indicators:
                results['ema_12'] = self.calculate_ema(data, 12)
            
            if 'ema_26' in indicators:
                results['ema_26'] = self.calculate_ema(data, 26)
            
            if 'rsi' in indicators:
                results['rsi'] = self.calculate_rsi(data, 14)
            
            if 'macd' in indicators:
                results['macd'] = self.calculate_macd(data)
            
            if 'bollinger_bands' in indicators:
                results['bollinger_bands'] = self.calculate_bollinger_bands(data)
            
            if 'volume_sma' in indicators:
                results['volume_sma'] = self.calculate_volume_sma(data, 20)
            
            return ToolResult(
                success=True,
                data=results,
                metadata={'indicators_calculated': indicators}
            )
        
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Technical analysis failed: {str(e)}"
            )
    
    def calculate_sma(self, data: pd.DataFrame, period: int) -> pd.Series:
        """Calculate Simple Moving Average."""
        return data['Close'].rolling(window=period).mean()
    
    def calculate_ema(self, data: pd.DataFrame, period: int) -> pd.Series:
        """Calculate Exponential Moving Average."""
        return data['Close'].ewm(span=period).mean()
    
    def calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index."""
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, data: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """Calculate MACD."""
        ema_fast = self.calculate_ema(data, fast)
        ema_slow = self.calculate_ema(data, slow)
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd_line': macd_line,
            'signal_line': signal_line,
            'histogram': histogram
        }
    
    def calculate_bollinger_bands(self, data: pd.DataFrame, period: int = 20, std_dev: float = 2) -> Dict[str, pd.Series]:
        """Calculate Bollinger Bands."""
        sma = self.calculate_sma(data, period)
        std = data['Close'].rolling(window=period).std()
        
        return {
            'middle_band': sma,
            'upper_band': sma + (std * std_dev),
            'lower_band': sma - (std * std_dev)
        }
    
    def calculate_volume_sma(self, data: pd.DataFrame, period: int) -> pd.Series:
        """Calculate Volume Simple Moving Average."""
        return data['Volume'].rolling(window=period).mean()
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            'data': {'type': 'DataFrame', 'required': True, 'description': 'Stock price data'},
            'indicators': {'type': 'list', 'required': False, 
                          'description': 'List of indicators to calculate'},
        }


class TradingSignals(BaseTool):
    """Generate trading signals based on technical analysis."""
    
    def __init__(self):
        super().__init__("trading_signals", ToolType.ANALYSIS)
    
    def execute(self, data: pd.DataFrame, technical_data: Dict[str, Any], **kwargs) -> ToolResult:
        """Generate trading signals."""
        try:
            signals = {}
            
            # Moving Average Crossover Signal
            if 'sma_20' in technical_data and 'sma_50' in technical_data:
                signals['ma_crossover'] = self.ma_crossover_signal(
                    technical_data['sma_20'], technical_data['sma_50']
                )
            
            # RSI Signal
            if 'rsi' in technical_data:
                signals['rsi_signal'] = self.rsi_signal(technical_data['rsi'])
            
            # MACD Signal
            if 'macd' in technical_data:
                signals['macd_signal'] = self.macd_signal(technical_data['macd'])
            
            # Bollinger Bands Signal
            if 'bollinger_bands' in technical_data:
                signals['bb_signal'] = self.bollinger_bands_signal(
                    data['Close'], technical_data['bollinger_bands']
                )
            
            # Overall Signal
            signals['overall_signal'] = self.calculate_overall_signal(signals)
            
            return ToolResult(
                success=True,
                data=signals,
                metadata={'signals_generated': list(signals.keys())}
            )
        
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Signal generation failed: {str(e)}"
            )
    
    def ma_crossover_signal(self, short_ma: pd.Series, long_ma: pd.Series) -> pd.Series:
        """Generate moving average crossover signals."""
        signal = pd.Series(0, index=short_ma.index)
        signal[short_ma > long_ma] = 1  # Buy signal
        signal[short_ma < long_ma] = -1  # Sell signal
        return signal
    
    def rsi_signal(self, rsi: pd.Series, oversold: float = 30, overbought: float = 70) -> pd.Series:
        """Generate RSI-based signals."""
        signal = pd.Series(0, index=rsi.index)
        signal[rsi < oversold] = 1  # Buy signal
        signal[rsi > overbought] = -1  # Sell signal
        return signal
    
    def macd_signal(self, macd_data: Dict[str, pd.Series]) -> pd.Series:
        """Generate MACD-based signals."""
        macd_line = macd_data['macd_line']
        signal_line = macd_data['signal_line']
        
        signal = pd.Series(0, index=macd_line.index)
        signal[macd_line > signal_line] = 1  # Buy signal
        signal[macd_line < signal_line] = -1  # Sell signal
        return signal
    
    def bollinger_bands_signal(self, price: pd.Series, bb_data: Dict[str, pd.Series]) -> pd.Series:
        """Generate Bollinger Bands signals."""
        signal = pd.Series(0, index=price.index)
        signal[price < bb_data['lower_band']] = 1  # Buy signal (oversold)
        signal[price > bb_data['upper_band']] = -1  # Sell signal (overbought)
        return signal
    
    def calculate_overall_signal(self, signals: Dict[str, pd.Series]) -> pd.Series:
        """Calculate overall signal by combining individual signals."""
        if not signals:
            return pd.Series()
        
        # Get the first signal to determine index
        first_signal = next(iter(signals.values()))
        overall = pd.Series(0, index=first_signal.index)
        
        # Sum all signals
        for signal in signals.values():
            if isinstance(signal, pd.Series):
                overall = overall.add(signal, fill_value=0)
        
        # Normalize the overall signal
        overall = overall.apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
        
        return overall
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            'data': {'type': 'DataFrame', 'required': True, 'description': 'Stock price data'},
            'technical_data': {'type': 'dict', 'required': True, 'description': 'Technical analysis results'}
        }