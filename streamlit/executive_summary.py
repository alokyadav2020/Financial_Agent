

import streamlit as st
import json
from huggingface_hub import InferenceClient
from datetime import datetime

def get_default_financial_data():
    """Return default financial data template"""
    return {
        "company_info": {
            "name": "Acme Manufacturing",
            "industry": "Industrial Components",
            "sectors": ["Automotive", "Aerospace"],
            "year_founded": 1995,
            "employees": 450,
        },
        "financial_metrics": {
            "revenue": {"2023": 85000000, "2022": 75000000, "2021": 65000000},
            "cogs": {
                "2023": 59500000,
                "2022": 48750000,
                "2021": 42250000,
            },
            "operating_expenses": {"2023": 12750000, "2022": 11250000, "2021": 9750000},
            "ebitda": {"2023": 12750000, "2022": 15000000, "2021": 13000000},
        },
        "balance_sheet": {
            "total_assets": 45000000,
            "total_liabilities": 27000000,
            "equity": 18000000,
            "debt": {"long_term": 20000000, "short_term": 5000000},
            "cash": 3500000,
        },
        "kpis": {
            "gross_margin": 0.30,
            "operating_margin": 0.15,
            "debt_to_equity": 1.39,
            "current_ratio": 1.5,
            "revenue_growth": 0.13,
            "market_share": 0.15,
        },
        "valuation": {
            "enterprise_value": 12000000,
            "ev_ebitda_multiple": 6.5,
            "valuation_range": {"low": 10000000, "high": 14000000},
        },
        "industry_benchmarks": {
            "avg_gross_margin": 0.35,
            "avg_operating_margin": 0.18,
            "avg_debt_to_equity": 0.8,
            "avg_revenue_growth": 0.08,
        },
        "risk_factors": {
            "high_customer_concentration": True,
            "geographic_concentration": True,
            "supply_chain_dependency": True,
            "debt_level": "High",
            "market_cyclicality": "Medium",
        },
    }

def calculate_key_metrics(data):
    """Calculate additional metrics from the financial data"""
    try:
        metrics = {}
        
        latest_revenue = data["financial_metrics"]["revenue"]["2023"]
        previous_revenue = data["financial_metrics"]["revenue"]["2022"]
        metrics["revenue_growth_rate"] = (latest_revenue - previous_revenue) / previous_revenue
        
        total_debt = (data["balance_sheet"]["debt"]["long_term"] + 
                     data["balance_sheet"]["debt"]["short_term"])
        equity = data["balance_sheet"]["equity"]
        metrics["debt_to_equity"] = total_debt / equity
        
        metrics["ebitda_margin"] = (data["financial_metrics"]["ebitda"]["2023"] / 
                                   latest_revenue)
        
        return metrics
    except Exception as e:
        st.error(f"Error calculating metrics: {str(e)}")
        return {}

def generate_report(prompt, metrics):
    """Generate financial report using HuggingFace model"""
    client = InferenceClient(
        #  model=st.secrets["hf_model"],
        provider="hf-inference",
        api_key=st.secrets["hf_token"],
    )

    messages = [
        {"role": "system", "content": "You are financial report expert."},
        {"role": "user", "content": prompt.format(metrics=metrics)},
    ]

    response_format = {
        "type": "json",
        "value": {
            "properties": {
                "Overview": {"type": "string"},
                "Valuation": {"type": "string"},
                "Financials": {"type": "string"},
                "Recommendations": {"type": "string"},
                "Conclusion": {"type": "string"},
            },
            "required": [
                "Overview",
                "Valuation",
                "Financials",
                "Recommendations",
                "Conclusion",
            ],
        },
    }

    response = client.chat_completion(
        model=st.secrets["hf_model"],
        messages=messages,
        response_format=response_format,
        max_tokens=8000,
        temperature=0.1,
    )

    return json.loads(response.choices[0].message.content)

