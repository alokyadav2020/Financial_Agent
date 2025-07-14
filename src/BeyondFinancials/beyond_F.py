import streamlit as st
import os


import streamlit as st
from huggingface_hub import InferenceClient
import json
import os
from src.db.sql_operation import execute_query, fetch_query
from sqlalchemy import text
from openai import AzureOpenAI 
from dotenv import load_dotenv
load_dotenv()

from src.Page_04_FNL import pnl_reports
from src.Page_5BalanceSheetAnalysis import balancesheet
from src.Page_6_cashFlow import cashflow

FPNL_REPORT= ""
BS_REPORT = ""
CF_REPORT = ""

# # Function to calculate margins for P&L
# def calculate_margins_for_pnl(financial_data):
#     """Calculate Gross Profit Margin and Net Profit Margin for the given financial data."""
#     margins = {}
#     for year, data in financial_data.items():
#         gross_profit_margin = round(((data["Revenue"] - data["COGS"]) / data["Revenue"]) * 100, 2)
#         net_profit_margin = round((data["Net Profit"] / data["Revenue"]) * 100, 2)
#         margins[year] = {
#             "Revenue": data["Revenue"],
#             "COGS": data["COGS"],
#             "Net Profit": data["Net Profit"],
#             "Gross Profit Margin": gross_profit_margin,
#             "Net Profit Margin": net_profit_margin
#         }
#     return margins


# # Function to generate the P&L report
# def generate_report(prompt, metrics):
#     """Generate financial report using HuggingFace model."""
#     # client = InferenceClient(
#     #     provider="hf-inference",
#     #     api_key=os.getenv("hf_token"),
#     # )

#     client = AzureOpenAI(
#         azure_endpoint= os.getenv("ENDPOINT_URL"),
#         azure_deployment=os.getenv("DEPLOYMENT_NAME"),
#         api_key=os.getenv("AZURE_OPENAI_API_KEY"),
#         api_version="2025-01-01-preview"
#     )



#     messages = [
#         {"role": "system", "content": "You are a financial report expert."},
#         {"role": "user", "content": prompt + "Use this metrics\n\n" + metrics},
#     ]
    

#     response = client.chat.completions.create(
#             model=os.getenv("DEPLOYMENT_NAME"),  # Use the deployment name instead of model name
#             messages=messages,
#             temperature=0.7
#         )

#     return response.choices[0].message.content


# # Default prompt
# DEFAULT_PROMPT = """
# <h3 style='color: #555; font-family: Arial, sans-serif;'>Profit & Loss Statement (P&L) Report</h3>

# <p style='font-family: Arial, sans-serif;'>This report analyzes the company's financial performance over three consecutive years. We will examine key metrics such as Revenue, Cost of Goods Sold (COGS), Gross Profit, Operating Expenses, Operating Income, and Net Income to assess profitability and efficiency.  We will also include key ratios to provide a more in-depth analysis. All values are in millions of USD.</p>

