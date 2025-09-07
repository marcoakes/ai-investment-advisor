"""
Optional web interface for the AI Investment Research Assistant
"""

import streamlit as st
import sys
import os
from io import StringIO
import base64

# Add the package to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from investment_advisor.cli import InvestmentAdvisorCLI

# Configure Streamlit page
st.set_page_config(
    page_title="AI Investment Research Assistant",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize the CLI backend
@st.cache_resource
def initialize_advisor():
    return InvestmentAdvisorCLI()

def main():
    st.title("🚀 AI Investment Research Assistant")
    st.markdown("---")
    
    # Initialize the advisor
    advisor = initialize_advisor()
    
    # Sidebar for session info
    with st.sidebar:
        st.header("📊 Session Info")
        
        if st.button("Clear Session"):
            advisor.session_memory.clear_session()
            st.success("Session cleared!")
        
        # Show session summary
        summary = advisor.session_memory.get_session_summary()
        st.metric("Interactions", summary['interactions_count'])
        st.metric("Symbols Analyzed", summary['symbols_analyzed'])
        
        if summary['recent_symbols']:
            st.write("**Recent Symbols:**")
            for symbol in summary['recent_symbols']:
                st.write(f"• {symbol}")
    
    # Main interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 Ask Your Investment Questions")
        
        # Example queries
        st.markdown("**Example queries:**")
        examples = [
            "Analyze AAPL stock",
            "Compare MSFT vs GOOGL", 
            "Show technical analysis for TSLA",
            "Backtest strategy for AMZN",
            "Create a report"
        ]
        
        for example in examples:
            if st.button(f"📋 {example}", key=example):
                st.session_state.query = example
        
        # Query input
        query = st.text_area(
            "Enter your investment question:",
            value=st.session_state.get('query', ''),
            height=100,
            placeholder="e.g., 'Analyze Apple stock' or 'Compare Tesla vs Ford'"
        )
        
        if st.button("🔍 Analyze", type="primary"):
            if query.strip():
                with st.spinner("Analyzing... This may take a moment."):
                    try:
                        # Capture output
                        old_stdout = sys.stdout
                        sys.stdout = captured_output = StringIO()
                        
                        # Process query
                        response = advisor.process_query(query)
                        
                        # Restore stdout
                        sys.stdout = old_stdout
                        console_output = captured_output.getvalue()
                        
                        # Display results
                        st.success("Analysis Complete!")
                        st.markdown("### 📊 Results")
                        st.write(response)
                        
                        if console_output:
                            with st.expander("🖥️ Console Output"):
                                st.code(console_output)
                        
                        # Display generated files
                        display_generated_files()
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            else:
                st.warning("Please enter a query.")
    
    with col2:
        st.header("🛠️ Available Tools")
        
        tools_by_type = {
            "Data Sources": ["yahoo_finance", "alpha_vantage", "finnhub", "stock_aggregator"],
            "Analysis": ["technical_analyzer", "trading_signals", "simple_backtester", "strategy_comparison", "risk_analyzer"],
            "Output": ["chart_generator", "pdf_report_generator", "powerpoint_generator"]
        }
        
        for category, tools in tools_by_type.items():
            st.subheader(f"📦 {category}")
            for tool in tools:
                st.write(f"• {tool}")

def display_generated_files():
    """Display any generated charts, reports, or presentations."""
    
    # Check for generated charts
    charts_dir = "charts"
    if os.path.exists(charts_dir):
        chart_files = [f for f in os.listdir(charts_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
        if chart_files:
            st.markdown("### 📊 Generated Charts")
            
            # Display most recent charts
            chart_files.sort(key=lambda x: os.path.getmtime(os.path.join(charts_dir, x)), reverse=True)
            
            for chart_file in chart_files[:3]:  # Show last 3 charts
                chart_path = os.path.join(charts_dir, chart_file)
                st.image(chart_path, caption=chart_file, use_column_width=True)
                
                # Download button
                with open(chart_path, "rb") as file:
                    btn = st.download_button(
                        label=f"Download {chart_file}",
                        data=file.read(),
                        file_name=chart_file,
                        mime="image/png"
                    )
    
    # Check for generated reports
    for dir_name, file_types, mime_type in [
        ("reports", [".pdf"], "application/pdf"),
        ("presentations", [".pptx"], "application/vnd.openxmlformats-officedocument.presentationml.presentation")
    ]:
        if os.path.exists(dir_name):
            files = [f for f in os.listdir(dir_name) if any(f.endswith(ext) for ext in file_types)]
            if files:
                st.markdown(f"### 📄 Generated {dir_name.title()}")
                
                files.sort(key=lambda x: os.path.getmtime(os.path.join(dir_name, x)), reverse=True)
                
                for file in files[:2]:  # Show last 2 files
                    file_path = os.path.join(dir_name, file)
                    
                    with open(file_path, "rb") as f:
                        st.download_button(
                            label=f"📥 Download {file}",
                            data=f.read(),
                            file_name=file,
                            mime=mime_type
                        )

if __name__ == "__main__":
    main()