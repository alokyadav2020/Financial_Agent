import os
import json
from typing import List
from pydantic import BaseModel, Field
# from openai import AzureOpenAI
# from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import PyPDF2  # Requires installation: pip install pypdf2
import streamlit as st
import tempfile
from agno.agent import Agent,RunResponse
from agno.models.azure import AzureOpenAI
from agno.team.team import Team
from textwrap import dedent
from dotenv import load_dotenv
import os
load_dotenv()

# Define the Pydantic models as provided


class CompanyInfo(BaseModel):
    name: str = Field(..., description="Company's legal name")
    industry: str = Field(..., description="Primary industry")
    sectors: List[str] = Field(..., description="List of business sectors")
    year_founded: int = Field(..., description="Year the company was founded")
    employees: int = Field(..., description="Number of employees as of the latest year")
    website: str = Field(..., description="Company website")
    ein: str = Field(..., description="Employer Identification Number (EIN) for tax purposes")

class YearlyFinancialData(BaseModel):
    year: str = Field(..., description="The fiscal or calendar year of the financial data, represented as a string (e.g., '2023', 'FY2022', or similar variations found in the document). Identify the most recent and prior years, typically the last 3 years available.")
    revenue: int = Field(..., description="Total net sales, revenue, or equivalent top-line income figure (may be labeled as 'Net sales', 'Total revenue', 'Operating revenue', 'Sales revenue', etc.) reported in millions of dollars or the primary currency used in the document.")
    cogs: int = Field(..., description="Cost of goods sold (COGS), cost of sales, or equivalent direct costs associated with producing goods or services (may be labeled as 'Cost of revenue', 'Cost of sales', 'Direct costs', etc.) in millions. This typically excludes operating expenses like SG&A.")
    operating_expenses: int = Field(..., description="Operating expenses, often including selling, general, and administrative expenses (SG&A), research and development (R&D), or other indirect costs (may be labeled as 'Operating expenses', 'Selling and administrative expenses', 'General expenses', etc.) in millions. Sum relevant sub-categories if broken down.")
    ebitda: int = Field(..., description="Earnings Before Interest, Taxes, Depreciation, and Amortization (EBITDA), which can be calculated as operating income plus depreciation and amortization if not directly stated (may be referred to as 'Adjusted EBITDA', 'EBITDA', or derived from 'Operating profit' + 'D&A'). Use the closest equivalent and report in millions.")

class FinancialMetrics(BaseModel):
    yearly_data: List[YearlyFinancialData] = Field(..., description="A list of YearlyFinancialData objects covering the last 3 available years (or fewer if not all are present), ordered from most recent to oldest. Ensure data is extracted for each year consistently from income statements or financial summaries.")

class Debt(BaseModel):
    long_term: int = Field(..., description="Long-term debt obligations, including finance lease obligations, notes payable, bonds, or other borrowings due after one year (may be labeled as 'Long-term debt', 'Non-current debt', 'Long-term borrowings', 'Finance leases - non-current', etc.) reported in millions of dollars or the primary currency. Sum relevant sub-categories if broken down and round to the nearest million.")
    short_term: int = Field(..., description="Short-term debt obligations, including the current portion of long-term debt, revolving credit facilities, or other borrowings due within one year (may be labeled as 'Short-term debt', 'Current debt', 'Current portion of long-term debt', 'Finance leases - current', etc.) in millions. Sum relevant sub-categories if necessary.")

class YearlyBalanceSheet(BaseModel):
    year: str = Field(..., description="The fiscal or calendar year of the balance sheet data, represented as a string (e.g., '2023', 'FY2022', or similar variations found in the document). Identify the most recent and prior years, typically the last 3 years available.")
    total_assets: int = Field(..., description="Total assets from the balance sheet, encompassing current and non-current assets (may be labeled as 'Total assets', 'Assets total', etc.) in millions. Round to the nearest million if necessary.")
    total_liabilities: int = Field(..., description="Total liabilities from the balance sheet, including current and non-current liabilities (may be labeled as 'Total liabilities', 'Liabilities total', etc.) in millions.")
    equity: int = Field(..., description="Total equity attributable to stockholders or shareholders (may be labeled as 'Stockholders' equity', 'Shareholders' equity', 'Total equity', 'Net assets', etc.), excluding non-controlling interests if specified, in millions.")
    debt: Debt
    cash: int = Field(..., description="Cash and cash equivalents, sometimes including short-term investments or marketable securities if grouped together (may be labeled as 'Cash and cash equivalents', 'Cash, cash equivalents, and short-term investments', etc.) in millions.")

class BalanceSheet(BaseModel):
    yearly_data: List[YearlyBalanceSheet] = Field(..., description="A list of YearlyBalanceSheet objects covering the last 3 available years (or fewer if not all are present), ordered from most recent to oldest. Ensure data is extracted consistently from consolidated balance sheets or financial position statements.")

