
import streamlit as st
from pypdf import PdfReader
from pydantic import BaseModel, Field
from typing import List,Dict
from agno.agent import Agent
from agno.models.azure import AzureOpenAI
from agno.team.team import Team
from dotenv import load_dotenv
import os
load_dotenv()

class CompanyInfo(BaseModel):
    name: str = Field(..., description="Company's legal name")
    industry: str = Field(..., description="Primary industry")
    sectors: List[str] = Field(..., description="List of business sectors")
    year_founded: int = Field(..., description="Year the company was founded")
    employees: int = Field(..., description="Number of employees as of the latest year")
    website: str = Field(..., description="Company website")
    ein: str = Field(..., description="Employer Identification Number (EIN) for tax purposes")

class YearlyFinancialData(BaseModel):
    year: str = Field(..., description="Year as string e.g. '2023'")
    revenue: int = Field(..., description="Total net sales and revenue in millions")
    cogs: int = Field(..., description="Cost of sales in millions")
    operating_expenses: int = Field(..., description="Selling, general and administrative expenses in millions")
    ebitda: int = Field(..., description="EBITDA in millions (operating income + depreciation and amortization)")

class FinancialMetrics(BaseModel):
    yearly_data: List[YearlyFinancialData] = Field(..., description="List of financial data for the last 3 years")

class Debt(BaseModel):
    long_term: int = Field(..., description="Long-term debt and finance lease obligations in millions")
    short_term: int = Field(..., description="Short-term debt and current portion of long-term debt in millions")

class YearlyBalanceSheet(BaseModel):
    year: str = Field(..., description="Year as string e.g. '2023'")
    current_assets: int = Field(..., description="Current assets in millions")
    non_current_assets: int = Field(..., description="Non-current assets in millions")
    total_assets: int = Field(..., description="Total assets in millions")

    current_liabilities: int = Field(..., description="Current liabilities in millions")
    non_current_liabilities: int = Field(..., description="Non-current liabilities in millions")
    total_liabilities: int = Field(..., description="Total liabilities in millions")
    shareholders_equity: int = Field(..., description="Total shareholders equity attributable to stockholders in millions")
    equity: int = Field(..., description="Total equity attributable to stockholders in millions")
    debt: Debt
    cash: int = Field(..., description="Cash and cash equivalents in millions")

class BalanceSheet(BaseModel):
    yearly_data: List[YearlyBalanceSheet] = Field(..., description="List of balance sheet data for the last 3 years where available")

class YearlyKPIs(BaseModel):
    year: str = Field(..., description="Year as string e.g. '2023'")
    gross_margin: float = Field(..., description="Gross margin percentage")
    operating_margin: float = Field(..., description="Operating margin percentage")
    debt_to_equity: float = Field(..., description="Debt to equity ratio")
    current_ratio: float = Field(..., description="Current ratio")
    revenue_growth: float = Field(..., description="Revenue growth percentage from previous year; 0 for the earliest year")
    market_share: float = Field(..., description="Market share percentage if available; otherwise 0.0")

class KPIs(BaseModel):
    yearly_data: List[YearlyKPIs] = Field(..., description="List of KPIs for the last 3 years")

class YearlyCashFlow(BaseModel):
    year: str = Field(..., description="Year as string e.g. '2023'")
    net_income: float = Field(..., description="Net Income")
    adjustments_for_non_cash_items: float = Field(..., description="Adjustments for Non-Cash Items")
    changes_in_working_capital: float = Field(..., description="Changes in Working Capital")
    cash_from_operating_activities: float = Field(..., description="Cash from Operating Activities")
    cash_from_investing_activities: float = Field(..., description="Cash from Investing Activities")
    cash_from_financing_activities: float = Field(..., description="Cash from Financing Activities")
    net_cash_flow: float = Field(..., description="Net Cash Flow")
    beginning_cash_balance: float = Field(..., description="Beginning Cash Balance")
    ending_cash_balance: float = Field(..., description="Ending Cash Balance")

