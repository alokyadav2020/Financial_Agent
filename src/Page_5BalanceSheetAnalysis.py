import streamlit as st
import random
from datetime import datetime
from huggingface_hub import InferenceClient
import json
from src.db.sql_operation import execute_query, fetch_query
from sqlalchemy import text
from openai import AzureOpenAI 
from dotenv import load_dotenv
import os
load_dotenv()

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
    # client = InferenceClient(
    #     provider="hf-inference",
    #     api_key=st.secrets["hf_token"],
    # )
    client = AzureOpenAI(
            azure_endpoint= os.getenv("ENDPOINT_URL"),
            azure_deployment=os.getenv("DEPLOYMENT_NAME"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2025-01-01-preview"
        )

    messages = [
        {"role": "system", "content": "You are a financial report expert."},
        {"role": "user", "content": prompt + f"Using data \n\n {data}"},
    ]

    response = client.chat.completions.create(
        model=os.getenv("DEPLOYMENT_NAME"),
        messages=messages,
        max_tokens=8000,
        temperature=0.1,
    )

    return response.choices[0].message.content

def balancesheet():
    
    generator = FinancialReportGenerator()

    # Generate dummy data for three years
    years = [2023, 2022, 2021]
    financial_data = generator.generate_dummy_financial_data(years)
    
    # Calculate financial ratios
    financial_ratios = generator.calculate_financial_ratios(financial_data)

  

    # Default prompt template
    default_prompt = """
    <|begin_of_text|><|start_header_id|>system<|end_header_id|>
   Objective:

To analyze a company's balance sheet data over three consecutive years and generate a comprehensive report that assesses its financial position, liquidity, and leverage. The report should be structured in HTML format and include detailed explanations and interpretations of key metrics, similar to an MBB consultant's analysis.

Agent Persona:

You are a Senior Financial Analyst at a top-tier consulting firm (e.g., McKinsey, BCG, Bain). You possess a deep understanding of balance sheet analysis and are skilled at communicating complex financial information in a clear, concise, and actionable manner.

Input Data:

The agent will receive balance sheet data for three consecutive years, including:

Total Assets (in millions of USD)

Total Liabilities (in millions of USD)

Shareholder's Equity (in millions of USD)

Current Assets (in millions of USD)

Current Liabilities (in millions of USD)

Tasks:

Data Presentation:

Present the data in a well-formatted HTML table with the following columns:

Metric

Year 1

Year 2

Year 3

Calculation

Interpretation

Ensure the table is styled for professional presentation (e.g., using CSS for borders, spacing, and alignment).

Metric Calculation:

Calculate the following key financial ratios for each year:

Current Ratio: Current Assets / Current Liabilities

Debt-to-Equity Ratio: Total Liabilities / Shareholder's Equity

Metric Interpretation:

Provide a clear and concise interpretation of each metric, explaining what it reveals about the company's financial health. The interpretation should be in 1-2 sentences.

Report Generation:

Generate an HTML report with the following sections:

Heading: "Balance Sheet Report"

Introduction: A brief overview of the purpose of the report and the metrics being analyzed.

Table: The formatted table with data, calculations, and interpretations.

Conclusion: A 3-4 line summary of the overall findings, highlighting key trends and the company's financial position.

Recommendations: 3-4 actionable recommendations for the company, based on the balance sheet analysis.

Additional Explanation of Calculations (MBB Style): Provide detailed explanations of the key balance sheet metrics and their significance, written in a style that an MBB consultant would use.
—-----------------------------------







<h3 style='color: #555; font-family: Arial, sans-serif;'>Balance Sheet Report</h3>

<p style='font-family: Arial, sans-serif;'>This report provides an analysis of key balance sheet metrics for three consecutive years.  We will examine Total Assets, Total Liabilities, Shareholder's Equity, the Current Ratio, and the Debt-to-Equity Ratio to assess the company's financial position, liquidity, and leverage. All values are in millions of USD.</p>

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
      <td style='padding: 8px; border: 1px solid #ddd;'>Total Assets</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>100</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>110</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>120</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Given</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Represents the company's total resources. Increasing assets can indicate growth.</td>
    </tr>
    <tr>
      <td style='padding: 8px; border: 1px solid #ddd;'>Total Liabilities</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>40</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>45</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>50</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Given</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Represents the company's total obligations to creditors.</td>
    </tr>
    <tr>
      <td style='padding: 8px; border: 1px solid #ddd;'>Shareholder's Equity</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>60</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>65</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>70</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Total Assets - Total Liabilities</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Represents the owners' stake in the company.</td>
    </tr>
    <tr>
      <td style='padding: 8px; border: 1px solid #ddd;'>Current Assets</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>50</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>55</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>60</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Given</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Assets that can be converted to cash within one year.</td>
    </tr>
    <tr>
      <td style='padding: 8px; border: 1px solid #ddd;'>Current Liabilities</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>25</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>27</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>28</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Given</td>
       <td style='padding: 8px; border: 1px solid #ddd;'>Obligations due within one year.</td>
    </tr>
    <tr>
      <td style='padding: 8px; border: 1px solid #ddd;'>Current Ratio</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>2x</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>2.04x</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>2.14x</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Current Assets / Current Liabilities</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Measures short-term liquidity; ability to pay short-term obligations. A higher ratio is generally better.</td>
    </tr>
    <tr>
      <td style='padding: 8px; border: 1px solid #ddd;'>Debt-to-Equity Ratio</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>0.67x</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>0.69x</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>0.71x</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Total Liabilities / Shareholder's Equity</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Measures financial leverage; proportion of financing from debt vs. equity. A lower ratio is generally better.</td>
    </tr>
  </tbody>
</table>

<h3 style='color: #555; font-family: Arial, sans-serif;'>Conclusion</h3>
<p style='font-family: Arial, sans-serif;'>
  The company's total assets, liabilities, and shareholder's equity are all showing a steady increase over the three years, indicating growth.  The Current Ratio is consistently above 2, demonstrating strong short-term liquidity.  The Debt-to-Equity Ratio is also relatively stable, suggesting a balanced capital structure.
</p>

<h3 style='color: #555; font-family: Arial, sans-serif;'>Recommendations</h3>
<p style='font-family: Arial, sans-serif;'>
  The company should maintain its strong liquidity position as indicated by the Current Ratio. While the Debt-to-Equity Ratio is reasonable, it should be monitored to ensure it doesn't increase significantly, which could increase financial risk.  Continued asset growth should be supported by profitable operations.
</p>




    <|eot_id|><|start_header_id|>user<|end_header_id|>

    
    Use this data and create a professional report.
    Make sure response must be in HTML format.

    <|eot_id|><|start_header_id|>assistant<|end_header_id|>
    """
    report_data = {
                        "financial_data": financial_data,
                        "ratios": financial_ratios
                    }
    
    prompt_template = ""
    
    query = text("SELECT [balance_sheet] FROM prompt_valuation_reports WHERE id = :id")
    params = {"id": 1}
    data = fetch_query(query, params)
    
    if data:
        default_prompt= data[0]['balance_sheet']
        prompt_template = default_prompt
    else:
       prompt_template = default_prompt
    


    report = generate_report(prompt_template + "Here is the balance sheet for the years 2023, 2022, and 2021: in {json}", report_data)


    return report


if __name__ == "__main__":
    balancesheet()