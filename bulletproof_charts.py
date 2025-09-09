"""
Bulletproof chart generation that handles any data type issues.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import Dict, Any
import os
from datetime import datetime

def bulletproof_chart(data: Dict[str, Any], chart_type: str = "price", output_dir: str = "charts") -> str:
    """
    Create a chart that absolutely will not fail due to data type issues.
    """
    print(f"DEBUG: Creating bulletproof {chart_type} chart")
    
    try:
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
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
        ax.set_title('Stock Price Chart')
        ax.set_xlabel('Time Period')
        ax.set_ylabel('Price ($)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Save the chart
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        save_path = os.path.join(output_dir, f"bulletproof_chart_{timestamp}.png")
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"DEBUG: Successfully saved chart to {save_path}")
        return save_path
        
    except Exception as e:
        print(f"DEBUG: Error in bulletproof chart: {e}")
        
        # Last resort: create error message chart
        try:
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.text(0.5, 0.5, f'Chart Generation Error:\n{str(e)}\n\nData keys: {list(data.keys()) if isinstance(data, dict) else "Not a dict"}', 
                   ha='center', va='center', transform=ax.transAxes, wrap=True)
            ax.set_title("Chart Error - Please Check Data")
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_path = os.path.join(output_dir, f"error_chart_{timestamp}.png")
            
            plt.tight_layout()
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return save_path
            
        except Exception as final_error:
            print(f"DEBUG: Even error chart failed: {final_error}")
            return None

if __name__ == "__main__":
    # Test with dummy data
    test_data = {
        'price_data': pd.DataFrame({
            'Close': [100, 101, 99, 102, 98]
        })
    }
    
    result = bulletproof_chart(test_data)
    print(f"Test result: {result}")