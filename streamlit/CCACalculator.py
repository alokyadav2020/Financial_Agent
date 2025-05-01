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

def main():
    st.title("Comparable Company Analysis (CCA) Report Generator")

    # Initialize CCA Calculator
    calculator = CCACalculator()
    cca_data = calculator.CCA_DATA()

    # Display raw calculations
    with st.expander("View CCA Calculations"):
        st.json(json.loads(cca_data))

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

    # Allow user to customize prompt
    st.subheader("Customize Report Generation Prompt")
    user_prompt = st.text_area(
        "Modify the prompt below to customize your report:",
        default_prompt,
        height=400,
        key="prompt_input"
    )

    # Generate report button
    if st.button("Generate Report", key="generate_button"):
        with st.spinner("Generating CCA report..."):
            try:
                # Generate report
                report = generate_report(user_prompt + " Here is the data: in {json} ", cca_data)

                # Display the report
                st.subheader("Generated CCA Report")
                st.markdown(report, unsafe_allow_html=True)

                # Download options
                st.download_button(
                    label="Download Report as HTML",
                    data=report,
                    file_name=f"cca_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                    mime="text/html",
                    key="download_html"
                )

                # Save to history
                if 'report_history' not in st.session_state:
                    st.session_state.report_history = []
                
                st.session_state.report_history.append({
                    # 'timestamp': current_time,
                    'report': report
                })

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

    # View Report History
    # if st.sidebar.checkbox("View Report History"):
    #     st.sidebar.markdown("### Report History")
    #     for i, hist in enumerate(st.session_state.get('report_history', [])):
    #         with st.sidebar.expander(f"Report {i+1} - {hist['timestamp']}"):
    #             if st.button(f"Load Report {i+1}", key=f"load_report_{i}"):
    #                 st.markdown(hist['report'], unsafe_allow_html=True)

if __name__ == "__main__":
    main()