class YearlyKPIs(BaseModel):
    year: str = Field(..., description="The fiscal or calendar year of the KPI data, represented as a string (e.g., '2023', 'FY2022', or similar variations found in the document). Identify the most recent and prior years, typically the last 3 years available.")
    gross_margin: float = Field(..., description="Gross margin percentage as directly stated in the document (may be labeled as 'Gross profit margin', 'Gross margin %', or similar). Report as a percentage (e.g., 25.5 for 25.5%). Use 0.0 if unavailable.")
    operating_margin: float = Field(..., description="Operating margin percentage as directly stated in the document (may be labeled as 'Operating profit margin', 'EBIT margin %', or similar). Report as a percentage (e.g., 15.2 for 15.2%). Use 0.0 if unavailable.")
    debt_to_equity: float = Field(..., description="Debt to equity ratio as directly stated in the document (may be labeled as 'D/E ratio', 'Leverage ratio', or similar). Report as a decimal (e.g., 1.5 for 1.5:1). Use 0.0 if unavailable.")
    current_ratio: float = Field(..., description="Current ratio as directly stated in the document (may be labeled as 'Current ratio', 'Liquidity ratio', or similar). Report as a decimal (e.g., 2.0 for 2:1). Use 0.0 if unavailable.")
    revenue_growth: float = Field(..., description="Revenue growth percentage from the previous year as directly stated in the document (may be labeled as 'Revenue growth %', 'YoY growth', or similar). Set to 0.0 for the earliest year or if unavailable.")
    market_share: float = Field(..., description="Market share percentage if explicitly stated in the document (may be labeled as 'Market share %', 'Share of market', or discussed in MD&A). Use 0.0 if not available or unclear.")

class KPIs(BaseModel):
    yearly_data: List[YearlyKPIs] = Field(..., description="A list of YearlyKPIs objects covering the last 3 available years (or fewer if not all are present), ordered from most recent to oldest. Extract KPIs directly from the document without any calculations.")


class ValuationRange(BaseModel):
    low: int = Field(..., description="Low estimate of the company valuation in millions as directly stated in the document (may be labeled as 'Low valuation estimate', 'Valuation range low end', or similar in valuation analysis sections). Round to the nearest million if necessary. Use 0 if unavailable.")
    high: int = Field(..., description="High estimate of the company valuation in millions as directly stated in the document (may be labeled as 'High valuation estimate', 'Valuation range high end', or similar in valuation analysis sections). Round to the nearest million if necessary. Use 0 if unavailable.")

class Valuation(BaseModel):
    enterprise_value: int = Field(..., description="Enterprise value (EV) in millions as directly stated in the document (may be labeled as 'Enterprise value', 'EV', 'Total enterprise value', or similar in financial summaries or valuation sections). Round to the nearest million if necessary. Use 0 if unavailable.")
    ev_ebitda_multiple: float = Field(..., description="EV/EBITDA multiple as directly stated in the document (may be labeled as 'EV/EBITDA', 'Enterprise value to EBITDA ratio', 'Valuation multiple', or similar). Report as a decimal (e.g., 12.5 for 12.5x). Use 0.0 if unavailable.")
    valuation_range: ValuationRange

class IndustryBenchmarks(BaseModel):
    avg_gross_margin: float = Field(..., description="Average gross margin percentage for the automotive industry as directly stated in the document (may be labeled as 'Industry average gross margin', 'Automotive sector gross profit margin avg', or similar in industry comparison sections). Report as a percentage (e.g., 25.5 for 25.5%). Use 0.0 if unavailable.")
    avg_operating_margin: float = Field(..., description="Average operating margin percentage for the automotive industry as directly stated in the document (may be labeled as 'Industry average operating margin', 'Automotive sector operating profit margin avg', or similar). Report as a percentage (e.g., 15.2 for 15.2%). Use 0.0 if unavailable.")
    avg_debt_to_equity: float = Field(..., description="Average debt to equity ratio for the automotive industry as directly stated in the document (may be labeled as 'Industry avg D/E ratio', 'Automotive sector leverage ratio avg', or similar). Report as a decimal (e.g., 1.5 for 1.5:1). Use 0.0 if unavailable.")
    avg_revenue_growth: float = Field(..., description="Average revenue growth percentage for the automotive industry as directly stated in the document (may be labeled as 'Industry avg revenue growth %', 'Automotive sector YoY growth avg', or similar). Report as a percentage (e.g., 5.0 for 5.0%). Use 0.0 if unavailable.")

class RiskFactors(BaseModel):
    high_customer_concentration: bool = Field(..., description="True if the document directly mentions or describes a high customer concentration risk (may be indicated in risk factors section as 'dependence on major customers', 'customer concentration', 'risk from loss of key clients', or similar discussions highlighting significant revenue from few customers). False if not mentioned or described as low/no risk.")
    geographic_concentration: bool = Field(..., description="True if the document directly mentions or describes a geographic concentration risk (may be indicated as 'geographic concentration', 'regional market dependence', 'risk from operations in specific areas', or similar, such as vulnerability to events in certain countries/regions). False if not mentioned or described as low/no risk.")
    supply_chain_dependency: bool = Field(..., description="True if the document directly mentions or describes a supply chain dependency risk (may be indicated as 'supply chain risks', 'dependence on key suppliers', 'vendor concentration', or similar, including disruptions from suppliers). False if not mentioned or described as low/no risk.")
    debt_level: str = Field(..., description="Assessed debt level as directly stated or described in the document: 'low', 'medium', or 'high' (may be inferred from discussions on leverage, debt ratios, or financial condition in MD&A or risk sections, e.g., 'high leverage', 'manageable debt', 'low indebtedness'). Use 'medium' if unclear or not specified.")
    market_cyclicality: str = Field(..., description="Assessed market cyclicality as directly stated or described in the document: 'low', 'medium', or 'high' (may be indicated in risk factors as 'cyclical industry', 'sensitivity to economic cycles', 'demand fluctuations', especially for automotive sector). Use 'medium' if unclear or not specified.")

