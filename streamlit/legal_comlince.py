import streamlit as st
from huggingface_hub import InferenceClient
from datetime import datetime
import os

class LegalComplianceAssessment:
    def __init__(self):
        self.client = InferenceClient(
            provider="hf-inference",
            api_key=os.getenv("hf_token")
        )
        self.phases = {
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

    def get_default_prompt(self, phase, task):
        """Get default prompt template based on phase and task."""
        prompts = {
            "Phase 1": {
                "Task 1": """
                Analyze the corporate governance structure focusing on:
                1. Board composition and independence
                2. Key committees and their effectiveness
                3. Management team assessment
                4. Governance policies and practices
                5. Regulatory compliance in corporate governance
                
                Provide specific insights and recommendations.
                """
            },
            "Phase 2": {
                "Task 2": """
                Assess regulatory compliance in the following areas:
                1. Industry-specific regulations
                2. Environmental, Health, and Safety (EHS)
                3. Data Privacy and Cybersecurity
                4. Anti-corruption and Anti-bribery
                5. International Trade
                
                Identify compliance gaps and recommend improvements.
                """
            },
            "Phase 3": {
                "Task 3": """
                Analyze litigation history and legal risks:
                1. Current pending litigation
                2. Historical legal issues
                3. Potential future risks
                4. Risk management approach
                5. Legal department assessment
                
                Provide risk assessment and mitigation strategies.
                """
            },
            "Phase 4": {
                "Task 4": """
                Synthesize key findings focusing on:
                1. Material non-compliance issues
                2. Significant litigation risks
                3. Governance weaknesses
                4. Emerging legal risks
                
                Prioritize issues by potential impact.
                """,
                "Task 5": """
                Develop targeted questions for leadership:
                1. Understanding of key issues
                2. Risk mitigation plans
                3. Financial impact assessment
                4. Operational implications
                
                Format questions for maximum clarity and insight.
                """,
                "Task 6": """
                Create comprehensive assessment report including:
                1. Executive summary
                2. Governance assessment
                3. Compliance review
                4. Litigation analysis
                5. Key issues and questions
                
                Follow MBB report structure and formatting.
                """
            }
        }
        return prompts.get(phase, {}).get(task, "Conduct thorough analysis for the selected phase and task.")

    def generate_analysis(self, prompt, phase, task, company_type):
        """Generate analysis using HuggingFace model."""
        formatted_prompt = f"""
        As an MBB consultant specializing in Legal & Compliance Assessment, analyze the following:
        
        Phase: {phase}
        Task: {task}
        Company Type: {company_type}
        
        Specific Instructions:
        {prompt}
        
        Provide a detailed analysis following MBB consulting standards.
        Focus on legal risks, compliance gaps, and actionable recommendations.
        """

        try:
            response = self.client.chat_completion(
                model=os.getenv("hf_model"),
                messages=[
                    {"role": "system", "content": "You are an experienced MBB consultant specializing in legal and compliance assessment."},
                    {"role": "user", "content": formatted_prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating analysis: {str(e)}"

def main():
    st.title("MBB Legal & Compliance Assessment Tool")

    # Fixed timestamp as per requirement
    timestamp = "2025-05-01 16:58:39"
    username = "alokyadav2020"

    # Session information
    st.sidebar.markdown("### Session Information")
    st.sidebar.info(f"Current Date and Time (UTC): {timestamp}")
    st.sidebar.info(f"Current User: {username}")

    # Initialize assessment object
    if 'assessment' not in st.session_state:
        st.session_state.assessment = LegalComplianceAssessment()
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []

    # Assessment Configuration
    st.subheader("Assessment Configuration")

    # Company Type Selection
    company_type = st.selectbox(
        "Select Company Type",
        ["Public Company", "Private Company", "Multinational Corporation", "Start-up"]
    )

    # Phase and Task Selection
    col1, col2 = st.columns(2)

    with col1:
        selected_phase = st.selectbox(
            "Select Phase",
            list(st.session_state.assessment.phases.keys()),
            format_func=lambda x: f"{x}: {st.session_state.assessment.phases[x]['name']}"
        )

    with col2:
        selected_task = st.selectbox(
            "Select Task",
            list(st.session_state.assessment.phases[selected_phase]['tasks'].keys()),
            format_func=lambda x: f"{x}: {st.session_state.assessment.phases[selected_phase]['tasks'][x]}"
        )

    # Get default prompt
    default_prompt = st.session_state.assessment.get_default_prompt(selected_phase, selected_task)

    # Prompt customization
    st.subheader("Customize Analysis Prompt")
    user_prompt = st.text_area(
        "Modify the prompt below:",
        default_prompt,
        height=300,
        key="prompt_input"
    )

    # Analysis generation
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("Generate Analysis"):
            with st.spinner("Generating legal and compliance analysis..."):
                analysis = st.session_state.assessment.generate_analysis(
                    user_prompt,
                    selected_phase,
                    selected_task,
                    company_type
                )

                # Save to history
                st.session_state.analysis_history.append({
                    'timestamp': timestamp,
                    'phase': selected_phase,
                    'task': selected_task,
                    'company_type': company_type,
                    'prompt': user_prompt,
                    'analysis': analysis
                })

                # Display analysis
                st.subheader("Generated Analysis")
                st.markdown(analysis)

    with col2:
        if st.button("Clear History"):
            st.session_state.analysis_history = []

    # Download options
    if st.session_state.analysis_history:
        analysis_text = "\n\n---\n\n".join([
            f"Timestamp: {entry['timestamp']}\n"
            f"Phase: {entry['phase']}\n"
            f"Task: {entry['task']}\n"
            f"Company Type: {entry['company_type']}\n"
            f"Analysis:\n{entry['analysis']}"
            for entry in st.session_state.analysis_history
        ])
        
        st.download_button(
            label="Download Analysis History",
            data=analysis_text,
            file_name=f"legal_compliance_analysis_{timestamp.replace(' ', '_').replace(':', '-')}.txt",
            mime="text/plain"
        )

    # View Analysis History
    if st.session_state.analysis_history:
        st.subheader("Analysis History")
        for i, entry in enumerate(st.session_state.analysis_history):
            with st.expander(f"Analysis {i+1} - {entry['phase']} - {entry['task']}"):
                st.markdown(f"**Timestamp:** {entry['timestamp']}")
                st.markdown(f"**Phase:** {entry['phase']}")
                st.markdown(f"**Task:** {entry['task']}")
                st.markdown(f"**Company Type:** {entry['company_type']}")
                st.markdown("**Analysis:**")
                st.markdown(entry['analysis'])

if __name__ == "__main__":
    main()