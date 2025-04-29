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
    Generate a detailed financial report in HTML format.  
    You are financial expert and having great experience in report generation
    You will be get data in json. Read data carefully and create a professional report.
    Heading should be in h3 tag only, Ex. <h3 style='color: #555; font-family: Arial, sans-serif;'>Comparable Company Analysis (CCA)</h3> 
    You have three tasks:
        1. TO display all data Revenue, COGS, Operating Expenses, Depreciation, Amortization, EBITDA, EV/EBITDA Ratio, Valuation. Display all data in one table.
        2. To write conclusion in 3 to 4 lines only.
        3. Do not provide any recommendation.
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