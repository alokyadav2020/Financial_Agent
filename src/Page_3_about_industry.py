import json
from huggingface_hub import InferenceClient
from scrapegraph_py import Client
from typing import Dict, Any
import streamlit as st


def initialize_clients():
    """Initialize API clients"""
    scrapegraph_client = Client(api_key =st.secrets["scrapegraph_api_key"])
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
        # Format data company as clean JSON string
        data_company_json_str = json.dumps(data_company, indent=2, ensure_ascii=False)
        
        messages = [
            {
                "role": "system", 
                "content": """You are a financial report expert. Generate a concise JSON report with this exact structure:
                {
                    "companyOverview": "brief company overview (max 100 words)",
                    "people": "key personnel and structure (max 100 words)",
                    "productServiceOfferings": "main products/services (max 150 words)",
                    "technologyStack": "key technologies (max 100 words)",
                    "marketPosition": "market position summary (max 100 words)",
                    "productPricingPosition": "pricing overview (max 100 words)",
                    "swotAnalysis": {
                        "strengths": "key strengths (max 50 words)",
                        "weaknesses": "key weaknesses (max 50 words)",
                        "opportunities": "key opportunities (max 50 words)",
                        "threats": "key threats (max 50 words)"
                    }
                }
                Keep all responses brief and ensure valid JSON format."""
            },
            {
                "role": "user", 
                "content": f"Analyze this data and return a JSON report: {data_company_json_str}"
            }
        ]

        # Generate response with increased max_tokens
        response = hf_client.chat_completion(
            messages=messages,
            max_tokens=12000,  # Increased from 8192
            temperature=0.1,
        )
        
        # Clean the response content
        raw_content = response.choices[0].message.content.strip()
        
        # Extract JSON from the response
        json_start = raw_content.find('{')
        json_end = raw_content.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            cleaned_content = raw_content[json_start:json_end]
        else:
            raise ValueError("No valid JSON found in response")

        # Parse and validate JSON
        try:
            report_json = json.loads(cleaned_content)
            required_keys = ["companyOverview", "people", "productServiceOfferings", 
                           "technologyStack", "marketPosition", "productPricingPosition", 
                           "swotAnalysis"]
            
            missing_keys = [key for key in required_keys if key not in report_json]
            if missing_keys:
                raise ValueError(f"Missing required keys in response: {missing_keys}")
                
            return report_json
            
        except json.JSONDecodeError as je:
            print(f"Invalid JSON response: {cleaned_content}")
            raise ValueError(f"Failed to parse response as JSON: {str(je)}")

    except Exception as e:
        print(f"Error during report generation: {str(e)}")
        return {
            "error": "Report generation failed",
            "details": str(e),
            "raw_response": raw_content if 'raw_content' in locals() else None
        }


def format_industry_analysis(report_json):
    """Format the industry analysis report in a clean, structured way"""
    # Get SWOT analysis with fallbacks
    swot = report_json.get('swotAnalysis', {})
    
    formatted_report = f"""
## Industry Analysis Report

### Company Overview
{report_json.get('companyOverview', 'No company overview available')}

### Organization & People
{report_json.get('people', 'No personnel information available')}

### Products & Services
{report_json.get('productServiceOfferings', 'No product/service information available')}

### Technology Infrastructure
{report_json.get('technologyStack', 'No technology information available')}

### Market Position & Competition
{report_json.get('marketPosition', 'No market position information available')}

### Pricing Strategy
{report_json.get('productPricingPosition', 'No pricing information available')}

### SWOT Analysis

#### Strengths
{swot.get('strengths', 'No strengths identified')}

#### Weaknesses
{swot.get('weaknesses', 'No weaknesses identified')}

#### Opportunities
{swot.get('opportunities', 'No opportunities identified')}

#### Threats
{swot.get('threats', 'No threats identified')}
"""
    return formatted_report
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

    # Format the report for better readability
    formatted_report = format_industry_analysis(report_data)
    return formatted_report

if __name__ == "__main__":
    # Example usage
    website_url =  "https://www.atlantacareerinstitute.net/"
   
    
    result = analyze_website(website_url)
    print(result)
    
    # Save the result to a JSON file
    # output_file = "industry_analysis_report.json"
    # with open(output_file, "w", encoding="utf-8") as f:
    #     json.dump(result, f, indent=2, ensure_ascii=False)
    
    # print(f"\nReport has been saved to {output_file}")