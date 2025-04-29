import streamlit as st
import random
from datetime import datetime
from huggingface_hub import InferenceClient
import json

class FinancialReportGenerator:
    def generate_dummy_financial_data(self, years):
        """Generate dummy financial data for given years."""
        financial_data = {}
        for year in years:
            current_assets = random.uniform(500000, 1000000)
            non_current_assets = random.uniform(1000000, 5000000)
            current_liabilities = random.uniform(200000, 800000)
            non_current_liabilities = random.uniform(500000, 2000000)
            shareholders_equity = random.uniform(500000, 3000000)

            total_assets = current_assets + non_current_assets
            total_liabilities = current_liabilities + non_current_liabilities

            financial_data[year] = {
                "Current Assets": round(current_assets, 2),
                "Non-Current Assets": round(non_current_assets, 2),
                "Total Assets": round(total_assets, 2),
                "Current Liabilities": round(current_liabilities, 2),
                "Non-Current Liabilities": round(non_current_liabilities, 2),
                "Total Liabilities": round(total_liabilities, 2),
                "Shareholders Equity": round(shareholders_equity, 2),
            }
        return financial_data

    def calculate_financial_ratios(self, financial_data):
        """Calculate financial ratios from the given data."""
        results = {}
        for year, data in financial_data.items():
            total_assets = data["Total Assets"]
            total_liabilities = data["Total Liabilities"]
            shareholders_equity = data["Shareholders Equity"]
            current_assets = data["Current Assets"]
            current_liabilities = data["Current Liabilities"]

            current_ratio = current_assets / current_liabilities
            debt_to_equity_ratio = total_liabilities / shareholders_equity

            results[year] = {
                "Total Assets": total_assets,
                "Total Liabilities": total_liabilities,
                "Shareholders Equity": shareholders_equity,
                "Current Ratio": round(current_ratio, 2),
                "Debt-to-Equity Ratio": round(debt_to_equity_ratio, 2),
            }
        return results

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
    st.title("Financial Report Generator")
    
    # Display current date/time and user
 
    # Initialize financial report generator
    generator = FinancialReportGenerator()

    # Generate dummy data for three years
    years = [2023, 2022, 2021]
    financial_data = generator.generate_dummy_financial_data(years)
    
    # Calculate financial ratios
    financial_ratios = generator.calculate_financial_ratios(financial_data)

    # Display raw data in expandable sections
    with st.expander("View Raw Financial Data"):
        st.json(financial_data)
    
    with st.expander("View Financial Ratios"):
        st.json(financial_ratios)

    # Default prompt template
    default_prompt = """
    <|begin_of_text|><|start_header_id|>system<|end_header_id|>
    Generate a detailed financial report in HTML format.
    You are financial expert and having great experience in Balance Sheet report generation
    Heading should be in h3 tag only, Ex. <h3 style='color: #555; font-family: Arial, sans-serif;'>Balance Sheet Report</h3>
    You will be given data of three consecutive years and you have to develop reports for each year.
    You have three tasks:
        1. TO display all data Total Assets, Total Liabilities, Shareholder's Equity, Current Ratio, Debt-to-Equity Ratio year wise in One table.
        2. To write conclusion in 3 to 4 lines.
        3. To provide recommendation in 3 to 4 lines.
    <|eot_id|><|start_header_id|>user<|end_header_id|>

    
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
            ["Raw Financial Data", "Financial Ratios", "Both"],
            key="data_choice"
        )

    # Generate report button
    if st.button("Generate Report", key="generate_button"):
        with st.spinner("Generating financial report..."):
            try:
                # Prepare data based on user choice
                if data_choice == "Raw Financial Data":
                    report_data = financial_data
                elif data_choice == "Financial Ratios":
                    report_data = financial_ratios
                else:
                    report_data = {
                        "financial_data": financial_data,
                        "ratios": financial_ratios
                    }

                # Generate report
                report = generate_report(user_prompt + "Here is the balance sheet for the years 2023, 2022, and 2021: in {json}", report_data)

                # Display the report
                st.subheader("Generated Financial Report")
                st.markdown(report, unsafe_allow_html=True)

                # Download options
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        label="Download as HTML",
                        data=report,
                        file_name=f"financial_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.html",
                        mime="text/html",
                        key="download_html"
                    )
                
                with col2:
                    # Save as PDF option (placeholder - actual PDF conversion would need additional libraries)
                    st.info("PDF download feature coming soon!")

            except Exception as e:
                st.error(f"An error occurred while generating the report: {str(e)}")

if __name__ == "__main__":
    main()