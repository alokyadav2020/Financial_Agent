import streamlit as st
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools
from agno.team import Team
from agno.tools.serpapi import SerpApiTools
from agno.tools.reasoning import ReasoningTools
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the API key
openai_api_key = os.getenv(st.secrets["open_api_key"])

# Use it in your OpenAI client
import openai
openai.api_key = openai_api_key


class MarketAnalyzer:
    def __init__(self):
        try:
            # Configure the LLM model
            self.model_config = OpenAIChat(
                id=st.secrets["openai_model"],
                api_key=st.secrets["open_api_key"],
                
            )

           
        except KeyError as e:
            raise Exception(f"Missing required API key in secrets: {e}")

    def _get_research_agent_prompt(self):
        return """
        Generate a comprehensive market research report including:
        
        Industry Overview:
        - Current state and future outlook of the industry
        - Market size and growth projections
        - Key industry trends and drivers
        
        Market Share Analysis: 
        - Detailed breakdown of market share by company
        - Key players and their positioning
        - Competitive landscape analysis
        
        SWOT Analysis:
        - In-depth analysis of Strengths, Weaknesses, Opportunities, and Threats
        - Market-specific factors affecting each SWOT element
        - Strategic implications for industry players
        
        Customer Analysis:
        - Detailed segmentation of customer base
        - Customer preferences and buying behavior
        - Key market demographics
        
        Sales Distribution:
        - Channel performance analysis
        - Geographic distribution of sales
        - Revenue contribution by segment

        Please ensure all data is fact-based and properly sourced.
        """

    def _get_writer_agent_prompt(self):
        return """
        As a Senior Market Analyst, analyze the research data and provide:
        
        1. Executive Summary
        - Key findings and market highlights
        - Critical trends and opportunities
        - Strategic recommendations
        
        2. Detailed Analysis
        - Market size and growth potential
        - Competitive dynamics
        - Customer insights
        - Distribution strategies
        
        3. Financial Implications
        - Market value assessment
        - Growth projections
        - Investment opportunities
        - Risk analysis
        
        Format the report professionally with clear sections and data-driven insights.
        """

    def _get_team_agent_prompt(self):
        return """
        Work together to create a comprehensive market report:
        
        1. Research Agent:
        - Gather accurate market data
        - Find relevant statistics and trends
        - Identify key market players
        
        2. Writer Agent:
        - Analyze gathered data
        - Create structured insights
        - Develop strategic recommendations
        
        Ensure all insights are:
        - Data-driven
        - Properly sourced
        - Strategically relevant
        - Actionable
        
        Deliver a cohesive report that combines thorough research with expert analysis.
        """

    def analyze_market(self, topic):
        """
        Generates a market analysis report for the given topic.
        
        Args:
            topic (str): The market or industry to analyze
            
        Returns:
            str: The generated market analysis report
        """
        if not topic:
            raise ValueError("Topic cannot be empty")

        try:
            # Define web agent for market research
            web_agent = Agent(
                name="Web Agent Researcher",
                role="Market Researcher from Internet",
                model=self.model_config,
                tools=[
                    SerpApiTools(api_key=st.secrets["SerpApi"]),
                    DuckDuckGoTools()
                ],
                instructions=self._get_research_agent_prompt(),
                markdown=True
            )

            # Define finance report writer agent
            finance_report_writer_agent = Agent(
                name="Finance Report Writer Agent",
                role="Senior Market Analyst",
                model=self.model_config,
                tools=[
                    YFinanceTools(
                        stock_price=True,
                        analyst_recommendations=True,
                        company_info=True
                    ),
                    ReasoningTools(add_instructions=True)
                ],
                instructions=self._get_writer_agent_prompt(),
                reasoning=True,
                markdown=True
            )

            # Combine agents into a team
            agent_team = Team(
                members=[web_agent, finance_report_writer_agent],
                model=self.model_config,
                instructions=self._get_team_agent_prompt(),
                reasoning=True
            )

            # Run the team to generate the report
            response = agent_team.run(
                f"{topic} US - Market Research Report (2014-2029)"
            )
            
            return response.content

        except Exception as e:
            raise Exception(f"Error generating market analysis: {str(e)}")

def generate_market_analysis(topic):
    """
    Wrapper function to generate market analysis report.
    
    Args:
        topic (str): The market or industry to analyze
        
    Returns:
        str: The generated market analysis report or error message
    """
    try:
        analyzer = MarketAnalyzer()
        return analyzer.analyze_market(topic)
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    # Example usage
    topic = "manufacturing industry"
    report = generate_market_analysis(topic)
    print(report)

