import streamlit as st
# from src.report_generator import generate_full_report
from src.executive_summary import generate_executive_summary_full
from src.Page_3_about_industry import analyze_website
from src.market_analysis import generate_market_analysis
from src.Page_04_FNL import pnl_reports
from src.Page_5BalanceSheetAnalysis import balancesheet
from src.Page_6_cashFlow import cashflow
from src.ValuationAnalyzer import valuationreports_
from src.DCFCalculator import dcf_analysis_report
from src.CCACalculator import cca_report
from src.hc_assessment_app import hc_reports
from src.OperationalAssessment import operationassessment
from src.legal_comlince import legal_compliance_assessment
from src.RiskAssessment import risk_assessment_report



def main():
    st.set_page_config(page_title="Complete Business Report", layout="wide")    # Main title with styling
    st.markdown("""
    <style>
    /* Global Typography */
    body, .full-report, .section, .section-content, .main-header, .section h1, .section h2, .section h3, .section h4, .section h5, .section h6, .section table, .section table th, .section table td {
        font-family: 'Arial', sans-serif !important;
        font-size: 14px !important;
        line-height: 1.5 !important;
        color: #2c3e50;
        font-weight: 400 !important;
    }
    
    /* Main Header */
    .main-header {
        text-align: center;
        padding: 20px;
        background-color: #f0f2f6;
        border-radius: 12px;
        margin-bottom: 24px;
    }
    .main-header h1 {
        font-size: 18px !important;
        font-weight: 400 !important;
        color: #1f77b4;
        margin: 0;
    }
    
    /* Sections */
    .section {
        padding: 24px;
        background-color: white;
        border-radius: 10px;
        margin: 20px 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.08);
    }
    
    /* Headings Hierarchy */
    .section h1 {
        font-size: 15px !important;
        font-weight: 400 !important;
        color: #1f77b4;
        margin: 0 0 10px 0;
    }
    .section h2.section-title {
        font-size: 14px !important;
        font-weight: 400 !important;
        color: #1f77b4;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 6px;
        margin-bottom: 10px;
        text-align: left;
    }
    .section h3.subsection-title {
        font-size: 13px !important;
        font-weight: 400 !important;
        color: #2c3e50;
        margin: 10px 0;
        padding-bottom: 4px;
        border-bottom: 1px solid #e0e0e0;
    }
    .section-content {
        padding: 10px 0;
        line-height: 1.5;
    }
    .section-content strong, .section-content b {
        color: #2c3e50;
        font-weight: 400 !important;
    }
    .section-content p {
        margin: 8px 0;
        line-height: 1.5;
    }
    .section-content ul, .section-content ol {
        margin: 8px 0;
        padding-left: 18px;
    }
    .section-content li {
        margin: 4px 0;
        line-height: 1.4;
    }
    .section table {
        width: 100%;
        border-collapse: collapse;
        margin: 10px 0;
    }
    .section table th, .section table td {
        padding: 6px;
        border: 1px solid #ddd;
        text-align: left;
        font-size: 13px !important;
        font-weight: 400 !important;
    }
    .section table th {
        background-color: #f5f7fa;
    }
    /* Code blocks and pre */
    .section pre, .section code {
        font-family: 'Consolas', 'Monaco', monospace !important;
        font-size: 12px !important;
        background-color: #f8f9fa;
        border-radius: 4px;
        padding: 8px;
        border: 1px solid #e9ecef;
        overflow-x: auto;
        font-weight: 400 !important;
    }
    /* Lists with better visual hierarchy */
    .section ul, .section ol {
        margin: 8px 0;
        padding-left: 18px;
    }
    .section ul li, .section ol li {
        margin: 4px 0;
        padding-left: 2px;
    }
    .section ul li::marker {
        color: #1f77b4;
    }
    /* Better section separation */
    .section + .section {
        margin-top: 24px;
        border-top: 2px solid #f0f2f6;
        padding-top: 24px;
    }
    /* Blockquotes */
    .section blockquote {
        margin: 12px 0;
        padding: 10px 14px;
        border-left: 4px solid #1f77b4;
        background-color: #f8f9fa;
        font-style: italic;
        font-size: 13px !important;
        font-weight: 400 !important;
    }
    </style>
    <div class="main-header">
        <h1>Complete Business Report Generator</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for inputs
    with st.sidebar:


        st.subheader("Report Configuration")
        with st.container(border=True):
            st.markdown("### Company Information")
            # Company information inputs
            company_name = st.text_input("Company Name", "Acme Manufacturing")
            industry = st.text_input("Industry", "Industrial Components")
            website_url = st.text_input("Company Website", "https://acmemfg.com/")
            # Phase selection
        phases = {
            "Phase 1": "Organizational Structure and Workforce Analysis",
            "Phase 2": "Compensation, Benefits, and Talent Development",
            "Phase 3": "Human Capital Risks and Strategic Alignment",
            "Phase 4": "Synthesis and Output"
        }

       

        # Task selection based on phase
        tasks = {
            "Phase 1": ["Task 1: Analyze Organizational Structure", 
                        "Task 2: Analyze Employee Metrics"],
            "Phase 2": ["Task 3: Analyze Compensation and Benefits", 
                        "Task 4: Evaluate Talent Development and Training"],
            "Phase 3": ["Task 5: Identify Human Capital Risks", 
                        "Task 6: Assess Strategic Alignment"],
            "Phase 4": ["Task 7: Synthesize Findings", 
                        "Task 8: Develop Strategic Moves", 
                        "Task 9: Create Assessment Report"]
        }


        with st.container(border=True):
            st.header("Human Capital Assessment", divider=True)

            selected_phase_hc = st.selectbox(
                "Select Analysis Phase",
                list(phases.keys()),
                format_func=lambda x: f"{x}: {phases[x]}"
            )

            selected_task_hc = st.selectbox(
                "Select Task",
                tasks[selected_phase_hc]
            )
        

        phases_operation = {
            "Phase 1": {
                "name": "Business Process Analysis",
                "tasks": {
                    "Task 1": "Identify and Document Key Operational Workflows",
                    "Task 2": "Create Process Flow Diagrams"
                }
            },
            "Phase 2": {
                "name": "Supply Chain Analysis",
                "tasks": {
                    "Task 3": "Analyze Supply Chain Structure",
                    "Task 4": "Map the Supply Chain",
                    "Task 5": "Assess Supply Chain Risks and Vulnerabilities"
                }
            },
            "Phase 3": {
                "name": "Performance Assessment and Benchmarking",
                "tasks": {
                    "Task 6": "Identify Key Operational Performance Indicators (KPIs)",
                    "Task 7": "Benchmark Performance"
                }
            },
            "Phase 4": {
                "name": "Synthesis and Output",
                "tasks": {
                    "Task 8": "Synthesize Findings and Identify Strategic Operational Moves",
                    "Task 9": "Create Operational Assessment Report"
                }
            }
        }

        with st.container(border=True):
            st.header("Operational Assessment", divider=True)

            # selected_phase = st.selectbox(
            #     "Select Analysis Phase",
            #     list(phases.keys()),
            #     format_func=lambda x: f"{x}: {phases[x]}"
            # )

            # selected_task = st.selectbox(
            #     "Select Task",
            #     tasks[selected_phase]
            # )

            selected_phase_operation = st.selectbox(
                "Select Phase",
                list(phases_operation.keys()),
                format_func=lambda x: f"{x}: {phases_operation[x]['name']}"
            )

            selected_task_operation = st.selectbox(
                "Select Task",
                list(phases_operation[selected_phase_operation]['tasks'].keys()),
                format_func=lambda x: f"{x}: {phases_operation[selected_phase_operation]['tasks'][x]}"
            )

            industry_context = st.text_input(
            "Industry Context (Optional)",
            placeholder="e.g., Manufacturing, Technology, Healthcare"
        )
        phases_legal = {
            "Phase 1": {
                "name": "Corporate Governance",
                "tasks": {
                    "Task 1": "Analyze Corporate Governance Structure"
                }
            },
            "Phase 2": {
                "name": "Regulatory Compliance",
                "tasks": {
                    "Task 2": "Assess Regulatory Compliance"
                }
            },
            "Phase 3": {
                "name": "Litigation History and Legal Risks",
                "tasks": {
                    "Task 3": "Analyze Litigation History and Legal Risks"
                }
            },
            "Phase 4": {
                "name": "Synthesis and Output",
                "tasks": {
                    "Task 4": "Synthesize Findings and Identify Key Issues",
                    "Task 5": "Develop Questions for Leadership",
                    "Task 6": "Create Legal and Compliance Assessment Report"
                }
            }
        }

        with st.container(border=True):
                st.header("Legal comlince", divider=True)
                
                company_type = st.selectbox(
            "Select Company Type",
            ["Public Company", "Private Company", "Multinational Corporation", "Start-up"]
        )
                selected_phase_legal = st.selectbox(
                "Select Phase",
                list(phases_legal.keys()),
                format_func=lambda x: f"{x}: {phases_legal[x]['name']}"
            )
                selected_task_legal = st.selectbox(
                "Select Task",
                list(phases_legal[selected_phase_legal]['tasks'].keys()),
                format_func=lambda x: f"{x}: {phases_legal[selected_phase_legal]['tasks'][x]}"
            )
                
        phases_risk = {
            "Phase 1": {
                "name": "Business Process Analysis",
                "tasks": {
                    "Task 1": "Identify and Document Key Operational Workflows",
                    "Task 2": "Create Process Flow Diagrams"
                }
            },
            "Phase 2": {
                "name": "Supply Chain Analysis",
                "tasks": {
                    "Task 3": "Analyze Supply Chain Structure",
                    "Task 4": "Map the Supply Chain",
                    "Task 5": "Assess Supply Chain Risks and Vulnerabilities"
                }
            },
            "Phase 3": {
                "name": "Performance Assessment and Benchmarking",
                "tasks": {
                    "Task 6": "Identify Key Operational Performance Indicators (KPIs)",
                    "Task 7": "Benchmark Performance"
                }
            },
            "Phase 4": {
                "name": "Synthesis and Output",
                "tasks": {
                    "Task 8": "Synthesize Findings and Identify Strategic Operational Moves",
                    "Task 9": "Create Operational Assessment Report"
                }
            }
        }   

        with st.container(border=True):
            st.header("Risk Assessment", divider=True)
            industry_type = st.selectbox(
        "Select Target Industry",
        ["Manufacturing", "Technology", "Services"],
        key="industry_select" # Add key for stability
    )     
            selected_phase_resk = st.selectbox(
        "Select Assessment Phase",
        list(phases_risk.keys()),
        format_func=lambda x: f"{x}: {phases_risk[x]['name']}",
        key="phase_select"
    )
            available_tasks = phases_risk[selected_phase_resk]['tasks']
            selected_task_risk = st.selectbox(
                "Select Specific Task",
                list(available_tasks.keys()),
                format_func=lambda x: f"{x}: {available_tasks[x]}",
                key="task_select"
            )
            
            # Generate report button
        generate_all = st.button("Generate Complete Report", use_container_width=True)
    
    if generate_all:
        with st.spinner("Generating comprehensive report..."):
            # Generate executive summary
            executive_summary = generate_executive_summary_full()
            
            if executive_summary:
                with st.container(border=True):
                    st.header("Executive Summary", divider=True)
                    st.markdown(executive_summary, unsafe_allow_html=True)
                # st.markdown(f"<h2>Executive Summary""</h2>", unsafe_allow_html=True)
                # st.markdown(executive_summary, unsafe_allow_html=True)
            else:
                st.error("Failed to generate executive summary. Please check your inputs.")
            IndustryAnalyzer = analyze_website(website_url)
            if IndustryAnalyzer:
                with st.container(border=True):
                    st.header(f"Industry Analysis for {website_url}", divider=True)
                    st.markdown(IndustryAnalyzer, unsafe_allow_html=True)   
            else:
                st.error("Failed to analyze the website. Please check the URL.")

            market_analysis_report = generate_market_analysis(industry)
            if market_analysis_report:
                with st.container(border=True):
                    st.header(f"Market Analysis for {industry}", divider=True)
                    st.markdown(market_analysis_report, unsafe_allow_html=True)
            else:
                st.error("Failed to generate market analysis report. Please check your inputs.")  

            pnl_reports_ = pnl_reports()
            if pnl_reports_:
                with st.container(border=True):
                    st.header("Profit & Loss Analysis", divider=True)
                    st.markdown(pnl_reports_, unsafe_allow_html=True)


            balancesheet_ = balancesheet()
            if balancesheet_:   
                with st.container(border=True):
                    st.header("Balance Sheet Analysis", divider=True)
                    st.markdown(balancesheet_, unsafe_allow_html=True)  

            cashflow_reports_ = cashflow()
            if cashflow_reports_:   
                with st.container(border=True):
                    st.header("Cash Flow Analysis", divider=True)
                    st.markdown(cashflow_reports_, unsafe_allow_html=True)              

            valuation_reports = valuationreports_()
            if valuation_reports:
                with st.container(border=True):
                    st.header("Valuation Analysis", divider=True)
                    st.markdown(valuation_reports, unsafe_allow_html=True)

            dcf_analysis = dcf_analysis_report()
            if dcf_analysis:
                with st.container(border=True):
                    st.header("Discounted Cash Flow Analysis", divider=True)
                    st.markdown(dcf_analysis, unsafe_allow_html=True)
            else:
                st.error("Failed to generate DCF analysis report. Please check your inputs.")

            cca_reprot_calculator = cca_report()
            if cca_reprot_calculator:
                with st.container(border=True):
                    st.header("Comparable Company Analysis", divider=True)
                    st.markdown(cca_reprot_calculator, unsafe_allow_html=True)
            else:
                st.error("Failed to generate CCA analysis report. Please check your inputs.")

      
        hc_reports_ = hc_reports(selected_phase_hc, 
                        selected_task_hc)
        if hc_reports_:
            with st.container(border=True):
                st.header("Human Capital Assessment", divider=True)
                st.markdown(hc_reports_, unsafe_allow_html=True)
        else:
            st.error("Failed to generate Human Capital Assessment report. Please check your inputs.")


        operationassessment_ = operationassessment(selected_phase_operation,
                        selected_task_operation,
                        industry_context)   
        if operationassessment_:
            with st.container(border=True):
                st.header("Operational Assessment", divider=True)
                st.markdown(operationassessment_, unsafe_allow_html=True)
        else:
            st.error("Failed to generate Operational Assessment report. Please check your inputs.")

        legal_compliance_assessment_ = legal_compliance_assessment(selected_phase_legal, selected_task_legal,company_type)
        if legal_compliance_assessment_:
            with st.container(border=True):
                st.header("Legal Compliance Assessment", divider=True)
                st.markdown(legal_compliance_assessment_, unsafe_allow_html=True)
        else:
            st.error("Failed to generate Legal Compliance Assessment report. Please check your inputs.")  



        risk_assessment_report_ = risk_assessment_report(selected_phase_resk, selected_task_risk, industry_type)
        if risk_assessment_report_:
            with st.container(border=True):
                st.header("Risk Assessment Report", divider=True)
                st.markdown(risk_assessment_report_, unsafe_allow_html=True)
        else:
            st.error("Failed to generate Risk Assessment report. Please check your inputs.")
        










if __name__ == "__main__":
    main()