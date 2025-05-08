

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
        {"role": "user", "content": report_prompt},
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
   
    **Business Description:** Detailed overview of the company's history, mission, and vision. Add 2-3 line
    **People:** hierarchical structure with departments for Operations, Sales & Marketing, Finance, and R&D, reporting to a CEO. Add 7-8 lines
    **Product/Service Offerings:** Comprehensive list and description of products or services. Add 10-12 lines
    **Technology Stack:** Overview of the technology and tools used in operations. Add 10-12 lines
    **Market Position:** Analysis of the company's position in the market, including competitors and market share. Add 10-12 lines
 **Product Pricing Position:** Analysis of the company's product pricing , list the product and its pricing and compare with its peers  in the market, including competitors and market share. Add 10-12 lines
**SWOT Analysis:** Analysis of the company's position in the market, including competitors and market share. Add 10-12 lines for each : strength , weakness , opportunity and Threats

    """

    # Scraping prompt input
    st.subheader("Website Scraping Prompt")
    scraping_prompt = st.text_area("Modify the scraping prompt:", default_scraping_prompt, height=200)

    # Default report generation prompt
    default_report_prompt = """
  **Detailed Prompt for Information Extraction**

You are an AI assistant tasked with extracting key information from various sources (documents, databases, web searches, etc.) to populate a due diligence report section. The goal is to provide a comprehensive and insightful overview of Acme Manufacturing, suitable for an investor or acquirer. Present the results in a structured HTML format, mimicking the clarity and conciseness of an MBB (McKinsey, BCG, Bain) consulting report.

**Extraction Requirements:**

For each of the following sections, gather and synthesize information to provide a detailed and analytical response, adhering to the specified line count. Prioritize factual data, avoid speculation, and cite your sources where possible.

**1. Business Description:**

* **Objective:** Provide a detailed overview of Acme Manufacturing's history, mission, and vision, demonstrating an understanding of its core business.
* **Key Principles:**
    * Concise and informative writing style.
    * Focus on key milestones, strategic decisions, and overall trajectory.
    * Highlight any unique aspects of the business model or competitive advantages.
* **Target Line Count:** 2-3 lines (this is too short, expand per instructions below)
* **Detailed Extraction Instructions (Expand to 10-12 lines):**
    * **History:**
        * Year founded, founding story (if relevant), key founders.
        * Significant milestones (e.g., major funding rounds, product launches, expansions).
        * Changes in ownership or leadership (if relevant).
    * **Mission:**
        * Explicitly stated mission statement (if available).
        * Inferred mission based on company actions and communications.
        * How the mission differentiates the company.
    * **Vision:**
        * Explicitly stated vision statement (if available).
        * Long-term goals and aspirations for the company.
        * How the vision shapes the company's strategy.
    * **Overall Business:**
        * Core competencies and competitive advantages.
        * Key products or services and their target markets.
        * Revenue model and key drivers of profitability.
        * Company culture and values (if discernible).
        * Future outlook and growth potential.
    * **Example Output Structure (HTML):**
        ```html
        <div class="section">
          <h2>1. Business Description</h2>
          <p>
            Acme Manufacturing was founded in 1995 by [Founders] with the aim of... [Founding Story].
            Key milestones include... [Milestone 1], ... [Milestone 2], and... [Milestone 3].
            The company's mission is to... [Mission Statement]... This is achieved through... [Key Activities].
            Acme's vision is to... [Vision Statement], striving to... [Long-term Goals].
            The company's core competencies lie in... [Competency 1], ... [Competency 2], and... [Competency 3].
            They serve the... [Target Market] market by providing... [Key Offerings].
            Acme's revenue model is based on... [Revenue Model], with key profitability drivers being... [Profitability Drivers].
            The company fosters a culture of... [Company Culture], emphasizing... [Key Values].
            Looking ahead, Acme aims to... [Future Outlook], capitalizing on... [Growth Opportunities].
          </p>
        </div>
        ```

**2. People:**

* **Objective:** Describe Acme Manufacturing's organizational structure and key personnel, assessing its leadership and talent base.
* **Key Principles:**
    * Clarity and accuracy in depicting the hierarchy.
    * Focus on leadership experience, skills, and potential.
    * Evaluation of employee demographics and talent management practices.
