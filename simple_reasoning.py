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
    
    def parse_query(self, user_query: str) -> Dict[str, Any]:
        """Parse user query to extract intent and entities."""
        symbols = re.findall(r'\b[A-Z]{2,5}\b', user_query.upper())
        symbols = [s for s in symbols if s not in ['THE', 'AND', 'OR', 'FOR', 'TO', 'VS']]
        
        query_info = {
            'original_query': user_query,
            'symbols': symbols,
            'query_type': 'stock_analysis',
            'parameters': {}
        }
        
        return query_info
    
    def create_task_plan(self, query_info: Dict[str, Any]) -> List[Task]:
        """Create a sequence of tasks based on the parsed query."""
        tasks = []
        symbols = query_info['symbols']
        
        for symbol in symbols:
            # Data acquisition
            tasks.append(Task(
                TaskType.DATA_FETCH,
                "stock_aggregator",
                {"symbol": symbol},
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
        
        for task in tasks:
            result = self._execute_task(task)
            self.execution_results[task.task_id] = result
            
            if not result.success:
                print(f"Task {task.task_id} failed: {result.error}")
        
        return self.execution_results
    
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
                if dep_result.success and dep_result.data:
                    if isinstance(dep_result.data, dict):
                        # For stock data from data fetching tasks
                        if 'historical_data' in dep_result.data:
                            params['data'] = dep_result.data['historical_data']
                        # For technical analysis results
                        elif any(key in dep_result.data for key in ['sma_20', 'rsi', 'macd']):
                            params['technical_data'] = dep_result.data
        
        try:
            result = tool.execute(**params)
            
            # Store result in session memory if successful
            if result.success and 'symbol' in params:
                self.session_memory.remember_symbol(params['symbol'])
            
            return result
        
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Task execution failed: {str(e)}"
            )