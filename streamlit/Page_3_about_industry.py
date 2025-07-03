import streamlit as st
import json
from huggingface_hub import InferenceClient
from scrapegraph_py import Client # Assuming this is the correct import
import os
from src.db.sql_operation import execute_query, fetch_query
from sqlalchemy import text

def initialize_clients():
    """Initialize API clients"""
    scrapegraph_client = Client(api_key=os.getenv("scrapegraph_api_key"))
    hf_client = InferenceClient(
        provider="hf-inference",
        model=os.getenv("hf_model"),
        token=os.getenv("hf_token"),
    )
    return scrapegraph_client, hf_client

def scrape_website_data(client, website_url, user_prompt):
    """Scrape website data using SmartScraper"""
    # Reverted to original arguments as per user's code and error message
    response = client.smartscraper(
        website_url=website_url,
        user_prompt=user_prompt
    )
    # Assuming the relevant data is in response['result'] as per original code.
    # This needs to be verified if scraping still fails.
    if isinstance(response, dict) and 'result' in response:
        return response['result']
    elif isinstance(response, (dict, list)): # If response itself is the data
        st.warning("Scrapegraph returned data directly, not in 'result' key. Using direct response.")
        return response
    else:
        st.error(f"Unexpected response format from scrapegraph: {type(response)}")
        st.json(response) # Show what was returned
        return {"error": "Failed to parse scrapegraph response", "details": "Unexpected format"}


def generate_report(client, data_company, report_prompt_template):
    """Generate report using HuggingFace model, expecting JSON output."""
    
    data_company_json_str = json.dumps(data_company, indent=2)

    messages = [
        {"role": "system", "content": "You are a financial report expert. Your task is to generate a comprehensive due diligence report. The report should be structured as a single JSON object. Each key in this JSON object will correspond to a section of the report (e.g., 'companyOverview', 'people', 'swotAnalysis'). The value for each key should be a string containing the detailed HTML content for that section, following the formatting guidelines provided in the user prompt. For the 'swotAnalysis' section, the value should be a nested JSON object with keys 'strengths', 'weaknesses', 'opportunities', 'threats', each holding an HTML string."},
        {"role": "user", "content": f"{report_prompt_template}\n\nHere is the scraped data to use:\n{data_company_json_str} "},
    ]

    raw_content = ""
    try:
        response = client.chat_completion(
            messages=messages,
            max_tokens=8192,
            temperature=0.1,
        )
        
        raw_content = response.choices[0].message.content
        
        cleaned_content = raw_content.strip()
        if cleaned_content.startswith("```json"):
            cleaned_content = cleaned_content[7:]
            if cleaned_content.endswith("```"):
                cleaned_content = cleaned_content[:-3]
        elif cleaned_content.startswith("```"):
            cleaned_content = cleaned_content[3:]
            if cleaned_content.endswith("```"):
                cleaned_content = cleaned_content[:-3]
        
        if not cleaned_content.strip():
            st.error("LLM returned empty content after cleaning.")
            st.text_area("LLM Raw Response:", raw_content, height=200)
            return {"error": "LLM returned empty content"}

        return json.loads(cleaned_content.strip())

    except json.JSONDecodeError as e:
        st.error(f"Failed to decode JSON from LLM response: {e}")
        st.text_area("LLM Raw Response (that caused JSON error):", raw_content, height=300)
        return {"error": "JSONDecodeError", "details": str(e), "raw_response": raw_content}
    except Exception as e:
        st.error(f"Error during LLM call or processing: {e}")
        if 'response' in locals() and hasattr(response, '__str__'):
             st.text_area("LLM API Response object (on error):", str(response), height=100)
        st.text_area("LLM Raw Response (if available):", raw_content, height=200)
        return {"error": "LLMProcessingError", "details": str(e)}

