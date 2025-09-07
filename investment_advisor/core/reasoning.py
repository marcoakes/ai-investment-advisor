"""
AI reasoning and task planning engine.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from .base import BaseTool, ToolResult, ToolType, ToolRegistry
from .session import SessionMemory


class TaskType(Enum):
    DATA_FETCH = "data_fetch"
    ANALYSIS = "analysis"
    VISUALIZATION = "visualization"
    REPORTING = "reporting"
    COMPARISON = "comparison"


@dataclass
class Task:
    task_type: TaskType
    tool_name: str
    parameters: Dict[str, Any]
    dependencies: List[str] = None
    task_id: str = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.task_id is None:
            self.task_id = f"{self.task_type.value}_{self.tool_name}"


class TaskPlanner:
    """Plans and sequences tasks based on user queries."""
    
    def __init__(self, tool_registry: ToolRegistry, session_memory: SessionMemory):
        self.tool_registry = tool_registry
        self.session_memory = session_memory
        self.query_patterns = self._initialize_patterns()
    
    def _initialize_patterns(self) -> Dict[str, List[str]]:
        """Initialize query patterns for task recognition."""
        return {
            'stock_analysis': [
                r'analyz[e|ing].*?(?:stock|symbol|ticker)\s+([A-Z]{1,5})',
                r'(?:stock|symbol|ticker)\s+([A-Z]{1,5}).*?analyz',
                r'tell me about\s+([A-Z]{1,5})',
                r'research\s+([A-Z]{1,5})'
            ],
            'comparison': [
                r'compar[e|ing].*?([A-Z]{1,5}).*?(?:and|vs|versus)\s+([A-Z]{1,5})',
                r'([A-Z]{1,5})\s+(?:vs|versus)\s+([A-Z]{1,5})',
                r'difference between\s+([A-Z]{1,5})\s+and\s+([A-Z]{1,5})'
            ],
            'technical_analysis': [
                r'technical\s+(?:analysis|indicators?)',
                r'(?:rsi|macd|bollinger|moving average)',
                r'trading\s+(?:signals?|strategy)',
                r'chart\s+(?:pattern|analysis)'
            ],
            'backtesting': [
                r'backtest',
                r'(?:test|testing)\s+(?:strategy|strategies)',
                r'historical\s+performance',
                r'strategy\s+performance'
            ],
            'reporting': [
                r'(?:create|generate|make)\s+(?:report|presentation)',
                r'(?:pdf|powerpoint|ppt)\s+report',
                r'export\s+(?:analysis|results)',
                r'summarize\s+(?:analysis|findings)'
            ],
            'chart_request': [
                r'(?:show|display|create|generate|plot)\s+(?:chart|graph)',
                r'visualiz[e|ation]',
                r'plot\s+(?:price|performance|data)',
                r'chart\s+(?:of|for)'
            ]
        }
    
    def parse_query(self, user_query: str) -> Dict[str, Any]:
        """Parse user query to extract intent and entities."""
        query = user_query.lower().strip()
        
        # Extract symbols
        symbols = self._extract_symbols(query)
        
        # Determine query type and create task plan
        query_info = {
            'original_query': user_query,
            'symbols': symbols,
            'query_type': None,
            'parameters': {}
        }
        
        # Check for comparison queries
        for pattern in self.query_patterns['comparison']:
            match = re.search(pattern, query)
            if match:
                query_info['query_type'] = 'comparison'
                query_info['symbols'] = [match.group(1).upper(), match.group(2).upper()]
                return query_info
        
        # Check for specific analysis types
        for analysis_type, patterns in self.query_patterns.items():
            if analysis_type == 'comparison':
                continue
            
            for pattern in patterns:
                if re.search(pattern, query):
                    query_info['query_type'] = analysis_type
                    if not symbols and analysis_type == 'stock_analysis':
                        # Try to extract symbol from pattern
                        match = re.search(pattern, query)
                        if match and match.groups():
                            symbols = [match.group(1).upper()]
                            query_info['symbols'] = symbols
                    break
            
            if query_info['query_type']:
                break
        
        # Default to stock analysis if symbols found but no specific type
        if not query_info['query_type'] and symbols:
            query_info['query_type'] = 'stock_analysis'
        elif not query_info['query_type']:
            query_info['query_type'] = 'general_query'
        
        return query_info
    
    def _extract_symbols(self, query: str) -> List[str]:
        """Extract stock symbols from query."""
        # Look for ticker symbols (1-5 uppercase letters)
        symbol_pattern = r'\b[A-Z]{1,5}\b'
        potential_symbols = re.findall(symbol_pattern, query.upper())
        
        # Filter out common English words that might be mistaken for symbols
        common_words = {'THE', 'AND', 'OR', 'FOR', 'TO', 'OF', 'IN', 'ON', 'AT', 'BY', 'IS', 'ARE', 'WAS', 'WERE'}
        symbols = [symbol for symbol in potential_symbols if symbol not in common_words]
        
        return symbols
    
    def create_task_plan(self, query_info: Dict[str, Any]) -> List[Task]:
        """Create a sequence of tasks based on the parsed query."""
        tasks = []
        query_type = query_info['query_type']
        symbols = query_info['symbols']
        
        if query_type == 'stock_analysis':
            tasks.extend(self._create_stock_analysis_plan(symbols))
        
        elif query_type == 'comparison':
            tasks.extend(self._create_comparison_plan(symbols))
        
        elif query_type == 'technical_analysis':
            if symbols:
                tasks.extend(self._create_technical_analysis_plan(symbols))
            else:
                # Use last analyzed symbol if available
                recent_symbols = self.session_memory.get_recent_symbols(1)
                if recent_symbols:
                    tasks.extend(self._create_technical_analysis_plan(recent_symbols))
        
        elif query_type == 'backtesting':
            if symbols:
                tasks.extend(self._create_backtesting_plan(symbols))
            else:
                recent_symbols = self.session_memory.get_recent_symbols(1)
                if recent_symbols:
                    tasks.extend(self._create_backtesting_plan(recent_symbols))
        
        elif query_type == 'chart_request':
            if symbols:
                tasks.extend(self._create_chart_plan(symbols))
            else:
                recent_symbols = self.session_memory.get_recent_symbols(1)
                if recent_symbols:
                    tasks.extend(self._create_chart_plan(recent_symbols))
        
        elif query_type == 'reporting':
            # Create report based on recent analysis
            tasks.extend(self._create_reporting_plan())
        
        return tasks
    
    def _create_stock_analysis_plan(self, symbols: List[str]) -> List[Task]:
        """Create task plan for stock analysis."""
        tasks = []
        
        for symbol in symbols:
            # Data acquisition
            tasks.append(Task(
                TaskType.DATA_FETCH,
                "stock_aggregator",
                {"symbol": symbol, "include_fundamentals": True, "include_news": True},
                task_id=f"data_{symbol}"
            ))
            
            # Technical analysis
            tasks.append(Task(
                TaskType.ANALYSIS,
                "technical_analyzer",
                {"symbol": symbol},
                dependencies=[f"data_{symbol}"],
                task_id=f"technical_{symbol}"
            ))
            
            # Trading signals
            tasks.append(Task(
                TaskType.ANALYSIS,
                "trading_signals",
                {"symbol": symbol},
                dependencies=[f"technical_{symbol}"],
                task_id=f"signals_{symbol}"
            ))
            
            # Chart generation
            tasks.append(Task(
                TaskType.VISUALIZATION,
                "chart_generator",
                {"chart_type": "technical_chart", "symbol": symbol},
                dependencies=[f"technical_{symbol}"],
                task_id=f"chart_{symbol}"
            ))
        
        return tasks
    
    def _create_comparison_plan(self, symbols: List[str]) -> List[Task]:
        """Create task plan for comparing multiple stocks."""
        tasks = []
        
        # Analyze each stock individually first
        for symbol in symbols:
            tasks.extend(self._create_stock_analysis_plan([symbol]))
        
        # Add comparison task
        tasks.append(Task(
            TaskType.ANALYSIS,
            "strategy_comparison",
            {"symbols": symbols},
            dependencies=[f"signals_{symbol}" for symbol in symbols],
            task_id="comparison_analysis"
        ))
        
        # Comparison chart
        tasks.append(Task(
            TaskType.VISUALIZATION,
            "chart_generator",
            {"chart_type": "comparison_chart", "symbols": symbols},
            dependencies=["comparison_analysis"],
            task_id="comparison_chart"
        ))
        
        return tasks
    
    def _create_technical_analysis_plan(self, symbols: List[str]) -> List[Task]:
        """Create focused technical analysis plan."""
        tasks = []
        
        for symbol in symbols:
            tasks.append(Task(
                TaskType.DATA_FETCH,
                "yahoo_finance",
                {"symbol": symbol, "period": "6mo"},
                task_id=f"data_{symbol}"
            ))
            
            tasks.append(Task(
                TaskType.ANALYSIS,
                "technical_analyzer",
                {"symbol": symbol, "indicators": ["sma_20", "sma_50", "rsi", "macd", "bollinger_bands"]},
                dependencies=[f"data_{symbol}"],
                task_id=f"technical_{symbol}"
            ))
            
            tasks.append(Task(
                TaskType.VISUALIZATION,
                "chart_generator",
                {"chart_type": "technical_chart", "symbol": symbol},
                dependencies=[f"technical_{symbol}"],
                task_id=f"technical_chart_{symbol}"
            ))
        
        return tasks
    
    def _create_backtesting_plan(self, symbols: List[str]) -> List[Task]:
        """Create backtesting plan."""
        tasks = []
        
        for symbol in symbols:
            # Get historical data
            tasks.append(Task(
                TaskType.DATA_FETCH,
                "yahoo_finance",
                {"symbol": symbol, "period": "2y"},
                task_id=f"data_{symbol}"
            ))
            
            # Technical analysis for signals
            tasks.append(Task(
                TaskType.ANALYSIS,
                "technical_analyzer",
                {"symbol": symbol},
                dependencies=[f"data_{symbol}"],
                task_id=f"technical_{symbol}"
            ))
            
            # Generate trading signals
            tasks.append(Task(
                TaskType.ANALYSIS,
                "trading_signals",
                {"symbol": symbol},
                dependencies=[f"technical_{symbol}"],
                task_id=f"signals_{symbol}"
            ))
            
            # Backtest strategy
            tasks.append(Task(
                TaskType.ANALYSIS,
                "simple_backtester",
                {"symbol": symbol, "initial_capital": 10000},
                dependencies=[f"signals_{symbol}"],
                task_id=f"backtest_{symbol}"
            ))
            
            # Performance chart
            tasks.append(Task(
                TaskType.VISUALIZATION,
                "chart_generator",
                {"chart_type": "performance_chart", "symbol": symbol},
                dependencies=[f"backtest_{symbol}"],
                task_id=f"performance_chart_{symbol}"
            ))
        
        return tasks
    
    def _create_chart_plan(self, symbols: List[str]) -> List[Task]:
        """Create chart generation plan."""
        tasks = []
        
        for symbol in symbols:
            tasks.append(Task(
                TaskType.DATA_FETCH,
                "yahoo_finance",
                {"symbol": symbol},
                task_id=f"data_{symbol}"
            ))
            
            tasks.append(Task(
                TaskType.VISUALIZATION,
                "chart_generator",
                {"chart_type": "price_chart", "symbol": symbol},
                dependencies=[f"data_{symbol}"],
                task_id=f"price_chart_{symbol}"
            ))
        
        return tasks
    
    def _create_reporting_plan(self) -> List[Task]:
        """Create reporting plan based on session history."""
        tasks = []
        
        recent_symbols = self.session_memory.get_recent_symbols(3)
        if recent_symbols:
            # Generate comprehensive report for recent symbols
            tasks.append(Task(
                TaskType.REPORTING,
                "pdf_report_generator",
                {"symbols": recent_symbols, "report_title": "Investment Analysis Report"},
                task_id="pdf_report"
            ))
        
        return tasks


class TaskExecutor:
    """Executes planned tasks in the correct order."""
    
    def __init__(self, tool_registry: ToolRegistry, session_memory: SessionMemory):
        self.tool_registry = tool_registry
        self.session_memory = session_memory
        self.execution_results: Dict[str, ToolResult] = {}
    
    def execute_plan(self, tasks: List[Task]) -> Dict[str, ToolResult]:
        """Execute a list of tasks in dependency order."""
        self.execution_results.clear()
        
        # Sort tasks by dependencies
        sorted_tasks = self._sort_tasks_by_dependencies(tasks)
        
        for task in sorted_tasks:
            result = self._execute_task(task)
            self.execution_results[task.task_id] = result
            
            if not result.success:
                print(f"Task {task.task_id} failed: {result.error}")
                # Continue with other tasks that don't depend on this one
        
        return self.execution_results
    
    def _sort_tasks_by_dependencies(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks based on their dependencies."""
        sorted_tasks = []
        task_dict = {task.task_id: task for task in tasks}
        completed = set()
        
        def can_execute(task: Task) -> bool:
            return all(dep in completed for dep in task.dependencies)
        
        while len(sorted_tasks) < len(tasks):
            for task in tasks:
                if task.task_id not in completed and can_execute(task):
                    sorted_tasks.append(task)
                    completed.add(task.task_id)
                    break
        
        return sorted_tasks
    
    def _execute_task(self, task: Task) -> ToolResult:
        """Execute a single task."""
        tool = self.tool_registry.get_tool(task.tool_name)
        
        if not tool:
            return ToolResult(
                success=False,
                error=f"Tool {task.tool_name} not found in registry"
            )
        
        # Prepare parameters with data from dependencies
        params = task.parameters.copy()
        for dep_id in task.dependencies:
            if dep_id in self.execution_results:
                dep_result = self.execution_results[dep_id]
                if dep_result.success:
                    # Pass dependency data to current task
                    params['dependency_data'] = params.get('dependency_data', {})
                    params['dependency_data'][dep_id] = dep_result.data
        
        try:
            result = tool.execute(**params)
            
            # Store result in session memory if successful
            if result.success:
                if 'symbol' in params:
                    self.session_memory.remember_symbol(params['symbol'])
                    self.session_memory.store_analysis_result(
                        params['symbol'], 
                        task.tool_name, 
                        result.data
                    )
            
            return result
        
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Task execution failed: {str(e)}"
            )