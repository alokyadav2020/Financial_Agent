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

<p style='font-family: Arial, sans-serif;'>This report analyzes the company's financial performance over three consecutive years.  We will examine key metrics such as Revenue, Cost of Goods Sold (COGS), Gross Profit, Operating Expenses, Operating Income, and Net Income to assess profitability and efficiency. All values are in millions of USD.</p>

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
      <td style='padding: 8px; border: 1px solid #ddd;'>Total sales revenue for the period.</td>
    </tr>
    <tr>
      <td style='padding: 8px; border: 1px solid #ddd;'>Cost of Goods Sold (COGS)</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>60</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>70</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>75</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Given</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Direct costs of producing goods sold.</td>
    </tr>
    <tr>
      <td style='padding: 8px; border: 1px solid #ddd;'>Gross Profit</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>40</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>50</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>55</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Revenue - COGS</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Profit after deducting direct production costs.</td>
    </tr>
    <tr>
      <td style='padding: 8px; border: 1px solid #ddd;'>Operating Expenses</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>20</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>22</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>25</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Given</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Costs incurred in running the business.</td>
    </tr>
    <tr>
      <td style='padding: 8px; border: 1px solid #ddd;'>Operating Income</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>20</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>28</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>30</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Gross Profit - Operating Expenses</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Profit from core operations before interest and taxes.</td>
    </tr>
    <tr>
      <td style='padding: 8px; border: 1px solid #ddd;'>Interest Expense</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>5</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>6</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>7</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Given</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Cost of borrowing.</td>
    </tr>
    <tr>
      <td style='padding: 8px; border: 1px solid #ddd;'>Income Before Taxes</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>15</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>22</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>23</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Operating Income - Interest Expense</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Profit before income taxes.</td>
    </tr>
    <tr>
      <td style='padding: 8px; border: 1px solid #ddd;'>Income Tax Expense</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>3</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>4.4</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>4.6</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Given</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Income taxes paid.</td>
    </tr>
    <tr>
      <td style='padding: 8px; border: 1px solid #ddd;'>Net Income</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>12</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>17.6</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>18.4</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Income Before Taxes - Income Tax Expense</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Final profit after all expenses and taxes.</td>
    </tr>
     <tr>
      <td style='padding: 8px; border: 1px solid #ddd;'>Gross Profit Margin</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>40%</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>41.67%</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>42.31%</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Gross Profit / Revenue</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Percentage of revenue remaining after accounting for the cost of goods sold.</td>
    </tr>
    <tr>
      <td style='padding: 8px; border: 1px solid #ddd;'>Net Profit Margin</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>12%</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>14.67%</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>14.15%</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Net Income / Revenue</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Percentage of revenue that is net profit.</td>
    </tr>
  </tbody>
</table>

<h3 style='color: #555; font-family: Arial, sans-serif;'>Financial Performance Overview</h3>
<p style='font-family: Arial, sans-serif;'>
  The company demonstrates consistent revenue growth over the three years, indicating increasing sales.  Profitability also shows improvement, with both Operating Income and Net Income trending upwards.  The company is managing its expenses effectively, contributing to the positive bottom-line performance.
</p>

<h3 style='color: #555; font-family: Arial, sans-serif;'>Conclusion</h3>
<p style='font-family: Arial, sans-serif;'>
   Gross Profit Margin shows a slight but consistent increase, indicating improved efficiency in managing production costs. Net Profit Margin also improves significantly from Year 1 to Year 2, suggesting better overall profitability, although it dips slightly in Year 3. Overall, the company demonstrates a trend of improving profitability.
</p>

<h3 style='color: #555; font-family: Arial, sans-serif;'>Recommendations</h3>
<p style='font-family: Arial, sans-serif;'>
  The company should aim to maintain or improve its Gross Profit Margin by controlling production costs. Further analysis of the slight dip in Net Profit Margin in Year 3 is warranted to identify potential areas for cost control or revenue enhancement. Continued focus on revenue growth and expense management will be key to maximizing profitability.
</p>



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