class CashFlowData(BaseModel):
    # yearly_data: Dict[str, YearlyCashFlow] = Field(..., description="Cash flow data keyed by year as string e.g. '2023'") 
    yearly_data: List[YearlyCashFlow] = Field(..., description="Cash flow data keyed by year as string e.g. '2023'")    

class ValuationRange(BaseModel):
    low: int = Field(..., description="Low estimate of company valuation in millions")
    high: int = Field(..., description="High estimate of company valuation in millions")

class Valuation(BaseModel):
    enterprise_value: int = Field(..., description="Enterprise value in millions")
    ev_ebitda_multiple: float = Field(..., description="EV/EBITDA multiple")
    valuation_range: ValuationRange

class IndustryBenchmarks(BaseModel):
    avg_gross_margin: float = Field(..., description="Average gross margin percentage for automotive industry")
    avg_operating_margin: float = Field(..., description="Average operating margin percentage for automotive industry")
    avg_debt_to_equity: float = Field(..., description="Average debt to equity ratio for automotive industry")
    avg_revenue_growth: float = Field(..., description="Average revenue growth percentage for automotive industry")

class RiskFactors(BaseModel):
    high_customer_concentration: bool = Field(..., description="True if high customer concentration risk")
    geographic_concentration: bool = Field(..., description="True if geographic concentration risk")
    supply_chain_dependency: bool = Field(..., description="True if supply chain dependency risk")
    debt_level: str = Field(..., description="Debt level: 'low', 'medium', or 'high'")
    market_cyclicality: str = Field(..., description="Market cyclicality: 'low', 'medium', or 'high'")

class CompanyData(BaseModel):
    company_info: CompanyInfo
    financial_metrics: FinancialMetrics
    balance_sheet: BalanceSheet
    kpis: KPIs
    valuation: Valuation
    industry_benchmarks: IndustryBenchmarks
    risk_factors: RiskFactors
    cash_flow : CashFlowData


# def model():
#     return AzureOpenAI(
#         azure_endpoint=os.getenv("ENDPOINT_URL"),
#         azure_deployment=os.getenv("DEPLOYMENT_NAME"),
#         api_key=os.getenv("AZURE_OPENAI_API_KEY"),
#         api_version=os.getenv("api_version"),  # Use the latest version
#         max_tokens=8192,  # Increased from 4096
#         temperature=0.1,
#     )