* **Target Line Count:** 7-8 lines (Expand further)
* **Detailed Extraction Instructions (Expand to 10-12 lines):**
    * **Overall Structure:**
        * Type of structure (e.g., hierarchical, matrix, flat).
        * Number of reporting levels and span of control.
        * Degree of centralization vs. decentralization.
        * How the structure supports or hinders efficiency.
    * **Key Departments:**
        * Operations: Size, key roles, skill levels, any outsourcing.
        * Sales & Marketing: Structure, key personnel, sales strategy.
        * Finance: Size, expertise, reporting capabilities.
        * R&D: Size, focus areas, innovation track record.
    * **Leadership:**
        * CEO: Background, experience, leadership style.
        * Other key executives: Roles, expertise, tenure.
        * Strength and depth of the leadership team.
        * Succession planning.
    * **Employees:**
        * Total headcount, demographics (if available and relevant).
        * Skill levels, training programs, employee morale.
        * Turnover rates, retention strategies.
        * Compensation and benefits.
    * **Example Output Structure (HTML):**
        ```html
        <div class="section">
          <h2>2. People</h2>
          <p>
            Acme Manufacturing employs a... [Structure Type] structure, with... [Number] reporting levels.
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

**3. Product/Service Offerings:**

* **Objective:** Provide a comprehensive overview of Acme Manufacturing's products or services, highlighting their features, target markets, and competitive advantages.
* **Key Principles:**
    * Detailed descriptions of each offering.
    * Focus on value proposition and customer benefits.
    * Analysis of product lifecycle and innovation.
* **Target Line Count:** 10-12 lines
* **Detailed Extraction Instructions (Expand to 10-12 lines):**
    * **Product/Service List:**
        * List each distinct product or service offering.
        * Provide clear and concise names.
    * **Detailed Descriptions:**
        * For each offering, describe its key features and functionalities.
        * Explain how it works and what problem it solves for customers.
        * Highlight any unique selling propositions (USPs) or competitive advantages.
    * **Target Markets:**
        * Identify the specific customer segments or industries served by each offering.
        * Describe the size and growth potential of each target market.
    * **Product Lifecycle:**
        * Assess the current stage of each offering in its lifecycle (e.g., introduction, growth, maturity, decline).
        * Evaluate the company's strategy for managing the lifecycle (e.g., new product development, product enhancements).
    * **Innovation:**
        * Describe the company's track record of innovation.
        * Evaluate its investment in R&D and new product development.
        * Assess the potential for future innovation to drive growth.
    * **Example Output Structure (HTML):**
        ```html
        <div class="section">
          <h2>3. Product/Service Offerings</h2>
          <p>
            Acme Manufacturing offers a diverse portfolio of products, including... [Product 1 Name] (...[Product 1 Description]),
            ... [Product 2 Name] (...[Product 2 Description]), and ... [Product 3 Name] (...[Product 3 Description]).
            ... [Product 1 Name] is targeted at... [Product 1 Target Market] and provides... [Product 1 Value Proposition].
            ... [Product 2 Name] is in the... [Product 2 Lifecycle Stage] stage and faces... [Product 2 Competitive Landscape].
            Acme's innovation strategy focuses on... [Innovation Focus], as evidenced by their... [R&D Investment].
            Overall, the product/service offerings are characterized by... [Overall Assessment].
          </p>
        </div>
        ```

**4. Technology Stack:**

* **Objective:** Provide an overview of the technology and tools used by Acme Manufacturing, assessing their suitability, efficiency, and potential risks.
* **Key Principles:**
    * Categorization of technology components.
    * Evaluation of technology's impact on business operations.
    * Identification of potential technology-related risks and opportunities.
* **Target Line Count:** 10-12 lines
* **Detailed Extraction Instructions (Expand to 10-12 lines):**
    * **Infrastructure:**
        * Hardware: Servers, workstations, network equipment (age, capacity, reliability).
        * Operating Systems: Versions, support status, security vulnerabilities.
        * Network: Architecture, bandwidth, security.
        * Cloud Infrastructure: Providers (AWS, Azure, GCP), services used, cost optimization.
    * **Software Applications:**
        * ERP Systems: Vendor, version, customizations, integration.
        * CRM Systems: Vendor, usage, data quality.
        * Product Design: CAD/CAM software, version, licensing.
        * Communication Tools: Email, collaboration platforms.
        * Data Management: Databases, data warehouses, business intelligence tools.
    * **Development Tools & Languages:**
        * Programming languages used for custom applications.
        * Development frameworks and methodologies.
        * Version control systems.
    * **Security:**
        * Cybersecurity measures: Firewalls, intrusion detection, antivirus.
        * Data security policies and procedures.
        * Compliance with relevant security standards.
    * **Technology Strategy:**
        * Overall IT strategy and alignment with business goals.
        * Investment in new technologies (cloud, AI, etc.).
        * Technology roadmap and future plans.
    * **Example Output Structure (HTML):**
        ```html
        <div class="section">
          <h2>4. Technology Stack</h2>
          <p>
            Acme Manufacturing's technology stack comprises a mix of... [Infrastructure Overview],
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