# <table style='width: 100%; border-collapse: collapse; font-family: Arial, sans-serif;'>
#   <thead style='background-color: #f2f2f2;'>
#     <tr>
#       <th style='padding: 8px; border: 1px solid #ddd;'>Metric</th>
#       <th style='padding: 8px; border: 1px solid #ddd;'>Year 1</th>
#       <th style='padding: 8px; border: 1px solid #ddd;'>Year 2</th>
#       <th style='padding: 8px; border: 1px solid #ddd;'>Year 3</th>
#       <th style='padding: 8px; border: 1px solid #ddd;'>Calculation</th>
#       <th style='padding: 8px; border: 1px solid #ddd;'>Interpretation</th>
#     </tr>
#   </thead>
#   <tbody>
#     <tr>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Revenue</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>100</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>120</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>130</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Given</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Total sales revenue for the period.</td>
#     </tr>
#     <tr>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Cost of Goods Sold (COGS)</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>60</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>70</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>75</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Given</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Direct costs of producing goods sold, including materials and labor.</td>
#     </tr>
#     <tr>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Gross Profit</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>40</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>50</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Revenue - COGS</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Profit after deducting direct production costs.</td>
#     </tr>
#     <tr>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Operating Expenses</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>20</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>22</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>25</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Given</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Costs incurred in running the business, excluding production costs and interest.</td>
#     </tr>
#     <tr>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Operating Income</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>20</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>28</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Gross Profit - Operating Expenses</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Profit from core operations before interest and taxes.</td>
#     </tr>
#     <tr>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Interest Expense</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>5</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>6</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>7</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Given</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Cost of borrowing money.</td>
#     </tr>
#     <tr>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Income Before Taxes</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>15</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>22</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>23</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Operating Income - Interest Expense</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Profit before income taxes.</td>
#     </tr>
#     <tr>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Income Tax Expense</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>3</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>4.4</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>4.6</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Given</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Income taxes paid.</td>
#     </tr>
#     <tr>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Net Income</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>12</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>17.6</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>18.4</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Income Before Taxes - Income Tax Expense</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Final profit after all expenses and taxes.</td>
#     </tr>
#     <tr>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Gross Profit Margin</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>40%</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>41.67%</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>42.31%</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Gross Profit / Revenue</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Percentage of revenue remaining after accounting for the cost of goods sold.</td>
#     </tr>
#     <tr>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Net Profit Margin</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>12%</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>14.67%</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>14.15%</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Net Income / Revenue</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Percentage of revenue that is net profit.</td>
#     </tr>
#     <tr>
#         <td style='padding: 8px; border: 1px solid #ddd;'>EBITDA</td>
#         <td style='padding: 8px; border: 1px solid #ddd;'>25</td>
#         <td style='padding: 8px; border: 1px solid #ddd;'>33</td>
#         <td style='padding: 8px; border: 1px solid #ddd;'>Operating Income + Depreciation + Amortization</td>
#         <td style='padding: 8px; border: 1px solid #ddd;'>Earnings before interest, taxes, depreciation, and amortization; a measure of core operational profitability.</td>
#       </tr>
#       <tr>
#         <td style='padding: 8px; border: 1px solid #ddd;'>Revenue Growth</td>
#         <td style='padding: 8px; border: 1px solid #ddd;'>N/A</td>
#         <td style='padding: 8px; border: 1px solid #ddd;'>20%</td>
#         <td style='padding: 8px; border: 1px solid #ddd;'>((Current Year Revenue - Previous Year Revenue) / Previous Year Revenue) * 100</td>
#         <td style='padding: 8px; border: 1px solid #ddd;'>The percentage change in revenue from the previous year, indicating growth trajectory.</td>
#       </tr>
#       <tr>
#         <td style='padding: 8px; border: 1px solid #ddd;'>Operating Expense Ratio</td>
#         <td style='padding: 8px; border: 1px solid #ddd;'>20%</td>
#         <td style='padding: 8px; border: 1px solid #ddd;'>18.33%</td>
#         <td style='padding: 8px; border: 1px solid #ddd;'>19.23%</td>
#         <td style='padding: 8px; border: 1px solid #ddd;'>Operating Expenses / Revenue</td>
#         <td style='padding: 8px; border: 1px solid #ddd;'>The proportion of revenue used to cover operating expenses, indicating operational efficiency.</td>
#       </tr>
#       <tr>
#         <td style='padding: 8px; border: 1px solid #ddd;'>Tax Burden Ratio</td>
#         <td style='padding: 8px; border: 1px solid #ddd;'>20%</td>
#         <td style='padding: 8px; border: 1px solid #ddd;'>20%</td>
#         <td style='padding: 8px; border: 1px solid #ddd;'>20%</td>
#         <td style='padding: 8px; border: 1px solid #ddd;'>Income Tax Expense / Income Before Taxes</td>
#         <td style='padding: 8px; border: 1px solid #ddd;'>The proportion of earnings before tax that is paid as tax, highlighting the impact of taxes on profitability.</td>
#       </tr>
#   </tbody>
# </table>

# <h3 style='color: #555; font-family: Arial, sans-serif;'>Financial Performance Overview</h3>
# <p style='font-family: Arial, sans-serif;'>
#   The company demonstrates consistent revenue growth over the three years, indicating increasing sales.  Profitability also shows improvement, with both Operating Income and Net Income trending upwards.  The company is managing its expenses effectively, contributing to the positive bottom-line performance.
# </p>

# <h3 style='color: #555; font-family: Arial, sans-serif;'>Conclusion</h3>
# <p style='font-family: Arial, sans-serif;'>
#   Gross Profit Margin shows a slight but consistent increase, indicating improved efficiency in managing production costs. Net Profit Margin also improves significantly from Year 1 to Year 2, suggesting better overall profitability, although it dips slightly in Year 3. Overall, the company demonstrates a trend of improving profitability.
# </p>

# <h3 style='color: #555; font-family: Arial, sans-serif;'>Recommendations</h3>
# <p style='font-family: Arial, sans-serif;'>
#   The company should aim to maintain or improve its Gross Profit Margin by controlling production costs. Further analysis of the slight dip in Net Profit Margin in Year 3 is warranted to identify potential areas for cost control or revenue enhancement. Continued focus on revenue growth and expense management will be key to maximizing profitability.
# </p>

# <h3 style='color: #555; font-family: Arial, sans-serif;'>Additional Explanation of Calculations (MBB Style)</h3>
# <p style='font-family: Arial, sans-serif;'>
#   To provide further clarity on the key profitability metrics, we can elaborate on their calculation and significance from an MBB perspective:
#   <br><br>
#   <strong>Gross Profit Margin:</strong> This metric is calculated as (Revenue - COGS) / Revenue.  It shows how much profit a company makes on its products or services, *before* considering other business expenses. A higher margin indicates greater efficiency in production.
#   <br><br>
#   <strong>Net Profit Margin:</strong> This metric is calculated as Net Income / Revenue. It measures how much profit a company keeps for each dollar of revenue earned, *after* all expenses are accounted for.  It's a key indicator of overall profitability.
#   <br><br>
#   <strong>EBITDA:</strong> This metric is calculated as Operating Income + Depreciation + Amortization.  It represents earnings before interest, taxes, depreciation, and amortization.  In simpler terms, it's a way to assess a company's operating performance without the influence of financing and accounting decisions.
#   <br><br>
#   <strong>Revenue Growth:</strong> This metric is calculated as ((Current Year Revenue - Previous Year Revenue) / Previous Year Revenue) * 100.  It tells us how much the company's sales have increased (or decreased) compared to the previous year.  A positive percentage indicates growth, while a negative percentage indicates a decline.
#   <br><br>
#   <strong>Operating Expense Ratio:</strong> This metric is calculated as Operating Expenses / Revenue.  It shows the proportion of revenue that is used to cover the day-to-day costs of running the business, such as salaries, rent, and marketing.  A lower percentage is generally better, as it indicates greater efficiency in managing these expenses.
#   <br><br>
#   <strong>Tax Burden Ratio:</strong> This metric is calculated as Income Tax Expense / Income Before Taxes. It shows the portion of a company's pre-tax profit that is paid as income taxes.
# </p>