class YearlyCashFlow(BaseModel):
    year: str = Field(..., description="The fiscal or calendar year of the cash flow data, represented as a string (e.g., '2023', 'FY2022', or similar variations found in the document). Identify the most recent and prior years, typically the last 3 years available.")
    net_income: float = Field(..., description="Net income or net earnings as the starting point of the cash flow statement (may be labeled as 'Net income', 'Net profit', 'Profit after tax', etc.) reported in millions of dollars or the primary currency. Use the value from the consolidated statement of cash flows.")
    adjustments_for_non_cash_items: float = Field(..., description="Adjustments for non-cash items, such as depreciation, amortization, stock-based compensation, impairment charges, etc. (may be labeled as 'Adjustments to reconcile net income to net cash provided by operating activities', 'Non-cash adjustments', or summed from individual line items like 'Depreciation and amortization', 'Share-based compensation') in millions. Sum relevant sub-items if broken down.")
    changes_in_working_capital: float = Field(..., description="Changes in operating assets and liabilities or working capital (may be labeled as 'Changes in working capital', 'Net changes in assets and liabilities', or summed from items like 'Accounts receivable', 'Inventory', 'Accounts payable', etc.) in millions. This can be positive or negative.")
    cash_from_operating_activities: float = Field(..., description="Net cash provided by (used in) operating activities (may be labeled as 'Cash flows from operating activities', 'Operating cash flow', etc.) in millions. This is typically the subtotal after adjustments and working capital changes.")
    cash_from_investing_activities: float = Field(..., description="Net cash provided by (used in) investing activities (may be labeled as 'Cash flows from investing activities', 'Investing cash flow', etc., including purchases/sales of property, equipment, investments, acquisitions) in millions.")
    cash_from_financing_activities: float = Field(..., description="Net cash provided by (used in) financing activities (may be labeled as 'Cash flows from financing activities', 'Financing cash flow', etc., including debt issuance/repayment, equity transactions, dividends) in millions.")
    net_cash_flow: float = Field(..., description="Net increase (decrease) in cash and cash equivalents (may be labeled as 'Net cash flow', 'Net change in cash', or calculated as sum of operating + investing + financing cash flows) in millions.")
    beginning_cash_balance: float = Field(..., description="Cash and cash equivalents at the beginning of the period (may be labeled as 'Beginning cash balance', 'Cash at start of year', etc.) in millions.")
    ending_cash_balance: float = Field(..., description="Cash and cash equivalents at the end of the period (may be labeled as 'Ending cash balance', 'Cash at end of year', etc.) in millions.")

class CashFlowData(BaseModel):
    yearly_data: List[YearlyCashFlow] = Field(..., description="A list of YearlyCashFlow objects covering the last 3 available years (or fewer if not all are present), ordered from most recent to oldest. Ensure data is extracted consistently from consolidated statements of cash flows or equivalent sections.")    


# Define a root model to encompass all the required information
class CompanyReport(BaseModel):
    company_info: CompanyInfo
    financial_metrics: FinancialMetrics
    balance_sheet: BalanceSheet
    kpis: KPIs
    valuation: Valuation
    industry_benchmarks: IndustryBenchmarks
    risk_factors: RiskFactors
    cash_flow : CashFlowData

