"""
Base classes and interfaces for the investment advisor tools.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class ToolType(Enum):
    DATA_ACQUISITION = "data_acquisition"
    ANALYSIS = "analysis"
    OUTPUT = "output"
    UTILITY = "utility"


@dataclass
class ToolResult:
    """Result from a tool execution."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseTool(ABC):
    """Base class for all investment advisor tools."""
    
    def __init__(self, name: str, tool_type: ToolType):
        self.name = name
        self.tool_type = tool_type
    
    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given parameters."""
        pass
    
    @abstractmethod
    def get_parameters(self) -> Dict[str, Any]:
        """Get the required parameters for this tool."""
        pass
    
    def validate_parameters(self, params: Dict[str, Any]) -> bool:
        """Validate the provided parameters."""
        required_params = self.get_parameters()
        for param_name, param_info in required_params.items():
            if param_info.get('required', True) and param_name not in params:
                return False
        return True


class ToolRegistry:
    """Registry for managing available tools."""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
    
    def register_tool(self, tool: BaseTool):
        """Register a new tool."""
        self._tools[tool.name] = tool
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def get_tools_by_type(self, tool_type: ToolType) -> List[BaseTool]:
        """Get all tools of a specific type."""
        return [tool for tool in self._tools.values() if tool.tool_type == tool_type]
    
    def list_tools(self) -> List[str]:
        """List all registered tool names."""
        return list(self._tools.keys())