# """


# # Streamlit App
# def main_FPNL():
#     st.title("Profit & Loss (P&L) Report Generator")

#     # Input financial data
#     financial_data = {
#         2023: {"Revenue": 10000000, "COGS": 6000000, "Net Profit": 1000000},
#         2022: {"Revenue": 9500000, "COGS": 5800000, "Net Profit": 900000},
#         2021: {"Revenue": 9000000, "COGS": 5500000, "Net Profit": 800000},
#     }

#     # Calculate margins
#     pnl_data = calculate_margins_for_pnl(financial_data)

#     # Display financial data and calculated margins
#     st.subheader("Financial Data and Margins")
#     st.json(pnl_data)

#     # Allow user to customize prompt
#     st.subheader("Customize the Prompt")

#     query = text("SELECT [fla] FROM prompt_valuation_reports WHERE id = :id")
#     params = {"id": 1}
#     data = fetch_query(query, params)
#     research_agent_prompt=""
    
#     if data:
#         retrieved_scraping_prompt = data[0]['fla']
#         research_agent_prompt = retrieved_scraping_prompt
        
        
#     else:
#         research_agent_prompt=DEFAULT_PROMPT


#     user_prompt = st.text_area(
#         "Modify the prompt below to test with various instructions:",
#         research_agent_prompt,
#         height=300,
#     )



#     if st.button("Save Prompt!!"):
#         try:
#             # Corrected UPDATE query with WHERE clause
#             query = text("UPDATE prompt_valuation_reports SET [fla] = :fla WHERE id = :id")
#             params = {
#                 "fla": user_prompt,
#                 "id": 1  # Make sure this matches the record you want to update
#             }
#             execute_query(query, params)
#             st.success("Prompt saved successfully!")

#             # Retrieve the saved prompt for confirmation
#             query = text("SELECT [fla] FROM prompt_valuation_reports WHERE id = :id")
#             params = {"id": 1}
#             data = fetch_query(query, params)
            
#             if data:
#                 retrieved_scraping_prompt = data[0]['fla']
#                 st.write(retrieved_scraping_prompt)
#             else:
#                 st.warning("No data found for the given ID.")
#         except Exception as e:
#             st.error(f"Database error: {e}")

#     st.markdown("---")
#     # Generate report button
#     if st.button("Generate Report!!!"):
#         with st.spinner("Generating the P&L report..."):
#             try:
#                 # Generate the report
#                 report = generate_report("Here is the Profit & Loss data for the years 2023, 2022, and 2021:{metrics}" + user_prompt, pnl_data)

#                 FPNL_REPORT = report

#                 # Display the report
#                 st.subheader("Generated P&L Report")
#                 st.markdown(report, unsafe_allow_html=True)

#                 # Download option
#                 st.download_button(
#                     label="Download Report (HTML)",
#                     data=report,
#                     file_name="pnl_report.html",
#                     mime="text/html",
#                 )

#             except Exception as e:
#                 st.error(f"An error occurred while generating the report: {str(e)}")



# import random
# from datetime import datetime


# class FinancialReportGenerator:
#     def generate_dummy_financial_data(self, years):
#         """Generate dummy financial data for given years."""
#         financial_data = {}
#         for year in years:
#             current_assets = random.uniform(500000, 1000000)
#             non_current_assets = random.uniform(1000000, 5000000)
#             current_liabilities = random.uniform(200000, 800000)
#             non_current_liabilities = random.uniform(500000, 2000000)
#             shareholders_equity = random.uniform(500000, 3000000)

#             total_assets = current_assets + non_current_assets
#             total_liabilities = current_liabilities + non_current_liabilities

#             financial_data[year] = {
#                 "Current Assets": round(current_assets, 2),
#                 "Non-Current Assets": round(non_current_assets, 2),
#                 "Total Assets": round(total_assets, 2),
#                 "Current Liabilities": round(current_liabilities, 2),
#                 "Non-Current Liabilities": round(non_current_liabilities, 2),
#                 "Total Liabilities": round(total_liabilities, 2),
#                 "Shareholders Equity": round(shareholders_equity, 2),
#             }
#         return financial_data

#     def calculate_financial_ratios(self, financial_data):
#         """Calculate financial ratios from the given data."""
#         results = {}
#         for year, data in financial_data.items():
#             total_assets = data["Total Assets"]
#             total_liabilities = data["Total Liabilities"]
#             shareholders_equity = data["Shareholders Equity"]
#             current_assets = data["Current Assets"]
#             current_liabilities = data["Current Liabilities"]

#             current_ratio = current_assets / current_liabilities
#             debt_to_equity_ratio = total_liabilities / shareholders_equity

#             results[year] = {
#                 "Total Assets": total_assets,
#                 "Total Liabilities": total_liabilities,
#                 "Shareholders Equity": shareholders_equity,
#                 "Current Ratio": round(current_ratio, 2),
#                 "Debt-to-Equity Ratio": round(debt_to_equity_ratio, 2),
#             }
#         return results

