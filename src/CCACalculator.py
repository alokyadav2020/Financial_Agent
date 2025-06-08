import streamlit as st
import json
from datetime import datetime
from huggingface_hub import InferenceClient

class CCACalculator:
    def calculate_ebitda(self, revenue, cogs, operating_expenses, depreciation, amortization):
        """Calculate EBITDA."""
        return revenue - cogs - operating_expenses + depreciation + amortization

    def calculate_valuation(self, ebitda, ev_ebitda_ratio):
        """Calculate valuation based on EBITDA."""
        return ebitda * ev_ebitda_ratio

    def generate_dummy_ebitda_data(self):
        """Generate dummy data for EBITDA calculation."""
        data = {
            "Revenue": 5e6,
            "COGS": 2e6,
            "Operating Expenses": 1e6,
            "Depreciation": 0.5e6,
            "Amortization": 0.2e6
        }
        return data

    def CCA_DATA(self):
        """Generate complete CCA analysis data."""
        dummy_data = self.generate_dummy_ebitda_data()
        
        ebitda = self.calculate_ebitda(
            dummy_data["Revenue"],
            dummy_data["COGS"],
            dummy_data["Operating Expenses"],
            dummy_data["Depreciation"],
            dummy_data["Amortization"]
        )

        ev_ebitda_ratio = 8
        valuation = self.calculate_valuation(ebitda, ev_ebitda_ratio)

        data = {
            "Dummy Data": dummy_data,
            "EBITDA": ebitda,
            "EV/EBITDA Ratio": ev_ebitda_ratio,
            "Valuation": valuation
        }

        return json.dumps(data, indent=4)

def generate_report(prompt, data):
    """Generate CCA report using HuggingFace model."""
    client = InferenceClient(
        provider="hf-inference",
        api_key=st.secrets["hf_token"],
    )

    messages = [
        {"role": "system", "content": "You are a financial report expert."},
        {"role": "user", "content": prompt.format(json=data)},
    ]

    response = client.chat_completion(
        model=st.secrets["hf_model"],
        messages=messages,
        max_tokens=8000,
        temperature=0.1,
    )

    return response.choices[0].message.content

def cca_report():
    # st.title("Comparable Company Analysis (CCA) Report Generator")

    # Initialize CCA Calculator
    calculator = CCACalculator()
    cca_data = calculator.CCA_DATA()

    # Display raw calculations
    # with st.expander("View CCA Calculations"):
    #     st.json(json.loads(cca_data))

    # Default prompt template
    default_prompt = """
    <|begin_of_text|><|start_header_id|>system<|end_header_id|>
   <h3 style='color: #555; font-family: Arial, sans-serif;'>Comparable Company Analysis (CCA)</h3>

<p style='font-family: Arial, sans-serif;'>This report presents a valuation analysis using the Comparable Company Analysis (CCA) method. CCA estimates a company's value by comparing it to similar publicly traded companies. All values are in millions of USD.</p>

<table style='width: 100%; border-collapse: collapse; font-family: Arial, sans-serif;'>
  <thead style='background-color: #f2f2f2;'>
    <tr>
      <th style='padding: 8px; border: 1px solid #ddd;'>Metric</th>
      <th style='padding: 8px; border: 1px solid #ddd;'>Value</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style='padding: 8px; border: 1px solid #ddd;'>Revenue</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>200</td>
    </tr>
    <tr>
      <td style='padding: 8px; border: 1px solid #ddd;'>COGS</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>120</td>
    </tr>
    <tr>
      <td style='padding: 8px; border: 1px solid #ddd;'>Operating Expenses</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>30</td>
    </tr>
     <tr>
      <td style='padding: 8px; border: 1px solid #ddd;'>Depreciation</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>10</td>
    </tr>
    <tr>
      <td style='padding: 8px; border: 1px solid #ddd;'>Amortization</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>5</td>
    </tr>
    <tr>
      <td style='padding: 8px; border: 1px solid #ddd;'>EBITDA</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>35</td>
    </tr>
    <tr>
      <td style='padding: 8px; border: 1px solid #ddd;'>EV/EBITDA Ratio</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>10x</td>
    </tr>
    <tr>
      <td style='padding: 8px; border: 1px solid #ddd;'>Valuation</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>350</td>
    </tr>
  </tbody>
</table>

<h3 style='color: #555; font-family: Arial, sans-serif;'>Calculations</h3>
    <p style='font-family: Arial, sans-serif;'>
        EBITDA is calculated as Revenue - COGS - Operating Expenses + Depreciation + Amortization.
        <br>
        In this case, EBITDA = 200 - 120 - 30 + 10 + 5 = 65.
        <br>
        The Valuation is then calculated by multiplying the EBITDA by the EV/EBITDA Ratio.
        <br>
        Valuation = EBITDA * EV/EBITDA Ratio
        <br>
        Valuation = 35 * 10 = 350
    </p>

<h3 style='color: #555; font-family: Arial, sans-serif;'>What this means to your Business</h3>
<p style='font-family: Arial, sans-serif;'>
    A CCA valuation of $350 million suggests the company is valued at 10 times its EBITDA, based on comparable companies in the market.  This indicates how the market values similar companies and provides a benchmark for the company's worth.  However, the accuracy of this valuation depends heavily on the selection of truly comparable companies and the stability of the EV/EBITDA multiple.  It's important to consider factors like differences in growth prospects, risk profiles, and accounting practices when interpreting this result. A higher multiple suggests higher growth expectations or lower risk relative to peers.
</p>

<h3 style='color: #555; font-family: Arial, sans-serif;'>Conclusion</h3>
<p style='font-family: Arial, sans-serif;'>
   The Comparable Company Analysis indicates a valuation of $350 million. This is derived by applying an EV/EBITDA multiple of 10x to the company's EBITDA. The selection of comparable companies and the market conditions at the time of the analysis significantly influence the result.
</p>



    <|eot_id|><|start_header_id|>user<|end_header_id|>

   
    Use this data and create a professional report.
    Make sure response must be in HTML format.

    <|eot_id|><|start_header_id|>assistant<|end_header_id|>
    """
    report = generate_report(default_prompt + " Here is the data: in {json} ", cca_data)
    return report
if __name__ == "__main__":
    cca_report()