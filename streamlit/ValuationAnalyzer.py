import streamlit as st
import json
from datetime import datetime
from huggingface_hub import InferenceClient
import os

class ValuationAnalyzer:
    def generate_valuation_dummy_data(self):
        """Generate dummy data for different valuation methods."""
        data = {
            "asset_based": {
                "total_assets": 15000000,
                "total_liabilities": 10000000,
                "net_asset_value": 5000000,
                "adjusted_book_value": 5500000
            },
            "dcf": {
                "projected_cash_flows": [2500000, 3000000, 3500000],
                "discount_rate": 0.10,
                "terminal_value": 45000000,
                "total_dcf_value": 7380000
            },
            "comparable_company": {
                "ebitda": 1500000,
                "industry_ev_ebitda_multiple": 8,
                "peer_companies": [
                    {"name": "Peer1", "ev_ebitda": 7.8},
                    {"name": "Peer2", "ev_ebitda": 8.2},
                    {"name": "Peer3", "ev_ebitda": 7.9}
                ],
                "calculated_value": 12000000
            },
            "rule_of_thumb": {
                "annual_revenue": 10000000,
                "industry_multiplier": 1.5,
                "calculated_value": 15000000
            },
            "earnings_multiplier": {
                "annual_earnings": 2000000,
                "pe_ratio": 12,
                "calculated_value": 24000000
            },
            "monte_carlo": {
                "simulations": 1000,
                "mean_value": 18500000,
                "min_value": 16000000,
                "max_value": 21000000
            }
        }
        return data

def generate_report(prompt, data):
    """Generate valuation report using HuggingFace model."""
    client = InferenceClient(
        provider="hf-inference",
        api_key=os.getenv("hf_token"),
    )

    # Include timestamp and username in the context
    context = {
        "data": data,
    
    }

    messages = [
        {"role": "system", "content": "You are a valuation expert."},
        {"role": "user", "content": prompt.format(json=json.dumps(context, indent=2))},
    ]

    response = client.chat_completion(
        model=os.getenv("hf_model"),
        messages=messages,
        max_tokens=8000,
        temperature=0.1,
    )

    return response.choices[0].message.content

def main():
    st.title("Dynamic Valuation Report Generator")

    

    # Initialize analyzer and get data
    analyzer = ValuationAnalyzer()
    valuation_data = analyzer.generate_valuation_dummy_data()

    # Display raw data in expandable section
    with st.expander("View Valuation Data"):
        st.json(valuation_data)

    # Prompt Templates
    prompt_templates = """"
       <|begin_of_text|><|start_header_id|>system<|end_header_id|>
       <h3 style='color: #555; font-family: Arial, sans-serif;'>Valuation Report</h3>

<p style='font-family: Arial, sans-serif;'>This report presents a valuation analysis using several methodologies to estimate the fair market value. The results of each method are summarized below.</p>

<table style='width: 100%; border-collapse: collapse; font-family: Arial, sans-serif;'>
  <thead style='background-color: #f2f2f2;'>
    <tr>
      <th style='padding: 8px; border: 1px solid #ddd;'>Valuation Method</th>
      <th style='padding: 8px; border: 1px solid #ddd;'>Value / Range (in millions of USD)</th>
      <th style='padding: 8px; border: 1px solid #ddd;'>Interpretation</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style='padding: 8px; border: 1px solid #ddd;'>Asset-Based Valuation</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Range: $40 - $60</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Reflects the net value of the company's assets, providing a floor value.</td>
    </tr>
    <tr>
      <td style='padding: 8px; border: 1px solid #ddd;'>Discounted Cash Flow (DCF) Valuation</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>$7.38</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Indicates value based on the present value of projected strong future cash flows.</td>
    </tr>
    <tr>
      <td style='padding: 8px; border: 1px solid #ddd;'>Comparable Company Analysis (CCA)</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>$12</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Value is in alignment with industry benchmarks.</td>
    </tr>
    <tr>
      <td style='padding: 8px; border: 1px solid #ddd;'>Rule of Thumb Methods</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Range: $11.5 - $13.5</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Provides a quick estimate, useful for initial assessment.</td>
    </tr>
    <tr>
      <td style='padding: 8px; border: 1px solid #ddd;'>Earnings Multiplier</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Range: $9.6 - $14.4</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Valuation based on a multiple of earnings.</td>
    </tr>
    <tr>
      <td style='padding: 8px; border: 1px solid #ddd;'>Monte Carlo Simulation</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Range: $8 - $13</td>
      <td style='padding: 8px; border: 1px solid #ddd;'>Provides a valuation range with statistical confidence.</td>
    </tr>
  </tbody>
</table>



                                           <|eot_id|><|start_header_id|>user<|end_header_id|>

        
        
                                          
       
                                          

        Generate a detailed HTML report with only ONE tables for all valuation method, showing the Name, Values and your brief interpretative comments. Format the report professionally with clear section headings and consistent styling.
                                           <|eot_id|><|start_header_id|>assistant<|end_header_id|>
        
        """
  
 
    # Advanced Settings
    # with st.expander("Advanced Settings"):
    #     col1, col2 = st.columns(2)
    #     with col1:
    #         include_charts = st.checkbox("Include Visual Charts", value=True)
    #     with col2:
    #         report_format = st.selectbox(
    #             "Report Format",
    #             ["Professional HTML", "Simple HTML", "Detailed HTML"]
    #         )

    # Generate report button
    user_prompt = st.text_area(
                                                "Modify the prompt template below:",
                                                prompt_templates,
                                                height=400,
                                                key="prompt_input"
                                            )
    if st.button("Generate Report", key="generate_button"):
        with st.spinner("Generating valuation report..."):
            try:
                # Format prompt with timestamp and username
                # formatted_prompt = prompt_templates.format(
                  
                #     json=json.dumps(valuation_data, indent=2)
                # )

                # Generate report
                
                report = generate_report(user_prompt + "Here is the JSON data containing the valuation metrics:{json}", valuation_data)

                # Display the report
                st.subheader("Generated Valuation Report")
                st.markdown(report, unsafe_allow_html=True)

                # Download options
                col1, col2 = st.columns(2)
                with col1:
                    # Download HTML
                    st.download_button(
                        label="Download as HTML",
                        data=report,
                        file_name=f"valuation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                        mime="text/html",
                        key="download_html"
                    )
                
                with col2:
                    # Save report history
                    if st.button("Save to History", key="save_history"):
                        st.session_state.setdefault('report_history', [])
                        st.session_state.report_history.append({
                            # 'timestamp': timestamp,
                            # 'template': template_choice,
                            'report': report
                        })
                        st.success("Report saved to history!")

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

    # View Report History
    if st.sidebar.checkbox("View Report History"):
        st.sidebar.markdown("### Report History")
        if 'report_history' in st.session_state and st.session_state.report_history:
            for i, hist in enumerate(st.session_state.report_history):
                with st.sidebar.expander(f"Report {i+1} - {hist['timestamp']}"):
                    st.write(f"Template: {hist['template']}")
                    if st.button(f"Load Report {i+1}", key=f"load_report_{i}"):
                        st.markdown(hist['report'], unsafe_allow_html=True)

if __name__ == "__main__":
    main()