# def generate_report(prompt, data):
#     """Generate financial report using HuggingFace model."""
#     # client = InferenceClient(
#     #     provider="hf-inference",
#     #     api_key=os.getenv("hf_token"),
#     # )

#     client = AzureOpenAI(
#         azure_endpoint= os.getenv("ENDPOINT_URL"),
#         azure_deployment=os.getenv("DEPLOYMENT_NAME"),
#         api_key=os.getenv("AZURE_OPENAI_API_KEY"),
#         api_version="2025-01-01-preview"
#     )

#     messages = [
#         {"role": "system", "content": "You are a financial report expert."},
#         {"role": "user", "content": prompt.format(json=json.dumps(data, indent=2))},
#     ]

#     # response = client.chat_completion(
#     #     model=os.getenv("hf_model"),
#     #     messages=messages,
#     #     max_tokens=8000,
#     #     temperature=0.1,
#     # )
#     response = client.chat.completions.create(
#             model=os.getenv("DEPLOYMENT_NAME"),  # Use the deployment name instead of model name
#             messages=messages,
#             temperature=0.7
#         )

#     return response.choices[0].message.content

# def main_BS():
#     st.title("Financial Report Generator")
    
#     # Display current date/time and user
 
#     # Initialize financial report generator
#     generator = FinancialReportGenerator()

#     # Generate dummy data for three years
#     years = [2023, 2022, 2021]
#     financial_data = generator.generate_dummy_financial_data(years)
    
#     # Calculate financial ratios
#     financial_ratios = generator.calculate_financial_ratios(financial_data)

#     # Display raw data in expandable sections
#     with st.expander("View Raw Financial Data"):
#         st.json(financial_data)
    
#     with st.expander("View Financial Ratios"):
#         st.json(financial_ratios)

#     # Default prompt template
#     default_prompt = """
#     <|begin_of_text|><|start_header_id|>system<|end_header_id|>
#    Objective:

# To analyze a company's balance sheet data over three consecutive years and generate a comprehensive report that assesses its financial position, liquidity, and leverage. The report should be structured in HTML format and include detailed explanations and interpretations of key metrics, similar to an MBB consultant's analysis.

# Agent Persona:

# You are a Senior Financial Analyst at a top-tier consulting firm (e.g., McKinsey, BCG, Bain). You possess a deep understanding of balance sheet analysis and are skilled at communicating complex financial information in a clear, concise, and actionable manner.

# Input Data:

# The agent will receive balance sheet data for three consecutive years, including:

# Total Assets (in millions of USD)

# Total Liabilities (in millions of USD)

# Shareholder's Equity (in millions of USD)

# Current Assets (in millions of USD)

# Current Liabilities (in millions of USD)

# Tasks:

# Data Presentation:

# Present the data in a well-formatted HTML table with the following columns:

# Metric

# Year 1

# Year 2

# Year 3

# Calculation

# Interpretation

# Ensure the table is styled for professional presentation (e.g., using CSS for borders, spacing, and alignment).

# Metric Calculation:

# Calculate the following key financial ratios for each year:

# Current Ratio: Current Assets / Current Liabilities

# Debt-to-Equity Ratio: Total Liabilities / Shareholder's Equity

# Metric Interpretation:

# Provide a clear and concise interpretation of each metric, explaining what it reveals about the company's financial health. The interpretation should be in 1-2 sentences.

# Report Generation:

# Generate an HTML report with the following sections:

# Heading: "Balance Sheet Report"

# Introduction: A brief overview of the purpose of the report and the metrics being analyzed.

# Table: The formatted table with data, calculations, and interpretations.

# Conclusion: A 3-4 line summary of the overall findings, highlighting key trends and the company's financial position.

# Recommendations: 3-4 actionable recommendations for the company, based on the balance sheet analysis.

# Additional Explanation of Calculations (MBB Style): Provide detailed explanations of the key balance sheet metrics and their significance, written in a style that an MBB consultant would use.
# —-----------------------------------







# <h3 style='color: #555; font-family: Arial, sans-serif;'>Balance Sheet Report</h3>

# <p style='font-family: Arial, sans-serif;'>This report provides an analysis of key balance sheet metrics for three consecutive years.  We will examine Total Assets, Total Liabilities, Shareholder's Equity, the Current Ratio, and the Debt-to-Equity Ratio to assess the company's financial position, liquidity, and leverage. All values are in millions of USD.</p>