def main():
    st.set_page_config(layout="wide")
    st.title("Company Analysis Report Generator")

    # Initialize clients
    try:
        scrapegraph_client, hf_client = initialize_clients()
    except Exception as e:
        st.error(f"Failed to initialize API clients: {e}")
        st.stop()

    website_url = st.text_input("Enter Website URL:", "https://www.atlantacareerinstitute.net/")

    default_scraping_prompt = """
    Extract the following information:
    - Business Description: Detailed overview of the company's history, mission, and vision. (Target 2-3 lines from source)
    - People: Hierarchical structure, key departments (Operations, Sales & Marketing, Finance, R&D), CEO. (Target 7-8 lines from source)
    - Product/Service Offerings: Comprehensive list and description of products or services. (Target 10-12 lines from source)
    - Technology Stack: Overview of the technology and tools used in operations. (Target 10-12 lines from source)
    - Market Position: Analysis of the company's position in the market, including competitors and market share. (Target 10-12 lines from source)
    - Product Pricing Position: Analysis of the company's product pricing, list products and pricing, compare with peers, competitors, market share. (Target 10-12 lines from source)
    - SWOT Analysis: Strengths, Weaknesses, Opportunities, and Threats. (Target 10-12 lines from source for each element)
    """

    st.subheader("Website Scraping Prompt")
    st.session_state.scraping_prompt = st.text_area("Modify the scraping prompt:", default_scraping_prompt, height=200)
    

    if st.button("Save Prompt"):
        try:
            
            query = text("INSERT INTO prompt_valuation_reports ([about_company_webscraping]) VALUES(:prompt)")
                           
            params = {"prompt": st.session_state.scraping_prompt}
            execute_query(query, params)
            st.success("Prompt saved successfully!")

            query = text("SELECT [about_company_webscraping] FROM prompt_valuation_reports WHERE id = :id")
            params = {"id": 1}
            data = fetch_query(query, params)
            
            if data:
                retrieved_scraping_prompt = data[0]['about_company_webscraping']
                st.write(retrieved_scraping_prompt)
            else:
                st.warning("No data found for the given ID.")
        except Exception as e:
            st.error(f"Database error: {e}")
            
            



    json_instruction_preamble = """
IMPORTANT: Based on the scraped data provided as {data_company}, and following all the detailed instructions below for each section, generate a comprehensive due diligence report.
Your entire response MUST be a single, valid JSON object.
The JSON object should have the following top-level keys: "companyOverview", "people", "productServiceOfferings", "technologyStack", "marketPosition", "productPricingPosition", "swotAnalysis".
The value for each key (except "swotAnalysis") must be an HTML string containing the content for that section, formatted as per the detailed examples.
The value for the "swotAnalysis" key must be a nested JSON object with keys: "strengths", "weaknesses", "opportunities", "threats". Each of these nested keys should have an HTML string as its value (e.g., using <ul> and <li> for lists).

Here is the scraped data to use:
{data_company}

Now, here are the detailed instructions for each section's content and HTML structure:
"""
    default_report_prompt_template_body = """
  **Detailed Prompt for Information Extraction (Use the data above as your primary source)**

You are an AI assistant tasked with extracting key information from various sources (documents, databases, web searches, etc.) to populate a due diligence report section. The goal is to provide a comprehensive and insightful overview of [Company Name - to be inferred from data], suitable for an investor or acquirer. Present the results in a structured HTML format, mimicking the clarity and conciseness of an MBB (McKinsey, BCG, Bain) consulting report.

**Extraction Requirements:**

For each of the following sections, gather and synthesize information to provide a detailed and analytical response, adhering to the specified line count. Prioritize factual data, avoid speculation, and cite your sources where possible.

**1. Business Description (map to JSON key "companyOverview"):**

* **Objective:** Provide a detailed overview of the company's history, mission, and vision, demonstrating an understanding of its core business.
* **Target Line Count:** 10-12 lines (expand from scraped data)
* **Example Output Structure (HTML for the value of "companyOverview"):**
    ```html
    <div class="section">
      <h2>1. Business Description</h2>
      <p>
        [Company Name] was founded in [Year] by [Founders] with the aim of... [Founding Story].
        Key milestones include... [Milestone 1], [Milestone 2], and [Milestone 3].
        The company's mission is to... [Mission Statement]... This is achieved through... [Key Activities].
        [Company Name]'s vision is to... [Vision Statement], striving to... [Long-term Goals].
        Core competencies lie in... [Competency 1], [Competency 2], and [Competency 3].
        They serve the... [Target Market] market by providing... [Key Offerings].
        Revenue model is based on... [Revenue Model], with key profitability drivers being... [Profitability Drivers].
        The company fosters a culture of... [Company Culture], emphasizing... [Key Values].
        Looking ahead, [Company Name] aims to... [Future Outlook], capitalizing on... [Growth Opportunities].
      </p>
    </div>
    ```

**2. People (map to JSON key "people"):**

* **Objective:** Describe the company's organizational structure and key personnel, assessing its leadership and talent base.
* **Target Line Count:** 10-12 lines
* **Example Output Structure (HTML for the value of "people"):**
    ```html
    <div class="section">
      <h2>2. People</h2>
      <p>
        [Company Name] employs a... [Structure Type] structure, with... [Number] reporting levels.
        Key departments include Operations (...[Operations Details]), Sales & Marketing (...[Sales & Marketing Details]),
        Finance (...[Finance Details]), and R&D (...[R&D Details]).
        The CEO, ... [CEO Name], has... [CEO Background] and leads a team of... [Key Executives].
        The leadership team demonstrates... [Leadership Strengths] but also faces... [Leadership Challenges].
        The company has a total headcount of... [Headcount], with... [Demographics Highlights].
        Employee turnover is... [Turnover Rate], and the company offers... [Compensation & Benefits].
        Overall, the organizational structure is... [Structure Assessment], and the talent base is... [Talent Assessment].
      </p>
    </div>
    ```

**3. Product/Service Offerings (map to JSON key "productServiceOfferings"):**

* **Objective:** Provide a comprehensive overview of the company's products or services, highlighting their features, target markets, and competitive advantages.
* **Target Line Count:** 10-12 lines
* **Example Output Structure (HTML for the value of "productServiceOfferings"):**
    ```html
    <div class="section">
      <h2>3. Product/Service Offerings</h2>
      <p>
        [Company Name] offers a diverse portfolio of products/services, including... [Product/Service 1 Name] (...[Description]),
        ... [Product/Service 2 Name] (...[Description]), and ... [Product/Service 3 Name] (...[Description]).
        ... [Product/Service 1 Name] is targeted at... [Target Market] and provides... [Value Proposition].
        ... [Product/Service 2 Name] is in the... [Lifecycle Stage] stage and faces... [Competitive Landscape].
        [Company Name]'s innovation strategy focuses on... [Innovation Focus], as evidenced by their... [R&D Investment].
        Overall, the product/service offerings are characterized by... [Overall Assessment].
      </p>
    </div>
    ```

**4. Technology Stack (map to JSON key "technologyStack"):**

* **Objective:** Provide an overview of the technology and tools used by the company, assessing their suitability, efficiency, and potential risks.
* **Target Line Count:** 10-12 lines
* **Example Output Structure (HTML for the value of "technologyStack"):**
    ```html
    <div class="section">
      <h2>4. Technology Stack</h2>
      <p>
        [Company Name]'s technology stack comprises a mix of... [Infrastructure Overview],
        key software applications such as... [ERP System Details], ... [CRM System Details], and
        ... [Product Design Software Details].
        The company's infrastructure relies on... [Network Details] and... [Cloud Details].
        Software development is primarily done using... [Programming Languages] and... [Development Frameworks].
        Security measures include... [Cybersecurity Measures] and compliance with... [Security Standards].
        The overall technology strategy is... [Technology Strategy Assessment], with a focus on... [Technology Focus].
        This stack enables... [Technology Strengths] but also presents... [Technology Weaknesses].
      </p>
    </div>
    ```

**5. Market Position (map to JSON key "marketPosition"):**

* **Objective:** Analyze the company's position within its industry, assessing its competitive landscape, market share, and growth potential.
* **Target Line Count:** 10-12 lines
* **Example Output Structure (HTML for the value of "marketPosition"):**
    ```html
    <div class="section">
      <h2>5. Market Position</h2>
      <p>
        [Company Name] operates in the... [Industry Definition] industry, which is characterized by... [Industry Characteristics].
        The industry is currently... [Industry Growth] and faces trends such as... [Industry Trends].
        Key competitors include... [Competitor 1], ... [Competitor 2], and... [Competitor 3], with [Company Name] holding a market share of... [Market Share].
        [Company Name]'s competitive advantages lie in... [Competitive Advantage 1] and... [Competitive Advantage 2],
        while its disadvantages include... [Competitive Disadvantage 1] and... [Competitive Disadvantage 2].
        Overall, [Company Name]'s market position is... [Market Position Assessment].
      </p>
    </div>
    ```

**6. Product Pricing Position (map to JSON key "productPricingPosition"):**

* **Objective:** Analyze the company's pricing strategy and the positioning of its products in the market, comparing them to competitors.
* **Target Line Count:** 10-12 lines
* **Example Output Structure (HTML for the value of "productPricingPosition"):**
    ```html
    <div class="section">
      <h2>6. Product Pricing Position</h2>
      <p>
        [Company Name] employs a... [Pricing Model] pricing strategy for its product portfolio, which includes... [Product 1 Name] (...[Product 1 Pricing Details]),
        ... [Product 2 Name] (...[Product 2 Pricing Details]), and ... [Product 3 Name] (...[Product 3 Pricing Details]).
        Compared to competitors, [Company Name]'s pricing for... [Product 1 Name] is... [Pricing Comparison for Product 1].
        This pricing strategy impacts [Company Name]'s market share by... [Market Share Impact].
        Overall, [Company Name]'s pricing is perceived by customers as... [Customer Perception], and its effectiveness is... [Pricing Strategy Effectiveness].
      </p>
    </div>
    ```

**7. SWOT Analysis (map to JSON key "swotAnalysis", which should have nested keys "strengths", "weaknesses", "opportunities", "threats", each with HTML string value):**

* **Objective:** Analyze the company's internal strengths and weaknesses, as well as external opportunities and threats, to assess its strategic position.
* **Target Line Count:** 10-12 lines for each of Strength, Weakness, Opportunity, and Threat.
* **Example Output Structure (HTML for the value of e.g., "swotAnalysis.strengths"):**
    ```html
    <h3>Strengths</h3>
    <ul>
      <li>[Strength 1]: [Strength 1 Detailed Description]</li>
      <li>[Strength 2]: [Strength 2 Detailed Description]</li>
      <li>[Strength 3]: [Strength 3 Detailed Description]</li>
      <!-- ... up to 10-12 lines total for strengths text -->
    </ul>
    ```
    (Similar structure for Weaknesses, Opportunities, Threats, each starting with its own `<h3>` tag)
    **And include an overall interrelationship paragraph at the end of the SWOT HTML content:**
    ```html
    <p><strong>SWOT Interrelationships:</strong> The interrelationships between these SWOT elements suggest that... [SWOT Interrelationship Analysis].</p>
    ```

**General HTML Styling Recommendations (applied within the HTML strings):**
* **Font:** Use a clean, professional sans-serif font.
* **Headings:** Use H2 for section titles (e.g., `<div class="section"><h2>1. Business Description</h2>...</div>`), H3 for sub-sections like SWOT components.
* **Spacing:** Use paragraph tags `<p>` and list tags `<ul><li>` appropriately.
* **Emphasis:** Use `<strong>` or `<b>` for bold text sparingly.
"""
    st.subheader("Report Generation Prompt")
    # Displaying only a part of it due to length
    st.text_area(
        "Report generation prompt (Preamble - Read-only):",
        json_instruction_preamble.split("{data_company}")[0] + "{data_company}" + json_instruction_preamble.split("{data_company}")[1].split("Now, here are the detailed instructions")[0] + "...",
        height=150,
        disabled=True
    )
    editable_report_prompt_body = st.text_area(
        "Modify the detailed instructions part of the report prompt here:",
        default_report_prompt_template_body,
        height=300
    )
    
    final_report_prompt_template = json_instruction_preamble + editable_report_prompt_body


    if st.button("Generate Report"):
        if not website_url:
            st.warning("Please enter a website URL.")
            st.stop()

        scraped_data = None # Initialize
        with st.spinner("Scraping website data..."):
            try:
                scraped_data = scrape_website_data(scrapegraph_client, website_url, st.session_state.scraping_prompt)
                if isinstance(scraped_data, dict) and "error" in scraped_data:
                    st.error(f"Failed to scrape data: {scraped_data.get('details', scraped_data['error'])}")
                    if "raw_response" in scraped_data: st.json(scraped_data["raw_response"])
                    st.stop()
                st.success("Website data scraped successfully!")
                
                st.subheader("Scraped Data (for LLM input)")
                st.json(scraped_data)

            except Exception as e:
                st.error(f"An error occurred during scraping: {str(e)}")
                st.exception(e)
                st.stop()
        
        if scraped_data is None: # Should not happen if previous blocks are correct
            st.error("Scraping completed but no data was returned. Cannot proceed.")
            st.stop()

        with st.spinner("Generating report with LLM... This may take some time."):
            try:
                report_data = generate_report(hf_client, scraped_data, final_report_prompt_template)

                if isinstance(report_data, dict) and "error" in report_data:
                    st.error(f"Report generation failed: {report_data.get('details', report_data['error'])}")
                    if "raw_response" in report_data:
                        st.text_area("LLM Raw Response (from error path):", report_data["raw_response"], height=200)
                    st.stop()
                
                if not isinstance(report_data, dict):
                    st.error(f"Report generation returned an unexpected type: {type(report_data)}. Expected a dictionary.")
                    st.text(str(report_data))
                    st.stop()

                st.subheader("Generated Report")
                
                sections_to_display = {
                    "companyOverview": "Company Overview",
                    "people": "People",
                    "productServiceOfferings": "Product/Service Offerings",
                    "technologyStack": "Technology Stack",
                    "marketPosition": "Market Position",
                    "productPricingPosition": "Product Pricing Position",
                }

                for key, title in sections_to_display.items():
                    if key in report_data and report_data[key]:
                        st.markdown(f"### {title}")
                        # The LLM is expected to include the <div class="section"><h2>...</h2>...</div>
                        st.markdown(report_data[key], unsafe_allow_html=True)
                    else:
                        st.warning(f"Section '{title}' (key: {key}) not found or empty in the generated report.")
                
                if "swotAnalysis" in report_data and isinstance(report_data["swotAnalysis"], dict):
                    st.markdown("### SWOT Analysis")
                    swot_data = report_data["swotAnalysis"]
                    
                    # Constructing the full HTML for SWOT based on the nested structure
                    # The prompt asks for each part (strengths, weaknesses etc.) to be HTML
                    # e.g. "strengths": "<h3>Strengths</h3><ul>...</ul>"
                    # We'll wrap it in the main section div/h2 here for display.
                    
                    swot_html_parts = []
                    if "strengths" in swot_data and swot_data["strengths"]:
                        swot_html_parts.append(swot_data["strengths"])
                    else:
                        st.warning(f"SWOT component 'Strengths' not found or empty.")
                    
                    if "weaknesses" in swot_data and swot_data["weaknesses"]:
                        swot_html_parts.append(swot_data["weaknesses"])
                    else:
                        st.warning(f"SWOT component 'Weaknesses' not found or empty.")

                    if "opportunities" in swot_data and swot_data["opportunities"]:
                        swot_html_parts.append(swot_data["opportunities"])
                    else:
                        st.warning(f"SWOT component 'Opportunities' not found or empty.")

                    if "threats" in swot_data and swot_data["threats"]:
                        swot_html_parts.append(swot_data["threats"])
                    else:
                        st.warning(f"SWOT component 'Threats' not found or empty.")
                    
                    # The prompt also asks for an interrelationship paragraph,
                    # which might be part of the 'threats' HTML or a separate key.
                    # For now, assuming it's included by the LLM within one of the components or at the end.
                    # If it's meant to be a separate field like swot_data["interrelationships_html"], handle that.

                    if swot_html_parts:
                        full_swot_section_html = '<div class="section"><h2>7. SWOT Analysis</h2>'
                        full_swot_section_html += "".join(swot_html_parts)
                        full_swot_section_html += '</div>'
                        st.markdown(full_swot_section_html, unsafe_allow_html=True)
                    else:
                        st.warning("No SWOT components were found to display.")
                else:
                    st.warning("SWOT Analysis section not found or not in the expected dictionary format in the generated report.")

                st.info("Report generation complete.")
                st.subheader("Full JSON Report Output (for debugging)")
                st.json(report_data)

            except Exception as e:
                st.error(f"An unexpected error occurred during report generation: {str(e)}")
                st.exception(e)

if __name__ == "__main__":
    main()