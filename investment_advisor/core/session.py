"""
Session management for maintaining context and memory.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json


class SessionMemory:
    """Manages session context and memory for the investment advisor."""
    
    def __init__(self):
        self.session_data: Dict[str, Any] = {
            'conversation_history': [],
            'context': {},
            'symbols_analyzed': [],
            'last_analysis_results': {},
            'user_preferences': {}
        }
        self.session_start = datetime.now()
    
    def add_to_history(self, user_input: str, response: str, tools_used: List[str] = None):
        """Add an interaction to the conversation history."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'response': response,
            'tools_used': tools_used or []
        }
        self.session_data['conversation_history'].append(entry)
    
    def set_context(self, key: str, value: Any):
        """Set a context value."""
        self.session_data['context'][key] = value
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """Get a context value."""
        return self.session_data['context'].get(key, default)
    
    def remember_symbol(self, symbol: str):
        """Remember an analyzed symbol."""
        if symbol not in self.session_data['symbols_analyzed']:
            self.session_data['symbols_analyzed'].append(symbol)
    
    def get_recent_symbols(self, count: int = 5) -> List[str]:
        """Get recently analyzed symbols."""
        return self.session_data['symbols_analyzed'][-count:]
    
    def store_analysis_result(self, symbol: str, analysis_type: str, result: Dict[str, Any]):
        """Store analysis results for later reference."""
        if symbol not in self.session_data['last_analysis_results']:
            self.session_data['last_analysis_results'][symbol] = {}
        self.session_data['last_analysis_results'][symbol][analysis_type] = {
            'result': result,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_analysis_result(self, symbol: str, analysis_type: str) -> Optional[Dict[str, Any]]:
        """Retrieve stored analysis results."""
        return self.session_data['last_analysis_results'].get(symbol, {}).get(analysis_type)
    
    def set_user_preference(self, key: str, value: Any):
        """Set a user preference."""
        self.session_data['user_preferences'][key] = value
    
    def get_user_preference(self, key: str, default: Any = None) -> Any:
        """Get a user preference."""
        return self.session_data['user_preferences'].get(key, default)
    
    def clear_session(self):
        """Clear session data."""
        self.__init__()
    
    def export_session(self) -> str:
        """Export session data as JSON."""
        export_data = self.session_data.copy()
        export_data['session_duration'] = (datetime.now() - self.session_start).total_seconds()
        return json.dumps(export_data, indent=2)
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get a summary of the current session."""
        return {
            'session_start': self.session_start.isoformat(),
            'session_duration': (datetime.now() - self.session_start).total_seconds(),
            'interactions_count': len(self.session_data['conversation_history']),
            'symbols_analyzed': len(self.session_data['symbols_analyzed']),
            'recent_symbols': self.get_recent_symbols(3)
        }