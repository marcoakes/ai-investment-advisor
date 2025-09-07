"""
Backtesting tools for trading strategies.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
from datetime import datetime
from ..core.base import BaseTool, ToolResult, ToolType


class SimpleBacktester(BaseTool):
    """Simple backtesting engine for trading strategies."""
    
    def __init__(self):
        super().__init__("simple_backtester", ToolType.ANALYSIS)
    
    def execute(self, data: pd.DataFrame, signals: pd.Series, 
                initial_capital: float = 10000, commission: float = 0.001, **kwargs) -> ToolResult:
        """Backtest a trading strategy."""
        try:
            # Initialize portfolio
            portfolio = pd.DataFrame(index=data.index)
            portfolio['price'] = data['Close']
            portfolio['signals'] = signals
            
            # Generate positions
            portfolio['positions'] = portfolio['signals'].diff()
            
            # Calculate portfolio value
            portfolio['holdings'] = (portfolio['positions'] * portfolio['price']).cumsum()
            portfolio['cash'] = initial_capital - (portfolio['positions'] * portfolio['price']).cumsum()
            portfolio['total'] = portfolio['cash'] + portfolio['holdings']
            portfolio['returns'] = portfolio['total'].pct_change()
            
            # Apply commission
            portfolio['commission'] = abs(portfolio['positions']) * portfolio['price'] * commission
            portfolio['total'] -= portfolio['commission'].cumsum()
            
            # Calculate performance metrics
            performance_metrics = self.calculate_performance_metrics(
                portfolio, initial_capital
            )
            
            return ToolResult(
                success=True,
                data={
                    'portfolio': portfolio,
                    'performance_metrics': performance_metrics,
                    'final_value': portfolio['total'].iloc[-1]
                },
                metadata={
                    'initial_capital': initial_capital,
                    'commission': commission,
                    'strategy_type': 'signal_based'
                }
            )
        
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Backtesting failed: {str(e)}"
            )
    
    def calculate_performance_metrics(self, portfolio: pd.DataFrame, 
                                    initial_capital: float) -> Dict[str, float]:
        """Calculate performance metrics for the strategy."""
        returns = portfolio['returns'].dropna()
        total_return = (portfolio['total'].iloc[-1] / initial_capital - 1) * 100
        
        # Calculate Sharpe ratio (assuming risk-free rate of 0)
        sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
        
        # Calculate maximum drawdown
        rolling_max = portfolio['total'].expanding().max()
        drawdown = (portfolio['total'] - rolling_max) / rolling_max
        max_drawdown = drawdown.min() * 100
        
        # Calculate volatility
        volatility = returns.std() * np.sqrt(252) * 100
        
        # Calculate win rate
        winning_returns = returns[returns > 0]
        win_rate = len(winning_returns) / len(returns) * 100 if len(returns) > 0 else 0
        
        return {
            'total_return': round(total_return, 2),
            'annualized_return': round((portfolio['total'].iloc[-1] / initial_capital) ** (252 / len(portfolio)) - 1, 4) * 100,
            'sharpe_ratio': round(sharpe_ratio, 3),
            'max_drawdown': round(max_drawdown, 2),
            'volatility': round(volatility, 2),
            'win_rate': round(win_rate, 2)
        }
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            'data': {'type': 'DataFrame', 'required': True, 'description': 'Stock price data'},
            'signals': {'type': 'Series', 'required': True, 'description': 'Trading signals'},
            'initial_capital': {'type': 'float', 'required': False, 'default': 10000,
                              'description': 'Initial capital for backtesting'},
            'commission': {'type': 'float', 'required': False, 'default': 0.001,
                         'description': 'Commission rate per trade'}
        }


class StrategyComparison(BaseTool):
    """Compare multiple trading strategies."""
    
    def __init__(self):
        super().__init__("strategy_comparison", ToolType.ANALYSIS)
        self.backtester = SimpleBacktester()
    
    def execute(self, data: pd.DataFrame, strategies: Dict[str, pd.Series], 
                initial_capital: float = 10000, **kwargs) -> ToolResult:
        """Compare multiple trading strategies."""
        try:
            results = {}
            
            for strategy_name, signals in strategies.items():
                backtest_result = self.backtester.execute(
                    data, signals, initial_capital, **kwargs
                )
                
                if backtest_result.success:
                    results[strategy_name] = {
                        'performance_metrics': backtest_result.data['performance_metrics'],
                        'final_value': backtest_result.data['final_value'],
                        'portfolio': backtest_result.data['portfolio']
                    }
            
            # Rank strategies
            ranking = self.rank_strategies(results)
            
            return ToolResult(
                success=True,
                data={
                    'strategy_results': results,
                    'ranking': ranking,
                    'comparison_summary': self.create_comparison_summary(results)
                },
                metadata={
                    'strategies_compared': len(strategies),
                    'initial_capital': initial_capital
                }
            )
        
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Strategy comparison failed: {str(e)}"
            )
    
    def rank_strategies(self, results: Dict[str, Dict]) -> List[Dict[str, Any]]:
        """Rank strategies based on risk-adjusted returns."""
        strategy_scores = []
        
        for strategy_name, result in results.items():
            metrics = result['performance_metrics']
            # Simple scoring: combine return and Sharpe ratio
            score = (metrics['total_return'] * 0.5 + 
                    metrics['sharpe_ratio'] * 10 * 0.3 - 
                    abs(metrics['max_drawdown']) * 0.2)
            
            strategy_scores.append({
                'strategy': strategy_name,
                'score': round(score, 2),
                'total_return': metrics['total_return'],
                'sharpe_ratio': metrics['sharpe_ratio'],
                'max_drawdown': metrics['max_drawdown']
            })
        
        return sorted(strategy_scores, key=lambda x: x['score'], reverse=True)
    
    def create_comparison_summary(self, results: Dict[str, Dict]) -> Dict[str, Any]:
        """Create a summary comparison of strategies."""
        if not results:
            return {}
        
        metrics_summary = {}
        for metric in ['total_return', 'sharpe_ratio', 'max_drawdown', 'volatility']:
            values = [result['performance_metrics'][metric] for result in results.values()]
            metrics_summary[metric] = {
                'best': max(values) if metric != 'max_drawdown' else max(values, key=abs),
                'worst': min(values) if metric != 'max_drawdown' else min(values, key=abs),
                'average': sum(values) / len(values)
            }
        
        return metrics_summary
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            'data': {'type': 'DataFrame', 'required': True, 'description': 'Stock price data'},
            'strategies': {'type': 'dict', 'required': True, 
                          'description': 'Dictionary of strategy names and their signals'},
            'initial_capital': {'type': 'float', 'required': False, 'default': 10000,
                              'description': 'Initial capital for backtesting'}
        }


class RiskAnalyzer(BaseTool):
    """Analyze risk metrics for trading strategies."""
    
    def __init__(self):
        super().__init__("risk_analyzer", ToolType.ANALYSIS)
    
    def execute(self, portfolio_returns: pd.Series, benchmark_returns: pd.Series = None, 
                **kwargs) -> ToolResult:
        """Analyze risk metrics."""
        try:
            risk_metrics = {}
            
            # Basic risk metrics
            risk_metrics['volatility'] = portfolio_returns.std() * np.sqrt(252) * 100
            risk_metrics['var_95'] = np.percentile(portfolio_returns, 5) * 100
            risk_metrics['cvar_95'] = portfolio_returns[portfolio_returns <= np.percentile(portfolio_returns, 5)].mean() * 100
            
            # Skewness and Kurtosis
            risk_metrics['skewness'] = portfolio_returns.skew()
            risk_metrics['kurtosis'] = portfolio_returns.kurtosis()
            
            # If benchmark provided, calculate additional metrics
            if benchmark_returns is not None:
                excess_returns = portfolio_returns - benchmark_returns
                risk_metrics['tracking_error'] = excess_returns.std() * np.sqrt(252) * 100
                risk_metrics['information_ratio'] = (excess_returns.mean() / excess_returns.std() * np.sqrt(252)) if excess_returns.std() > 0 else 0
                
                # Beta calculation
                covariance = np.cov(portfolio_returns, benchmark_returns)[0, 1]
                benchmark_variance = benchmark_returns.var()
                risk_metrics['beta'] = covariance / benchmark_variance if benchmark_variance > 0 else 0
            
            return ToolResult(
                success=True,
                data=risk_metrics,
                metadata={'analysis_type': 'risk_analysis'}
            )
        
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Risk analysis failed: {str(e)}"
            )
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            'portfolio_returns': {'type': 'Series', 'required': True, 
                                'description': 'Portfolio returns series'},
            'benchmark_returns': {'type': 'Series', 'required': False, 
                                'description': 'Benchmark returns for comparison'}
        }