# <table style='width: 100%; border-collapse: collapse; font-family: Arial, sans-serif;'>
#   <thead style='background-color: #f2f2f2;'>
#     <tr>
#       <th style='padding: 8px; border: 1px solid #ddd;'>Metric</th>
#       <th style='padding: 8px; border: 1px solid #ddd;'>Year 1</th>
#       <th style='padding: 8px; border: 1px solid #ddd;'>Year 2</th>
#       <th style='padding: 8px; border: 1px solid #ddd;'>Year 3</th>
#       <th style='padding: 8px; border: 1px solid #ddd;'>Calculation</th>
#       <th style='padding: 8px; border: 1px solid #ddd;'>Interpretation</th>
#     </tr>
#   </thead>
#   <tbody>
#     <tr>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Total Assets</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>100</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>110</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>120</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Given</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Represents the company's total resources. Increasing assets can indicate growth.</td>
#     </tr>
#     <tr>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Total Liabilities</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>40</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>45</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>50</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Given</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Represents the company's total obligations to creditors.</td>
#     </tr>
#     <tr>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Shareholder's Equity</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>60</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>65</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>70</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Total Assets - Total Liabilities</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Represents the owners' stake in the company.</td>
#     </tr>
#     <tr>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Current Assets</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>50</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>55</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>60</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Given</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Assets that can be converted to cash within one year.</td>
#     </tr>
#     <tr>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Current Liabilities</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>25</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>27</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>28</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Given</td>
#        <td style='padding: 8px; border: 1px solid #ddd;'>Obligations due within one year.</td>
#     </tr>
#     <tr>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Current Ratio</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>2x</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>2.04x</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>2.14x</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Current Assets / Current Liabilities</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Measures short-term liquidity; ability to pay short-term obligations. A higher ratio is generally better.</td>
#     </tr>
#     <tr>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Debt-to-Equity Ratio</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>0.67x</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>0.69x</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>0.71x</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Total Liabilities / Shareholder's Equity</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Measures financial leverage; proportion of financing from debt vs. equity. A lower ratio is generally better.</td>
#     </tr>
#   </tbody>
# </table>

# <h3 style='color: #555; font-family: Arial, sans-serif;'>Conclusion</h3>
# <p style='font-family: Arial, sans-serif;'>
#   The company's total assets, liabilities, and shareholder's equity are all showing a steady increase over the three years, indicating growth.  The Current Ratio is consistently above 2, demonstrating strong short-term liquidity.  The Debt-to-Equity Ratio is also relatively stable, suggesting a balanced capital structure.
# </p>

# <h3 style='color: #555; font-family: Arial, sans-serif;'>Recommendations</h3>
# <p style='font-family: Arial, sans-serif;'>
#   The company should maintain its strong liquidity position as indicated by the Current Ratio. While the Debt-to-Equity Ratio is reasonable, it should be monitored to ensure it doesn't increase significantly, which could increase financial risk.  Continued asset growth should be supported by profitable operations.
# </p>




#     <|eot_id|><|start_header_id|>user<|end_header_id|>

    
#     Use this data and create a professional report.
#     Make sure response must be in HTML format.

#     <|eot_id|><|start_header_id|>assistant<|end_header_id|>
#     """

#     query = text("SELECT [balance_sheet] FROM prompt_valuation_reports WHERE id = :id")
#     params = {"id": 1}
#     data = fetch_query(query, params)
    
#     if data:
#         default_prompt= data[0]['balance_sheet']
#     else:
#         pass

#     # Allow user to customize prompt
#     st.subheader("Customize Report Generation Prompt")
#     user_prompt = st.text_area(
#         "Modify the prompt template below:",
#         default_prompt,
#         height=400,
      
#     )



#     if st.button("Save promt!"):
#             #st.session_state.user_prompt = default_prompt
#         id = 1
#         try:
#             update_query = text("""
#                 UPDATE prompt_valuation_reports
#                 SET [balance_sheet] = :summary
#                 WHERE id = :id
#             """)
#             params = {
#                 "summary": user_prompt,
#                 "id": id
#             }
#             execute_query(update_query, params)
#             st.success("Data updated successfully!")
#         except Exception as e:
#             st.error(f"Update failed: {e}")
#         st.success("Prompt reset to default!")
#         st.rerun()

#         try:
#             query = text("SELECT [balance_sheet] FROM prompt_valuation_reports WHERE id = :id")
#             params = {"id": 1}
#             data = fetch_query(query, params)
#             if data:
#                 st.write("Executive Summary:")
#                 st.write(data[0]["balance_sheet"])
#             else:
#                 st.warning("No report found.")
#         except Exception as e:
#             st.error(f"Error fetching data: {e}")


#     st.markdown("----")        

#     # Add controls for report generation
#     col1, col2 = st.columns(2)
#     with col1:
#         data_choice = st.radio(
#             "Choose data to include in report:",
#             ["Raw Financial Data", "Financial Ratios", "Both"],
            
#         )

#     # Generate report button
#     if st.button("Generate Report!"):
#         with st.spinner("Generating financial report..."):
#             try:
#                 # Prepare data based on user choice
#                 if data_choice == "Raw Financial Data":
#                     report_data = financial_data
#                 elif data_choice == "Financial Ratios":
#                     report_data = financial_ratios
#                 else:
#                     report_data = {
#                         "financial_data": financial_data,
#                         "ratios": financial_ratios
#                     }

#                 # Generate report
#                 report = generate_report(user_prompt + "Here is the balance sheet for the years 2023, 2022, and 2021: in {json}", report_data)
#                 BS_REPORT = report

#                 # Display the report
#                 st.subheader("Generated Financial Report")
#                 st.markdown(report, unsafe_allow_html=True)

#                 # Download options
#                 col1, col2 = st.columns(2)
#                 with col1:
#                     st.download_button(
#                         label="Download as HTML",
#                         data=report,
#                         file_name=f"financial_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.html",
#                         mime="text/html",
#                         key="download_html"
#                     )
                
#                 with col2:
#                     # Save as PDF option (placeholder - actual PDF conversion would need additional libraries)
#                     st.info("PDF download feature coming soon!")

#             except Exception as e:
#                 st.error(f"An error occurred while generating the report: {str(e)}")