# def edit_nested_dict(prefix, d, indent=0):
#     """Recursively create input fields for nested dictionary"""
#     for key, value in d.items():
#         if isinstance(value, dict):
#             st.markdown(f"{'  ' * indent}**{key}:**")
#             d[key] = edit_nested_dict(f"{prefix}{key}.", value, indent + 1)
#         elif isinstance(value, list):
#             d[key] = st.text_input(
#                 f"{'  ' * indent}{key} (comma-separated)",
#                 ",".join(map(str, value))
#             ).split(",")
#         elif isinstance(value, bool):
#             d[key] = st.checkbox(f"{'  ' * indent}{key}", value)
#         elif isinstance(value, (int, float)):
#             d[key] = type(value)(
#                 st.number_input(f"{'  ' * indent}{key}", value=value)
#             )
#         else:
#             d[key] = type(value)(
#                 st.text_input(f"{'  ' * indent}{key}", value)
#             )
#     return d
def edit_nested_dict(prefix, d, indent=0):
    """Recursively create input fields for nested dictionary"""
    for key, value in d.items():
        unique_key = f"{prefix}{key}"
        if isinstance(value, dict):
            st.markdown(f"{'  ' * indent}**{key}:**")
            d[key] = edit_nested_dict(f"{unique_key}.", value, indent + 1)
        elif isinstance(value, list):
            d[key] = st.text_input(
                f"{'  ' * indent}{key} (comma-separated)",
                ",".join(map(str, value)),
                key=unique_key
            ).split(",")
        elif isinstance(value, bool):
            d[key] = st.checkbox(f"{'  ' * indent}{key}", value, key=unique_key)
        elif isinstance(value, (int, float)):
            d[key] = type(value)(
                st.number_input(f"{'  ' * indent}{key}", value=value, key=unique_key)
            )
        else:
            d[key] = type(value)(
                st.text_input(f"{'  ' * indent}{key}", value, key=unique_key)
            )
    return d

