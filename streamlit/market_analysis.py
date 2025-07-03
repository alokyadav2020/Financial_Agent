import streamlit as st
from agno.agent import Agent
from agno.models.openai import OpenAIChat
# from agno.models.azure import ai_foundry
from agno.models.azure import AzureOpenAI
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools
from agno.team import Team
from agno.tools.serpapi import SerpApiTools
from agno.tools.reasoning import ReasoningTools
from src.db.sql_operation import execute_query, fetch_query
from sqlalchemy import text
import os
from dotenv import load_dotenv
load_dotenv()
 # Replace with actual tool imports

def market_analysis_report(topic, research_agent_prompt,writer_agent_prompt, team_agent_prompt):
    """
    Generates a market analysis report dynamically based on the user's topic and instructions.
    """
    
    azure_model_config= AzureOpenAI(
        azure_endpoint=os.getenv("ENDPOINT_URL"),
        azure_deployment=os.getenv("DEPLOYMENT_NAME"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2025-01-01-preview"
    )
    # Configure the LLM model
    model_config = OpenAIChat(
        id=os.getenv("openai_model"),
        api_key=os.getenv("open_api_key"),
    )

    # Define web agent for market research
    web_agent = Agent(
        name="Web Agent Researcher",
        role="Market Researcher from Internet",
        model=azure_model_config,
        tools=[SerpApiTools(api_key=os.getenv("SerpApi")),DuckDuckGoTools()],
        instructions=research_agent_prompt,
        markdown=True,  # Enable markdown rendering for the response
    )

    # Define finance report writer agent
    finance_report_writer_agent = Agent(
        name="Finance Report Writer Agent",
        role="Senior Market Analyst",
        model=azure_model_config,
        tools=[YFinanceTools(stock_price=True, analyst_recommendations=True, company_info=True),ReasoningTools(add_instructions=True),],
        instructions=writer_agent_prompt,reasoning=True,markdown=True,
    )

    # Combine agents into a team
    agent_team = Team(
        members=[web_agent, finance_report_writer_agent],
        model=azure_model_config,
        instructions=team_agent_prompt,
        reasoning=True
    )

    try:
        # Run the team to generate the report
        response = agent_team.run(
            f"""{topic} US - Market Research Report (2014-2029)""",
           # stream=True # Enable streaming and markdown rendering
        )
        return response.content  # Return the generated HTML report
    except Exception as e:
        st.error(f"Error occurred: {str(e)}")
        return None

def main():
    st.title("Market Analysis Report Generator")

    # Sidebar for user inputs
    st.sidebar.header("User Inputs")
    topic = st.sidebar.text_input("Enter a topic for the market analysis:", "AI in Healthcare")
    research_agent_prompt_ = """
       **Industry Overview:** Current state and future outlook of the industry. (IBIS)
        **Market Share Analysis:** Pie charts illustrating the company's share relative to competitors.
        **SWOT Analysis:** Matrix highlighting strengths, weaknesses, opportunities, and threats.
        **Customer Analysis:** Breakdown of customer segments.
        **Sales Distribution:** Pareto chart showing revenue contribution by customer segment.


    """

    query = text("SELECT [market_analysis_research_agent] FROM prompt_valuation_reports WHERE id = :id")
    params = {"id": 1}
    data = fetch_query(query, params)
    research_agent_prompt=""
    
    if data:
        retrieved_scraping_prompt = data[0]['market_analysis_research_agent']
        research_agent_prompt = retrieved_scraping_prompt
        
        
    else:
        research_agent_prompt=research_agent_prompt_

    research_agent_prompt_txt = st.text_area(
        "Research Agent Instructions:",
        research_agent_prompt,
        height=400
    )

    if st.button("Save Research Agent Prompt"):
        try:
            # Corrected UPDATE query with WHERE clause
            query = text("UPDATE prompt_valuation_reports SET [market_analysis_research_agent] = :prompt WHERE id = :id")
            params = {
                "prompt": research_agent_prompt_txt,
                "id": 1  # Make sure this matches the record you want to update
            }
            execute_query(query, params)
            st.success("Prompt saved successfully!")

            # Retrieve the saved prompt for confirmation
            query = text("SELECT [market_analysis_research_agent] FROM prompt_valuation_reports WHERE id = :id")
            params = {"id": 1}
            data = fetch_query(query, params)
            
            if data:
                retrieved_scraping_prompt = data[0]['market_analysis_research_agent']
                st.write(retrieved_scraping_prompt)
            else:
                st.warning("No data found for the given ID.")
        except Exception as e:
            st.error(f"Database error: {e}")

    st.markdown("---")
    # st.header("Section 1")         




    writer_agent_prompt = """  
  Objective: To conduct a thorough market analysis for the industrial components sector, with a specific focus on the automotive and aerospace sub-segments relevant to company. The goal is to provide actionable insights into the industry landscape, competitive dynamics, customer behavior, and future trends to inform Acme's strategic decision-making.

Analyst Persona: As a senior market analyst with 15+ years of experience, the AI agent should prioritize data that is insightful, statistically sound, and directly applicable to strategic considerations. The output should reflect a deep understanding of market dynamics and competitive forces.

Topics & Specific Instructions:

1. Industry Overview (IBIS):

Instruction: Identify recent (last 1-2 years) comprehensive industry reports from reputable sources like IBISWorld, McKinsey, BCG, Bain, Deloitte, PwC, and industry-specific associations for the "Industrial Components ," "Automotive Parts ," and "Aerospace Component " sectors. Focus on:
Current State: Market size, key drivers, major trends, and existing challenges.
Growth Trajectory: Historical growth rates and factors influencing them.
Future Outlook: Forecasted growth (CAGR), emerging opportunities, and potential disruptions over the next 3-5 years.
Output Requirements:
Executive Summary: A concise (2-3 sentence) overview of the industry's current state and future outlook relevant to Acme.
Key Statistics: Market size (global and relevant regional breakdowns), historical and projected growth rates, and major driving forces.
Source: Link to the report and the specific section(s) used.
2. Market Share Analysis:

Instruction: Gather data on the competitive landscape within the automotive and aerospace industrial components markets. Identify key players, their estimated market share, and their primary areas of focus (e.g., product specialization, geographic presence). Look for:
Market Share Reports: Publications from market research firms (e.g., Gartner, Forrester, smaller industry-specific analysts).
Company Financial Reports: Annual reports and investor presentations of major competitors (focus on market share discussions).
Industry News and Articles: Reports of significant market share shifts or competitive moves.
Output Requirements:
Key Players: A list of the top 5-10 major competitors in the relevant segments.
Estimated Market Share: Provide approximate market share percentages or ranges for these key players.
Competitive Positioning: Briefly describe each key player's strengths and primary market focus.
Source: Link to the data source.
3. SWOT Analysis:

Instruction: Based on the gathered industry and competitor data, identify potential strengths, weaknesses, opportunities, and threats relevant to a company like company operating in this space. Look for:
Industry Trends as Opportunities/Threats: How macro trends (e.g., electrification in automotive, sustainability in aerospace) could be opportunities or threats.
Competitor Strengths/Weaknesses: Areas where competitors excel or underperform that companycould leverage or needs to address.
Potential Internal Strengths/Weaknesses: While the agent won't know Acme's internal details, it should identify common strengths and weaknesses of similar-sized players in the industry.
Output Requirements:
Concise Bullet Points: List 3-5 key points for each SWOT category (Strengths, Weaknesses, Opportunities, Threats).
Supporting Rationale: Briefly (1 sentence) explain the basis for each point, referencing broader market dynamics or competitor activities.
Source: Link to the data or trend that informed the SWOT point.
4. Customer Analysis:

Instruction: Research the customer landscape for industrial components in the automotive and aerospace sectors. Focus on:
Key Customer Segments: Identify the major types of customers (e.g., OEMs, Tier 1 suppliers, aftermarket).
Buying Behavior: What are the key factors influencing purchasing decisions (e.g., price, quality, reliability, innovation, sustainability)?
Evolving Needs: How are customer needs changing due to industry trends (e.g., demand for lightweighting, electric vehicle components, advanced materials)?
Output Requirements:
Segmentation: Clearly list and describe the primary customer segments.
Key Buying Factors: Identify and prioritize the most important factors influencing customer decisions.
Emerging Needs: Highlight 2-3 key shifts in customer requirements driven by industry trends.
Source: Link to relevant market research or industry analysis.
5. Sales Distribution:

Instruction: Look for information on typical sales channels and revenue contribution in the industrial components sector, particularly for automotive and aerospace. This might be more challenging to find specific data, so focus on general trends and dominant channels. Consider:
Direct Sales vs. Distributors: The prevalence of each channel.
Geographic Sales Patterns: Regional strengths and weaknesses in demand.
Customer Segment Revenue Contribution (General Trends): How different customer types typically contribute to revenue in this sector.
Output Requirements:
Dominant Channels: Identify the primary ways industrial components are sold (direct, distributors, online platforms).
Geographic Considerations: Highlight any significant regional variations in demand.
Qualitative Insights: Provide general insights into revenue contribution by customer segment based on industry structure. Acknowledge if specific data is limited.
Source: Link to any relevant industry reports or articles discussing sales channels.
6. Trend Forecasting:

Instruction: Synthesize the information gathered across all the above topics to identify 3-5 key trends that are likely to significantly impact the industrial components market (specifically automotive and aerospace) over the next 3-5 years. Focus on trends that have strategic implications for companies like Acme. Examples include technological shifts, regulatory changes, or evolving customer demands.
Output Requirements:
Trend Identification: Clearly state each identified trend.
Impact Analysis: Briefly (2-3 sentences) explain the potential impact of each trend on the market and companies like Acme.
Supporting Evidence: Reference data points or insights from previous sections to support the forecast.
Source: Link back to the relevant data.
 

 """
    
    query = text("SELECT [market_analysis_writer_agent] FROM prompt_valuation_reports WHERE id = :id")
    params = {"id": 1}
    data = fetch_query(query, params)
    writer_agent_prompt_=""
    
    if data:
        retrieved_data = data[0]['market_analysis_writer_agent']
        writer_agent_prompt_ = retrieved_data
        
        
    else:
        writer_agent_prompt_=writer_agent_prompt

    
    writer_agent_prompt_txt = st.text_area(
        "Report Writer Agent Instructions:",
        writer_agent_prompt_,
        height=400
    )







    if st.button("Save Writer Agent Prompt"):
        try:
            # Corrected UPDATE query with WHERE clause
            query = text("UPDATE prompt_valuation_reports SET [market_analysis_writer_agent] = :prompt WHERE id = :id")
            params = {
                "prompt": writer_agent_prompt_txt,
                "id": 1  # Make sure this matches the record you want to update
            }
            execute_query(query, params)
            st.success("Prompt saved successfully!")

            # Retrieve the saved prompt for confirmation
            query = text("SELECT [market_analysis_writer_agent] FROM prompt_valuation_reports WHERE id = :id")
            params = {"id": 1}
            data = fetch_query(query, params)
            
            if data:
                retrieved_scraping_prompt = data[0]['market_analysis_writer_agent']
                st.write(retrieved_scraping_prompt)
            else:
                st.warning("No data found for the given ID.")
        except Exception as e:
            st.error(f"Database error: {e}")


    st.markdown("---")
    # st.header("Section 2")        

    team_agent_prompt = """
   Collaborative Market Research Team Prompt:
"Our team of expert AI agents is tasked with generating a comprehensive and insightful market research report focused on the industrial components sector, with a specific emphasis on the automotive and aerospace sub-segments relevant to company. Our collaborative approach leverages the specialized skills of two key agents:"
1. Web Agent (Market Data & Insights Gathering):
Role: To efficiently and effectively gather relevant market data and industry insights based on clearly defined instructions.
Guiding Principles (MBB Style - for data relevance and conciseness): Prioritize reputable sources (industry reports, financial filings, analyst briefings), focus on data with strategic implications, and extract concise, fact-based information directly relevant to the research topics.
Output Requirements: For each data point or insight gathered, provide:
A concise summary (1-2 sentences) of the key finding.
The specific data point(s) supporting the finding (e.g., statistics, quotes, trends).
A direct link to the original source.
(Optional) A preliminary assessment of the data's relevance to company's strategic context.
Specific Search Areas (aligned with previous instructions):
Industry Overview (IBIS, McKinsey, etc.)
Market Share Analysis (Competitor data, market reports)
SWOT Analysis (Industry trends, competitor analysis)
Customer Analysis (Buying behavior, segmentation)
Sales Distribution (Channel trends, geographic patterns)
Trend Forecasting (Emerging technologies, regulatory changes, demand shifts)
2. Finance Report Writer Agent (Data Interpretation & Synthesis):
Role: To interpret the market data and industry insights gathered by the Web Agent, synthesize them into a cohesive market research report, and draw actionable conclusions relevant to company's financial performance and strategic decisions.
Analytical Focus (Senior Market Analyst Persona - 15+ years experience): Apply expertise in extracting actionable insights from complex data, identifying emerging trends, evaluating competitive landscapes, understanding customer behavior, and assessing regulatory impacts.
Report Structure (MBB Style): Organize the findings into a clear and concise report with the following sections:
Executive Summary: Key findings and overall market assessment.
Industry Overview: Current state, growth drivers, and future outlook.
Market Share Analysis: Key players and competitive dynamics.
SWOT Analysis: Strengths, weaknesses, opportunities, and threats for company(inferred from market data).
Customer Analysis: Key segments and their evolving needs.
Sales Distribution Trends: Relevant channel and geographic considerations.
Trend Forecasting: Key market trends and their potential impact on Acme.
Implications for company: Actionable insights and strategic considerations based on the market analysis.
Output Requirements:
A well-structured market research report adhering to MBB principles of conciseness, analytical depth, and actionability.
Clear and concise language, avoiding jargon where possible or explaining it briefly.
Data-driven conclusions, directly supported by the information gathered by the Web Agent.
Actionable insights and strategic implications specifically tailored to company's context (as understood from previous turns).
Workflow:
The Web Agent will be provided with specific search instructions for each section of the market research report.
The Web Agent will gather relevant data and insights, adhering to the output requirements.
The Finance Report Writer Agent will receive the compiled data from the Web Agent.
The Finance Report Writer Agent will interpret, synthesize, and structure the information into the comprehensive market research report, focusing on actionable insights for company.

    """


    query = text("SELECT [market_analysis_team_agents] FROM prompt_valuation_reports WHERE id = :id")
    params = {"id": 1}
    data = fetch_query(query, params)
    team_agent_prompt_=""
    
    if data:
        retrieved_data = data[0]['market_analysis_team_agents']
        team_agent_prompt_ = retrieved_data
        
        
    else:
        team_agent_prompt_=team_agent_prompt



    team_agent_prompt_txt = st.text_area(
        "team Agent Instructions:",
        team_agent_prompt_,
        height=400
    )



    if st.button("Save Team Agent Prompt"):
        try:
            # Corrected UPDATE query with WHERE clause
            query = text("UPDATE prompt_valuation_reports SET [market_analysis_team_agents] = :prompt WHERE id = :id")
            params = {
                "prompt": team_agent_prompt_txt,
                "id": 1  # Make sure this matches the record you want to update
            }
            execute_query(query, params)
            st.success("Prompt saved successfully!")

            # Retrieve the saved prompt for confirmation
            query = text("SELECT [market_analysis_team_agents] FROM prompt_valuation_reports WHERE id = :id")
            params = {"id": 1}
            data = fetch_query(query, params)
            
            if data:
                retrieved_scraping_prompt = data[0]['market_analysis_team_agents']
                st.write(retrieved_scraping_prompt)
            else:
                st.warning("No data found for the given ID.")
        except Exception as e:
            st.error(f"Database error: {e}")
    st.markdown("---")
    # Button to generate the report
    if st.button("Generate Report"):
        with st.spinner("Generating market analysis report..."):
            report = market_analysis_report(topic, research_agent_prompt_txt,writer_agent_prompt_txt,team_agent_prompt_txt)
            if report:
                st.success("Report generated successfully!")
                st.subheader("Market Analysis Report")
                st.markdown(report)  # Render HTML report

                # Option to download the report
                # st.download_button(
                #     label="Download Report as HTML",
                #     data=report,
                #     file_name="market_analysis_report.html",
                #     mime="text/html"
                # )

if __name__ == "__main__":
    main()