# class CashFlowAnalyzer:
#     def generate_dummy_cash_flow_data(self, years):
#         """Generate dummy cash flow data for given years."""
#         cash_flow_data = {}
#         for year in years:
#             net_income = random.uniform(500000, 2000000)
#             adjustments_for_non_cash_items = random.uniform(100000, 500000)
#             changes_in_working_capital = random.uniform(-100000, 100000)
#             cash_from_operating_activities = (
#                 net_income + adjustments_for_non_cash_items + changes_in_working_capital
#             )
            
#             cash_from_investing_activities = random.uniform(-1000000, -500000)
#             cash_from_financing_activities = random.uniform(-500000, 500000)
            
#             net_cash_flow = (
#                 cash_from_operating_activities +
#                 cash_from_investing_activities +
#                 cash_from_financing_activities
#             )
            
#             beginning_cash_balance = random.uniform(1000000, 5000000)
#             ending_cash_balance = beginning_cash_balance + net_cash_flow
            
#             cash_flow_data[year] = {
#                 "Net Income": round(net_income, 2),
#                 "Adjustments for Non-Cash Items": round(adjustments_for_non_cash_items, 2),
#                 "Changes in Working Capital": round(changes_in_working_capital, 2),
#                 "Cash from Operating Activities": round(cash_from_operating_activities, 2),
#                 "Cash from Investing Activities": round(cash_from_investing_activities, 2),
#                 "Cash from Financing Activities": round(cash_from_financing_activities, 2),
#                 "Net Cash Flow": round(net_cash_flow, 2),
#                 "Beginning Cash Balance": round(beginning_cash_balance, 2),
#                 "Ending Cash Balance": round(ending_cash_balance, 2),
#             }
#         return cash_flow_data

#     def generate_dummy_balance_sheet(self, years):
#         """Generate dummy balance sheet data for cash flow metrics calculation."""
#         balance_sheet_data = {}
#         for year in years:
#             balance_sheet_data[year] = {
#                 "Total Liabilities": round(random.uniform(1000000, 5000000), 2)
#             }
#         return balance_sheet_data

#     def calculate_cash_flow_metrics(self, cash_flow_data, balance_sheet_data):
#         """Calculate cash flow metrics from the given data."""
#         metrics = {}
#         for year in cash_flow_data.keys():
#             ocf = cash_flow_data[year]["Cash from Operating Activities"]
#             capital_expenditures = random.uniform(100000, 500000)
#             fcf = ocf - capital_expenditures
#             total_debt = balance_sheet_data[year]["Total Liabilities"]
#             cash_flow_coverage_ratio = ocf / total_debt
            
#             metrics[year] = {
#                 "Operating Cash Flow (OCF)": round(ocf, 2),
#                 "Free Cash Flow (FCF)": round(fcf, 2),
#                 "Cash Flow Coverage Ratio": round(cash_flow_coverage_ratio, 2),
#             }
#         return metrics

# def generate_report(prompt, data):
#     """Generate financial report using HuggingFace model."""
#     # client = InferenceClient(
#     #     provider="hf-inference",
#     #     api_key=os.getenv("hf_token"),
#     # )

#     client = AzureOpenAI(
#         azure_endpoint= os.getenv("ENDPOINT_URL"),
#         azure_deployment=os.getenv("DEPLOYMENT_NAME"),
#         api_key=os.getenv("AZURE_OPENAI_API_KEY"),
#         api_version="2025-01-01-preview"
#     )


#     messages = [
#         {"role": "system", "content": "You are a financial report expert."},
#         {"role": "user", "content": prompt.format(json=json.dumps(data, indent=2))},
#     ]

#     # response = client.chat_completion(
#     #     model=os.getenv("hf_model"),
#     #     messages=messages,
#     #     max_tokens=8000,
#     #     temperature=0.1,
#     # )

#     response = client.chat.completions.create(
#             model=os.getenv("DEPLOYMENT_NAME"),  # Use the deployment name instead of model name
#             messages=messages,
#             temperature=0.7
#         )

#     return response.choices[0].message.content

# def main_CF():
#     st.title("Cash Flow Analysis Report Generator")
    
#     # Display current date/time and user
#     st.sidebar.markdown(f"""
#     **Session Information:**
#     - Date (UTC): {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}
#     - User: alokyadav2020
#     """)

#     # Initialize analyzer
#     analyzer = CashFlowAnalyzer()

#     # Generate data for three years
#     years = [2023, 2022, 2021]
#     cash_flow_data = analyzer.generate_dummy_cash_flow_data(years)
#     balance_sheet_data = analyzer.generate_dummy_balance_sheet(years)
    
#     # Calculate metrics
#     cash_flow_metrics = analyzer.calculate_cash_flow_metrics(cash_flow_data, balance_sheet_data)

#     # Display raw data in expandable sections
#     with st.expander("View Cash Flow Data"):
#         st.json(cash_flow_data)
    
#     with st.expander("View Cash Flow Metrics"):
#         st.json(cash_flow_metrics)

#     # Default prompt template
#     default_prompt = """
#    <h3 style='color: #555; font-family: Arial, sans-serif;'>Cash Flow Statement Analysis Report</h3>

# <p style='font-family: Arial, sans-serif;'>This report provides an analysis of cash flow metrics for three consecutive years.  We will examine Operating Cash Flow (OCF), Free Cash Flow (FCF), and the Cash Flow Coverage Ratio to assess the company's ability to generate cash, fund its operations, and service its debt.  All values are in millions of USD.</p>