def validate_environment():
    """Validate all required environment variables exist"""
    required_vars = {
        'ENDPOINT_URL': os.getenv('ENDPOINT_URL'),
        'DEPLOYMENT_NAME': os.getenv('DEPLOYMENT_NAME'),
        'AZURE_OPENAI_API_KEY': os.getenv('AZURE_OPENAI_API_KEY'),
        'api_version': os.getenv('api_version')
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    
    if missing_vars:
        raise ValueError(f"Missing environment variables: {missing_vars}")
    
    return required_vars

def create_model():
    """Create Azure OpenAI model with validation"""
    try:
        # Validate environment variables first
        env_vars = validate_environment()
        
        # Ensure endpoint URL has correct format
        endpoint_url = env_vars['ENDPOINT_URL']
        if not endpoint_url.startswith('https://'):
            endpoint_url = f"https://{endpoint_url}"
        if not endpoint_url.endswith('/'):
            endpoint_url = f"{endpoint_url}/"
            
        print(f"Connecting to: {endpoint_url}")
        print(f"Using deployment: {env_vars['DEPLOYMENT_NAME']}")
        print(f"API version: {env_vars['api_version']}")
        
        return AzureOpenAI(
            azure_endpoint=endpoint_url,
            azure_deployment=env_vars['DEPLOYMENT_NAME'],
            api_key=env_vars['AZURE_OPENAI_API_KEY'],
            api_version=env_vars['api_version'],
            max_tokens=4000,  # Reduced to avoid rate limits
            temperature=0.1,
        )
    except Exception as e:
        raise Exception(f"Failed to create Azure OpenAI model: {str(e)}")

def company_info_extractor(prompt):
    model_instance = create_model()
   
    agent = Agent(
        model=model_instance,
        description="Extract and analyze company profile information",
        response_model=CompanyInfo,
        use_json_mode=True,
        instructions="""
        Analyze the financial statements and extract key company information:
        1. Identify the complete legal company name (e.g., General Motors Company)
        2. Determine the primary industry classification (e.g., Automotive)
        3. List all business sectors the company operates in (e.g., electric vehicles, safety services)
        4. Find or infer the year the company was founded; if not in document, use known value 1908 for GM
        5. Find the number of employees; if not in document, set to 0 or known approximate
        6. Find the company website (e.g., https://www.gm.com)
        7. Locate the Employer Identification Number (EIN) for tax purposes; if not in document, set to 'unknown'
        
        Ensure information is sourced from the document where possible; use reasonable defaults if missing.
        """
    )
    r1= agent.run(prompt)
    return r1.content.model_dump_json(indent=2)


def financial_metrics_extractor(prompt):
    
    model = create_model()
    agent = Agent(
        model=model,
        description="Extract yearly financial metrics from documents",
        response_model=FinancialMetrics,
        use_json_mode=True,
        instructions="""
        Analyze the financial statements and extract yearly financial data for the last 3 years (2021, 2022, 2023 where available):
        - For each year, include the year and:
          - Revenue: total net sales and revenue in millions
          - COGS: cost of sales in millions; if not explicit, calculate or estimate
          - Operating expenses: selling, general and administrative expenses in millions
          - EBITDA: operating income + depreciation and amortization; extract or calculate
        Provide as a list of YearlyFinancialData objects.
        
        Clean the noisy OCR text to find accurate numbers. If data for a year is missing, omit that entry. Ensure all information is sourced from the document.
        """
    )
    r2= agent.run(prompt)
    return r2.content.model_dump_json(indent=2)

    

def balance_sheet_extractor(prompt):
    model = create_model()
    agent = Agent(
        model=model,
        description="Extract balance sheet data from documents",
        response_model=BalanceSheet,
        use_json_mode=True,
        instructions="""
        Analyze the financial statements and extract balance sheet data for the last 3 years (2021, 2022, 2023 where available):
        - For each year, include the year and:
          - Current assets
          - Non-current assets
          - Total assets
          - Current liabilities
          - Non-current liabilities
          - Total liabilities
          - Shareholders equity
          - Total equity
          - Debt
          - Cash
        Provide as a list of YearlyBalanceSheet objects.

        Clean the noisy OCR text to find accurate numbers. If data for a year is missing, omit that entry. Ensure all information is sourced from the document.
        """
    )
    r3= agent.run(prompt).content.model_dump_json(indent=2)
    return r3


def kpis_extractor(prompt):
    model_ = create_model()
    agent = Agent(
        model=model_,
        description="Calculate and extract KPIs from documents",
        response_model=KPIs,
        use_json_mode=True,
        instructions="""
        Using data from the financial statements, calculate KPIs for each of the last 3 years (2021, 2022, 2023 where available):
        - For each year, include the year and:
          - Gross margin: ((revenue - cogs) / revenue) * 100
          - Operating margin: (ebitda / revenue) * 100
          - Debt to equity: (long_term debt + short_term debt) / equity
          - Current ratio: if available, current assets / current liabilities; else 1.0
          - Revenue growth: ((current revenue - previous revenue) / previous revenue) * 100; 0.0 for earliest
          - Market share: extract if mentioned; else 0.0
        Provide as a list of YearlyKPIs objects.
        
        Base calculations on document data.
        """
    )
    r5= agent.run(prompt).content.model_dump_json(indent=2)
    # r5 = agent.run(prompt)
    return r5

def cash_flow_extractor(prompt):
    model = create_model()

    agent = Agent(
        model=model,
        description="Extract cash flow data from documents",
        response_model=CashFlowData,
        use_json_mode=True,
        instructions="""
        Analyze the financial statements and extract cash flow data for the last 3 years available:
        - For each year reported (try to find at least the last 3 years if available), extract:
        - Net Income (in millions, rounded to 2 decimal places)
        - Adjustments for Non-Cash Items
        - Changes in Working Capital
        - Cash from Operating Activities
        - Cash from Investing Activities
        - Cash from Financing Activities
        - Net Cash Flow
        - Beginning Cash Balance
        - Ending Cash Balance
        Organize the data by year in a dictionary with string keys for years (e.g., "2023").
        
        Ensure all information is directly sourced from official documents. If a value is not found, set to 0.0.
        """
    )
    r6= agent.run(prompt).content.model_dump_json(indent=2)
    # r6 = agent.run(prompt)
    return r6

def valuation_extractor(prompt):
    model = create_model()
    agent = Agent(
        model=model,
        description="Estimate valuation metrics based on financials",
        response_model=Valuation,
        use_json_mode=True,
        instructions="""
        Based on the financial statements and company knowledge:
        - Enterprise value: market cap + total debt - cash (estimate market cap if needed)
        - EV/EBITDA multiple: EV / latest EBITDA
        - Valuation range: low and high estimates
        
        Use numbers in millions. Reasonable assumptions for missing data.
        """
    )
    r7= agent.run(prompt).content.model_dump_json(indent=2)
    return r7

def industry_benchmarks_extractor(prompt):
    model_ = create_model()
    agent = Agent(
        model=model_,
        description="Provide industry benchmark averages",
        response_model=IndustryBenchmarks,
        use_json_mode=True,
        instructions="""
        For the automotive industry, provide averages:
        - Avg gross margin (%)
        - Avg operating margin (%)
        - Avg debt to equity
        - Avg revenue growth (%)
        
        Use standard data from knowledge (e.g., gross margin ~20%, etc.).
        """
    )
    r8= agent.run(prompt).content.model_dump_json(indent=2)
    return r8

def risk_factors_extractor(prompt):
    model = create_model()
    agent = Agent(
        model=model,
        description="Analyze risk factors from documents",
        response_model=RiskFactors,
        use_json_mode=True,
        instructions="""
        Analyze the document for risks:
        - High customer concentration: true if indicated
        - Geographic concentration: true if operations concentrated
        - Supply chain dependency: true if mentioned
        - Debt level: 'low', 'medium', 'high' based on ratios
        - Market cyclicality: 'high' for automotive
        
        Base on document content.
        """
    )
    r9= agent.run(prompt).content.model_dump_json(indent=2)
    return r9



def main():
    st.title("Financial Information Extractor")

    uploaded_file = st.file_uploader("Upload PDF File", type="pdf")

    if uploaded_file is not None:
        reader = PdfReader(uploaded_file)
        txt = ""
        for page in reader.pages:
            txt += page.extract_text() + "\n"
        
        st.write("Text extracted from PDF.")
        
        
        
        with st.spinner("Extracting financial information..."):
            try:
                prompt = f"Here is the financial statement of General Motors:\n\n{txt}"
                
                

                # model = AzureOpenAI(
                #     azure_endpoint= os.getenv("ENDPOINT_URL"),
                #     azure_deployment=os.getenv("DEPLOYMENT_NAME"),
                #     api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                #     api_version=os.getenv("api_version", "2025-04-01-preview"),  # Use the latest version
                #     max_tokens=8192,  # Increased from 4096
                #     temperature=0.1,
                # )

                # CompanyInfoAgent = Agent(
                #     model=model,
                #     description="Extract and analyze company profile information",
                #     response_model=CompanyInfo,
                #     use_json_mode=True,
                #     instructions="""
                #     Analyze the financial statements and extract key company information:
                #     1. Identify the complete legal company name (e.g., General Motors Company)
                #     2. Determine the primary industry classification (e.g., Automotive)
                #     3. List all business sectors the company operates in (e.g., electric vehicles, safety services)
                #     4. Find or infer the year the company was founded; if not in document, use known value 1908 for GM
                #     5. Find the number of employees; if not in document, set to 0 or known approximate
                #     6. Find the company website (e.g., https://www.gm.com)
                #     7. Locate the Employer Identification Number (EIN) for tax purposes; if not in document, set to 'unknown'
                    
                #     Ensure information is sourced from the document where possible; use reasonable defaults if missing.
                #     """
                # )

                # FinancialMetricsAgent = Agent(
                #     model=model,
                #     description="Extract yearly financial metrics from documents",
                #     response_model=FinancialMetrics,
                #     use_json_mode=True,
                #     instructions="""
                #     Analyze the financial statements and extract yearly financial data for the last 3 years (2021, 2022, 2023 where available):
                #     - For each year, include the year and:
                #       - Revenue: total net sales and revenue in millions
                #       - COGS: cost of sales in millions; if not explicit, calculate or estimate
                #       - Operating expenses: selling, general and administrative expenses in millions
                #       - EBITDA: operating income + depreciation and amortization; extract or calculate
                #     Provide as a list of YearlyFinancialData objects.
                    
                #     Clean the noisy OCR text to find accurate numbers. If data for a year is missing, omit that entry. Ensure all information is sourced from the document.
                #     """
                # )

                # BalanceSheetAgent = Agent(
                #     model=model,
                #     description="Extract balance sheet data from documents",
                #     response_model=BalanceSheet,
                #     use_json_mode=True,
                #     instructions="""
                #     Analyze the balance sheet sections and extract figures for the last 3 years (2021, 2022, 2023 where available):
                #     - For each year, include the year and:
                #       - Total assets in millions
                #       - Total liabilities in millions
                #       - Equity: total equity attributable to stockholders in millions
                #       - Debt: long-term and short-term in millions
                #       - Cash: cash and cash equivalents in millions
                #     Provide as a list of YearlyBalanceSheet objects.
                    
                #     Clean the noisy text to extract numbers. If missing, omit entry. Ensure sourced from document.
                #     """
                # )

                # KPIsAgent = Agent(
                #     model=model,
                #     description="Calculate and extract KPIs from documents",
                #     response_model=KPIs,
                #     use_json_mode=True,
                #     instructions="""
                #     Using data from the financial statements, calculate KPIs for each of the last 3 years (2021, 2022, 2023 where available):
                #     - For each year, include the year and:
                #       - Gross margin: ((revenue - cogs) / revenue) * 100
                #       - Operating margin: (ebitda / revenue) * 100
                #       - Debt to equity: (long_term debt + short_term debt) / equity
                #       - Current ratio: if available, current assets / current liabilities; else 1.0
                #       - Revenue growth: ((current revenue - previous revenue) / previous revenue) * 100; 0.0 for earliest
                #       - Market share: extract if mentioned; else 0.0
                #     Provide as a list of YearlyKPIs objects.
                    
                #     Base calculations on document data.
                #     """
                # )

                # CashFlowAgent = Agent(
                #         model=model,  # Assume model is defined elsewhere, e.g., AzureOpenAI instance
                #         description="Extract cash flow data from documents",
                #         response_model=CashFlowData,
                #         use_json_mode=True,
                #         instructions="""
                #         Analyze the financial statements and extract cash flow data for the last 3 years available:
                #         - For each year reported (try to find at least the last 3 years if available), extract:
                #         - Net Income (in millions, rounded to 2 decimal places)
                #         - Adjustments for Non-Cash Items
                #         - Changes in Working Capital
                #         - Cash from Operating Activities
                #         - Cash from Investing Activities
                #         - Cash from Financing Activities
                #         - Net Cash Flow
                #         - Beginning Cash Balance
                #         - Ending Cash Balance
                #         Organize the data by year in a dictionary with string keys for years (e.g., "2023").
                        
                #         Ensure all information is directly sourced from official documents. If a value is not found, set to 0.0.
                #         """
                #     )

                # ValuationAgent = Agent(
                #     model=model,
                #     description="Estimate valuation metrics based on financials",
                #     response_model=Valuation,
                #     use_json_mode=True,
                #     instructions="""
                #     Based on the financial statements and company knowledge:
                #     - Enterprise value: market cap + total debt - cash (estimate market cap if needed)
                #     - EV/EBITDA multiple: EV / latest EBITDA
                #     - Valuation range: low and high estimates
                    
                #     Use numbers in millions. Reasonable assumptions for missing data.
                #     """
                # )

                # IndustryBenchmarksAgent = Agent(
                #     model=model,
                #     description="Provide industry benchmark averages",
                #     response_model=IndustryBenchmarks,
                #     use_json_mode=True,
                #     instructions="""
                #     For the automotive industry, provide averages:
                #     - Avg gross margin (%)
                #     - Avg operating margin (%)
                #     - Avg debt to equity
                #     - Avg revenue growth (%)
                    
                #     Use standard data from knowledge (e.g., gross margin ~20%, etc.).
                #     """
                # )

                # RiskFactorsAgent = Agent(
                #     model=model,
                #     description="Analyze risk factors from documents",
                #     response_model=RiskFactors,
                #     use_json_mode=True,
                #     instructions="""
                #     Analyze the document for risks:
                #     - High customer concentration: true if indicated
                #     - Geographic concentration: true if operations concentrated
                #     - Supply chain dependency: true if mentioned
                #     - Debt level: 'low', 'medium', 'high' based on ratios
                #     - Market cyclicality: 'high' for automotive
                    
                #     Base on document content.
                #     """
                # )

                # CompanyData_team = Team(
                #     name="Company Data Extraction Team",
                #     mode="coordinate",
                #     model=model,
                #     members=[CompanyInfoAgent, FinancialMetricsAgent, BalanceSheetAgent, KPIsAgent,CashFlowAgent ,ValuationAgent, IndustryBenchmarksAgent, RiskFactorsAgent],
                #     response_model=CompanyData,
                #     markdown=True,
                #     show_members_responses=True,
                # )
                # CompanyData_ = CompanyData_team.run(prompt)
                # st.json(CompanyData_.content.model_dump_json(indent=2), expanded=True)

                
                
                st.subheader("Extracted Financial Information")
                st.write("Company Information:")
                st.json(company_info_extractor(prompt), expanded=True)
                st.write("Financial Metrics:")
                st.json(financial_metrics_extractor(prompt), expanded=True)
                st.write("Balance Sheet:")
                st.json(balance_sheet_extractor(prompt=prompt), expanded=True)
                st.write("Key Performance Indicators:")
                st.json(kpis_extractor(prompt=prompt), expanded=True)
                st.write("Cash Flow:")
                st.json(cash_flow_extractor(prompt=prompt), expanded=True)
                st.write("Valuation:")
                st.json(valuation_extractor(prompt=prompt), expanded=True)
                st.write("Industry Benchmarks:")
                st.json(industry_benchmarks_extractor(prompt=prompt), expanded=True)
                st.write("Risk Factors:")
                st.json(risk_factors_extractor(prompt=prompt), expanded=True)


                # st.json({
                #     "company_info": r1.content.model_dump(),
                #     "financial_metrics": r2.content.model_dump(),
                #     "balance_sheet": r4.content.model_dump(),
                #     "kpis": r5.content.model_dump(),
                #     "cash_flow": r6.content.model_dump(),
                #     "valuation": r7.content.model_dump(),
                #     "industry_benchmarks": r8.content.model_dump(),
                #     "risk_factors": r9.content.model_dump()
                # }, expanded=True)   

                
            except Exception as e:
                st.error(f"Error extracting data: {str(e)}")

if __name__ == "__main__":
    main()
