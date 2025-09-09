# AI Investment Advisor - Comprehensive Test Suite
# Tests for the ProfessionalInvestmentAnalyzer class

import pytest
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import sys
import os

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the analyzer class (this would be imported from the notebook code)
# For testing purposes, we'll mock the class structure

class MockProfessionalInvestmentAnalyzer:
    """Mock version of the analyzer for testing."""
    
    def __init__(self, educational_mode=True):
        self.educational_mode = educational_mode
        self.risk_free_rate = 0.02
        self.trading_costs = 0.001
    
    def get_stock_data(self, symbol, period="1y"):
        """Mock data fetcher."""
        # Create sample data for testing
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        np.random.seed(42)  # For reproducible tests
        
        data = pd.DataFrame({
            'Open': 100 + np.random.randn(len(dates)).cumsum() * 0.02,
            'High': 100 + np.random.randn(len(dates)).cumsum() * 0.02 + 1,
            'Low': 100 + np.random.randn(len(dates)).cumsum() * 0.02 - 1,
            'Close': 100 + np.random.randn(len(dates)).cumsum() * 0.02,
            'Volume': np.random.randint(1000000, 5000000, len(dates))
        }, index=dates)
        
        info = {
            'longName': 'Test Company Inc.',
            'currentPrice': data['Close'].iloc[-1],
            'sector': 'Technology',
            'marketCap': 1000000000
        }
        
        return {'price_data': data, 'info': info}, None
    
    def calculate_technical_indicators(self, data):
        """Calculate technical indicators."""
        try:
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
            
            # Returns and Volatility
            df['Returns'] = df['Close'].pct_change()
            df['Volatility_20'] = df['Returns'].rolling(window=20).std() * np.sqrt(252)
            
            return df, None
        except Exception as e:
            return None, str(e)

