import streamlit as st
import random
from datetime import datetime
from huggingface_hub import InferenceClient
import json

class CashFlowAnalyzer:
    def generate_dummy_cash_flow_data(self, years):
        """Generate dummy cash flow data for given years."""
        cash_flow_data = {}
        for year in years:
            net_income = random.uniform(500000, 2000000)
            adjustments_for_non_cash_items = random.uniform(100000, 500000)
            changes_in_working_capital = random.uniform(-100000, 100000)
            cash_from_operating_activities = (
                net_income + adjustments_for_non_cash_items + changes_in_working_capital
            )
            
            cash_from_investing_activities = random.uniform(-1000000, -500000)
            cash_from_financing_activities = random.uniform(-500000, 500000)
            
            net_cash_flow = (
                cash_from_operating_activities +
                cash_from_investing_activities +
                cash_from_financing_activities
            )
            
            beginning_cash_balance = random.uniform(1000000, 5000000)
            ending_cash_balance = beginning_cash_balance + net_cash_flow
            
            cash_flow_data[year] = {
                "Net Income": round(net_income, 2),
                "Adjustments for Non-Cash Items": round(adjustments_for_non_cash_items, 2),
                "Changes in Working Capital": round(changes_in_working_capital, 2),
                "Cash from Operating Activities": round(cash_from_operating_activities, 2),
                "Cash from Investing Activities": round(cash_from_investing_activities, 2),
                "Cash from Financing Activities": round(cash_from_financing_activities, 2),
                "Net Cash Flow": round(net_cash_flow, 2),
                "Beginning Cash Balance": round(beginning_cash_balance, 2),
                "Ending Cash Balance": round(ending_cash_balance, 2),
            }
        return cash_flow_data

    def generate_dummy_balance_sheet(self, years):
        """Generate dummy balance sheet data for cash flow metrics calculation."""
        balance_sheet_data = {}
        for year in years:
            balance_sheet_data[year] = {
                "Total Liabilities": round(random.uniform(1000000, 5000000), 2)
            }
        return balance_sheet_data

    def calculate_cash_flow_metrics(self, cash_flow_data, balance_sheet_data):
        """Calculate cash flow metrics from the given data."""
        metrics = {}
        for year in cash_flow_data.keys():
            ocf = cash_flow_data[year]["Cash from Operating Activities"]
            capital_expenditures = random.uniform(100000, 500000)
            fcf = ocf - capital_expenditures
            total_debt = balance_sheet_data[year]["Total Liabilities"]
            cash_flow_coverage_ratio = ocf / total_debt
            
            metrics[year] = {
                "Operating Cash Flow (OCF)": round(ocf, 2),
                "Free Cash Flow (FCF)": round(fcf, 2),
                "Cash Flow Coverage Ratio": round(cash_flow_coverage_ratio, 2),
            }
        return metrics

def generate_report(prompt, data):
    """Generate financial report using HuggingFace model."""
    client = InferenceClient(
        provider="hf-inference",
        api_key=st.secrets["hf_token"],
    )

    messages = [
        {"role": "system", "content": "You are a financial report expert."},
        {"role": "user", "content": prompt.format(json=json.dumps(data, indent=2))},
    ]

    response = client.chat_completion(
        model=st.secrets["hf_model"],
        messages=messages,
        max_tokens=8000,
        temperature=0.1,
    )

    return response.choices[0].message.content

def main():
    st.title("Cash Flow Analysis Report Generator")
    
    # Display current date/time and user
    st.sidebar.markdown(f"""
    **Session Information:**
    - Date (UTC): {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}
    - User: alokyadav2020
    """)

    # Initialize analyzer
    analyzer = CashFlowAnalyzer()

    # Generate data for three years
    years = [2023, 2022, 2021]
    cash_flow_data = analyzer.generate_dummy_cash_flow_data(years)
    balance_sheet_data = analyzer.generate_dummy_balance_sheet(years)
    
    # Calculate metrics
    cash_flow_metrics = analyzer.calculate_cash_flow_metrics(cash_flow_data, balance_sheet_data)

    # Display raw data in expandable sections
    with st.expander("View Cash Flow Data"):
        st.json(cash_flow_data)
    
    with st.expander("View Cash Flow Metrics"):
        st.json(cash_flow_metrics)

    # Default prompt template
    default_prompt = """
    <|begin_of_text|><|start_header_id|>system<|end_header_id|>
    Generate a detailed financial report in HTML format.         
    You are financial expert and having great experience in Cash Flow Statement report generation
    You will be get data of three consecutive years and you have to develop reports for each year.
    Heading should be in h3 tag only, Ex. <h3 style='color: #555; font-family: Arial, sans-serif;'>Cash Flow Statement Report</h3>        
    You have three tasks:
        1. TO display all data Operating Cash Flow (OCF), Free Cash Flow (FCF), Cash Flow Coverage Ratio year wise in One table.
        2. To write conclusion in 3 to 4 lines.
        3. To provide recommendation in 3 to 4 lines.
    <|eot_id|><|start_header_id|>user<|end_header_id|>

    Here is the cash flow data for the years 2023, 2022, and 2021: in {json}
    Use this data and create a professional report.
    Make sure response must be in HTML format.

    <|eot_id|><|start_header_id|>assistant<|end_header_id|>
    """

    # Allow user to customize prompt
    st.subheader("Customize Report Generation Prompt")
    user_prompt = st.text_area(
        "Modify the prompt template below:",
        default_prompt,
        height=400,
        key="prompt_input"
    )

    # Add controls for report generation
    col1, col2 = st.columns(2)
    with col1:
        data_choice = st.radio(
            "Choose data to include in report:",
            ["Cash Flow Data", "Cash Flow Metrics", "Both"],
            key="data_choice"
        )

    # Generate report button
    if st.button("Generate Report", key="generate_button"):
        with st.spinner("Generating cash flow report..."):
            try:
                # Prepare data based on user choice
                if data_choice == "Cash Flow Data":
                    report_data = cash_flow_data
                elif data_choice == "Cash Flow Metrics":
                    report_data = cash_flow_metrics
                else:
                    report_data = {
                        "cash_flow_data": cash_flow_data,
                        "metrics": cash_flow_metrics
                    }

                # Generate report
                report = generate_report(user_prompt, report_data)

                # Display the report
                st.subheader("Generated Cash Flow Report")
                st.markdown(report, unsafe_allow_html=True)

                # Download options
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        label="Download as HTML",
                        data=report,
                        file_name=f"cash_flow_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.html",
                        mime="text/html",
                        key="download_html"
                    )
                
                with col2:
                    st.markdown("""
                    <style>
                        .stButton>button {
                            background-color: #f0f2f6;
                            color: #000000;
                        }
                    </style>
                    """, unsafe_allow_html=True)
                    st.button("Export to PDF (Coming Soon)", disabled=True)

            except Exception as e:
                st.error(f"An error occurred while generating the report: {str(e)}")

if __name__ == "__main__":
    main()