#!/usr/bin/env python3
"""
Simple, self-contained demo of the AI Investment Research Assistant
"""

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class SimpleInvestmentAnalyzer:
    """A simple, self-contained investment analysis tool."""
    
    def __init__(self):
        print("🚀 Simple Investment Analyzer initialized!")
    
    def get_stock_data(self, symbol: str, period: str = "6mo"):
        """Fetch stock data using yfinance."""
        try:
            print(f"📊 Fetching data for {symbol}...")
            
            # Get stock data
            stock = yf.Ticker(symbol)
            data = stock.history(period=period)
            info = stock.info
            
            if data.empty:
                return None, f"No data found for symbol {symbol}"
            
            print(f"✅ Retrieved {len(data)} data points for {symbol}")
            return {'price_data': data, 'info': info}, None
            
        except Exception as e:
            return None, f"Error fetching data: {str(e)}"
    
    def calculate_technical_indicators(self, data):
        """Calculate technical indicators."""
        try:
            print("🔧 Calculating technical indicators...")
            
            df = data.copy()
            
            # Simple Moving Averages
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            df['SMA_50'] = df['Close'].rolling(window=50).mean()
            
            # RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # Bollinger Bands
            rolling_mean = df['Close'].rolling(window=20).mean()
            rolling_std = df['Close'].rolling(window=20).std()
            df['BB_Upper'] = rolling_mean + (rolling_std * 2)
            df['BB_Lower'] = rolling_mean - (rolling_std * 2)
            df['BB_Middle'] = rolling_mean
            
            print("✅ Technical indicators calculated successfully!")
            return df, None
            
        except Exception as e:
            return None, f"Error calculating indicators: {str(e)}"
    
    def create_safe_chart(self, data, symbol, title="Stock Analysis"):
        """Create a chart with maximum safety against data type errors."""
        try:
            print("🎨 Creating chart with safe data handling...")
            
            # Clean and validate data
            if data is None or len(data) == 0:
                raise ValueError("No data available for charting")
            
            # Ensure we have numeric data
            numeric_data = data.select_dtypes(include=[np.number])
            if numeric_data.empty:
                raise ValueError("No numeric data found")
            
            # Create the chart
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
            
            # Convert index to range if needed for safety
            x_range = range(len(data))
            
            # 1. Price chart with moving averages
            if 'Close' in data.columns:
                close_clean = pd.to_numeric(data['Close'], errors='coerce').dropna()
                if not close_clean.empty:
                    ax1.plot(x_range[-len(close_clean):], close_clean, 
                           label='Close Price', linewidth=2, color='blue')
                    
                    # Add SMAs if available
                    if 'SMA_20' in data.columns:
                        sma20_clean = pd.to_numeric(data['SMA_20'], errors='coerce').dropna()
                        if not sma20_clean.empty:
                            ax1.plot(x_range[-len(sma20_clean):], sma20_clean, 
                                   label='SMA 20', alpha=0.7, color='orange')
                    
                    if 'SMA_50' in data.columns:
                        sma50_clean = pd.to_numeric(data['SMA_50'], errors='coerce').dropna()
                        if not sma50_clean.empty:
                            ax1.plot(x_range[-len(sma50_clean):], sma50_clean, 
                                   label='SMA 50', alpha=0.7, color='red')
            
            ax1.set_title(f'{symbol} - Price with Moving Averages')
            ax1.set_xlabel('Time Period')
            ax1.set_ylabel('Price ($)')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # 2. RSI Chart
            if 'RSI' in data.columns:
                rsi_clean = pd.to_numeric(data['RSI'], errors='coerce').dropna()
                if not rsi_clean.empty:
                    ax2.plot(x_range[-len(rsi_clean):], rsi_clean, 
                           color='purple', linewidth=2)
                    ax2.axhline(y=70, color='r', linestyle='--', alpha=0.5)
                    ax2.axhline(y=30, color='g', linestyle='--', alpha=0.5)
                    ax2.set_ylim(0, 100)
                    ax2.set_title('RSI (Relative Strength Index)')
                    ax2.set_ylabel('RSI')
                    ax2.grid(True, alpha=0.3)
            else:
                ax2.text(0.5, 0.5, 'RSI data not available', 
                        ha='center', va='center', transform=ax2.transAxes)
                ax2.set_title('RSI')
            
            # 3. Volume Chart
            if 'Volume' in data.columns:
                volume_clean = pd.to_numeric(data['Volume'], errors='coerce').dropna()
                if not volume_clean.empty:
                    ax3.bar(x_range[-len(volume_clean):], volume_clean, 
                          alpha=0.7, color='green')
                    ax3.set_title('Trading Volume')
                    ax3.set_ylabel('Volume')
                    ax3.grid(True, alpha=0.3)
            else:
                ax3.text(0.5, 0.5, 'Volume data not available', 
                        ha='center', va='center', transform=ax3.transAxes)
                ax3.set_title('Volume')
            
            # 4. Bollinger Bands
            if all(col in data.columns for col in ['Close', 'BB_Upper', 'BB_Lower', 'BB_Middle']):
                close_clean = pd.to_numeric(data['Close'], errors='coerce').dropna()
                upper_clean = pd.to_numeric(data['BB_Upper'], errors='coerce').dropna()
                lower_clean = pd.to_numeric(data['BB_Lower'], errors='coerce').dropna()
                middle_clean = pd.to_numeric(data['BB_Middle'], errors='coerce').dropna()
                
                min_len = min(len(close_clean), len(upper_clean), len(lower_clean), len(middle_clean))
                if min_len > 0:
                    x_bb = x_range[-min_len:]
                    ax4.plot(x_bb, close_clean[-min_len:], label='Close', linewidth=2, color='blue')
                    ax4.plot(x_bb, upper_clean[-min_len:], label='BB Upper', linestyle='--', alpha=0.7, color='red')
                    ax4.plot(x_bb, middle_clean[-min_len:], label='BB Middle', alpha=0.7, color='orange')
                    ax4.plot(x_bb, lower_clean[-min_len:], label='BB Lower', linestyle='--', alpha=0.7, color='red')
                    ax4.fill_between(x_bb, upper_clean[-min_len:], lower_clean[-min_len:], alpha=0.1)
                    ax4.set_title('Bollinger Bands')
                    ax4.legend()
                    ax4.grid(True, alpha=0.3)
            else:
                ax4.text(0.5, 0.5, 'Bollinger Bands data not available', 
                        ha='center', va='center', transform=ax4.transAxes)
                ax4.set_title('Bollinger Bands')
            
            plt.tight_layout()
            plt.show()
            
            print("✅ Chart created successfully!")
            return True, None
            
        except Exception as e:
            print(f"❌ Chart creation failed: {str(e)}")
            # Create a simple fallback chart
            try:
                plt.figure(figsize=(10, 6))
                if 'Close' in data.columns:
                    close_clean = pd.to_numeric(data['Close'], errors='coerce').dropna()
                    if not close_clean.empty:
                        plt.plot(close_clean, linewidth=2, label=f'{symbol} Price')
                        plt.title(f'{symbol} - Simple Price Chart')
                        plt.xlabel('Time Period')
                        plt.ylabel('Price ($)')
                        plt.legend()
                        plt.grid(True, alpha=0.3)
                        plt.show()
                        return True, "Simplified chart created"
                
                plt.text(0.5, 0.5, f'Chart Error:\n{str(e)}', 
                        ha='center', va='center', transform=plt.gca().transAxes)
                plt.title("Chart Generation Error")
                plt.show()
                return False, str(e)
                
            except Exception as final_e:
                return False, f"Complete chart failure: {str(final_e)}"
    
    def generate_trading_signals(self, data):
        """Generate simple trading signals."""
        try:
            print("🎯 Generating trading signals...")
            
            signals = pd.DataFrame(index=data.index)
            signals['Close'] = data['Close']
            signals['Signal'] = 0
            
            # Simple SMA crossover strategy
            if 'SMA_20' in data.columns and 'SMA_50' in data.columns:
                # Buy signal: SMA20 crosses above SMA50
                signals['Signal'][20:] = np.where(
                    data['SMA_20'][20:] > data['SMA_50'][20:], 1, 0
                )
                signals['Position'] = signals['Signal'].diff()
                
                # Add RSI filter if available
                if 'RSI' in data.columns:
                    # Only buy if RSI < 70 (not overbought)
                    # Only sell if RSI > 30 (not oversold)
                    signals.loc[data['RSI'] > 70, 'Signal'] = 0
                    signals.loc[data['RSI'] < 30, 'Position'] = 0
            
            buy_signals = signals[signals['Position'] == 1]
            sell_signals = signals[signals['Position'] == -1]
            
            current_signal = "HOLD"
            if not signals.empty:
                last_signal = signals['Signal'].iloc[-1]
                current_signal = "BUY" if last_signal == 1 else "SELL" if last_signal == -1 else "HOLD"
            
            print(f"🎯 Current Signal: {current_signal}")
            print(f"📊 Buy signals: {len(buy_signals)}, Sell signals: {len(sell_signals)}")
            
            return signals, None
            
        except Exception as e:
            return None, f"Error generating signals: {str(e)}"
    
    def analyze_stock(self, symbol: str, period: str = "6mo"):
        """Complete stock analysis workflow."""
        print(f"\n🔍 Starting analysis for {symbol}")
        print("=" * 50)
        
        # 1. Fetch data
        result, error = self.get_stock_data(symbol, period)
        if error:
            print(f"❌ {error}")
            return False
        
        stock_data = result['price_data']
        stock_info = result['info']
        
        # 2. Display basic info
        print(f"🏢 Company: {stock_info.get('longName', symbol)}")
        print(f"💰 Current Price: ${stock_info.get('currentPrice', 'N/A')}")
        print(f"🏢 Sector: {stock_info.get('sector', 'N/A')}")
        print(f"📅 Data Range: {len(stock_data)} trading days")
        
        # 3. Calculate technical indicators
        enhanced_data, error = self.calculate_technical_indicators(stock_data)
        if error:
            print(f"⚠️ Technical analysis warning: {error}")
            enhanced_data = stock_data
        
        # 4. Create charts
        chart_success, chart_error = self.create_safe_chart(enhanced_data, symbol)
        if chart_error:
            print(f"⚠️ Chart warning: {chart_error}")
        
        # 5. Generate trading signals
        signals, signal_error = self.generate_trading_signals(enhanced_data)
        if signal_error:
            print(f"⚠️ Signal warning: {signal_error}")
        
        # 6. Display recent data
        print(f"\n📊 Recent Price Data (Last 5 Days):")
        recent_data = stock_data[['Open', 'High', 'Low', 'Close', 'Volume']].tail()
        print(recent_data.to_string())
        
        # 7. Current technical levels
        if enhanced_data is not None and len(enhanced_data) > 0:
            print(f"\n📈 Current Technical Indicators:")
            latest = enhanced_data.iloc[-1]
            
            if 'SMA_20' in enhanced_data.columns and not pd.isna(latest['SMA_20']):
                print(f"   SMA 20: ${latest['SMA_20']:.2f}")
            if 'SMA_50' in enhanced_data.columns and not pd.isna(latest['SMA_50']):
                print(f"   SMA 50: ${latest['SMA_50']:.2f}")
            if 'RSI' in enhanced_data.columns and not pd.isna(latest['RSI']):
                print(f"   RSI: {latest['RSI']:.2f}")
        
        print(f"\n✅ Analysis complete for {symbol}!")
        return True

def main():
    """Main demo function."""
    print("🤖 AI Investment Research Assistant - Simple Demo")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = SimpleInvestmentAnalyzer()
    
    # Demo stocks to analyze
    stocks = ["AAPL", "TSLA", "GOOGL"]
    
    for symbol in stocks:
        try:
            success = analyzer.analyze_stock(symbol)
            if not success:
                print(f"⚠️ Analysis failed for {symbol}")
        except Exception as e:
            print(f"❌ Error analyzing {symbol}: {str(e)}")
        
        print("\n" + "="*60 + "\n")
    
    print("🎉 Demo completed!")
    print("\n💡 Tips:")
    print("- Charts use safe data conversion to avoid matplotlib errors")
    print("- All calculations include error handling")
    print("- Technical indicators are optional and won't break the analysis")
    print("- This is for educational purposes only - not financial advice")

if __name__ == "__main__":
    main()