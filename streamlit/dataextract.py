import os
import json
from typing import List
from pydantic import BaseModel, Field
from openai import AzureOpenAI
# from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import PyPDF2  # Requires installation: pip install pypdf2
import streamlit as st
import tempfile
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
        deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4.1-nano")
        
        # Initialize Azure OpenAI client with Entra ID authentication
        
        
        self.client = AzureOpenAI(
            azure_endpoint=endpoint,
            azure_deployment=deployment,
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("api_version", "2024-12-01-preview"),  # Use the latest version
            
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

    def extract_company_info(self, text: str) -> dict:
        """
        Extracts company information from the provided text in the specified JSON format.
        
        :param text: Extracted text from the PDF.
        :return: Dictionary containing the extracted company information.
        """
        # Prepare the JSON schema for structured output
        schema = CompanyInfo.model_json_schema()
        strict_schema = self.make_schema_strict(schema)
        
        # Prompt for extraction
        system_prompt = (
            "You are an expert at extracting structured company information from financial documents. "
            "Extract the information accurately based on the provided text. If data is missing or unclear, "
            "use reasonable defaults or estimates where specified (e.g., 0.0 for market_share if unavailable). "
            "Ensure all fields are filled."
        )
        user_prompt = f"Extract the company info from the following text:\n\n{text}"
        
        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "company_info",
                    "strict": True,
                    "schema": strict_schema
                }
            },
            temperature=0.0
        )
        
        # Parse the JSON response
        extracted_json = json.loads(response.choices[0].message.content)
        return extracted_json

    def extract_financial_metrics(self, text: str) -> dict:
        """
        Extracts financial metrics from the provided text in the specified JSON format.
        
        :param text: Extracted text from the PDF.
        :return: Dictionary containing the extracted financial metrics.
        """
        # Prepare the JSON schema for structured output
        schema = FinancialMetrics.model_json_schema()
        strict_schema = self.make_schema_strict(schema)
        
        # Prompt for extraction
        system_prompt = (
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
        )
        user_prompt = f"Extract the financial metrics from the following text (which may be extensive):\n\n{text}"
        
        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "financial_metrics",
                    "strict": True,
                    "schema": strict_schema
                }
            },
            temperature=0.0
        )
        
        # Parse the JSON response
        extracted_json = json.loads(response.choices[0].message.content)
        return extracted_json

    def extract_balance_sheet(self, text: str) -> dict:
        """
        Extracts balance sheet from the provided text in the specified JSON format.
        
        :param text: Extracted text from the PDF.
        :return: Dictionary containing the extracted balance sheet.
        """
        # Prepare the JSON schema for structured output
        schema = BalanceSheet.model_json_schema()
        strict_schema = self.make_schema_strict(schema)
        
        # Prompt for extraction
        system_prompt = (
            "You are BalanceSheetExtractor, an AI agent specialized in parsing and extracting key balance sheet data from lengthy financial documents such as annual reports, 10-K filings, or financial statements, which may span 80-90 pages or more.\n\n"
            "Agent Aim: Your primary goal is to accurately identify and extract balance sheet metrics for the last 3 years (or available years) from the provided text, handling variations in terminology, table formats, and document structures. Focus on consolidated balance sheets or statements of financial position, cross-referencing sections like financial highlights, notes to financial statements, or management's discussion for completeness. If data is incomplete, use logical estimates based on context (e.g., sum sub-items for totals) and fill all fields without leaving any blank.\n\n"
            "Instructions:\n"
            "- Scan the entire text thoroughly, including tables, footnotes, and narrative sections, to locate relevant balance sheet data.\n"
            "- Handle synonyms and variations: Fields may use different names across documents (e.g., 'Total assets' could be 'Assets' or 'Total resources').\n"
            "- Prioritize the most recent fiscal years, typically the last 3, and order them from newest to oldest.\n"
            "- Convert all monetary values to millions (e.g., if reported in thousands, divide by 1,000; if in billions, multiply by 1,000). Round to the nearest integer.\n"
            "- If exact values are missing, derive them where possible (e.g., Total liabilities = Current liabilities + Non-current liabilities) or use 0 as a last resort.\n"
            "- Ensure the output strictly adheres to the JSON schema; do not add extra fields or explanations.\n\n"
            "Field Descriptions (use these to guide extraction):\n"
            "- year: The fiscal or calendar year as a string (e.g., '2023'). Look for headers like 'As of December 31, 2023' or 'FY2022'.\n"
            "- total_assets: Grand total of all assets in millions.\n"
            "- total_liabilities: Grand total of all liabilities in millions.\n"
            "- equity: Equity attributable to owners/stockholders in millions.\n"
            "- debt.long_term: Non-current debt obligations in millions.\n"
            "- debt.short_term: Current debt obligations in millions.\n"
            "- cash: Cash holdings and equivalents in millions."
        )
        user_prompt = f"Extract the balance sheet from the following text (which may be extensive):\n\n{text}"
        
        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "balance_sheet",
                    "strict": True,
                    "schema": strict_schema
                }
            },
            temperature=0.0
        )
        
        # Parse the JSON response
        extracted_json = json.loads(response.choices[0].message.content)
        return extracted_json

    def extract_kpis(self, text: str) -> dict:
        """
        Extracts KPIs from the provided text in the specified JSON format.
        
        :param text: Extracted text from the PDF.
        :return: Dictionary containing the extracted KPIs.
        """
        # Prepare the JSON schema for structured output
        schema = KPIs.model_json_schema()
        strict_schema = self.make_schema_strict(schema)
        
        # Prompt for extraction
        system_prompt = (
            "You are KPIsExtractor, an AI agent specialized in parsing and extracting key performance indicators (KPIs) from lengthy financial documents such as annual reports, 10-K filings, or earnings statements, which may span 80-90 pages or more.\n\n"
            "Agent Aim: Your primary goal is to accurately identify and extract KPIs for the last 3 years (or available years) from the provided text, handling variations in terminology, table formats, and document structures. Focus on financial ratios and growth metrics from income statements, balance sheets, MD&A, or key metrics sections, extracting only values that are directly stated in the document. Do not perform any calculations or derivations; assume all required values are explicitly available in the 10-K or financial documents. If a value is not directly stated, use 0.0 as specified. Fill all fields without leaving any blank.\n\n"
            "Instructions:\n"
            "- Scan the entire text thoroughly, including tables, footnotes, narrative sections, and management's discussion to locate explicitly stated KPIs.\n"
            "- Handle synonyms and variations: Fields may use different names across documents (e.g., 'Gross margin' could be 'Gross profit margin').\n"
            "- Prioritize the most recent fiscal years, typically the last 3, and order them from newest to oldest.\n"
            "- Do not calculate any values; extract only what is directly provided in the text.\n"
            "- If a value is not explicitly stated, use 0.0 as a default.\n"
            "- Ensure the output strictly adheres to the JSON schema; do not add extra fields or explanations.\n\n"
            "Field Descriptions (use these to guide extraction):\n"
            "- year: The fiscal or calendar year as a string (e.g., '2023'). Look for headers like 'Year Ended December 31, 2023' or 'FY2022'.\n"
            "- gross_margin: Gross profit margin as a percentage, directly stated.\n"
            "- operating_margin: Operating profit margin as a percentage, directly stated.\n"
            "- debt_to_equity: Total debt to equity as a ratio, directly stated.\n"
            "- current_ratio: Current assets to current liabilities as a ratio, directly stated.\n"
            "- revenue_growth: Year-over-year revenue increase as a percentage, directly stated (0 for the first year).\n"
            "- market_share: Company's share of the market as a percentage, directly stated (0.0 if not specified)."
        )
        user_prompt = f"Extract the KPIs from the following text (which may be extensive):\n\n{text}"
        
        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "kpis",
                    "strict": True,
                    "schema": strict_schema
                }
            },
            temperature=0.0
        )
        
        # Parse the JSON response
        extracted_json = json.loads(response.choices[0].message.content)
        return extracted_json

    def extract_valuation(self, text: str) -> dict:
        """
        Extracts valuation from the provided text in the specified JSON format.
        
        :param text: Extracted text from the PDF.
        :return: Dictionary containing the extracted valuation.
        """
        # Prepare the JSON schema for structured output
        schema = Valuation.model_json_schema()
        strict_schema = self.make_schema_strict(schema)
        
        # Prompt for extraction
        system_prompt = (
            "You are ValuationExtractor, an AI agent specialized in parsing and extracting valuation metrics from lengthy financial documents such as annual reports, 10-K filings, or earnings statements, which may span 80-90 pages or more.\n\n"
            "Agent Aim: Your primary goal is to accurately identify and extract valuation data from the provided text, handling variations in terminology, table formats, and document structures. Focus on valuation sections, financial highlights, or MD&A, extracting only values that are directly stated in the document. Do not perform any calculations or derivations; assume all required values are explicitly available in the 10-K or financial documents. If a value is not directly stated, use 0 or 0.0 as specified. Fill all fields without leaving any blank.\n\n"
            "Instructions:\n"
            "- Scan the entire text thoroughly, including tables, footnotes, narrative sections, and management's discussion to locate explicitly stated valuation data.\n"
            "- Handle synonyms and variations: Fields may use different names across documents (e.g., 'Enterprise value' could be 'EV' or 'Total firm value').\n"
            "- Do not calculate any values; extract only what is directly provided in the text.\n"
            "- If a value is not explicitly stated, use 0 or 0.0 as a default.\n"
            "- Ensure the output strictly adheres to the JSON schema; do not add extra fields or explanations.\n\n"
            "Field Descriptions (use these to guide extraction):\n"
            "- enterprise_value: Enterprise value in millions, directly stated.\n"
            "- ev_ebitda_multiple: EV to EBITDA multiple as a decimal, directly stated.\n"
            "- valuation_range.low: Low end of valuation range in millions, directly stated.\n"
            "- valuation_range.high: High end of valuation range in millions, directly stated."
        )
        user_prompt = f"Extract the valuation from the following text (which may be extensive):\n\n{text}"
        
        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "valuation",
                    "strict": True,
                    "schema": strict_schema
                }
            },
            temperature=0.0
        )
        
        # Parse the JSON response
        extracted_json = json.loads(response.choices[0].message.content)
        return extracted_json

    def extract_industry_benchmarks(self, text: str) -> dict:
        """
        Extracts industry benchmarks from the provided text in the specified JSON format.
        
        :param text: Extracted text from the PDF.
        :return: Dictionary containing the extracted industry benchmarks.
        """
        # Prepare the JSON schema for structured output
        schema = IndustryBenchmarks.model_json_schema()
        strict_schema = self.make_schema_strict(schema)
        
        # Prompt for extraction
        system_prompt = (
            "You are IndustryBenchmarksExtractor, an AI agent specialized in parsing and extracting industry benchmark metrics from lengthy financial documents such as annual reports, 10-K filings, or earnings statements, which may span 80-90 pages or more.\n\n"
            "Agent Aim: Your primary goal is to accurately identify and extract automotive industry benchmarks from the provided text, handling variations in terminology, table formats, and document structures. Focus on industry comparison sections, MD&A, or key metrics tables, extracting only values that are directly stated in the document. Do not perform any calculations or derivations; assume all required values are explicitly available in the 10-K or financial documents. If a value is not directly stated, use 0.0 as specified. Fill all fields without leaving any blank.\n\n"
            "Instructions:\n"
            "- Scan the entire text thoroughly, including tables, footnotes, narrative sections, and management's discussion to locate explicitly stated industry benchmarks.\n"
            "- Handle synonyms and variations: Fields may use different names across documents (e.g., 'Average gross margin' could be 'Industry gross profit margin avg').\n"
            "- Do not calculate any values; extract only what is directly provided in the text.\n"
            "- If a value is not explicitly stated, use 0.0 as a default.\n"
            "- Ensure the output strictly adheres to the JSON schema; do not add extra fields or explanations.\n\n"
            "Field Descriptions (use these to guide extraction):\n"
            "- avg_gross_margin: Average gross margin % for automotive industry, directly stated.\n"
            "- avg_operating_margin: Average operating margin % for automotive industry, directly stated.\n"
            "- avg_debt_to_equity: Average debt to equity ratio for automotive industry, directly stated.\n"
            "- avg_revenue_growth: Average revenue growth % for automotive industry, directly stated."
        )
        user_prompt = f"Extract the industry benchmarks from the following text (which may be extensive):\n\n{text}"
        
        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "industry_benchmarks",
                    "strict": True,
                    "schema": strict_schema
                }
            },
            temperature=0.0
        )
        
        # Parse the JSON response
        extracted_json = json.loads(response.choices[0].message.content)
        return extracted_json
    
    def extract_risk_factors(self, text: str) -> dict:
        """
        Extracts risk factors from the provided text in the specified JSON format.
        
        :param text: Extracted text from the PDF.
        :return: Dictionary containing the extracted risk factors.
        """
        # Prepare the JSON schema for structured output
        schema = RiskFactors.model_json_schema()
        strict_schema = self.make_schema_strict(schema)
        
        # Prompt for extraction
        system_prompt = (
            "You are RiskFactorsExtractor, an AI agent specialized in parsing and extracting risk factors from lengthy financial documents such as annual reports, 10-K filings, or earnings statements, which may span 80-90 pages or more.\n\n"
            "Agent Aim: Your primary goal is to accurately identify and extract risk factors from the provided text, handling variations in terminology, table formats, and document structures. Focus on the 'Risk Factors' section, MD&A, or related disclosures, extracting based on direct mentions or descriptions in the document. Do not perform any calculations or external inferences; base assessments solely on the text provided. If a risk is not directly mentioned or described, set booleans to False and levels to 'medium' as default. Fill all fields without leaving any blank.\n\n"
            "Instructions:\n"
            "- Scan the entire text thoroughly, including risk factors sections, footnotes, narrative descriptions, and management's discussion to locate explicitly mentioned or described risks.\n"
            "- Handle synonyms and variations: Risks may be phrased differently across documents (e.g., 'customer concentration' could be 'reliance on key customers').\n"
            "- Set boolean fields to True only if the risk is directly discussed as significant; otherwise False.\n"
            "- For string levels (debt_level, market_cyclicality), use the described intensity ('low', 'medium', 'high') or default to 'medium' if unclear.\n"
            "- Ensure the output strictly adheres to the JSON schema; do not add extra fields or explanations.\n\n"
            "Field Descriptions (use these to guide extraction):\n"
            "- high_customer_concentration: True if high customer concentration risk is directly mentioned or described.\n"
            "- geographic_concentration: True if geographic concentration risk is directly mentioned or described.\n"
            "- supply_chain_dependency: True if supply chain dependency risk is directly mentioned or described.\n"
            "- debt_level: Debt level assessment as 'low', 'medium', or 'high', directly from text or default 'medium'.\n"
            "- market_cyclicality: Market cyclicality assessment as 'low', 'medium', or 'high', directly from text or default 'medium'."
        )
        user_prompt = f"Extract the risk factors from the following text (which may be extensive):\n\n{text}"
        
        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "risk_factors",
                    "strict": True,
                    "schema": strict_schema
                }
            },
            temperature=0.0
        )
        
        # Parse the JSON response
        extracted_json = json.loads(response.choices[0].message.content)
        return extracted_json

    def extract_cash_flow(self, text: str) -> dict:
        """
        Extracts cash flow data from the provided text in the specified JSON format.
        
        :param text: Extracted text from the PDF.
        :return: Dictionary containing the extracted cash flow data.
        """
        # Prepare the JSON schema for structured output
        schema = CashFlowData.model_json_schema()
        strict_schema = self.make_schema_strict(schema)
        
        # Prompt for extraction
        system_prompt = (
            "You are CashFlowExtractor, an AI agent specialized in parsing and extracting cash flow statement data from lengthy financial documents such as annual reports, 10-K filings, or financial statements, which may span 80-90 pages or more.\n\n"
            "Agent Aim: Your primary goal is to accurately identify and extract cash flow metrics for the last 3 years (or available years) from the provided text, handling variations in terminology, table formats, and document structures. Focus on consolidated statements of cash flows, cross-referencing sections like financial highlights, notes to financial statements, or management's discussion for completeness. If data is incomplete, use logical estimates based on context (e.g., sum sub-items for adjustments or changes) and fill all fields without leaving any blank.\n\n"
            "Instructions:\n"
            "- Scan the entire text thoroughly, including tables, footnotes, and narrative sections, to locate relevant cash flow data.\n"
            "- Handle synonyms and variations: Fields may use different names across documents (e.g., 'Net cash from operations' could be 'Cash provided by operating activities').\n"
            "- Prioritize the most recent fiscal years, typically the last 3, and order them from newest to oldest.\n"
            "- Convert all monetary values to millions (e.g., if reported in thousands, divide by 1,000; if in billions, multiply by 1,000). Use floats to preserve decimals if present, rounding appropriately.\n"
            "- If exact values are missing, derive them where possible (e.g., Adjustments = sum of depreciation + amortization + other non-cash items; Net cash flow = operating + investing + financing) or use 0.0 as a last resort.\n"
            "- Ensure the output strictly adheres to the JSON schema; do not add extra fields or explanations.\n\n"
            "Field Descriptions (use these to guide extraction):\n"
            "- year: The fiscal or calendar year as a string (e.g., '2023'). Look for headers like 'Year Ended December 31, 2023' or 'FY2022'.\n"
            "- net_income: Starting net income in millions.\n"
            "- adjustments_for_non_cash_items: Sum of non-cash adjustments in millions.\n"
            "- changes_in_working_capital: Net changes in working capital in millions.\n"
            "- cash_from_operating_activities: Operating cash flow subtotal in millions.\n"
            "- cash_from_investing_activities: Investing cash flow subtotal in millions.\n"
            "- cash_from_financing_activities: Financing cash flow subtotal in millions.\n"
            "- net_cash_flow: Net change in cash in millions.\n"
            "- beginning_cash_balance: Cash at period start in millions.\n"
            "- ending_cash_balance: Cash at period end in millions."
        )
        user_prompt = f"Extract the cash flow data from the following text (which may be extensive):\n\n{text}"
        
        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "cash_flow",
                    "strict": True,
                    "schema": strict_schema
                }
            },
            temperature=0.0
        )
        
        # Parse the JSON response
        extracted_json = json.loads(response.choices[0].message.content)
        return extracted_json

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

                status.write("Extracting Company Info...")
                final_report['company_info'] = extractor.extract_company_info(pdf_text)
                
                status.write("Extracting Financial Metrics...")
                final_report['financial_metrics'] = extractor.extract_financial_metrics(pdf_text)
                
                status.write("Extracting Balance Sheet...")
                final_report['balance_sheet'] = extractor.extract_balance_sheet(pdf_text)

                status.write("Extracting KPIs...")
                final_report['kpis'] = extractor.extract_kpis(pdf_text)

                status.write("Extracting Valuation...")
                final_report['valuation'] = extractor.extract_valuation(pdf_text)

                status.write("Extracting Industry Benchmarks...")
                final_report['industry_benchmarks'] = extractor.extract_industry_benchmarks(pdf_text)

                status.write("Extracting Risk Factors...")
                final_report['risk_factors'] = extractor.extract_risk_factors(pdf_text)
                
                status.write("Extracting Cash Flow Data...")
                final_report['cash_flow'] = extractor.extract_cash_flow(pdf_text)

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