class PDFCompanyExtractor:
    def __init__(self):
        endpoint = os.getenv("ENDPOINT_URL", "https://info-mdeiaw6z-eastus2.cognitiveservices.azure.com/")
        deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4.1-mini")
        
        # Initialize Azure OpenAI client with Entra ID authentication
        
        
        self.client = AzureOpenAI(
                    azure_endpoint=endpoint,
                    azure_deployment=deployment,
                    api_key=os.getenv("AZURE_OPENAI_API_KEY", "your_api_key_here"),
                    api_version="2024-12-01-preview",
                    
            
        )
        self.deployment = deployment

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Reads a PDF file and extracts all text from it.
        
        :param pdf_path: Path to the PDF file.
        :return: Extracted text as a single string.
        """
        text = ""
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()

    def make_schema_strict(self, schema: dict) -> dict:
        """
        Recursively sets 'additionalProperties': False for all objects in the JSON schema.
        
        :param schema: The JSON schema dictionary.
        :return: Modified schema with strict properties.
        """
        if isinstance(schema, dict):
            if 'properties' in schema and schema.get('type') == 'object':
                schema['additionalProperties'] = False
            for key, value in schema.items():
                schema[key] = self.make_schema_strict(value)
        elif isinstance(schema, list):
            schema = [self.make_schema_strict(item) for item in schema]
        return schema

    def extract_company_info(self, financial_doc: str) -> RunResponse:
        """
        Extracts company information from the provided text in the specified JSON format.
        
        :param text: Extracted text from the PDF.
        :return: Dictionary containing the extracted company information.
        """
        # Prepare the JSON schema for structured output
        CompanyInfoAgent = Agent(
        name="CompanyInfoExtractor",
        model=self.client,
        description="Extract and analyze company profile information",
        response_model=CompanyInfo,
        use_json_mode=True,
        context={"financial_doc":financial_doc},
        add_context=True,
        instructions=dedent("""
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
    ))
        return CompanyInfoAgent

    def extract_financial_metrics(self, financial_doc: str) -> RunResponse:
        """
        Extracts financial metrics from the provided text in the specified JSON format.
        
        :param text: Extracted text from the PDF.
        :return: Dictionary containing the extracted financial metrics.
        """
        FinancialMetricsAgent = Agent(
        name="FinancialMetricsExtractor",
        model=self.client,
        goal="Extract yearly financial metrics from financial documents",
        description=dedent("""
    An AI agent designed to extract key yearly financial metrics from financial documents such as annual reports, 10-K filings, or earnings statements. It parses lengthy texts to identify and structure data like revenue, COGS, operating expenses, and EBITDA for the most recent years available.

    """),
        response_model=FinancialMetrics,
        use_json_mode=True,
        context={"financial_doc":financial_doc},
        add_context=True,
        instructions=dedent("""
        "You are FinancialMetricsExtractor, an AI agent specialized in parsing and extracting key financial metrics from lengthy financial documents such as annual reports, 10-K filings, or earnings statements, which may span 80-90 pages or more.\n\n"
                "Agent Aim: Your primary goal is to accurately identify and extract financial metrics for the last 3 years (or available years) from the provided text, handling variations in terminology, table formats, and document structures. Focus on income statement-related data, cross-referencing sections like consolidated statements of operations, financial highlights, or management's discussion for completeness. If data is incomplete fill all fields with blank.\n\n"
                "Instructions:\n"
                "- Scan the entire text thoroughly, including tables, footnotes, and narrative sections, to locate relevant financial data.\n"
                "- Handle synonyms and variations: Fields may use different names across documents (e.g., 'Revenue' could be 'Net sales' or 'Total income').\n"
                "- Prioritize the most recent fiscal years, typically the last 3, and order them from newest to oldest.\n"
                "- Extract the following fields for each year:\n"
                "- If a field is not explicitly stated, use reasonable defaults (e.g., 0.0 for market share if not available).\n"
                "- Ensure the output strictly adheres to the JSON schema; do not add extra fields or explanations.\n\n"
                "Field Descriptions (use these to guide extraction):\n"
                "- year: The fiscal or calendar year as a string (e.g., '2023'). Look for headers like 'Year Ended December 31, 2023' or 'FY2022'.\n"
                "- revenue: Top-line figure like total net sales or revenue in millions.\n"
                "- cogs: Direct costs like cost of goods sold or cost of sales in millions.\n"
                "- operating_expenses: Indirect costs like SG&A or operating expenses in millions.\n"
                "- ebitda: EBITDA, DO not use calculable equivalent in millions."
                """
    ))

        return FinancialMetricsAgent

    def extract_balance_sheet(self, financial_doc: str) -> RunResponse:
        """
        Extracts balance sheet from the provided text in the specified JSON format.
        
        :param text: Extracted text from the PDF.
        :return: Dictionary containing the extracted balance sheet.
        """
        # Prepare the JSON schema for structured output
        BalanceSheetAgent = Agent(
        name="BalanceSheetExtractor",
        goal="Your primary goal is to precisely parse and extract structured balance sheet data from provided financial documents, covering the most recent available years while accounting for inconsistencies in formatting, terminology, and reporting standards. Prioritize accuracy, completeness, and direct sourcing from the text to enable reliable financial analysis, setting any unavailable values to 0 for consistency.",
        model=self.client,
        description=dedent("""An AI agent designed to extract key balance sheet data from financial documents such as annual reports, 10-K filings, or financial statements. It parses lengthy texts to identify and structure data like total assets, liabilities, equity, debt (short-term and long-term), and cash for the most recent years available. """),
        response_model=BalanceSheet,
        use_json_mode=True,
        context={"financial_doc":financial_doc},
        add_context=True,
        instructions=dedent("""
        You are BalanceSheetExtractor, an AI agent specialized in parsing and extracting key balance sheet data from lengthy financial documents such as annual reports, 10-K filings, or financial statements, which may span 80-90 pages or more.

            Agent Aim: Your primary goal is to accurately identify and extract balance sheet metrics for the last 3 years (or available years if fewer) from the provided text, handling variations in terminology, table formats, and document structures. Focus on consolidated balance sheet or statement of financial position data, cross-referencing sections like financial highlights, notes, or management's discussion for completeness. Clean noisy text to extract accurate numbers, ensuring all data is sourced directly from the document. If data for a field is incomplete or not found, set the value to 0 (do not leave blank or use null).

            Instructions:
            - Scan the entire text thoroughly, including tables, footnotes, and narrative sections, to locate relevant balance sheet data.
            - Handle synonyms and variations: Fields may use different names across documents (e.g., 'Total assets' could be 'Assets, total' or 'Combined assets').
            - Prioritize the most recent fiscal years, typically the last 3 (e.g., 2023, 2022, 2021), and order them from newest to oldest in the output list.
            - Extract values in millions, rounding to the nearest integer if necessary. Assume the primary currency is USD unless otherwise specified.
            - For debt: Sum sub-categories for long-term and short-term as needed; if not distinguished, allocate based on descriptions or set to 0 if unclear.
            - Ensure the output strictly adheres to the JSON schema; do not add extra fields, explanations, or narrative text.
            - If no balance sheet data is found for a year, do not include that year in the list.

            Field Descriptions (use these to guide extraction):
            - year: The fiscal or calendar year as a string (e.g., '2023'). Look for headers like 'As of December 31, 2023' or 'FY2022'.
            - total_assets: Total assets in millions.
            - total_liabilities: Total liabilities in millions.
            - equity: Total equity attributable to stockholders in millions, excluding non-controlling interests.
            - debt: Nested object with long_term (non-current debt) and short_term (current debt) in millions.
            - cash: Cash and cash equivalents in millions, potentially including short-term investments if combined.
        """
    )  )
        return BalanceSheetAgent

    def extract_kpis(self, financial_doc: str) -> RunResponse:
        """
        Extracts KPIs from the provided text in the specified JSON format.
        
        :param text: Extracted text from the PDF.
        :return: Dictionary containing the extracted KPIs.
        """
        # Prepare the JSON schema for structured output
        KPIsAgent = Agent(
        name="KPIsExtractor",
        model=self.client,
        goal="Precisely parse and extract structured key performance indicators (KPIs) from provided financial documents, covering the most recent available years while accounting for inconsistencies in formatting, terminology, and reporting standards. Prioritize accuracy, completeness, and direct sourcing from the text to enable reliable financial analysis, setting any unavailable values to 0.0 for consistency.",
        description="An AI agent designed to extract key performance indicators (KPIs) such as margins, ratios, growth rates, and market share from financial documents like annual reports, 10-K filings, or earnings statements. It parses lengthy texts to identify and structure KPI data for the most recent years available, using direct extraction where possible and calculations only if explicitly allowed in field descriptions.",
        response_model=KPIs,
        use_json_mode=True,
        context={"financial_doc":financial_doc},
        add_context=True,
        instructions=dedent("""
        You are KPIsExtractor, an AI agent specialized in parsing and extracting key performance indicators (KPIs) from lengthy financial documents such as annual reports, 10-K filings, or earnings statements, which may span 80-90 pages or more.

            Agent Aim: Your primary goal is to accurately identify and extract KPIs for the last 3 years (or available years if fewer) from the provided text, handling variations in terminology, table formats, and document structures. Focus on sections like financial highlights, management's discussion and analysis (MD&A), or KPI summaries, cross-referencing with income statements, balance sheets, or notes for completeness. Extract values directly as stated; perform calculations only if the field description explicitly allows it (e.g., for revenue growth if not stated but revenues are available). If data for a field is incomplete or not found, set the value to 0.0 (do not leave blank or use null).

            Instructions:
            - Scan the entire text thoroughly, including tables, footnotes, and narrative sections, to locate relevant KPI data.
            - Handle synonyms and variations: Fields may use different names across documents (e.g., 'Gross margin' could be 'Gross profit percentage' or 'GM%').
            - Prioritize the most recent fiscal years, typically the last 3, and order them from newest to oldest in the output list.
            - For percentages and ratios, report as floats (e.g., 25.5 for 25.5%, 1.5 for 1.5:1).
            - For revenue_growth: If not directly stated, calculate as ((current revenue - previous revenue) / previous revenue) * 100 if revenues are available in the document; set to 0.0 for the earliest year or if unavailable.
            - For other fields: Extract directly if stated; set to 0.0 if not available (do not calculate unless specified).
            - Ensure the output strictly adheres to the JSON schema; do not add extra fields, explanations, or narrative text.
            - If no KPI data is found for a year, do not include that year in the list.

            Field Descriptions (use these to guide extraction):
            - year: The fiscal or calendar year as a string (e.g., '2023'). Look for headers like 'Year Ended December 31, 2023' or 'FY2022'.
            - gross_margin: Gross margin percentage as directly stated, in percent (e.g., 25.5).
            - operating_margin: Operating margin percentage as directly stated, in percent (e.g., 15.2).
            - debt_to_equity: Debt to equity ratio as directly stated, as a decimal (e.g., 1.5).
            - current_ratio: Current ratio as directly stated, as a decimal (e.g., 2.0).
            - revenue_growth: Revenue growth percentage as directly stated or calculated if possible, in percent (set to 0.0 for earliest year).
            - market_share: Market share percentage if explicitly stated, in percent (e.g., 12.3).
        """
    ))

        return KPIsAgent

    def extract_valuation(self, financial_doc: str) -> RunResponse:
        """
        Extracts valuation from the provided text in the specified JSON format.
        
        :param text: Extracted text from the PDF.
        :return: Dictionary containing the extracted valuation.
        """
        # Prepare the JSON schema for structured output
        ValuationAgent = Agent(
        name="ValuationMetricsExtractor",
        model=self.client,
        goal="Precisely parse, extract, and estimate structured valuation metrics from provided financial documents, including enterprise value, EV/EBITDA multiple, and valuation range, while accounting for inconsistencies in formatting, terminology, and reporting standards. Prioritize accuracy, completeness, and direct sourcing from the text, using calculations where necessary to enable reliable financial analysis, setting any unavailable values to 0 or 0.0 for consistency.",
        description="An AI agent designed to extract and estimate valuation metrics such as enterprise value, EV/EBITDA multiple, and valuation range from financial documents like annual reports, 10-K filings, or valuation analyses. It parses lengthy texts to identify and structure valuation data, using direct extraction where possible and calculations or reasonable estimations if direct values are not available.",
        response_model=Valuation,
        context={"financial_doc":financial_doc},
        add_context=True,
        use_json_mode=True,
        instructions=dedent("""
        You are ValuationMetricsExtractor, an AI agent specialized in parsing, extracting, and estimating valuation metrics from lengthy financial documents such as annual reports, 10-K filings, or valuation reports, which may span 80-90 pages or more.

            Agent Aim: Your primary goal is to accurately identify and extract or calculate valuation metrics from the provided text, handling variations in terminology, table formats, and document structures. Focus on sections like financial summaries, valuation analysis, or management's discussion and analysis (MD&A), cross-referencing with balance sheets, income statements, or notes for completeness. Extract values directly as stated; perform calculations if the field description allows or if necessary for completeness. If data for a field is incomplete or not found, set the value to 0 or 0.0 (do not leave blank or use null).

            Instructions:
            - Scan the entire text thoroughly, including tables, footnotes, and narrative sections, to locate relevant valuation data.
            - Handle synonyms and variations: Fields may use different names across documents (e.g., 'Enterprise value' could be 'EV' or 'Total firm value').
            - Extract values in millions, rounding to the nearest integer if necessary. Assume the primary currency is USD unless otherwise specified.
            - For enterprise_value: If directly stated, use that; otherwise, calculate as (estimated market cap + total debt - cash) using latest available data from the document. If market cap is not stated, use a reasonable estimate based on document context or set to 0 if unclear.
            - For ev_ebitda_multiple: If directly stated, use that; otherwise, calculate as enterprise_value / latest EBITDA if both are available (or calculated); set to 0.0 if unavailable.
            - For valuation_range: Extract low and high directly if stated; set to 0 if unavailable.
            - Ensure the output strictly adheres to the JSON schema; do not add extra fields, explanations, or narrative text.

            Field Descriptions (use these to guide extraction):
            - enterprise_value: Enterprise value (EV) in millions, directly stated or calculated as described.
            - ev_ebitda_multiple: EV/EBITDA multiple as a decimal (e.g., 12.5), directly stated or calculated.
            - valuation_range: Nested object with low and high valuation estimates in millions, directly stated.
        """
    ))
        return ValuationAgent

    def extract_industry_benchmarks(self, financial_doc: str) -> RunResponse:
        """
        Extracts industry benchmarks from the provided text in the specified JSON format.
        
        :param text: Extracted text from the PDF.
        :return: Dictionary containing the extracted industry benchmarks.
        """
        # Prepare the JSON schema for structured output
        IndustryBenchmarksAgent = Agent(
        name="IndustryBenchmarksExtractor",
        model=self.client,
        goal="Precisely parse and extract structured industry benchmark averages for key financial metrics in the automotive sector from provided financial documents, while accounting for inconsistencies in formatting, terminology, and reporting standards. Prioritize accuracy, completeness, and direct sourcing from the text to enable reliable comparative analysis, setting any unavailable values to 0.0 for consistency.",
        description="An AI agent designed to extract automotive industry benchmark averages for metrics like gross margin, operating margin, debt to equity, and revenue growth from financial documents such as annual reports, 10-K filings, or industry analyses. It parses lengthy texts to identify and structure benchmark data, using direct extraction from the document.",
        response_model=IndustryBenchmarks,
        use_json_mode=True,
        context={"financial_doc":financial_doc},
        add_context=True,
        instructions=dedent("""
        You are IndustryBenchmarksExtractor, an AI agent specialized in parsing and extracting industry benchmark averages for the automotive sector from lengthy financial documents such as annual reports, 10-K filings, or industry reports, which may span 80-90 pages or more.

            Agent Aim: Your primary goal is to accurately identify and extract automotive industry benchmark metrics from the provided text, handling variations in terminology, table formats, and document structures. Focus on sections like industry comparisons, peer analysis, or management's discussion and analysis (MD&A), cross-referencing with financial summaries or notes for completeness. Extract values directly as stated; if data for a field is incomplete or not found, set the value to 0.0 (do not leave blank or use null). Do not use external knowledge or assumptions; rely solely on the document.

            Instructions:
            - Scan the entire text thoroughly, including tables, footnotes, and narrative sections, to locate relevant industry benchmark data specific to the automotive sector.
            - Handle synonyms and variations: Fields may use different names across documents (e.g., 'Avg gross margin' could be 'Industry gross profit average' or 'Sector GM%').
            - For percentages and ratios, report as floats (e.g., 25.5 for 25.5%, 1.5 for 1.5:1).
            - Ensure the output strictly adheres to the JSON schema; do not add extra fields, explanations, or narrative text.

            Field Descriptions (use these to guide extraction):
            - avg_gross_margin: Average gross margin percentage for automotive industry as directly stated, in percent (e.g., 25.5).
            - avg_operating_margin: Average operating margin percentage for automotive industry as directly stated, in percent (e.g., 15.2).
            - avg_debt_to_equity: Average debt to equity ratio for automotive industry as directly stated, as a decimal (e.g., 1.5).
            - avg_revenue_growth: Average revenue growth percentage for automotive industry as directly stated, in percent (e.g., 5.0).
        """
    ))
        return IndustryBenchmarksAgent
    
    def extract_risk_factors(self, financial_doc: str) -> RunResponse:
        """
        Extracts risk factors from the provided text in the specified JSON format.
        
        :param text: Extracted text from the PDF.
        :return: Dictionary containing the extracted risk factors.
        """
        # Prepare the JSON schema for structured output
        RiskFactorsAgent = Agent(
        name="RiskFactorsExtractor",
        model=self.client,
        goal="Precisely parse and extract structured risk factors from provided financial documents, covering aspects like concentrations, dependencies, debt levels, and market cyclicality, while accounting for inconsistencies in formatting, terminology, and reporting standards. Prioritize accuracy, completeness, and direct sourcing from the text to enable reliable risk assessment, using default values where specified for consistency.",
        description="An AI agent designed to extract and assess risk factors such as customer concentration, geographic concentration, supply chain dependency, debt level, and market cyclicality from financial documents like annual reports, 10-K filings, or risk disclosures. It parses lengthy texts to identify and structure risk data based on direct mentions and descriptions.",
        response_model=RiskFactors,
        use_json_mode=True,
        context={"financial_doc":financial_doc},
        add_context=True,
        instructions=dedent("""
        You are RiskFactorsExtractor, an AI agent specialized in parsing and extracting risk factors from lengthy financial documents such as annual reports, 10-K filings, or risk factor sections, which may span 80-90 pages or more.

            Agent Aim: Your primary goal is to accurately identify and extract or assess risk factors from the provided text, handling variations in terminology, table formats, and document structures. Focus on sections like risk factors, management's discussion and analysis (MD&A), or notes to financial statements, cross-referencing for completeness. Extract or infer based directly on the document content as described in the fields; use defaults like False or 'medium' if not mentioned or unclear.

            Instructions:
            - Scan the entire text thoroughly, including tables, footnotes, and narrative sections, to locate relevant risk factor data.
            - Handle synonyms and variations: Risks may be described differently across documents (e.g., 'customer concentration' could be 'reliance on key clients' or 'major customer dependency').
            - For boolean fields: Set to True only if the document directly mentions or describes it as a significant risk; False otherwise (including if described as low or no risk).
            - For string fields: Assess as 'low', 'medium', or 'high' based on direct statements or descriptions; use 'medium' if unclear, not specified, or neutral.
            - Ensure the output strictly adheres to the JSON schema; do not add extra fields, explanations, or narrative text.

            Field Descriptions (use these to guide extraction):
            - high_customer_concentration: True if high customer concentration risk is directly mentioned or described; False otherwise.
            - geographic_concentration: True if geographic concentration risk is directly mentioned or described; False otherwise.
            - supply_chain_dependency: True if supply chain dependency risk is directly mentioned or described; False otherwise.
            - debt_level: Assessed debt level as 'low', 'medium', or 'high' based on document descriptions or ratios discussed; 'medium' if unclear.
            - market_cyclicality: Assessed market cyclicality as 'low', 'medium', or 'high' based on document descriptions (e.g., cyclical nature of automotive industry); 'medium' if unclear.
        """
    ))
        return RiskFactorsAgent

    def extract_cash_flow(self, financial_doc: str) -> RunResponse:
        """
        Extracts cash flow data from the provided text in the specified JSON format.
        
        :param text: Extracted text from the PDF.
        :return: Dictionary containing the extracted cash flow data.
        """
        # Prepare the JSON schema for structured output
        CashFlowAgent = Agent(
        name="CashFlowExtractor",
        model=self.client,
        goal="Precisely parse and extract structured cash flow statement data from provided financial documents, covering the most recent available years while accounting for inconsistencies in formatting, terminology, and reporting standards. Prioritize accuracy, completeness, and direct sourcing from the text to enable reliable financial analysis, setting any unavailable values to 0.0 for consistency.",
        description="An AI agent designed to extract key cash flow data from financial documents such as annual reports, 10-K filings, or cash flow statements. It parses lengthy texts to identify and structure data like net income, operating cash flow, investing cash flow, financing cash flow, and cash balances for the most recent years available.",
        response_model=CashFlowData,
        use_json_mode=True,
        context={"financial_doc": financial_doc},
        add_context=True,
        instructions=dedent("""
            You are CashFlowExtractor, an AI agent specialized in parsing and extracting key cash flow data from lengthy financial documents such as annual reports, 10-K filings, or statements of cash flows, which may span 80-90 pages or more.

            Agent Aim: Your primary goal is to accurately identify and extract cash flow metrics for the last 3 years (or available years if fewer) from the provided text, handling variations in terminology, table formats, and document structures. Focus on consolidated statements of cash flows or equivalent sections, cross-referencing with financial highlights, notes, or management's discussion for completeness. Clean noisy text to extract accurate numbers, ensuring all data is sourced directly from the document. If data for a field is incomplete or not found, set the value to 0.0 (do not leave blank or use null).

            Instructions:
            - Scan the entire text thoroughly, including tables, footnotes, and narrative sections, to locate relevant cash flow data.
            - Handle synonyms and variations: Fields may use different names across documents (e.g., 'Cash from operating activities' could be 'Operating cash flows' or 'Net cash from operations').
            - Prioritize the most recent fiscal years, typically the last 3 (e.g., 2023, 2022, 2021), and order them from newest to oldest in the output list.
            - Extract values in millions, using floats for precision and rounding if necessary. Assume the primary currency is USD unless otherwise specified. Values can be positive or negative.
            - For aggregated fields like adjustments_for_non_cash_items or changes_in_working_capital: Sum relevant sub-items if broken down and directly available.
            - For net_cash_flow: If not directly stated, calculate as the sum of cash_from_operating_activities + cash_from_investing_activities + cash_from_financing_activities if those are available; set to 0.0 if unclear.
            - For ending_cash_balance: If not directly stated, calculate as beginning_cash_balance + net_cash_flow if available; set to 0.0 if unclear.
            - Ensure the output strictly adheres to the JSON schema; do not add extra fields, explanations, or narrative text.
            - If no cash flow data is found for a year, do not include that year in the list.

            Field Descriptions (use these to guide extraction):
            - year: The fiscal or calendar year as a string (e.g., '2023'). Look for headers like 'Year Ended December 31, 2023' or 'FY2022'.
            - net_income: Net income in millions from cash flow statement.
            - adjustments_for_non_cash_items: Sum of non-cash adjustments in millions.
            - changes_in_working_capital: Net changes in working capital in millions (positive or negative).
            - cash_from_operating_activities: Net operating cash flow in millions.
            - cash_from_investing_activities: Net investing cash flow in millions.
            - cash_from_financing_activities: Net financing cash flow in millions.
            - net_cash_flow: Net change in cash in millions, calculated if necessary.
            - beginning_cash_balance: Starting cash balance in millions.
            - ending_cash_balance: Ending cash balance in millions, calculated if necessary.
                            """))
        return CashFlowAgent

