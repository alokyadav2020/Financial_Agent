import streamlit as st
import json
from datetime import datetime
from huggingface_hub import InferenceClient

class DCFCalculator:
    def present_value(self, future_cash_flow, discount_rate, year):
        """Calculate the present value of a single future cash flow."""
        return future_cash_flow / ((1 + discount_rate) ** year)

    def total_dcf(self, projected_cash_flows, discount_rate):
        """Calculate the total discounted cash flow (DCF)."""
        total_value = 0
        for year, cash_flow in enumerate(projected_cash_flows, start=1):
            total_value += self.present_value(cash_flow, discount_rate, year)
        return total_value

    def dcf_data(self):
        """Generate DCF calculations and return JSON data."""
        projected_cash_flows = [2.5e6, 3e6, 3.5e6]
        discount_rate = 0.10

        pv_year_1 = self.present_value(projected_cash_flows[0], discount_rate, 1)
        pv_year_2 = self.present_value(projected_cash_flows[1], discount_rate, 2)
        pv_year_3 = self.present_value(projected_cash_flows[2], discount_rate, 3)

        total_dcf_value = self.total_dcf(projected_cash_flows, discount_rate)

        data = {
            "Projected Cash Flows": projected_cash_flows,
            "Discount Rate": discount_rate,
            "Present Values": {
                "Year 1": pv_year_1,
                "Year 2": pv_year_2,
                "Year 3": pv_year_3
            },
            "Total DCF": total_dcf_value
        }

        return json.dumps(data, indent=4)

def generate_report(prompt, data):
    """Generate DCF report using HuggingFace model."""
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

def dcf_analysis_report():
    # st.title("DCF Analysis Report Generator")

    # Display current date/time and user
    # current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    # st.sidebar.markdown("### Session Information")
    # st.sidebar.info(f"Current Date and Time (UTC): {current_time}")
    # st.sidebar.info(f"Current User: alokyadav2020")

    # Initialize DCF Calculator
    calculator = DCFCalculator()
    dcf_data = calculator.dcf_data()

    # Display raw DCF data
    # with st.expander("View DCF Calculations"):
    #     st.json(json.loads(dcf_data))

    # Default prompt template
    default_prompt = """
    <|begin_of_text|><|start_header_id|>system<|end_header_id|>
    
<h3 style='color: #555; font-family: Arial, sans-serif;'>Discounted Cash Flow (DCF) Report</h3>

<p style='font-family: Arial, sans-serif;'>This report presents a valuation analysis using the Discounted Cash Flow (DCF) method. The DCF method estimates the intrinsic value of an investment based on its projected future cash flows, discounted to their present value.  All values are in millions of USD.</p>

<table style='width: 100%; border-collapse: collapse; font-family: Arial, sans-serif;'>
  <thead style='background-color: #f2f2f2;'>
    <tr>
      <th style='padding: 8px; border: 1px solid #ddd;'>Year</th>
      <th style='padding: 8px; border: 1px solid #ddd;'>Projected Cash Flows</th>
      <th style='padding: 8px; border: 1px solid #ddd;'>Discount Rate</th>
      <th style='padding: 8px; border: 1px solid #ddd;'>Present Value</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style='padding: 8px; border: 1px solid #ddd;'>1</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>25</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>10%</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>22.73</td>
    </tr>
    <tr>
      <td style='padding: 8px; border: 1px solid #ddd;'>2</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>30</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>10%</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>24.79</td>
    </tr>
    <tr>
      <td style='padding: 8px; border: 1px solid #ddd;'>3</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>35</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>10%</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>26.31</td>
    </tr>
    <tr>
      <td style='padding: 8px; border: 1px solid #ddd;'>4</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>40</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>10%</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>27.32</td>
    </tr>
     <tr>
      <td style='padding: 8px; border: 1px solid #ddd;'>5</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>45</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>10%</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>27.84</td>
    </tr>
    <tr>
      <td style='padding: 8px; border: 1px solid #ddd;'>Total DCF Value</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>129.0</td>
      <td style='padding: 8px; border: 1px solid #ddd;'></td>
      <td style='padding: 8px; border: 1px solid #ddd;'></td>
    </tr>
  </tbody>
</table>

<h3 style='color: #555; font-family: Arial, sans-serif;'>Calculations</h3>
<p style='font-family: Arial, sans-serif;'>
    The present value (PV) of each year's projected cash flow is calculated using the following formula:
    <br>
    PV = Cash Flow / (1 + Discount Rate)^Year
    <br>
    For example, the present value for Year 1 is calculated as: 25 / (1 + 0.10)^1 = 22.73.  The Total DCF Value is the sum of the present values of all projected cash flows over the forecast period.
</p>

<h3 style='color: #555; font-family: Arial, sans-serif;'>What this means to your Business</h3>
<p style='font-family: Arial, sans-serif;'>
    A DCF valuation of $129.0 million suggests the intrinsic value of the business, based on its projected cash-generating ability, is  $129.0 million. This indicates the business is expected to generate significant cash flow in the future.  However, this valuation is highly sensitive to the projected cash flows and the discount rate, both of which involve assumptions about future performance and market conditions.  A higher discount rate would result in a lower valuation, and vice-versa.  It's crucial to regularly review and update the assumptions to ensure the valuation remains relevant.
</p>

<h3 style='color: #555; font-family: Arial, sans-serif;'>Conclusion</h3>
<p style='font-family: Arial, sans-serif;'>
  The Discounted Cash Flow analysis indicates a total value of $129.0 million. This valuation is derived from the present value of projected future cash flows, discounted at a rate of 10%. The DCF method is sensitive to both the projected cash flows and the discount rate, and these should be carefully considered.
</p>


    <|eot_id|><|start_header_id|>user<|end_header_id|>

   
    Use this data and create a professional report.
    Make sure response must be in HTML format.

    <|eot_id|><|start_header_id|>assistant<|end_header_id|>
    """
    report = generate_report(default_prompt + " Here is the data: in {json}", dcf_data)
    return report
if __name__ == "__main__":
    dcf_analysis_report()