# <table style='width: 100%; border-collapse: collapse; font-family: Arial, sans-serif;'>
#   <thead style='background-color: #f2f2f2;'>
#     <tr>
#       <th style='padding: 8px; border: 1px solid #ddd;'>Metric</th>
#       <th style='padding: 8px; border: 1px solid #ddd;'>Year 1</th>
#       <th style='padding: 8px; border: 1px solid #ddd;'>Year 2</th>
#       <th style='padding: 8px; border: 1px solid #ddd;'>Year 3</th>
#       <th style='padding: 8px; border: 1px solid #ddd;'>Calculation</th>
#       <th style='padding: 8px; border: 1px solid #ddd;'>Interpretation</th>
#     </tr>
#   </thead>
#   <tbody>
#     <tr>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Revenue</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>100</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>120</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>130</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Given</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Increasing revenue indicates potential for stronger cash flow generation.</td>
#     </tr>
#     <tr>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Operating Cash Flow (OCF)</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>20</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>25</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>30</td>
#        <td style='padding: 8px; border: 1px solid #ddd;'>Given</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>OCF shows the cash generated from core business operations. Upward trend is positive.</td>
#     </tr>
#     <tr>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Capital Expenditures (CAPEX)</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>10</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>12</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>15</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Given</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>CAPEX represents investments in fixed assets. Increasing CAPEX may indicate growth.</td>
#     </tr>
#     <tr>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Free Cash Flow (FCF)</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>10</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>13</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>15</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>OCF - CAPEX</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>FCF is the cash available to the company after covering operating expenses and capital expenditures.  Positive and increasing FCF is highly desirable.</td>
#     </tr>
#      <tr>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Interest Expense</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>5</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>6</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>7</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Given</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Interest expense is the cost of borrowing.</td>
#     </tr>
#     <tr>
#       <td style='padding: 8px; border: 1px solid #ddd;'>Cash Flow Coverage Ratio</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>4x</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>4.17x</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>4.29x</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>OCF / Interest Expense</td>
#       <td style='padding: 8px; border: 1px solid #ddd;'>This ratio measures the company's ability to pay its interest obligations. A higher ratio indicates stronger solvency.</td>
#     </tr>
#   </tbody>
# </table>

# <h3 style='color: #555; font-family: Arial, sans-serif;'>Conclusion</h3>
# <p style='font-family: Arial, sans-serif;'>
#   The company demonstrates a positive trend in cash flow generation, with both OCF and FCF increasing over the three years. The Cash Flow Coverage Ratio is also healthy, indicating a strong ability to service debt. The consistent increase in revenue is a positive indicator for future cash flow.
#   <br>
#   <b style='color:red'>However, the analysis does not delve into the reasons behind the increase in OCF.  A deeper dive into the components of OCF (e.g., changes in working capital) would provide more insight. Additionally, while the Cash Flow Coverage Ratio is increasing, it's important to compare it against industry benchmarks to assess its true strength.</b>
# </p>

# <h3 style='color: #555; font-family: Arial, sans-serif;'>Recommendations</h3>
# <p style='font-family: Arial, sans-serif;'>
#   The company should continue to focus on maintaining and improving its operating efficiency to further enhance OCF.  Monitoring CAPEX is crucial to balance growth investments with free cash flow generation.  Maintaining a strong Cash Flow Coverage Ratio is essential for investor confidence and access to capital.
#   <br>
#   <b style='color:red'>It is recommended to analyze working capital management trends to understand how changes in accounts receivable, inventory, and accounts payable are affecting OCF.  Furthermore, a comparison of the company's CAPEX to industry averages would help determine if the investment levels are appropriate for its growth stage.</b>
# <





#     """
#     query = text("SELECT [cash_flow] FROM prompt_valuation_reports WHERE id = :id")
#     params = {"id": 1}
#     data = fetch_query(query, params)
    
#     if data:
#         default_prompt= data[0]['cash_flow']
#     else:
#         pass

#     # Allow user to customize prompt
#     st.subheader("Customize Report Generation Prompt")
#     user_prompt = st.text_area(
#         "Modify the prompt template below:",
#         default_prompt,
#         height=400,
      
#     )

#     if st.button("Save promt"):
#             #st.session_state.user_prompt = default_prompt
#         id = 1
#         try:
#             update_query = text("""
#                 UPDATE prompt_valuation_reports
#                 SET [cash_flow] = :cash_flow
#                 WHERE id = :id
#             """)
#             params = {
#                 "cash_flow": user_prompt,
#                 "id": id
#             }
#             execute_query(update_query, params)
#             st.success("Data updated successfully!")
#         except Exception as e:
#             st.error(f"Update failed: {e}")
#         st.success("Prompt reset to default!")
#         st.rerun()

#         try:
#             query = text("SELECT [cash_flow] FROM prompt_valuation_reports WHERE id = :id")
#             params = {"id": 1}
#             data = fetch_query(query, params)
#             if data:
#                 st.write("Executive Summary:")
#                 st.write(data[0]["cash_flow"])
#             else:
#                 st.warning("No report found.")
#         except Exception as e:
#             st.error(f"Error fetching data: {e}")

