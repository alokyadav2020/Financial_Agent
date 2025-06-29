import streamlit as st
import random
from datetime import datetime
from huggingface_hub import InferenceClient
import json
import os

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
        api_key=os.getenv("hf_token"),
    )

    messages = [
        {"role": "system", "content": "You are a financial report expert."},
        {"role": "user", "content": prompt.format(json=json.dumps(data, indent=2))},
    ]

    response = client.chat_completion(
        model=os.getenv("hf_model"),
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
   <h3 style='color: #555; font-family: Arial, sans-serif;'>Cash Flow Statement Analysis Report</h3>

<p style='font-family: Arial, sans-serif;'>This report provides an analysis of cash flow metrics for three consecutive years.  We will examine Operating Cash Flow (OCF), Free Cash Flow (FCF), and the Cash Flow Coverage Ratio to assess the company's ability to generate cash, fund its operations, and service its debt.  All values are in millions of USD.</p>

<table style='width: 100%; border-collapse: collapse; font-family: Arial, sans-serif;'>
  <thead style='background-color: #f2f2f2;'>
    <tr>
      <th style='padding: 8px; border: 1px solid #ddd;'>Metric</th>
      <th style='padding: 8px; border: 1px solid #ddd;'>Year 1</th>
      <th style='padding: 8px; border: 1px solid #ddd;'>Year 2</th>
      <th style='padding: 8px; border: 1px solid #ddd;'>Year 3</th>
      <th style='padding: 8px; border: 1px solid #ddd;'>Calculation</th>
      <th style='padding: 8px; border: 1px solid #ddd;'>Interpretation</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style='padding: 8px; border: 1px solid #ddd;'>Revenue</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>100</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>120</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>130</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Given</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Increasing revenue indicates potential for stronger cash flow generation.</td>
    </tr>
    <tr>
      <td style='padding: 8px; border: 1px solid #ddd;'>Operating Cash Flow (OCF)</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>20</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>25</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>30</td>
       <td style='padding: 8px; border: 1px solid #ddd;'>Given</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>OCF shows the cash generated from core business operations. Upward trend is positive.</td>
    </tr>
    <tr>
      <td style='padding: 8px; border: 1px solid #ddd;'>Capital Expenditures (CAPEX)</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>10</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>12</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>15</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Given</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>CAPEX represents investments in fixed assets. Increasing CAPEX may indicate growth.</td>
    </tr>
    <tr>
      <td style='padding: 8px; border: 1px solid #ddd;'>Free Cash Flow (FCF)</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>10</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>13</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>15</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>OCF - CAPEX</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>FCF is the cash available to the company after covering operating expenses and capital expenditures.  Positive and increasing FCF is highly desirable.</td>
    </tr>
     <tr>
      <td style='padding: 8px; border: 1px solid #ddd;'>Interest Expense</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>5</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>6</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>7</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Given</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Interest expense is the cost of borrowing.</td>
    </tr>
    <tr>
      <td style='padding: 8px; border: 1px solid #ddd;'>Cash Flow Coverage Ratio</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>4x</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>4.17x</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>4.29x</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>OCF / Interest Expense</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>This ratio measures the company's ability to pay its interest obligations. A higher ratio indicates stronger solvency.</td>
    </tr>
  </tbody>
</table>

<h3 style='color: #555; font-family: Arial, sans-serif;'>Conclusion</h3>
<p style='font-family: Arial, sans-serif;'>
  The company demonstrates a positive trend in cash flow generation, with both OCF and FCF increasing over the three years. The Cash Flow Coverage Ratio is also healthy, indicating a strong ability to service debt. The consistent increase in revenue is a positive indicator for future cash flow.
  <br>
  <b style='color:red'>However, the analysis does not delve into the reasons behind the increase in OCF.  A deeper dive into the components of OCF (e.g., changes in working capital) would provide more insight. Additionally, while the Cash Flow Coverage Ratio is increasing, it's important to compare it against industry benchmarks to assess its true strength.</b>
</p>

<h3 style='color: #555; font-family: Arial, sans-serif;'>Recommendations</h3>
<p style='font-family: Arial, sans-serif;'>
  The company should continue to focus on maintaining and improving its operating efficiency to further enhance OCF.  Monitoring CAPEX is crucial to balance growth investments with free cash flow generation.  Maintaining a strong Cash Flow Coverage Ratio is essential for investor confidence and access to capital.
  <br>
  <b style='color:red'>It is recommended to analyze working capital management trends to understand how changes in accounts receivable, inventory, and accounts payable are affecting OCF.  Furthermore, a comparison of the company's CAPEX to industry averages would help determine if the investment levels are appropriate for its growth stage.</b>
<





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
                report = generate_report(user_prompt + " Here is the cash flow data for the years 2023, 2022, and 2021: in {json}", report_data)

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