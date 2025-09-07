"""
Main CLI application for the AI Investment Research Assistant.
"""

import sys
import os
import argparse
from typing import Dict, Any, List
import traceback

# Add the package to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from investment_advisor.core.base import ToolRegistry, ToolType
from investment_advisor.core.session import SessionMemory
from investment_advisor.core.reasoning import TaskPlanner, TaskExecutor

# Import all tools
from investment_advisor.data.stock_data import YahooFinanceAPI, AlphaVantageAPI, FinnhubAPI, StockDataAggregator
from investment_advisor.analysis.technical import TechnicalAnalyzer, TradingSignals
from investment_advisor.analysis.backtesting import SimpleBacktester, StrategyComparison, RiskAnalyzer
from investment_advisor.output.charts import ChartGenerator
from investment_advisor.output.reports import PDFReportGenerator, PowerPointGenerator


class InvestmentAdvisorCLI:
    """Main CLI application class."""
    
    def __init__(self):
        self.tool_registry = ToolRegistry()
        self.session_memory = SessionMemory()
        self.task_planner = TaskPlanner(self.tool_registry, self.session_memory)
        self.task_executor = TaskExecutor(self.tool_registry, self.session_memory)
        self.setup_tools()
        print("AI Investment Research Assistant initialized successfully!")
    
    def setup_tools(self):
        """Register all available tools."""
        # Data acquisition tools
        self.tool_registry.register_tool(YahooFinanceAPI())
        self.tool_registry.register_tool(AlphaVantageAPI())
        self.tool_registry.register_tool(FinnhubAPI())
        self.tool_registry.register_tool(StockDataAggregator())
        
        # Analysis tools
        self.tool_registry.register_tool(TechnicalAnalyzer())
        self.tool_registry.register_tool(TradingSignals())
        self.tool_registry.register_tool(SimpleBacktester())
        self.tool_registry.register_tool(StrategyComparison())
        self.tool_registry.register_tool(RiskAnalyzer())
        
        # Output tools
        self.tool_registry.register_tool(ChartGenerator())
        self.tool_registry.register_tool(PDFReportGenerator())
        self.tool_registry.register_tool(PowerPointGenerator())
    
    def display_welcome_message(self):
        """Display welcome message and instructions."""
        print("\\n" + "="*70)
        print("🚀 AI INVESTMENT RESEARCH ASSISTANT")
        print("="*70)
        print("Welcome to your personal AI investment advisor!")
        print("\\nI can help you with:")
        print("• Stock analysis and research")
        print("• Technical analysis and trading signals")
        print("• Strategy backtesting and performance analysis")
        print("• Comparative analysis between stocks")
        print("• Chart generation and visualization")
        print("• PDF reports and PowerPoint presentations")
        print("\\nExample queries:")
        print("- 'Analyze AAPL stock'")
        print("- 'Compare AAPL vs MSFT'")
        print("- 'Show me technical analysis for TSLA'")
        print("- 'Backtest a strategy for GOOGL'")
        print("- 'Create a report for my recent analysis'")
        print("\\nType 'help' for more commands, 'quit' to exit")
        print("="*70 + "\\n")
    
    def display_help(self):
        """Display help information."""
        print("\\n📋 AVAILABLE COMMANDS:")
        print("="*50)
        print("🔍 ANALYSIS COMMANDS:")
        print("  analyze <SYMBOL>     - Comprehensive stock analysis")
        print("  technical <SYMBOL>   - Technical analysis only")
        print("  compare <SYM1> <SYM2> - Compare two stocks")
        print("  backtest <SYMBOL>    - Backtest trading strategy")
        print("\\n📊 VISUALIZATION COMMANDS:")
        print("  chart <SYMBOL>       - Generate stock charts")
        print("  plot <SYMBOL>        - Create price visualization")
        print("\\n📄 REPORTING COMMANDS:")
        print("  report               - Generate PDF report")
        print("  presentation         - Create PowerPoint presentation")
        print("\\n⚙️ UTILITY COMMANDS:")
        print("  status               - Show session status")
        print("  history              - Show analysis history")
        print("  tools                - List available tools")
        print("  clear                - Clear session memory")
        print("  help                 - Show this help message")
        print("  quit/exit            - Exit the application")
        print("="*50 + "\\n")
    
    def display_tools(self):
        """Display available tools."""
        print("\\n🛠️ AVAILABLE TOOLS:")
        print("="*40)
        
        tool_types = {
            ToolType.DATA_ACQUISITION: "📥 Data Sources",
            ToolType.ANALYSIS: "🔬 Analysis Tools", 
            ToolType.OUTPUT: "📊 Output Tools"
        }
        
        for tool_type, title in tool_types.items():
            tools = self.tool_registry.get_tools_by_type(tool_type)
            if tools:
                print(f"\\n{title}:")
                for tool in tools:
                    print(f"  • {tool.name}")
        
        print("="*40 + "\\n")
    
    def process_query(self, user_input: str) -> str:
        """Process user query and return response."""
        try:
            # Parse the query
            query_info = self.task_planner.parse_query(user_input)
            
            print(f"\\n🧠 Understanding your query...")
            print(f"   Query type: {query_info['query_type']}")
            if query_info['symbols']:
                print(f"   Symbols found: {', '.join(query_info['symbols'])}")
            
            # Create task plan
            tasks = self.task_planner.create_task_plan(query_info)
            
            if not tasks:
                return "I'm not sure how to help with that. Try 'help' for available commands."
            
            print(f"\\n📋 Planned {len(tasks)} task(s):")
            for i, task in enumerate(tasks, 1):
                print(f"   {i}. {task.tool_name} ({task.task_type.value})")
            
            # Execute tasks
            print("\\n⚙️ Executing analysis...")
            results = self.task_executor.execute_plan(tasks)
            
            # Generate response
            response = self.generate_response(query_info, results)
            
            # Add to conversation history
            tools_used = [task.tool_name for task in tasks]
            self.session_memory.add_to_history(user_input, response, tools_used)
            
            return response
        
        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            print(f"\\n❌ {error_msg}")
            if "--debug" in sys.argv:
                traceback.print_exc()
            return error_msg
    
    def generate_response(self, query_info: Dict[str, Any], results: Dict[str, Any]) -> str:
        """Generate a comprehensive response based on results."""
        response_parts = []
        successful_results = {k: v for k, v in results.items() if v.success}
        
        if not successful_results:
            return "❌ Analysis failed. Please check your input and try again."
        
        response_parts.append("✅ Analysis completed successfully!\\n")
        
        # Summary based on query type
        query_type = query_info['query_type']
        symbols = query_info.get('symbols', [])
        
        if query_type == 'stock_analysis':
            response_parts.append(self.generate_stock_analysis_summary(symbols, successful_results))
        elif query_type == 'comparison':
            response_parts.append(self.generate_comparison_summary(symbols, successful_results))
        elif query_type == 'technical_analysis':
            response_parts.append(self.generate_technical_summary(symbols, successful_results))
        elif query_type == 'backtesting':
            response_parts.append(self.generate_backtesting_summary(symbols, successful_results))
        
        # Add file outputs information
        charts_created = []
        reports_created = []
        
        for result_id, result in successful_results.items():
            if 'chart_path' in str(result.data):
                if isinstance(result.data, dict) and 'chart_path' in result.data:
                    charts_created.append(result.data['chart_path'])
            elif 'report_path' in str(result.data):
                if isinstance(result.data, dict) and 'report_path' in result.data:
                    reports_created.append(result.data['report_path'])
            elif 'presentation_path' in str(result.data):
                if isinstance(result.data, dict) and 'presentation_path' in result.data:
                    reports_created.append(result.data['presentation_path'])
        
        if charts_created:
            response_parts.append(f"\\n📊 Charts created: {len(charts_created)} file(s)")
            for chart in charts_created[:3]:  # Show first 3
                response_parts.append(f"   • {os.path.basename(chart)}")
        
        if reports_created:
            response_parts.append(f"\\n📄 Reports created: {len(reports_created)} file(s)")
            for report in reports_created:
                response_parts.append(f"   • {os.path.basename(report)}")
        
        return "\\n".join(response_parts)
    
    def generate_stock_analysis_summary(self, symbols: List[str], results: Dict[str, Any]) -> str:
        """Generate summary for stock analysis."""
        summary = ["📈 STOCK ANALYSIS SUMMARY"]
        
        for symbol in symbols:
            summary.append(f"\\n🏢 {symbol}:")
            
            # Look for stock data
            data_results = [r for r_id, r in results.items() if f"data_{symbol}" in r_id and r.success]
            if data_results:
                data = data_results[0].data
                if isinstance(data, dict):
                    if 'yahoo_data' in data and 'company_info' in data['yahoo_data']:
                        info = data['yahoo_data']['company_info']
                        summary.append(f"   Company: {info.get('longName', 'N/A')}")
                        summary.append(f"   Sector: {info.get('sector', 'N/A')}")
                        summary.append(f"   Current Price: ${info.get('currentPrice', info.get('regularMarketPrice', 0)):.2f}")
            
            # Look for technical analysis
            tech_results = [r for r_id, r in results.items() if f"technical_{symbol}" in r_id and r.success]
            if tech_results:
                summary.append("   📊 Technical indicators calculated")
            
            # Look for signals
            signal_results = [r for r_id, r in results.items() if f"signals_{symbol}" in r_id and r.success]
            if signal_results:
                summary.append("   📡 Trading signals generated")
        
        return "\\n".join(summary)
    
    def generate_comparison_summary(self, symbols: List[str], results: Dict[str, Any]) -> str:
        """Generate summary for comparison analysis."""
        summary = [f"⚖️ COMPARISON ANALYSIS: {' vs '.join(symbols)}"]
        
        # Look for comparison results
        comp_results = [r for r_id, r in results.items() if "comparison" in r_id and r.success]
        if comp_results:
            summary.append("\\n✅ Comparative analysis completed")
            summary.append("   • Performance metrics calculated")
            summary.append("   • Risk-adjusted returns compared") 
            summary.append("   • Strategy rankings generated")
        
        return "\\n".join(summary)
    
    def generate_technical_summary(self, symbols: List[str], results: Dict[str, Any]) -> str:
        """Generate summary for technical analysis."""
        summary = ["📊 TECHNICAL ANALYSIS SUMMARY"]
        
        for symbol in symbols:
            summary.append(f"\\n🔍 {symbol}:")
            
            tech_results = [r for r_id, r in results.items() if f"technical_{symbol}" in r_id and r.success]
            if tech_results:
                summary.append("   ✅ Technical indicators:")
                summary.append("     • Moving averages (SMA 20, SMA 50)")
                summary.append("     • RSI momentum indicator")
                summary.append("     • MACD trend analysis")
                summary.append("     • Bollinger Bands volatility")
        
        return "\\n".join(summary)
    
    def generate_backtesting_summary(self, symbols: List[str], results: Dict[str, Any]) -> str:
        """Generate summary for backtesting results."""
        summary = ["📈 BACKTESTING RESULTS"]
        
        for symbol in symbols:
            backtest_results = [r for r_id, r in results.items() if f"backtest_{symbol}" in r_id and r.success]
            if backtest_results:
                result_data = backtest_results[0].data
                if isinstance(result_data, dict) and 'performance_metrics' in result_data:
                    metrics = result_data['performance_metrics']
                    summary.append(f"\\n📊 {symbol} Strategy Performance:")
                    summary.append(f"   • Total Return: {metrics.get('total_return', 0):.2f}%")
                    summary.append(f"   • Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.3f}")
                    summary.append(f"   • Max Drawdown: {metrics.get('max_drawdown', 0):.2f}%")
                    summary.append(f"   • Win Rate: {metrics.get('win_rate', 0):.2f}%")
        
        return "\\n".join(summary)
    
    def handle_command(self, user_input: str) -> str:
        """Handle special commands."""
        command = user_input.lower().strip()
        
        if command in ['help', 'h']:
            self.display_help()
            return ""
        
        elif command == 'tools':
            self.display_tools()
            return ""
        
        elif command == 'status':
            summary = self.session_memory.get_session_summary()
            response = ["\\n📊 SESSION STATUS:"]
            response.append(f"   • Session duration: {summary['session_duration']:.0f} seconds")
            response.append(f"   • Interactions: {summary['interactions_count']}")
            response.append(f"   • Symbols analyzed: {summary['symbols_analyzed']}")
            if summary['recent_symbols']:
                response.append(f"   • Recent symbols: {', '.join(summary['recent_symbols'])}")
            return "\\n".join(response)
        
        elif command == 'history':
            history = self.session_memory.session_data['conversation_history']
            if not history:
                return "\\n📝 No analysis history yet."
            
            response = ["\\n📝 RECENT ANALYSIS HISTORY:"]
            for i, entry in enumerate(history[-5:], 1):  # Show last 5
                response.append(f"   {i}. {entry['user_input'][:50]}...")
                if entry['tools_used']:
                    response.append(f"      Tools: {', '.join(entry['tools_used'])}")
            return "\\n".join(response)
        
        elif command == 'clear':
            self.session_memory.clear_session()
            return "\\n🧹 Session memory cleared."
        
        elif command in ['quit', 'exit', 'q']:
            return "quit"
        
        return None
    
    def run_interactive(self):
        """Run the interactive CLI."""
        self.display_welcome_message()
        
        while True:
            try:
                user_input = input("💬 Ask me anything about investments: ").strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                command_response = self.handle_command(user_input)
                if command_response == "quit":
                    print("\\n👋 Thank you for using AI Investment Research Assistant!")
                    break
                elif command_response is not None:
                    if command_response:  # Only print if not empty
                        print(command_response)
                    continue
                
                # Process regular queries
                response = self.process_query(user_input)
                print(f"\\n{response}\\n")
                
            except KeyboardInterrupt:
                print("\\n\\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\\n❌ Unexpected error: {str(e)}")
                if "--debug" in sys.argv:
                    traceback.print_exc()
    
    def run_single_query(self, query: str):
        """Run a single query and exit."""
        print("🚀 AI Investment Research Assistant")
        print("=" * 40)
        response = self.process_query(query)
        print(f"\\n{response}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="AI Investment Research Assistant")
    parser.add_argument("--query", "-q", type=str, help="Run a single query and exit")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    try:
        cli = InvestmentAdvisorCLI()
        
        if args.query:
            cli.run_single_query(args.query)
        else:
            cli.run_interactive()
            
    except Exception as e:
        print(f"❌ Failed to start application: {str(e)}")
        if args.debug:
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()