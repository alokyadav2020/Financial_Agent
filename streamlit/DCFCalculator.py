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

def main():
    st.title("DCF Analysis Report Generator")

    # Display current date/time and user
    # current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    # st.sidebar.markdown("### Session Information")
    # st.sidebar.info(f"Current Date and Time (UTC): {current_time}")
    # st.sidebar.info(f"Current User: alokyadav2020")

    # Initialize DCF Calculator
    calculator = DCFCalculator()
    dcf_data = calculator.dcf_data()

    # Display raw DCF data
    with st.expander("View DCF Calculations"):
        st.json(json.loads(dcf_data))

    # Default prompt template
    default_prompt = """
    <|begin_of_text|><|start_header_id|>system<|end_header_id|>
    Generate a detailed financial report in HTML format.         
    You are financial expert and having great experience in report generation
    You will be get data in json. Read data carefully and create a professional report.
    Heading should be in h3 tag only, Ex. <h3 style='color: #555; font-family: Arial, sans-serif;'>Discounted Cash Flow (DCF) Report</h3> 
    
    You have three tasks:
        1. TO display all data Projected Cash Flows, Discount Rate, Present Values, Total DCF.
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
        with st.spinner("Generating DCF report..."):
            try:
                # Generate report
                report = generate_report(user_prompt + " Here is the data: in {json}", dcf_data)

                # Display the report
                st.subheader("Generated DCF Report")
                st.markdown(report, unsafe_allow_html=True)

                # Download button
                st.download_button(
                    label="Download Report as HTML",
                    data=report,
                    file_name=f"dcf_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
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