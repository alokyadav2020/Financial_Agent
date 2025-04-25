import streamlit as st
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools
from agno.team import Team
from agno.tools.serpapi import SerpApiTools
from agno.tools.reasoning import ReasoningTools
 # Replace with actual tool imports

def market_analysis_report(topic, research_agent_prompt,writer_agent_prompt, team_agent_prompt):
    """
    Generates a market analysis report dynamically based on the user's topic and instructions.
    """
    # Configure the LLM model
    model_config = OpenAIChat(
        id=st.secrets["openai_model"],
        api_key=st.secrets["open_api_key"],
    )

    # Define web agent for market research
    web_agent = Agent(
        name="Web Agent Researcher",
        role="Market Researcher from Internet",
        model=model_config,
        tools=[SerpApiTools(api_key=st.secrets["SerpApi"]),DuckDuckGoTools()],
        instructions=research_agent_prompt,
        markdown=True,  # Enable markdown rendering for the response
    )

    # Define finance report writer agent
    finance_report_writer_agent = Agent(
        name="Finance Report Writer Agent",
        role="Senior Market Analyst",
        model=model_config,
        tools=[YFinanceTools(stock_price=True, analyst_recommendations=True, company_info=True),ReasoningTools(add_instructions=True),],
        instructions=writer_agent_prompt,reasoning=True,markdown=True,
    )

    # Combine agents into a team
    agent_team = Team(
        members=[web_agent, finance_report_writer_agent],
        model=model_config,
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
    research_agent_prompt = """
        **Industry Overview:** Current state and future outlook of the industry. (IBIS)
        **Market Share Analysis:** Pie charts illustrating the company's share relative to competitors.
        **SWOT Analysis:** Matrix highlighting strengths, weaknesses, opportunities, and threats.
        **Customer Analysis:** Breakdown of customer segments.
        **Sales Distribution:** Pareto chart showing revenue contribution by customer segment.
    """
    research_agent_prompt_txt = st.sidebar.text_area(
        "Research Agent Instructions:",
        research_agent_prompt,
        height=400
    )

    writer_agent_prompt = """  
You are a senior market analyst with 15+ years of experience across multiple industries. "
            "Your expertise lies in extracting actionable insights from complex market data and identifying "
            "emerging trends before they become mainstream. You've consulted for Fortune 500 companies "
            "and startups alike, helping them make strategic decisions based on thorough market intelligence. "
            "You specialize in:"
            "\n- Comprehensive industry analysis using both quantitative and qualitative methods"
            "\n- Competitive landscape evaluation and positioning strategies"
            "\n- Market sizing and growth projections with statistical rigor"
            "\n- Consumer behavior patterns and preference shifts"
            "\n- Regulatory impact assessment on market dynamics"
            "\nFor each analysis, you collect and synthesize:"
            "\n- **Industry Overview:** Current state, growth trajectory, and future outlook"
            "\n- **Market Share Analysis:** Detailed breakdown of key players and competitive positioning"
            "\n- **SWOT Analysis:** In-depth evaluation of strengths, weaknesses, opportunities, and threats"
            "\n- **Customer Analysis:** Segmentation by demographics, psychographics, and buying behavior"
            "\n- **Sales Distribution:** Revenue attribution across channels, regions, and customer segments"
            "\n- **Trend Forecasting:** Predictive analysis of where the market is heading in the next 3-5 years

 """
    
    writer_agent_prompt_txt = st.sidebar.text_area(
        "Report Writer Agent Instructions:",
        writer_agent_prompt,
        height=400
    )

    team_agent_prompt = """
    "You are a team of experts working together to create a comprehensive market research report.",
            " \n The Web Agent will gather market data and industry insights, and the Finance Report Writer Agent will interpret the data.
    """
    team_agent_prompt_txt = st.sidebar.text_area(
        "team Agent Instructions:",
        team_agent_prompt,
        height=400
    )

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