def main():
    st.set_page_config(layout="wide")
    st.title("Financial Report Generator")
    
    # Display current time and user
    # st.sidebar.info(f"Current Time (UTC): {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
    # st.sidebar.info(f"Current User: {st.session_state.get('current_user', 'alokyadav2020')}")

    # Initialize session state for financial data
    if 'financial_data' not in st.session_state:
        st.session_state.financial_data = get_default_financial_data()

    # Create tabs for different sections
    data_tab, prompt_tab, report_tab = st.tabs(["Financial Data", "Report Prompt", "Generated Report"])

    with data_tab:
        st.header("Edit Financial Data")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Button to reset to default data
            if st.button("Reset to Default Data"):
                st.session_state.financial_data = get_default_financial_data()
                st.success("Data reset to default values!")
                st.rerun()
            
            # Edit financial data
            st.session_state.financial_data = edit_nested_dict(
                "", 
                st.session_state.financial_data.copy()
            )

        with col2:
            # Display current financial data as JSON
            st.subheader("Current Financial Data (JSON)")
            st.json(st.session_state.financial_data)

    with prompt_tab:
        st.header("Customize Report Generation Prompt")
        
        # Default prompt template
        default_prompt = """
        you are financial report expert. create reports on topics with using given data.

        **Topics**
        1. Overview 
        2. Valuation   
        3. Financials
        4. Recommendations
        5. Conclusion 


        Examples:

1. Overview: This report presents a due diligence assessment of Acme Manufacturing, a
producer of industrial components for the automotive and aerospace industries.
Our analysis indicates that Acme Manufacturing demonstrates solid revenue
growth and operational efficiency but faces challenges related to leverage and
profitability optimization.

2. Valuation: The estimated valuation range is $10 to $14 million.
3. Financials: Revenue↑ but COGS ↑ in-proportionally.
4. Recommendations: To enhance Acme Manufacturing's long-term value and mitigate identified risks,
we recommend the following:

<h4>Process improvements:</h4>
<ul>
    <li>☑ Supplier contract renegotiate (refer the cost reduction scenarios)</li>
    <li>☑ Reduce the Debt-to-Equity Ratio (High among peers: Top 25th Quartile)</li>
    <li>☑ Penetrate new markets (Avoid new geography)</li>
</ul>

<h4>Profitability Optimization:</h4>
<p>Implement cost optimization measures targeting
overhead expenses to improve the Net Profit Margin. Specific initiatives could
include streamlining administrative processes, negotiating better terms with
suppliers, and optimizing resource allocation.</p>

<h4>Capital Structure Improvement:</h4>
<p>Restructure existing debt to reduce the Debt-
to-Equity Ratio and decrease interest expense. The refinancing debt at lower
interest rates or seeking equity financing to reduce the overall debt burden.</p>

<h4>Growth and Innovation:</h4>
<p>Invest in research and development (R&D) to expand
product offerings, penetrate new markets, and maintain a competitive advantage.
This will also help to mitigate risks associated with reliance on cyclical industries.</p> 
5. Conclusion:Acme Manufacturing establishes a strong revenue growth trajectory & holds a
favorable market position. By addressing the identified challenges related to
profitability and leverage, & by capitalizing on growth opportunities, Acme
Manufacturing can enhance its financial performance, reduce risk exposure, and
maximize shareholder values.



        
        """

        # Prompt input
        if 'user_prompt' not in st.session_state:
            st.session_state.user_prompt = default_prompt

        st.session_state.user_prompt = st.text_area(
            "Modify the prompt template:",
            st.session_state.user_prompt,
            height=300,
            help="You can modify this prompt to customize the report generation. Use {metrics} to reference the financial data."
        )

        # Reset prompt button
        if st.button("Reset Prompt to Default"):
            st.session_state.user_prompt = default_prompt
            st.success("Prompt reset to default!")
            st.rerun()

    with report_tab:
        st.header("Generated Financial Report")

        # Calculate metrics and generate report
        if st.button("Generate Report"):
            with st.spinner("Calculating metrics and generating report..."):
                try:
                    # Calculate metrics
                    metrics = calculate_key_metrics(st.session_state.financial_data)
                    
                    # Generate report
                    report = generate_report(st.session_state.user_prompt + "\n" + "Given Data is {metrics}", metrics)
                    
                    # Store report in session state
                    st.session_state.report = report
                    
                    # Display success message
                    st.success("Report generated successfully!")
                    
                except Exception as e:
                    st.error(f"Error generating report: {str(e)}")
                    return

        # Display report if it exists in session state
        if 'report' in st.session_state:
            report = st.session_state.report
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("### Overview")
                st.markdown(report["Overview"], unsafe_allow_html=True)
                
                st.markdown("### Valuation")
                st.markdown(report["Valuation"], unsafe_allow_html=True)
                
                st.markdown("### Financials")
                st.markdown(report["Financials"], unsafe_allow_html=True)
                
                st.markdown("### Recommendations")
                st.markdown(report["Recommendations"], unsafe_allow_html=True)
                
                st.markdown("### Conclusion")
                st.markdown(report["Conclusion"], unsafe_allow_html=True)

            with col2:
                st.markdown("### Download Options")
                
                # Option to download report
                report_text = "\n\n".join([
                    "# Financial Report\n",
                    "## Overview\n" + report["Overview"],
                    "## Valuation\n" + report["Valuation"],
                    "## Financials\n" + report["Financials"],
                    "## Recommendations\n" + report["Recommendations"],
                    "## Conclusion\n" + report["Conclusion"]
                ])
                
                st.download_button(
                    label="Download Report as Markdown",
                    data=report_text,
                    file_name=f"financial_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown"
                )
                
                # Option to download financial data
                st.download_button(
                    label="Download Financial Data as JSON",
                    data=json.dumps(st.session_state.financial_data, indent=2),
                    file_name=f"financial_data_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )

if __name__ == "__main__":
    main()