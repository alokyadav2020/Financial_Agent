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
    revenue: int = Field(..., description="Total net sales, revenue, or equivalent top-line income figure (may be labeled as 'Net sales', 'Total revenue', 'Operating revenue', 'Sales revenue', etc.) reported in millions of dollars or the primary currency used in the document. Round to the nearest million if necessary.")
    cogs: int = Field(..., description="Cost of goods sold (COGS), cost of sales, or equivalent direct costs associated with producing goods or services (may be labeled as 'Cost of revenue', 'Cost of sales', 'Direct costs', etc.) in millions. This typically excludes operating expenses like SG&A.")
    operating_expenses: int = Field(..., description="Operating expenses, often including selling, general, and administrative expenses (SG&A), research and development (R&D), or other indirect costs (may be labeled as 'Operating expenses', 'Selling and administrative expenses', 'General expenses', etc.) in millions. Sum relevant sub-categories if broken down.")
    ebitda: int = Field(..., description="Earnings Before Interest, Taxes, Depreciation, and Amortization (EBITDA), which can be calculated as operating income plus depreciation and amortization if not directly stated (may be referred to as 'Adjusted EBITDA', 'EBITDA', or derived from 'Operating profit' + 'D&A'). Use the closest equivalent and report in millions.")

class FinancialMetrics(BaseModel):
    yearly_data: List[YearlyFinancialData] = Field(..., description="A list of YearlyFinancialData objects covering the last 3 available years (or fewer if not all are present), ordered from most recent to oldest. Ensure data is extracted for each year consistently from income statements or financial summaries.")

class Debt(BaseModel):
    long_term: int = Field(..., description="Long-term debt and finance lease obligations in millions")
    short_term: int = Field(..., description="Short-term debt and current portion of long-term debt in millions")

class YearlyBalanceSheet(BaseModel):
    year: str = Field(..., description="Year as string e.g. '2023'")
    total_assets: int = Field(..., description="Total assets in millions")
    total_liabilities: int = Field(..., description="Total liabilities in millions")
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
            "Agent Aim: Your primary goal is to accurately identify and extract financial metrics for the last 3 years (or available years) from the provided text, handling variations in terminology, table formats, and document structures. Focus on income statement-related data, cross-referencing sections like consolidated statements of operations, financial highlights, or management's discussion for completeness. If data is incomplete, use logical estimates based on context (e.g., calculate EBITDA if components are available) and fill all fields without leaving any blank.\n\n"
            "Instructions:\n"
            "- Scan the entire text thoroughly, including tables, footnotes, and narrative sections, to locate relevant financial data.\n"
            "- Handle synonyms and variations: Fields may use different names across documents (e.g., 'Revenue' could be 'Net sales' or 'Total income').\n"
            "- Prioritize the most recent fiscal years, typically the last 3, and order them from newest to oldest.\n"
            "- Convert all monetary values to millions (e.g., if reported in thousands, divide by 1,000; if in billions, multiply by 1,000). Round to the nearest integer.\n"
            "- If exact values are missing, derive them where possible (e.g., EBITDA = Operating Income + Depreciation + Amortization) or use 0 as a last resort.\n"
            "- Ensure the output strictly adheres to the JSON schema; do not add extra fields or explanations.\n\n"
            "Field Descriptions (use these to guide extraction):\n"
            "- year: The fiscal or calendar year as a string (e.g., '2023'). Look for headers like 'Year Ended December 31, 2023' or 'FY2022'.\n"
            "- revenue: Top-line figure like total net sales or revenue in millions.\n"
            "- cogs: Direct costs like cost of goods sold or cost of sales in millions.\n"
            "- operating_expenses: Indirect costs like SG&A or operating expenses in millions.\n"
            "- ebitda: EBITDA or calculable equivalent in millions."
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
            "You are an expert at extracting structured company information from financial documents. "
            "Extract the information accurately based on the provided text. If data is missing or unclear, "
            "use reasonable defaults or estimates where specified (e.g., 0.0 for market_share if unavailable). "
            "Ensure all fields are filled."
        )
        user_prompt = f"Extract the balance sheet from the following text:\n\n{text}"
        
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
            "You are an expert at extracting structured company information from financial documents. "
            "Extract the information accurately based on the provided text. If data is missing or unclear, "
            "use reasonable defaults or estimates where specified (e.g., 0.0 for market_share if unavailable). "
            "Ensure all fields are filled."
        )
        user_prompt = f"Extract the KPIs from the following text:\n\n{text}"
        
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
            "You are an expert at extracting structured company information from financial documents. "
            "Extract the information accurately based on the provided text. If data is missing or unclear, "
            "use reasonable defaults or estimates where specified (e.g., 0.0 for market_share if unavailable). "
            "Ensure all fields are filled."
        )
        user_prompt = f"Extract the valuation from the following text:\n\n{text}"
        
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
            "You are an expert at extracting structured company information from financial documents. "
            "Extract the information accurately based on the provided text. If data is missing or unclear, "
            "use reasonable defaults or estimates where specified (e.g., 0.0 for market_share if unavailable). "
            "Ensure all fields are filled."
        )
        user_prompt = f"Extract the industry benchmarks from the following text:\n\n{text}"
        
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
            "You are an expert at extracting structured company information from financial documents. "
            "Extract the information accurately based on the provided text. If data is missing or unclear, "
            "use reasonable defaults or estimates where specified (e.g., 0.0 for market_share if unavailable). "
            "Ensure all fields are filled."
        )
        user_prompt = f"Extract the risk factors from the following text:\n\n{text}"
        
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
            "You are an expert at extracting structured company information from financial documents. "
            "Extract the information accurately based on the provided text. If data is missing or unclear, "
            "use reasonable defaults or estimates where specified (e.g., 0.0 for market_share if unavailable). "
            "Ensure all fields are filled."
        )
        user_prompt = f"Extract the cash flow data from the following text:\n\n{text}"
        
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
            text = extractor.extract_text_from_pdf(tmp_path)

            # Extract each section one by one
            company_info = extractor.extract_company_info(text)
            financial_metrics = extractor.extract_financial_metrics(text)
            balance_sheet = extractor.extract_balance_sheet(text)
            kpis = extractor.extract_kpis(text)
            valuation = extractor.extract_valuation(text)
            industry_benchmarks = extractor.extract_industry_benchmarks(text)
            risk_factors = extractor.extract_risk_factors(text)
            cash_flow = extractor.extract_cash_flow(text)

            # Combine into a single result
            result = {
                "company_info": company_info,
                "financial_metrics": financial_metrics,
                "balance_sheet": balance_sheet,
                "kpis": kpis,
                "valuation": valuation,
                "industry_benchmarks": industry_benchmarks,
                "risk_factors": risk_factors,
                "cash_flow": cash_flow
            }

            # Display JSON result
            st.json(result)

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

if __name__ == "__main__":
    main()
