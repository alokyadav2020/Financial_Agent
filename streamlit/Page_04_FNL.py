import streamlit as st
from huggingface_hub import InferenceClient
import json


# Function to calculate margins for P&L
def calculate_margins_for_pnl(financial_data):
    """Calculate Gross Profit Margin and Net Profit Margin for the given financial data."""
    margins = {}
    for year, data in financial_data.items():
        gross_profit_margin = round(((data["Revenue"] - data["COGS"]) / data["Revenue"]) * 100, 2)
        net_profit_margin = round((data["Net Profit"] / data["Revenue"]) * 100, 2)
        margins[year] = {
            "Revenue": data["Revenue"],
            "COGS": data["COGS"],
            "Net Profit": data["Net Profit"],
            "Gross Profit Margin": gross_profit_margin,
            "Net Profit Margin": net_profit_margin
        }
    return margins


# Function to generate the P&L report
def generate_report(prompt, metrics):
    """Generate financial report using HuggingFace model."""
    client = InferenceClient(
        provider="hf-inference",
        api_key=st.secrets["hf_token"],
    )

    messages = [
        {"role": "system", "content": "You are a financial report expert."},
        {"role": "user", "content": prompt.format(metrics=json.dumps(metrics))},
    ]

    response = client.chat_completion(
        model=st.secrets["hf_model"],
        messages=messages,
        max_tokens=8000,
        temperature=0.1,
    )

    return response.choices[0].message.content


# Default prompt
DEFAULT_PROMPT = """
<h3 style='color: #555; font-family: Arial, sans-serif;'>Profit & Loss Statement (P&L) Report</h3>


You are tasked to:
1. Display the data in a well-formatted table.
2. Provide a brief overview of the company's financial performance.
3. Write a conclusion about Gross Profit Margin and Net Profit Margin in 3 to 4 lines.
4. Provide recommendations for improving financial performance in 3 to 4 lines.

Make sure the response is professional and in a format suitable for a financial report.
"""


# Streamlit App
def main():
    st.title("Profit & Loss (P&L) Report Generator")

    # Input financial data
    financial_data = {
        2023: {"Revenue": 10000000, "COGS": 6000000, "Net Profit": 1000000},
        2022: {"Revenue": 9500000, "COGS": 5800000, "Net Profit": 900000},
        2021: {"Revenue": 9000000, "COGS": 5500000, "Net Profit": 800000},
    }

    # Calculate margins
    pnl_data = calculate_margins_for_pnl(financial_data)

    # Display financial data and calculated margins
    st.subheader("Financial Data and Margins")
    st.json(pnl_data)

    # Allow user to customize prompt
    st.subheader("Customize the Prompt")
    user_prompt = st.text_area(
        "Modify the prompt below to test with various instructions:",
        DEFAULT_PROMPT,
        height=300,
    )

    # Generate report button
    if st.button("Generate Report"):
        with st.spinner("Generating the P&L report..."):
            try:
                # Generate the report
                report = generate_report("Here is the Profit & Loss data for the years 2023, 2022, and 2021:{metrics}" + user_prompt, pnl_data)

                # Display the report
                st.subheader("Generated P&L Report")
                st.markdown(report, unsafe_allow_html=True)

                # Download option
                st.download_button(
                    label="Download Report (HTML)",
                    data=report,
                    file_name="pnl_report.html",
                    mime="text/html",
                )

            except Exception as e:
                st.error(f"An error occurred while generating the report: {str(e)}")


if __name__ == "__main__":
    main()