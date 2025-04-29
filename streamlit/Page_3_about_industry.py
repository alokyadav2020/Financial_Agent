

import streamlit as st
import json
from huggingface_hub import InferenceClient
from scrapegraph_py import Client


def initialize_clients():
    """Initialize API clients"""
    scrapegraph_client = Client(api_key=st.secrets["scrapegraph_api_key"])
    hf_client = InferenceClient(
        model=st.secrets["hf_model"],
        provider="hf-inference",
        api_key=st.secrets["hf_token"],
    )
    return scrapegraph_client, hf_client

def scrape_website_data(client, website_url, user_prompt):
    """Scrape website data using SmartScraper"""
    response = client.smartscraper(
        website_url=website_url,
        user_prompt=user_prompt
    )
    return response['result']

def generate_report(client, data_company, report_prompt):
    """Generate report using HuggingFace model"""
    messages = [
        {"role": "system", "content": "You are financial report expert."},
        {"role": "user", "content": report_prompt.format(data_company=data_company)},
    ]

    response_format = {
        "type": "json",
        "value": {
            "properties": {
                "companyOverview": {"type": "string"},
                "marketPosition": {"type": "string"},
            },
            "required": [
                "companyOverview",
                "marketPosition",
            ],
        },
    }

    response = client.chat_completion(
        messages=messages,
        response_format=response_format,
        max_tokens=8000,
        temperature=0.1,
    )

    return json.loads(response.choices[0].message.content)

def main():
    st.title("Company Analysis Report Generator")

    # Initialize clients
    scrapegraph_client, hf_client = initialize_clients()

    # Input section for website URL
    website_url = st.text_input("Enter Website URL:", "https://www.atlantacareerinstitute.net/")

    # Default scraping prompt
    default_scraping_prompt = """
    **Business Description:** Detailed overview of the company's history, mission, and vision.
    **People:** hierarchical structure with departments for Operations, Sales & Marketing, Finance, and R&D, reporting to a CEO.
    **Product/Service Offerings:** Comprehensive list and description of products or services.
    **Technology Stack:** Overview of the technology and tools used in operations.
    **Market Position:** Analysis of the company's position in the market, including competitors and market share.
    """

    # Scraping prompt input
    st.subheader("Website Scraping Prompt")
    scraping_prompt = st.text_area("Modify the scraping prompt:", default_scraping_prompt, height=200)

    # Default report generation prompt
    default_report_prompt = """
    
    **Topics**
    Company Overview: create a report on company overview with using given data.

    Example:
    <p>Acme Manufacturing, founded in 1995, is a manufacturer of industrial components for the automotive and aerospace industries. The company's mission is to provide high-quality, reliable components while adhering to sustainable manufacturing principles.</p>
    <h4 class="details-heading">People:</h4>
    <p>Acme Manufacturing has a hierarchical structure with departments for Operations, Sales & Marketing, Finance, and R&D, reporting to a CEO.</p>
    <h4 class="details-heading">Products / Services offerings:</h4>
    <p>Acme Manufacturing offers a range of precision-engineered components, including:</p>
    <ul class="details-list">
        <li>High-strength fasteners</li>
        <li>Precision gears</li>
        <li>Custom-machined parts.</li>
    </ul>
    <h4 class="details-heading">Technology:</h4>
    <p>Acme Manufacturing, founded in 1995, is a manufacturer of industrial components for the automotive and aerospace industries. The company's mission is to provide high-quality, reliable components while adhering to sustainable manufacturing principles.</p>

    Market Position: create a report on market position with using given data.
    Example:
    <p>Acme Manufacturing establishes a strong revenue growth trajectory & holds a favorable market position.</p>
    <p>By addressing the identified challenges related to profitability and leverage, & by capitalizing on growth opportunities, Acme Manufacturing can enhance its financial performance, reduce risk exposure, and maximize shareholder values.</p>
    """

    # Report generation prompt input
    st.subheader("Report Generation Prompt")
    report_prompt = st.text_area("Modify the report generation prompt:", default_report_prompt, height=300)

    if st.button("Generate Report"):
        with st.spinner("Scraping website data..."):
            try:
                website_data = scrape_website_data(scrapegraph_client, website_url, scraping_prompt)
                st.success("Website data scraped successfully!")
                
                st.subheader("Scraped Data")
                st.json(website_data)

                with st.spinner("Generating report..."):
                    report = generate_report(hf_client, website_data,  "use this data {data_company} to create a report on topics with using given data." + "\n" + report_prompt)
                    
                    st.subheader("Generated Report")
                    
                    st.markdown("### Company Overview")
                    st.markdown(report["companyOverview"], unsafe_allow_html=True)
                    
                    st.markdown("### Market Position")
                    st.markdown(report["marketPosition"], unsafe_allow_html=True)

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()