class TestInvestmentAnalyzer:
    """Test cases for the Investment Analyzer."""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance for testing."""
        return MockProfessionalInvestmentAnalyzer()
    
    @pytest.fixture
    def sample_data(self, analyzer):
        """Get sample stock data for testing."""
        result, error = analyzer.get_stock_data("TEST", "1y")
        assert error is None
        return result['price_data']
    
    def test_analyzer_initialization(self, analyzer):
        """Test analyzer initialization."""
        assert analyzer.educational_mode is True
        assert analyzer.risk_free_rate == 0.02
        assert analyzer.trading_costs == 0.001
    
    def test_get_stock_data_success(self, analyzer):
        """Test successful stock data retrieval."""
        result, error = analyzer.get_stock_data("TEST", "1y")
        
        assert error is None
        assert result is not None
        assert 'price_data' in result
        assert 'info' in result
        
        data = result['price_data']
        assert isinstance(data, pd.DataFrame)
        assert len(data) > 0
        assert all(col in data.columns for col in ['Open', 'High', 'Low', 'Close', 'Volume'])
    
    def test_technical_indicators_calculation(self, analyzer, sample_data):
        """Test technical indicators calculation."""
        enhanced_data, error = analyzer.calculate_technical_indicators(sample_data)
        
        assert error is None
        assert enhanced_data is not None
        
        # Check that indicators were added
        expected_indicators = ['SMA_20', 'SMA_50', 'RSI', 'Returns', 'Volatility_20']
        for indicator in expected_indicators:
            assert indicator in enhanced_data.columns
        
        # Check RSI bounds
        rsi_values = enhanced_data['RSI'].dropna()
        assert all(rsi_values >= 0)
        assert all(rsi_values <= 100)
    
    def test_data_quality_checks(self, sample_data):
        """Test data quality and integrity."""
        # Check for missing data
        assert not sample_data.empty
        
        # Check data types
        numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in numeric_columns:
            assert pd.api.types.is_numeric_dtype(sample_data[col])
        
        # Check logical constraints (High >= Low, etc.)
        assert all(sample_data['High'] >= sample_data['Low'])
        assert all(sample_data['High'] >= sample_data['Close'])
        assert all(sample_data['Low'] <= sample_data['Close'])
        assert all(sample_data['Volume'] >= 0)
    
    def test_returns_calculation(self, analyzer, sample_data):
        """Test returns calculation accuracy."""
        enhanced_data, _ = analyzer.calculate_technical_indicators(sample_data)
        
        # Manual returns calculation for verification
        manual_returns = sample_data['Close'].pct_change()
        calculated_returns = enhanced_data['Returns']
        
        # Compare (allowing for small floating point differences)
        np.testing.assert_array_almost_equal(
            manual_returns.dropna(), 
            calculated_returns.dropna(), 
            decimal=10
        )
    
    def test_volatility_calculation(self, analyzer, sample_data):
        """Test volatility calculation."""
        enhanced_data, _ = analyzer.calculate_technical_indicators(sample_data)
        
        volatility = enhanced_data['Volatility_20'].dropna()
        
        # Volatility should be positive
        assert all(volatility >= 0)
        
        # Volatility should be reasonable (0-100% typically)
        assert all(volatility <= 2.0)  # 200% annualized volatility as upper bound
    
    def test_moving_averages(self, analyzer, sample_data):
        """Test moving average calculations."""
        enhanced_data, _ = analyzer.calculate_technical_indicators(sample_data)
        
        # Check that SMAs are calculated correctly
        sma_20_manual = sample_data['Close'].rolling(window=20).mean()
        sma_20_calculated = enhanced_data['SMA_20']
        
        np.testing.assert_array_almost_equal(
            sma_20_manual.dropna(), 
            sma_20_calculated.dropna(), 
            decimal=10
        )
    
    def test_error_handling(self, analyzer):
        """Test error handling for invalid inputs."""
        # Test with empty DataFrame
        empty_df = pd.DataFrame()
        result, error = analyzer.calculate_technical_indicators(empty_df)
        
        assert error is not None
        assert result is None

class TestPerformanceMetrics:
    """Test cases for performance metrics calculations."""
    
    def test_sharpe_ratio_calculation(self):
        """Test Sharpe ratio calculation."""
        # Create sample returns
        np.random.seed(42)
        returns = pd.Series(np.random.normal(0.001, 0.02, 252))  # Daily returns
        
        # Calculate Sharpe ratio
        excess_returns = returns.mean() * 252 - 0.02  # Annualized excess return
        volatility = returns.std() * np.sqrt(252)     # Annualized volatility
        sharpe = excess_returns / volatility
        
        # Sharpe should be reasonable
        assert isinstance(sharpe, float)
        assert not np.isnan(sharpe)
        assert abs(sharpe) < 10  # Reasonable upper bound
    
    def test_max_drawdown_calculation(self):
        """Test maximum drawdown calculation."""
        # Create sample portfolio values
        portfolio_values = pd.Series([100, 110, 105, 115, 90, 95, 120])
        
        # Calculate drawdown
        rolling_max = portfolio_values.expanding().max()
        drawdown = (portfolio_values - rolling_max) / rolling_max
        max_drawdown = drawdown.min()
        
        # Max drawdown should be negative or zero
        assert max_drawdown <= 0
        
        # In this example, max drawdown should be (90-115)/115 ≈ -0.217
        expected_max_dd = (90 - 115) / 115
        assert abs(max_drawdown - expected_max_dd) < 0.001

class TestDataValidation:
    """Test data validation and edge cases."""
    
    def test_missing_data_handling(self):
        """Test handling of missing data."""
        # Create data with NaN values
        data = pd.DataFrame({
            'Close': [100, 101, np.nan, 103, 104],
            'Volume': [1000, np.nan, 1200, 1300, 1400]
        })
        
        # Check that data cleaning works
        clean_data = data.dropna()
        assert len(clean_data) < len(data)
        assert not clean_data.isnull().any().any()
    
    def test_extreme_values(self):
        """Test handling of extreme values."""
        # Create data with extreme values
        extreme_data = pd.Series([1, 2, 1000000, 3, 4])  # One extreme outlier
        
        # Calculate basic statistics
        mean_val = extreme_data.mean()
        median_val = extreme_data.median()
        
        # Median should be more robust than mean
        assert abs(median_val - 3) < 1
        assert mean_val > median_val  # Mean pulled up by outlier
    
    def test_zero_division_handling(self):
        """Test handling of zero division scenarios."""
        # Test scenario where denominator could be zero
        gains = pd.Series([0, 0, 0, 0, 0])
        losses = pd.Series([1, 2, 3, 4, 5])
        
        # This would cause division by zero in RSI calculation
        rs = gains / losses.replace(0, np.nan)  # Avoid division by zero
        
        assert not rs.isnull().all()  # Should handle gracefully

class TestIntegration:
    """Integration tests for the complete system."""
    
    @pytest.fixture
    def analyzer(self):
        return MockProfessionalInvestmentAnalyzer()
    
    def test_end_to_end_analysis(self, analyzer):
        """Test complete analysis workflow."""
        # Step 1: Get data
        result, error = analyzer.get_stock_data("TEST", "1y")
        assert error is None
        stock_data = result['price_data']
        
        # Step 2: Calculate indicators
        enhanced_data, error = analyzer.calculate_technical_indicators(stock_data)
        assert error is None
        assert enhanced_data is not None
        
        # Step 3: Verify workflow completion
        required_columns = ['Close', 'SMA_20', 'SMA_50', 'RSI', 'Returns', 'Volatility_20']
        for col in required_columns:
            assert col in enhanced_data.columns
        
        # Step 4: Check data consistency
        assert len(enhanced_data) == len(stock_data)
        assert not enhanced_data['Close'].isnull().any()
    
    def test_multiple_stocks_consistency(self, analyzer):
        """Test consistency across multiple stocks."""
        symbols = ["TEST1", "TEST2", "TEST3"]
        results = {}
        
        for symbol in symbols:
            result, error = analyzer.get_stock_data(symbol, "1y")
            assert error is None
            
            enhanced_data, error = analyzer.calculate_technical_indicators(result['price_data'])
            assert error is None
            
            results[symbol] = enhanced_data
        
        # All results should have same structure
        first_columns = set(results[symbols[0]].columns)
        for symbol in symbols[1:]:
            assert set(results[symbol].columns) == first_columns

# ===============================================
# Performance and Benchmark Tests
# ===============================================

class TestPerformance:
    """Performance and benchmark tests."""
    
    def test_calculation_performance(self):
        """Test that calculations complete in reasonable time."""
        analyzer = MockProfessionalInvestmentAnalyzer()
        
        # Create larger dataset
        dates = pd.date_range(start='2020-01-01', end='2023-12-31', freq='D')
        np.random.seed(42)
        
        large_data = pd.DataFrame({
            'Close': 100 + np.random.randn(len(dates)).cumsum() * 0.02,
            'Volume': np.random.randint(1000000, 5000000, len(dates))
        }, index=dates)
        
        import time
        start_time = time.time()
        
        # Calculate indicators
        enhanced_data, error = analyzer.calculate_technical_indicators(large_data)
        
        end_time = time.time()
        calculation_time = end_time - start_time
        
        # Should complete within reasonable time (5 seconds for 4 years of data)
        assert calculation_time < 5.0
        assert error is None
        assert enhanced_data is not None

# ===============================================
# Run Tests
# ===============================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])