#     # Add controls for report generation
#     col1, col2 = st.columns(2)
#     with col1:
#         data_choice = st.radio(
#             "Choose data to include in report:",
#             ["Cash Flow Data", "Cash Flow Metrics", "Both"],
            
#         )

#     # Generate report button
#     if st.button("Generate Report!!"):
#         with st.spinner("Generating cash flow report..."):
#             try:
#                 # Prepare data based on user choice
#                 if data_choice == "Cash Flow Data":
#                     report_data = cash_flow_data
#                 elif data_choice == "Cash Flow Metrics":
#                     report_data = cash_flow_metrics
#                 else:
#                     report_data = {
#                         "cash_flow_data": cash_flow_data,
#                         "metrics": cash_flow_metrics
#                     }

#                 # Generate report
#                 report = generate_report(user_prompt + " Here is the cash flow data for the years 2023, 2022, and 2021: in {json}", report_data)

#                 CF_REPORT = report

#                 # Display the report
#                 st.subheader("Generated Cash Flow Report")
#                 st.markdown(report, unsafe_allow_html=True)

#                 # Download options
#                 col1, col2 = st.columns(2)
#                 with col1:
#                     st.download_button(
#                         label="Download as HTML",
#                         data=report,
#                         file_name=f"cash_flow_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.html",
#                         mime="text/html",
#                         key="download_html"
#                     )
                
#                 with col2:
#                     st.markdown("""
#                     <style>
#                         .stButton>button {
#                             background-color: #f0f2f6;
#                             color: #000000;
#                         }
#                     </style>
#                     """, unsafe_allow_html=True)
#                     st.button("Export to PDF (Coming Soon)", disabled=True)

#             except Exception as e:
#                 st.error(f"An error occurred while generating the report: {str(e)}")







def main_beyond_FR():
   
    st.title("Beyond Financials Report Generator")

    # fpnl,bs,cf,bfr = st.tabs(["P&L Report", "BS Report","CF Report", "Generated Report"])

   
    st.subheader("Generated Reports")
    st.markdown("""
    <style>
        .stButton>button {
            background-color: #f0f2f6;
            color: #000000;
        }
    </style>
    """, unsafe_allow_html=True)
    user_prompt1 =f""" create a professional report using the following data:"""
    
    if FPNL_REPORT != "" and BS_REPORT != "" and CF_REPORT != "":
        st.markdown("### Generated Reports")
        st.markdown("#### Beyond Financial Report")

        
                    
        
        
        query = text("SELECT [beyondFR] FROM prompt_valuation_reports WHERE id = :id")
        params = {"id": 1}
        data = fetch_query(query, params)
        
        if data:
            user_prompt1 = data[0]['beyondFR']
        else:
            pass
            # st.session_state.user_prompt = default_prompt   
        #st.session_state.user_prompt = default_prompt

    user_prompt1 = st.text_area(
        "Modify the prompt template:",
        user_prompt1,
        height=300,
        
    )

    # Reset prompt button
    if st.button("Reset Prompt to Default"):
        #st.session_state.user_prompt = default_prompt
        id = 1
        try:
            update_query = text("""
                UPDATE prompt_valuation_reports
                SET [beyondFR] = :summary
                WHERE id = :id
            """)
            params = {
                "summary": user_prompt1,
                "id": id
            }
            execute_query(update_query, params)
            st.success("Data updated successfully!")
        except Exception as e:
            st.error(f"Update failed: {e}")
        st.success("Prompt reset to default!")
        st.rerun()

    try:
        query = text("SELECT [beyondFR] FROM prompt_valuation_reports WHERE id = :id")
        params = {"id": 1}
        data = fetch_query(query, params)
        if data:
            st.write("beyondFR:")
            st.write(data[0]["beyondFR"])
        else:
            st.warning("No report found.")
    except Exception as e:
        st.error(f"Error fetching data: {e}")   

    st.markdown("----")    


    if st.button("Beyond finanical Report", key="generate_report_button"):     


        st.markdown("P&NL Report")
        reports_pnl = pnl_reports()
        st.markdown(reports_pnl)

        st.markdown("---")

        st.markdown("balance sheet Report")
        reports_balane = balancesheet()
        st.markdown(reports_balane)

        st.markdown("---")

        st.markdown("Cash flow Report")
        reports_cash = cashflow()
        st.markdown(reports_cash)
        st.markdown("---")



        try:
            client = AzureOpenAI(
            azure_endpoint= os.getenv("ENDPOINT_URL"),
            azure_deployment=os.getenv("DEPLOYMENT_NAME"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2025-01-01-preview"
        )

            messages = [
                {"role": "system", "content": "You are a financial report expert."},
                {"role": "user", "content": user_prompt1 + " Using Profit & Loss report, balance sheet report and cahsh flow reports. Here is all reports porvided :: "
                " Profit & Loss report:-> {reports_pnl}, --------- Balance Sheet report:-> {reports_balane}, --------- Cash Flow report:-> {reports_cash}"}
            ]

            response = client.chat.completions.create(
                    model=os.getenv("DEPLOYMENT_NAME"),  # Use the deployment name instead of model name
                    messages=messages,
                    temperature=0.7
                )

            result = response.choices[0].message.content

            st.subheader("Generated Financial Report")
            st.markdown(result, unsafe_allow_html=True)






        except Exception as e:
            st.error(f"An error occurred while generating the report: {str(e)}")    




        
        
    