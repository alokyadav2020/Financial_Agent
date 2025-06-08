import json
from huggingface_hub import InferenceClient
from scrapegraph_py import Client
from typing import Dict, Any
import streamlit as st


def initialize_clients():
    """Initialize API clients"""
    scrapegraph_client = Client(api_key=st.secrets["scrapegraph_api_key"])
    hf_client = InferenceClient(
        provider="hf-inference",
        model=st.secrets["hf_model"],
        token=st.secrets["hf_token"],
    )
    return scrapegraph_client, hf_client

def scrape_website_data(client,website_url: str, user_prompt: str) -> Dict[str, Any]:
    """Scrape website data using SmartScraper"""
    try:
        response = client.smartscraper(
            website_url=website_url,
            user_prompt=user_prompt
        )
        
        if isinstance(response, dict) and 'result' in response:
            return response['result']
        elif isinstance(response, (dict, list)):
            print("Warning: Scrapegraph returned data directly, not in 'result' key.")
            return response
        else:
            print(f"Error: Unexpected response format from scrapegraph: {type(response)}")
            return {"error": "Failed to parse scrapegraph response", "details": "Unexpected format"}
    except Exception as e:
        print(f"Error during scraping: {str(e)}")
        return {"error": "Scraping failed", "details": str(e)}

def generate_report(hf_client, data_company: Dict[str, Any], report_prompt_template: str) -> Dict[str, Any]:
    """Generate report using HuggingFace model"""
    try:
        data_company_json_str = json.dumps(data_company, indent=2)
        messages = [
            {"role": "system", "content": "You are a financial report expert. Your task is to generate a comprehensive due diligence report. The report should be structured as a single JSON object with sections for company overview, people, SWOT analysis, etc."},
            {"role": "user", "content": report_prompt_template.format(data_company=data_company_json_str)},
        ]

        response = hf_client.chat_completion(
            messages=messages,
            max_tokens=8192,
            temperature=0.1,
        )
        
        raw_content = response.choices[0].message.content
        cleaned_content = raw_content.strip()
        
        # Clean JSON content if wrapped in code blocks
        if cleaned_content.startswith("```json"):
            cleaned_content = cleaned_content[7:]
        elif cleaned_content.startswith("```"):
            cleaned_content = cleaned_content[3:]
        if cleaned_content.endswith("```"):
            cleaned_content = cleaned_content[:-3]

        if not cleaned_content.strip():
            return {"error": "LLM returned empty content"}

        return json.loads(cleaned_content.strip())

    except json.JSONDecodeError as e:
        print(f"JSON decode error: {str(e)}")
        return {"error": "JSONDecodeError", "details": str(e)}
    except Exception as e:
        print(f"Error during report generation: {str(e)}")
        return {"error": "Report generation failed", "details": str(e)}

def analyze_website(website_url: str) -> Dict[str, Any]:
    """Main function to analyze a website and generate a report"""
  
    scrapegraph_client, hf_client = initialize_clients()
    
    
    # Default scraping prompt
    scraping_prompt = """
    Extract the following information:
    - Business Description: Detailed overview of the company's history, mission, and vision. (Target 2-3 lines from source)
    - People: Hierarchical structure, key departments (Operations, Sales & Marketing, Finance, R&D), CEO. (Target 7-8 lines from source)
    - Product/Service Offerings: Comprehensive list and description of products or services. (Target 10-12 lines from source)
    - Technology Stack: Overview of the technology and tools used in operations. (Target 10-12 lines from source)
    - Market Position: Analysis of the company's position in the market, including competitors and market share. (Target 10-12 lines from source)
    - Product Pricing Position: Analysis of the company's product pricing, list products and pricing, compare with peers, competitors, market share. (Target 10-12 lines from source)
    - SWOT Analysis: Strengths, Weaknesses, Opportunities, and Threats. (Target 10-12 lines from source for each element)
    """

    # Scrape website data
    print("Scraping website data...")
    scraped_data = scrape_website_data(scrapegraph_client,website_url, scraping_prompt)
    if isinstance(scraped_data, dict) and "error" in scraped_data:
        print(f"Scraping failed: {scraped_data.get('details', scraped_data['error'])}")
        return scraped_data

    # Generate report
    print("Generating report...")
    report_prompt_template = """
    Based on the scraped data provided as {data_company}, generate a comprehensive due diligence report.
    Format the response as a JSON object with the following structure:
    {
        "companyOverview": "HTML formatted company overview",
        "people": "HTML formatted people section",
        "productServiceOfferings": "HTML formatted products/services section",
        "technologyStack": "HTML formatted technology section",
        "marketPosition": "HTML formatted market position section",
        "productPricingPosition": "HTML formatted pricing section",
        "swotAnalysis": {
            "strengths": "HTML formatted strengths",
            "weaknesses": "HTML formatted weaknesses",
            "opportunities": "HTML formatted opportunities",
            "threats": "HTML formatted threats"
        }
    }
    """
    
    report_data = generate_report(hf_client,scraped_data, report_prompt_template)
    if isinstance(report_data, dict) and "error" in report_data:
        print(f"Report generation failed: {report_data.get('details', report_data['error'])}")
        return report_data

    print("Analysis completed successfully!")
    return report_data

if __name__ == "__main__":
    # Example usage
    website_url =  "https://www.atlantacareerinstitute.net/"
   
    
    result = analyze_website(website_url)
    
    # Save the result to a JSON file
    # output_file = "industry_analysis_report.json"
    # with open(output_file, "w", encoding="utf-8") as f:
    #     json.dump(result, f, indent=2, ensure_ascii=False)
    
    # print(f"\nReport has been saved to {output_file}")