**5. Market Position:**

* **Objective:** Analyze Acme Manufacturing's position within its industry, assessing its competitive landscape, market share, and growth potential.
* **Key Principles:**
    * Industry definition and segmentation.
    * Identification of key competitors.
    * Analysis of market share and trends.
    * Assessment of competitive advantages and disadvantages.
* **Target Line Count:** 10-12 lines
* **Detailed Extraction Instructions (Expand to 10-12 lines):**
    * **Industry Definition:**
        * Clearly define the industry in which Acme Manufacturing operates (e.g., "Industrial Components Manufacturing," "Precision Engineered Parts").
        * Identify any sub-segments or niches within the industry.
    * **Industry Overview:**
        * Describe the current size and growth rate of the industry.
        * Identify key trends, challenges, and opportunities in the industry.
        * Assess the industry's attractiveness (e.g., profitability, barriers to entry).
    * **Competitive Landscape:**
        * Identify the major competitors in the industry.
        * Analyze their market share, product offerings, pricing strategies, and marketing efforts.
        * Assess the level of competition and the intensity of rivalry.
    * **Market Share Analysis:**
        * Determine Acme Manufacturing's market share (if available).
        * Analyze trends in market share (e.g., increasing, decreasing, stable).
        * Compare Acme's market share to that of its competitors.
    * **Competitive Advantages:**
        * Identify Acme Manufacturing's key competitive advantages (e.g., brand reputation, technology, customer relationships).
        * Assess the sustainability and defensibility of these advantages.
    * **Competitive Disadvantages:**
        * Identify Acme Manufacturing's key competitive disadvantages (e.g., limited resources, outdated technology, narrow product line).
        * Assess the impact of these disadvantages on the company's performance.
    * **Example Output Structure (HTML):**
        ```html
        <div class="section">
          <h2>5. Market Position</h2>
          <p>
            Acme Manufacturing operates in the... [Industry Definition] industry, which is characterized by... [Industry Characteristics].
            The industry is currently... [Industry Growth] and faces trends such as... [Industry Trends].
            Key competitors include... [Competitor 1], ... [Competitor 2], and... [Competitor 3], with Acme holding a market share of... [Market Share].
            Acme's competitive advantages lie in... [Competitive Advantage 1] and... [Competitive Advantage 2],
            while its disadvantages include... [Competitive Disadvantage 1] and... [Competitive Disadvantage 2].
            Overall, Acme's market position is... [Market Position Assessment].
          </p>
        </div>
        ```

**6. Product Pricing Position:**

* **Objective:** Analyze Acme Manufacturing's pricing strategy and the positioning of its products in the market, comparing them to competitors.
* **Key Principles:**
    * Detailed breakdown of product pricing.
    * Comparison with competitor pricing.
    * Assessment of pricing strategy effectiveness.
* **Target Line Count:** 10-12 lines
* **Detailed Extraction Instructions (Expand to 10-12 lines):**
    * **Product Pricing List:**
        * List each distinct product or service offering.
        * Provide clear and concise names.
    * **Pricing Details:**
        * For each offering, specify the pricing model (e.g., cost-plus, value-based, competitive).
        * Provide price ranges or specific prices for different product variations or order volumes.
        * Identify any discounts, promotions, or pricing tiers.
    * **Competitive Pricing Comparison:**
        * Compare Acme Manufacturing's pricing to that of its main competitors.
        * Analyze price differences and explain the potential reasons (e.g., quality, features, brand).
    * **Pricing Strategy Analysis:**
        * Assess the overall effectiveness of Acme's pricing strategy.
        * Evaluate its impact on profitability, market share, and customer perception.
        * Identify any potential pricing risks or opportunities.
    * **Market Share Impact:**
        * Analyze how pricing influences Acme's market share and competitiveness.
        * Determine if pricing is a driver or a barrier to growth.
    * **Customer Perception:**
        * Assess how customers perceive Acme's pricing (e.g., fair, expensive, value-oriented).
        * Evaluate the impact of pricing on customer satisfaction and loyalty.
    * **Example Output Structure (HTML):**
        ```html
        <div class="section">
          <h2>6. Product Pricing Position</h2>
          <p>
            Acme Manufacturing employs a... [Pricing Model] pricing strategy for its product portfolio, which includes... [Product 1 Name] (...[Product 1 Pricing Details]),
            ... [Product 2 Name] (...[Product 2 Pricing Details]), and ... [Product 3 Name] (...[Product 3 Pricing Details]).
            Compared to competitors, Acme's pricing for... [Product 1 Name] is... [Pricing Comparison for Product 1].
            This pricing strategy impacts Acme's market share by... [Market Share Impact].
            Overall, Acme's pricing is perceived by customers as... [Customer Perception], and its effectiveness is... [Pricing Strategy Effectiveness].
          </p>
        </div>
        ```

