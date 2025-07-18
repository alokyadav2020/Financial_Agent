import streamlit as st
import os
from pathlib import Path


if "role" not in st.session_state:
    st.session_state.role = None

ROLES = [None,"Admin"]

PASSWORD = os.getenv("PASSWORD")
USER = os.getenv("USER")
def login():

    # st.header("Log in")
    # role = st.selectbox("Choose your role", ROLES)
    with st.form("Login Form", clear_on_submit=True):
        st.write("Login Form")
        
        # Username and password inputs
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        # Submit button
        submit_button = st.form_submit_button("Login",use_container_width=True)
        
        # Check if the form was submitted
        if submit_button:

            if USER == username and PASSWORD == password:
                st.session_state.role = "Admin"
                st.success("Login successful!")
                st.session_state["logged_in"] = True
                st.rerun()
           


def logout():
    st.session_state.role = None
    st.rerun()


role = st.session_state.role

logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
full_reports = st.Page(os.path.join("streamlit","Full_reports.py"), title="Full Reports", icon=":material/analytics:")
ein_check = st.Page(os.path.join("streamlit","ein_check.py"), title="EIN Check",icon=":material/person_add:" )

beyond_FR_reports = st.Page(os.path.join("streamlit","beyond_financial_report.py"), title="Beyond FR", icon=":material/analytics:")
data_extract = st.Page(os.path.join("streamlit","dataextract.py"), title="Financial Data extraction", icon=":material/analytics:")


admin_1 = st.Page(os.path.join("streamlit","executive_summary.py"),title="Executive Summary",icon=":material/security:",default=(role == "Admin"),)
admin_2 = st.Page(os.path.join("streamlit","Page_3_about_industry.py"), title="About Company",icon=":material/person_add:" )
admin_3 = st.Page(os.path.join("streamlit","market_analysis.py"), title="Market Analysis Report",icon=":material/person_add:" )
admin_4 = st.Page(os.path.join("streamlit","Page_04_FNL.py"), title="Profit & Loss Analysis",icon=":material/person_add:" )
admin_5 = st.Page(os.path.join("streamlit","Page_5BalanceSheetAnalysis.py"), title="Balance Sheet Analysis",icon=":material/person_add:" )   
admin_6 = st.Page(os.path.join("streamlit","Page_6_cashFlow.py"), title="Cash Flow Analysis",icon=":material/person_add:" ) 
admin_7 = st.Page(os.path.join("streamlit","ValuationAnalyzer.py"), title="Valuation Analyzer",icon=":material/person_add:" )
admin_8 = st.Page(os.path.join("streamlit","DCFCalculator.py"), title="DCF Calculator",icon=":material/person_add:" )
admin_9 = st.Page(os.path.join("streamlit","CCACalculator.py"), title="CCA Calculator",icon=":material/person_add:" )
admin_10 = st.Page(os.path.join("streamlit","DeliveryAssuranceAgent.py"), title="Delivery Assurance Agent",icon=":material/person_add:" )
admin_11 = st.Page(os.path.join("streamlit","hc_assessment_app.py"), title="Human Capital Assessment",icon=":material/person_add:" )
admin_12 = st.Page(os.path.join("streamlit","OperationalAssessment.py"), title="Operational Assessment",icon=":material/person_add:" )
admin_13 = st.Page(os.path.join("streamlit","legal_comlince.py"), title="Legal Compliance Assessment",icon=":material/person_add:" )
admin_14 = st.Page(os.path.join("streamlit","RiskAssessment.py"), title="Risk Assessment",icon=":material/person_add:" )
admin_15 = st.Page(os.path.join("streamlit","VirtualDataRoomAgent.py"), title="Virtual Data Room Agent",icon=":material/person_add:" )


account_pages = [logout_page, full_reports,ein_check,beyond_FR_reports,data_extract]


admin_pages = [admin_1, admin_2,admin_3,admin_4,admin_5,admin_6,admin_7,admin_8,admin_9,admin_11,admin_12,admin_13,admin_14,admin_10,admin_15]




page_dict = {}

if st.session_state.role == "Admin":
    # page_dict["Admin"] =[admin_16]
    # st.markdown("---")
    page_dict["Admin"] = admin_pages

if len(page_dict) > 0:
    pg = st.navigation({"Account": account_pages} | page_dict)
else:
    pg = st.navigation([st.Page(login)])

pg.run()