def main():
    # Streamlit app
    st.title("PDF Company Information Extractor")

    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

    if uploaded_file is not None:
        try:
            # Save uploaded file to a temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name

            # Initialize extractor
            extractor = PDFCompanyExtractor()

            # Extract text once
            # text = extractor.extract_text_from_pdf(tmp_path)
            with st.spinner("Extracting text from PDF..."):
                pdf_text = extractor.extract_text_from_pdf(tmp_path)
            
            st.success("Text extracted from PDF.")
            final_report = {}
            with st.spinner("Extracting company information section by section..."):
                
                status = st.status("Processing...", expanded=True)
                prompt = """You are an AI specialized in extracting data from financial docs like 10-Ks. Order newest to oldest. Output JSON only."""

                status.write("Extracting Company Info...")
                a1 = extractor.extract_company_info(pdf_text)
                a1.run(prompt=prompt)
                final_report['company_info'] = CompanyInfo.model_dump_json(a1.content,include=2)


                status.write("Extracting Financial Metrics...")
                a2 = extractor.extract_financial_metrics(pdf_text)
                a2.run(prompt=prompt)
                final_report['financial_metrics'] = FinancialMetrics.model_dump_json(a2.content,include=2)

                status.write("Extracting Balance Sheet...")
                a3 = extractor.extract_balance_sheet(pdf_text)
                a3.run(prompt=prompt)
                final_report['balance_sheet'] = BalanceSheet.model_dump_json(a3.content,include=2)

                status.write("Extracting KPIs...")
                a4 = extractor.extract_kpis(pdf_text)
                a4.run(prompt=prompt)
                final_report['kpis'] = KPIs.model_dump_json(a4.content,include=2)   

                status.write("Extracting Valuation...")
                a5 = extractor.extract_valuation(pdf_text)
                a5.run(prompt=prompt)
                final_report['valuation'] = Valuation.model_dump_json(a5.content,include=2)

                status.write("Extracting Industry Benchmarks...")
                a6 = extractor.extract_industry_benchmarks(pdf_text)
                a6.run(prompt=prompt)
                final_report['industry_benchmarks'] = IndustryBenchmarks.model_dump_json(a6.content,include=2)

                status.write("Extracting Risk Factors...")
                a7 = extractor.extract_risk_factors(pdf_text)
                a7.run(prompt=prompt)
                final_report['risk_factors'] = RiskFactors.model_dump_json(a7.content,include=2)

                status.write("Extracting Cash Flow Data...")
                a8 = extractor.extract_cash_flow(pdf_text)
                a8.run(prompt=prompt)
                final_report['cash_flow'] = CashFlowData.model_dump_json(a8.content,include=2)

                status.update(label="Extraction complete!", state="complete", expanded=False)

            st.success("All sections extracted successfully!")
            
            # Display JSON result
            st.json(final_report)

            # Extract each section one by one
            # company_info = extractor.extract_company_info(text)
            # financial_metrics = extractor.extract_financial_metrics(text)
            # balance_sheet = extractor.extract_balance_sheet(text)
            # kpis = extractor.extract_kpis(text)
            # valuation = extractor.extract_valuation(text)
            # industry_benchmarks = extractor.extract_industry_benchmarks(text)
            # risk_factors = extractor.extract_risk_factors(text)
            # cash_flow = extractor.extract_cash_flow(text)

            # # Combine into a single result
            # result = {
            #     "company_info": company_info,
            #     "financial_metrics": financial_metrics,
            #     "balance_sheet": balance_sheet,
            #     "kpis": kpis,
            #     "valuation": valuation,
            #     "industry_benchmarks": industry_benchmarks,
            #     "risk_factors": risk_factors,
            #     "cash_flow": cash_flow
            # }

            # # Display JSON result
            # st.json(result)

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

if __name__ == "__main__":
    main()
