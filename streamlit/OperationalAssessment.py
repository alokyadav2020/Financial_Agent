import streamlit as st
from huggingface_hub import InferenceClient
from datetime import datetime
import json
import os

from src.db.sql_operation import execute_query, fetch_query
from sqlalchemy import text
from openai import AzureOpenAI 
from dotenv import load_dotenv
load_dotenv()

class OperationalAssessment:
    def __init__(self):
        # self.client = InferenceClient(
        #     provider="hf-inference",
        #     api_key=os.getenv("hf_token")
        # )
        self.client = AzureOpenAI(
        azure_endpoint= os.getenv("ENDPOINT_URL"),
        azure_deployment=os.getenv("DEPLOYMENT_NAME"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2025-01-01-preview"
    )


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

    def generate_analysis(self, prompt, phase, task, industry_context=""):
        """Generate analysis using HuggingFace model."""
        formatted_prompt = f"""
        As an MBB consultant specializing in Operational Assessment, analyze the following:
        
        Phase: {phase}
        Task: {task}
        Industry Context: {industry_context}
        
        Specific Instructions:
        {prompt}
        
        Provide a detailed analysis following MBB consulting standards.
        Focus on actionable insights and data-driven recommendations.
        """

        try:
            # response = self.client.chat_completion(
            #     model=os.getenv("hf_model"),
            #     ,
            #     max_tokens=1000,
            #     temperature=0.7
            # )

            messages=[
                    {"role": "system", "content": "You are an experienced MBB consultant specializing in operational strategy."},
                    {"role": "user", "content": formatted_prompt}
                ]


            response = self.client.chat.completions.create(
            model=os.getenv("DEPLOYMENT_NAME"),  # Use the deployment name instead of model name
            messages=messages,
            temperature=0.7
        )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating analysis: {str(e)}"

def main():
    st.title("MBB Operational Assessment Tool")

    # Fixed timestamp and username as per requirement
    timestamp = "2025-05-01 16:54:26"
    username = "alokyadav2020"

    # Session information
    st.sidebar.markdown("### Session Information")
    st.sidebar.info(f"Current Date and Time (UTC): {timestamp}")
    st.sidebar.info(f"Current User: {username}")

    # Initialize assessment object
    if 'assessment' not in st.session_state:
        st.session_state.assessment = OperationalAssessment()
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []

    # Phase and Task Selection
    st.subheader("Assessment Configuration")
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

    # Industry Context
    industry_context = st.text_input(
        "Industry Context (Optional)",
        placeholder="e.g., Manufacturing, Technology, Healthcare"
    )

    # Default prompt template based on selected phase and task
    default_prompt = f"""
    Conduct a thorough analysis for {selected_phase} - {selected_task}.
    
    Consider the following aspects:
    1. Current state assessment
    2. Key challenges and opportunities
    3. Industry best practices and benchmarks
    4. Specific recommendations
    5. Implementation considerations
    
    Please provide detailed insights and actionable recommendations
    focusing on operational excellence and efficiency improvements.
    """

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
            with st.spinner("Generating operational analysis..."):
                analysis = st.session_state.assessment.generate_analysis(
                    user_prompt,
                    selected_phase,
                    selected_task,
                    industry_context
                )

                # Save to history
                st.session_state.analysis_history.append({
                    'timestamp': timestamp,
                    'phase': selected_phase,
                    'task': selected_task,
                    'industry': industry_context,
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
        # Prepare analysis history for download
        analysis_text = "\n\n---\n\n".join([
            f"Timestamp: {entry['timestamp']}\n"
            f"Phase: {entry['phase']}\n"
            f"Task: {entry['task']}\n"
            f"Industry: {entry['industry']}\n"
            f"Analysis:\n{entry['analysis']}"
            for entry in st.session_state.analysis_history
        ])
        
        st.download_button(
            label="Download Analysis History",
            data=analysis_text,
            file_name=f"operational_analysis_{timestamp.replace(' ', '_').replace(':', '-')}.txt",
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
                st.markdown(f"**Industry:** {entry['industry']}")
                st.markdown("**Analysis:**")
                st.markdown(entry['analysis'])

if __name__ == "__main__":
    main()