**7. SWOT Analysis:**

* **Objective:** Analyze Acme Manufacturing's internal strengths and weaknesses, as well as external opportunities and threats, to assess its strategic position.
* **Key Principles:**
    * Clear and concise identification of each SWOT element.
    * Prioritization of the most significant factors.
    * Analysis of the interrelationships between SWOT elements.
* **Target Line Count:** 10-12 lines for each of Strength, Weakness, Opportunity, and Threat.
* **Detailed Extraction Instructions (Expand to 10-12 lines for each):**
    * **Strengths:**
        * Identify Acme Manufacturing's key internal strengths (e.g., strong brand, efficient operations, skilled workforce).
        * Provide specific examples and evidence to support each strength.
        * Assess the sustainability and competitive advantage of each strength.
    * **Weaknesses:**
        * Identify Acme Manufacturing's key internal weaknesses (e.g., high debt, outdated technology, limited product diversification).
        * Provide specific examples and evidence to support each weakness.
        * Assess the impact of each weakness on the company's performance and future prospects.
    * **Opportunities:**
        * Identify key external opportunities that Acme Manufacturing could capitalize on (e.g., new market segments, technological advancements, changing customer needs).
        * Assess the likelihood and attractiveness of each opportunity.
        * Evaluate Acme's ability to pursue each opportunity.
    * **Threats:**
        * Identify key external threats that could negatively impact Acme Manufacturing (e.g., economic downturn, increased competition, changing regulations).
        * Assess the likelihood and potential impact of each threat.
        * Evaluate Acme's vulnerability to each threat.
    * **SWOT Interrelationships:**
        * Analyze how Acme Manufacturing's strengths can be used to capitalize on opportunities or mitigate threats.
        * Analyze how Acme Manufacturing's weaknesses could hinder its ability to pursue opportunities or make it more vulnerable to threats.
    * **Example Output Structure (HTML):**
        ```html
        <div class="section">
          <h2>7. SWOT Analysis</h2>
          <h3>Strengths</h3>
          <ul>
            <li>[Strength 1]: [Strength 1 Detailed Description]</li>
            <li>[Strength 2]: [Strength 2 Detailed Description]</li>
            <li>[Strength 3]: [Strength 3 Detailed Description]</li>
            <li>... (Up to 10-12 lines)</li>
          </ul>
          <h3>Weaknesses</h3>
          <ul>
            <li>[Weakness 1]: [Weakness 1 Detailed Description]</li>
            <li>[Weakness 2]: [Weakness 2 Detailed Description]</li>
            <li>[Weakness 3]: [Weakness 3 Detailed Description]</li>
            <li>... (Up to 10-12 lines)</li>
          </ul>
          <h3>Opportunities</h3>
          <ul>
            <li>[Opportunity 1]: [Opportunity 1 Detailed Description]</li>
            <li>[Opportunity 2]: [Opportunity 2 Detailed Description]</li>
            <li>[Opportunity 3]: [Opportunity 3 Detailed Description]</li>
            <li>... (Up to 10-12 lines)</li>
          </ul>
          <h3>Threats</h3>
          <ul>
            <li>[Threat 1]: [Threat 1 Detailed Description]</li>
            <li>[Threat 2]: [Threat 2 Detailed Description]</li>
            <li>[Threat 3]: [Threat 3 Detailed Description]</li>
            <li>... (Up to 10-12 lines)</li>
          </ul>
          <p>
            The interrelationships between these SWOT elements suggest that... [SWOT Interrelationship Analysis].
          </p>
        </div>
        ```

**General HTML Styling Recommendations :**

* **Font:** Use a clean, professional sans-serif font (e.g., Arial, Helvetica, Calibri, Open Sans) for the main text.
* **Headings:** Use clear and concise headings (H1, H2, H3) to structure the content.
* **Spacing:** Use ample white space to improve readability.
* **Tables and Lists:** Use tables for data presentation and lists (UL, OL) for bullet points.
* **Emphasis:** Use bold text sparingly for key terms or phrases.
* **Colors:** Use a limited and professional color palette (e.g., shades of gray, blue, and white). Avoid bright or distracting colors.
* **Charts:** If you include charts (which would be excellent), use clear and simple chart types (bar charts, line charts, pie charts) with concise labels.



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