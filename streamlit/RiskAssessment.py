# Your provided code is structurally correct.
# Ensure you restart the Streamlit application fully
# after making changes to the OperationalAssessment class.

import streamlit as st
from huggingface_hub import InferenceClient
# Using a fixed datetime for demonstration as requested
from datetime import datetime

class OperationalAssessment:
    def __init__(self):
        # Use st.secrets for sensitive information like API keys
        # Ensure you have hf_token and hf_model defined in your Streamlit secrets
        try:
            self.client = InferenceClient(
                provider="hf-inference",
                model=st.secrets["hf_model"], # Added model here for clarity, though chat_completion needs it too
                token=st.secrets["hf_token"] # Use token argument
            )
            self.model_name = st.secrets["hf_model"]
        except KeyError as e:
            st.error(f"Missing Streamlit secret: {e}. Please add 'hf_token' and 'hf_model' to your secrets.")
            st.stop()
        except Exception as e:
            st.error(f"Failed to initialize HuggingFace client: {e}")
            st.stop()

        self.phases = {
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

    def get_default_prompt(self, phase, task, industry_type="Manufacturing"):
        """Get default prompt template based on phase, task, and industry type."""
        industry_specifics = {
            "Manufacturing": {
                "processes": "production lines, assembly, quality control",
                "metrics": "OEE, yield rates, cycle time",
                "supply_chain": "raw materials, WIP, finished goods"
            },
            "Technology": {
                "processes": "software development lifecycle (SDLC), agile sprints, CI/CD pipelines, testing automation, infrastructure provisioning",
                "metrics": "deployment frequency, lead time for changes, change failure rate, mean time to recovery (MTTR), bug detection rate, system uptime/availability (SLAs/SLOs)",
                "supply_chain": "cloud provider services (IaaS, PaaS, SaaS), third-party APIs, open-source libraries, hardware procurement (servers, network gear), data center management"
            },
            "Services": {
                "processes": "client onboarding, service delivery workflows, project management, customer support ticketing, knowledge base management, quality assurance checks",
                "metrics": "customer satisfaction (CSAT/NPS), first call resolution (FCR), average handling time (AHT), service level agreement (SLA) adherence, ticket backlog, employee utilization rate",
                "supply_chain": "subcontractor management, technology platforms (CRM, ERP, ticketing systems), professional development resources, partner ecosystems"
            }
        }

        # Use get with a default to avoid KeyError if industry_type is unexpected
        specs = industry_specifics.get(industry_type, industry_specifics["Manufacturing"])

        # Using f-strings directly within the dictionary for cleaner formatting
        prompts = {
            "Task 1": f"""
Analyze the key operational workflows for a '{industry_type}' company. Focus on:
1.  **Core Processes:** Detail the primary value-delivery workflows (e.g., {specs['processes']}). Map the sequence of activities, inputs, outputs, and responsible parties for each.
2.  **Support Processes:** Identify critical supporting workflows (e.g., IT support, HR onboarding for operational roles, maintenance).
3.  **Management Processes:** Describe operational planning, performance monitoring, and decision-making processes.
4.  **Interactions & Dependencies:** Analyze handoffs and dependencies between different workflows. Identify potential bottlenecks or communication gaps.

Provide specific insights on efficiency, clarity of roles, and potential areas for optimization or automation, tailored to the '{industry_type}' context.
""",
            "Task 2": f"""
Create high-level process flow diagrams (using standard flowchart notation conceptually - describe the flow) for the most critical operational workflows identified in Task 1 for a '{industry_type}' company. For each diagram, clearly illustrate:
1.  **Sequence of Activities:** Major steps involved.
2.  **Decision Points:** Key forks in the process (e.g., quality checks, approval gates).
3.  **Information Flows:** Critical data exchanges (e.g., order details, production specs, support tickets).
4.  **Resource Allocation (Conceptual):** Note where key resources (personnel, equipment, systems - specific to {specs['processes']}) are utilized.

Highlight areas prone to delays, errors, or inefficiencies based on the visual flow, considering '{industry_type}' best practices.
""",
            "Task 3": f"""
Analyze the end-to-end supply chain structure for this '{industry_type}' company:
1.  **Supplier Network:** Identify key suppliers (materials, components, software, services, data). Assess supplier concentration risk (reliance on few suppliers), geographic distribution, and supplier relationship management practices. For {industry_type}, consider specifics like {specs['supply_chain']}.
2.  **Internal Operations / Production Network:** Detail the company's footprint (locations of factories, data centers, service centers). Analyze capacity, utilization, technology level, and degree of vertical integration.
3.  **Distribution Network:** Describe how the product/service reaches the end customer (e.g., direct sales, distributors, e-commerce, APIs, service teams). Analyze logistics partners, transportation modes (if applicable), and channel effectiveness.
4.  **Inventory/Resource Management:** Evaluate practices for managing key resources (e.g., {specs['supply_chain']}). Analyze inventory levels, turnover rates, lead times, and potential obsolescence (physical or technological).

Focus on identifying structural strengths, weaknesses, potential cost savings, and risks related to resilience and efficiency within the '{industry_type}' context.
""",
            "Task 4": f"""
Conceptually map the supply chain for the '{industry_type}' company, illustrating the key flows:
1.  **Material/Service Flow:** Visualize the path from raw inputs/suppliers through internal operations/transformation to the end customer. Include key stages like {specs['supply_chain']}.
2.  **Information Flow:** Map the critical data exchanges that enable the supply chain (e.g., forecasts, orders, inventory levels, delivery status, customer feedback). Identify key systems involved (ERP, SCM, CRM, Ticketing).
3.  **Financial Flow:** Outline the flow of payments between entities (customer payments, supplier payments, logistics costs).
4.  **Key Relationships:** Identify the primary entities (Tier 1/2 suppliers, internal departments, logistics providers, key distributors/partners, end customers) and the nature of their connections.

The goal is to provide a clear visual understanding (described textually) of the interconnectedness and complexity of the '{industry_type}' supply chain.
""",
            "Task 5": f"""
Assess the key supply chain risks and vulnerabilities specific to this '{industry_type}' company:
1.  **Supplier Risks:** Evaluate risks associated with key suppliers (financial instability, quality issues, concentration, geopolitical factors, ethical sourcing).
2.  **Operational Risks:** Analyze risks within the company's own operations (e.g., production disruptions, capacity constraints, quality failures, cybersecurity breaches affecting operations, infrastructure outages for {industry_type}).
3.  **Demand/Customer Risks:** Assess risks related to demand forecasting errors, changing customer preferences, or major customer dependency.
4.  **Logistics/Distribution Risks:** Evaluate risks in transportation, warehousing, or final delivery/service provision (e.g., delays, damage, partner failures).
5.  **External Risks:** Consider broader risks like natural disasters, pandemics, regulatory changes, economic downturns, and significant technological shifts impacting the '{industry_type}' supply chain.

For each significant risk identified, propose specific, actionable mitigation strategies (e.g., dual sourcing, safety stock, contingency planning, enhanced cybersecurity, contract negotiation, scenario planning).
""",
            "Task 6": f"""
Identify and prioritize the Key Performance Indicators (KPIs) essential for measuring operational performance in this '{industry_type}' company. Categorize them and provide industry context:
1.  **Efficiency Metrics:** Examples: {specs['metrics']}, labor productivity, resource utilization, process cycle time. Define how they apply in '{industry_type}'.
2.  **Quality Metrics:** Examples: Defect rates, first-pass yield, error rates, rework levels, customer-reported issues (bugs, service failures), adherence to SLAs/standards. Define for '{industry_type}'.
3.  **Cost Metrics:** Examples: Cost per unit/service, cost of goods sold (COGS), operational expenditure (OpEx) breakdown (labor, materials, overhead, cloud spend), cost of quality (prevention, appraisal, failure). Define for '{industry_type}'.
4.  **Delivery/Responsiveness Metrics:** Examples: On-time delivery/deployment, order/ticket fulfillment time, lead times, system availability/uptime. Define for '{industry_type}'.
5.  **Inventory/Resource Metrics (If Applicable):** Examples: Inventory turnover, days of supply, resource utilization rates, obsolescence rate. Define for '{industry_type}'.

Justify the selection of the top 5-7 *most critical* KPIs for strategic monitoring in this specific '{industry_type}' context. Suggest target ranges based on industry benchmarks if possible.
""",
            "Task 7": f"""
Benchmark the operational performance of the '{industry_type}' company using the critical KPIs identified in Task 6.
1.  **Data Collection:** Outline hypothetical or typical performance data for the company on its key KPIs (e.g., current OEE is 65%, deployment frequency is weekly, CSAT is 80%).
2.  **Benchmark Identification:** Identify relevant industry benchmarks (e.g., typical OEE in {industry_type} is 75%, best-in-class is 85%; leading tech firms deploy multiple times per day; top service firms achieve >90% CSAT). Cite sources conceptually (e.g., industry reports, consulting studies).
3.  **Competitor Comparison (Conceptual):** Briefly compare against known direct competitors if possible (e.g., Competitor A is known for faster delivery times).
4.  **Gap Analysis:** Clearly identify the performance gaps between the company and benchmarks/best practices for each key KPI (e.g., 10% gap in OEE, significantly lower deployment frequency).
5.  **Root Cause Hypothesis:** Briefly hypothesize potential root causes for the major performance gaps based on insights from earlier phases (e.g., outdated machinery, inefficient development pipeline, inadequate training).

Focus on quantifying the performance gaps related to {specs['metrics']} and identifying the most significant areas where the company lags.
""",
            "Task 8": f"""
Synthesize the findings from the entire operational assessment (Phases 1-3) for this '{industry_type}' company. Identify 3-5 high-impact, strategic operational moves to drive improvement:
1.  **Summarize Key Findings:** Briefly reiterate the major strengths, weaknesses, opportunities, and threats (SWOT) identified in processes, supply chain, and performance. Link weaknesses to performance gaps.
2.  **Propose Strategic Moves:** Define specific, actionable initiatives. Examples:
    *   *(Manufacturing Example):* Implement Lean Manufacturing principles on Assembly Line X to target a 15% reduction in cycle time.
    *   *(Technology Example):* Adopt a full CI/CD pipeline for Product Y to increase deployment frequency from weekly to daily.
    *   *(Services Example):* Develop a tiered customer support model with dedicated teams for enterprise clients to improve FCR by 20%.
3.  **Justification & Alignment:** Explain the rationale for each move, linking it to specific findings and the overall business strategy (e.g., cost reduction, market share growth, customer retention).
4.  **Define KPIs for Tracking:** For each strategic move, define 1-2 clear KPIs to measure its success and set specific, measurable, achievable, relevant, and time-bound (SMART) targets (e.g., "Reduce cycle time by 15% within 12 months," "Increase deployment frequency to daily within 6 months," "Improve FCR for enterprise clients by 20% within 9 months").

Prioritize these moves based on potential impact and feasibility.
""",
            "Task 9": f"""
Structure and outline the content for a final Operational Assessment Report for this '{industry_type}' company, following MBB standards. The report should be suitable for inclusion in a due diligence package.
1.  **Executive Summary:** (1-2 pages) High-level overview of the assessment scope, key findings (major strengths, critical weaknesses/risks), summary of proposed strategic moves, and potential financial/operational impact. Target audience: Senior executives/investors.
2.  **Business Process Analysis:** Detailed findings on core operational workflows, including summaries of process maps (or references to an appendix), identified inefficiencies, bottlenecks, and areas for improvement.
3.  **Supply Chain Analysis:** Comprehensive overview of the supply chain structure (sourcing, manufacturing/operations, distribution), supply chain map summary (or appendix reference), key risks and vulnerabilities identified, and assessment of resilience.
4.  **Performance Assessment & Benchmarking:** Analysis of key operational KPIs, comparison against industry benchmarks and best practices, clear identification of performance gaps, and hypothesized root causes. Use charts and tables for clarity.
5.  **Strategic Operational Moves:** Detailed description of the 3-5 prioritized recommendations, including specific actions required, expected benefits (qualitative and quantitative), implementation roadmap (high-level phases, timelines, owners), and KPIs with targets for tracking success.
6.  **Appendix (Optional):** Detailed process maps, raw benchmarking data, extensive KPI lists, etc.

Ensure the language is concise, data-driven, professional, and focuses on actionable insights. Specify the use of clear headings, subheadings, and visual aids (charts, tables - described conceptually).
"""
        }

        # Return the specific prompt or a generic message if the task is not found
        return prompts.get(task, f"Conduct a thorough operational analysis for {phase} - {task} in the {industry_type} industry.")


    def generate_analysis(self, prompt, phase, task, industry_type):
        """Generate analysis using HuggingFace model."""
        # Construct a more detailed system prompt for the LLM
        system_message = f"""You are a highly experienced senior consultant from a top-tier firm (like McKinsey, BCG, Bain) specializing in Operations Strategy and Performance Improvement for the '{industry_type}' industry. Your task is to analyze a specific aspect of a target company's operations as part of a due diligence process.

        **Your Response Must:**
        - Be structured logically and clearly.
        - Use professional, concise, and data-driven language (use hypothetical data where appropriate for illustration).
        - Directly address the specific instructions provided in the user prompt.
        - Focus on actionable insights and strategic recommendations relevant to '{industry_type}'.
        - Identify potential risks and opportunities.
        - Maintain the persona of an expert MBB consultant throughout.
        - If asked to create diagrams or maps, describe them vividly in text format.
        - If asked for KPIs, justify their relevance to the '{industry_type}'.
        - If asked to benchmark, clearly state hypothetical company performance, benchmark values, and the resulting gap.
        - If asked for recommendations, ensure they are SMART (Specific, Measurable, Achievable, Relevant, Time-bound) conceptually.
        """

        user_message = f"""
        **Assessment Context:**
        - Target Company Industry: {industry_type}
        - Due Diligence Phase: Operational Assessment
        - Current Focus: {phase} - {self.phases[phase]['name']}
        - Specific Task: {task} - {self.phases[phase]['tasks'][task]}

        **Consultant Instructions:**
        {prompt}

        **Provide your analysis below:**
        """

        try:
            # Use the client initialized in __init__
            response = self.client.chat_completion(
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=1500,  # Increased max_tokens for potentially detailed analysis
                temperature=0.6, # Slightly lower temp for more focused output
                # model=self.model_name # Model defined during init
                # Ensure you pass the model name if InferenceClient requires it per call,
                # otherwise it uses the one from init. Check library documentation.
                # If the client was initialized with the model, this might not be needed.
            )
            # Check if response structure is as expected
            if response.choices and response.choices[0].message:
                 return response.choices[0].message.content.strip() # .strip() to remove leading/trailing whitespace
            else:
                 return "Error: Received an unexpected response structure from the model."

        except Exception as e:
            st.error(f"Error generating analysis via Hugging Face API: {str(e)}")
            # Provide more context on the error if possible
            return f"Error generating analysis: {str(e)}. Please check API key, model name, network connection, and API availability."


def main():
    st.set_page_config(layout="wide", page_title="MBB Ops Assessment Tool")
    st.title("MBB-Style Operational Assessment Tool")

    # Use a fixed timestamp and username for demo purposes as requested
    fixed_timestamp = "2025-05-01 17:07:02 UTC" # Added UTC for clarity
    username = "alokyadav2020"

    # --- Session State Initialization ---
    if 'assessment' not in st.session_state:
        # Ensure secrets are loaded before initializing
        if "hf_token" not in st.secrets or "hf_model" not in st.secrets:
             st.error("ERROR: 'hf_token' or 'hf_model' not found in Streamlit Secrets. Please configure secrets.")
             st.stop() # Stop execution if secrets are missing
        st.session_state.assessment = OperationalAssessment()

    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []

    # --- Sidebar ---
    st.sidebar.markdown("### Session Information")
    st.sidebar.info(f"👤 User: {username}")
    st.sidebar.info(f"⏱️ Session Time (Fixed): {fixed_timestamp}")
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Configuration")

    # Industry Selection in Sidebar
    industry_type = st.sidebar.selectbox(
        "Select Target Industry",
        ["Manufacturing", "Technology", "Services"],
        key="industry_select" # Add key for stability
    )

    # Phase Selection in Sidebar
    selected_phase = st.sidebar.selectbox(
        "Select Assessment Phase",
        list(st.session_state.assessment.phases.keys()),
        format_func=lambda x: f"{x}: {st.session_state.assessment.phases[x]['name']}",
        key="phase_select"
    )

    # Task Selection in Sidebar (dynamically updated based on phase)
    available_tasks = st.session_state.assessment.phases[selected_phase]['tasks']
    selected_task = st.sidebar.selectbox(
        "Select Specific Task",
        list(available_tasks.keys()),
        format_func=lambda x: f"{x}: {available_tasks[x]}",
        key="task_select"
    )

    st.sidebar.markdown("---")
    # Clear History Button in Sidebar
    if st.sidebar.button("Clear Analysis History"):
        st.session_state.analysis_history = []
        st.success("Analysis history cleared.")
        st.experimental_rerun() # Rerun to reflect the cleared history immediately


    # --- Main Area ---

    st.subheader(f"Analyze Task: {selected_task} - {available_tasks[selected_task]}")
    st.markdown(f"**Industry:** {industry_type} | **Phase:** {selected_phase} - {st.session_state.assessment.phases[selected_phase]['name']}")
    st.markdown("---")


    # Get default prompt based on selections
    # Use a temporary key that changes with selections to force prompt refresh
    prompt_key = f"prompt_input_{industry_type}_{selected_phase}_{selected_task}"
    default_prompt = st.session_state.assessment.get_default_prompt(
        selected_phase,
        selected_task,
        industry_type
    )

    # Prompt customization area
    st.markdown("#### Customize Analysis Prompt")
    user_prompt = st.text_area(
        "You can modify the specific instructions for the consultant below:",
        value=default_prompt, # Use value instead of default_prompt directly
        height=250,
        key=prompt_key # Use dynamic key
    )

    # Analysis generation button
    if st.button("Generate Analysis", key="generate_button"):
        if not user_prompt.strip():
             st.warning("Prompt cannot be empty.")
        else:
            with st.spinner(f"Generating analysis for {selected_task}... Please wait."):
                analysis = st.session_state.assessment.generate_analysis(
                    user_prompt,
                    selected_phase,
                    selected_task,
                    industry_type
                )

                # Prepend new analysis to history (shows most recent first)
                st.session_state.analysis_history.insert(0, {
                    'timestamp': fixed_timestamp, # Use the fixed timestamp
                    'industry': industry_type,
                    'phase': selected_phase,
                    'task': selected_task,
                    'prompt': user_prompt, # Store the actual prompt used
                    'analysis': analysis
                })

                # Display the latest analysis immediately
                st.subheader("Generated Analysis")
                st.markdown(analysis) # Display raw markdown from LLM
                st.success("Analysis generated and added to history.")


    # --- Analysis History Display ---
    if st.session_state.analysis_history:
        st.markdown("---")
        st.subheader("Analysis History")

        # Download Button
        history_text = ""
        for i, entry in enumerate(reversed(st.session_state.analysis_history)): # Iterate reversed for chronological file
            history_text += f"--- Analysis {len(st.session_state.analysis_history) - i} ---\n"
            history_text += f"Timestamp: {entry['timestamp']}\n"
            history_text += f"Industry: {entry['industry']}\n"
            history_text += f"Phase: {entry['phase']} ({st.session_state.assessment.phases[entry['phase']]['name']})\n"
            history_text += f"Task: {entry['task']} ({st.session_state.assessment.phases[entry['phase']]['tasks'][entry['task']]})\n\n"
            history_text += f"Prompt Used:\n{entry['prompt']}\n\n"
            history_text += f"Generated Analysis:\n{entry['analysis']}\n\n"

        download_filename = f"operational_analysis_history_{fixed_timestamp.replace(':', '-').replace(' ', '_')}.txt"
        st.download_button(
            label="Download Full Analysis History",
            data=history_text,
            file_name=download_filename,
            mime="text/plain"
        )

        # Display history entries using expanders (most recent first)
        for i, entry in enumerate(st.session_state.analysis_history):
            expander_title = f"#{len(st.session_state.analysis_history) - i}: {entry['timestamp']} - {entry['industry']} - {entry['task']}"
            with st.expander(expander_title):
                st.markdown(f"**Industry:** {entry['industry']}")
                st.markdown(f"**Phase:** {entry['phase']} ({st.session_state.assessment.phases[entry['phase']]['name']})")
                st.markdown(f"**Task:** {entry['task']} ({st.session_state.assessment.phases[entry['phase']]['tasks'][entry['task']]})")
                st.markdown("**Prompt Used:**")
                st.text_area("Prompt", value=entry['prompt'], height=150, disabled=True, key=f"prompt_hist_{i}")
                st.markdown("**Generated Analysis:**")
                st.markdown(entry['analysis']) # Render analysis as markdown

if __name__ == "__main__":
    main()