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


class MBBConsultant:
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

    def generate_analysis(self, prompt, phase, task):
        """Generate analysis using HuggingFace model."""
        formatted_prompt = f"""
        As an MBB consultant specializing in Human Capital Assessment, analyze the following:
        
        Phase: {phase}
        Task: {task}
        
        Specific Instructions:
        {prompt}
        
        Provide a detailed analysis following MBB consulting standards.
        Focus on actionable insights and data-driven recommendations.
        """

        messages = [
            {"role": "system", "content": "You are an experienced MBB consultant specializing in human capital strategy."},
            {"role": "user", "content": formatted_prompt}
        ]

        try:
            # response = self.client.chat_completion(
            #     model=os.getenv("hf_model"),
            #     messages=messages,
            #     max_tokens=1000,
            #     temperature=0.7
            # )

            response = self.client.chat.completions.create(
            model=os.getenv("DEPLOYMENT_NAME"),  # Use the deployment name instead of model name
            messages=messages,
            temperature=0.7
        )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating analysis: {str(e)}"

def initialize_session_state():
    """Initialize session state variables."""
    if 'consultant' not in st.session_state:
        st.session_state.consultant = MBBConsultant()
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    if 'last_prompt' not in st.session_state:
        st.session_state.last_prompt = None

def main():
    st.title("MBB Human Capital Assessment Tool")

    # Fixed timestamp and username
    timestamp = "2025-05-01 16:45:26"
    username = "alokyadav2020"

    # Session Information
    st.sidebar.markdown("### Session Information")
    st.sidebar.info(f"Current Date and Time (UTC): {timestamp}")
    st.sidebar.info(f"Current User: {username}")

    # Initialize session state
    initialize_session_state()

    # Phase selection
    phases = {
        "Section 1": "Organizational Structure and Workforce Analysis",
        "Section 2": "Compensation, Benefits, and Talent Development",
        "Section 3": "Human Capital Risks and Strategic Alignment",
        "Section 4": "Synthesis and Output"
    }

    selected_phase = st.selectbox(
        "Select Analysis Phase",
        list(phases.keys()),
        format_func=lambda x: f"{x}: {phases[x]}"
    )

    # Task selection based on phase
    tasks = {
        "Section 1": ["Task 1: Analyze Organizational Structure", 
                    "Task 2: Analyze Employee Metrics"],
        "Section 2": ["Task 3: Analyze Compensation and Benefits", 
                    "Task 4: Evaluate Talent Development and Training"],
        "Section 3": ["Task 5: Identify Human Capital Risks", 
                    "Task 6: Assess Strategic Alignment"],
        "Section 4": ["Task 7: Synthesize Findings", 
                    "Task 8: Develop Strategic Moves", 
                    "Task 9: Create Assessment Report"]
    }

    selected_task = st.selectbox(
        "Select Task",
        tasks[selected_phase]
    )

    print(f"Selected Phase: {selected_phase}, Task: {selected_task}")

    # Default prompt template
    default_prompt = """
    Conduct a thorough analysis for the selected phase and task.
    Consider the following aspects:
    1. Current state assessment
    2. Key challenges and opportunities
    3. Industry benchmarks and best practices
    4. Specific recommendations
    5. Implementation considerations
    
    Please provide detailed insights and actionable recommendations.
    """
    HCA_Section_1 = ""
    
    if selected_phase == "Section 1":
        HCA_Section_1 = "HCA_Section_1"
    elif selected_phase == "Section 2":
        HCA_Section_1 = "HCA_Section_2"
    elif selected_phase == "Section 3":
        HCA_Section_1 = "HCA_Section_3"
    elif selected_phase == "Section 4":
        HCA_Section_1 = "HCA_Section_4"

    query = text(f"SELECT [{HCA_Section_1}] FROM prompt_valuation_reports WHERE id = :id")
    params = {"id": 1}
    data = fetch_query(query, params)
    
    if data:
        default_prompt= data[0][f'{HCA_Section_1}']
    else:
        pass

    # Allow user to customize prompt
    st.subheader("Customize Analysis Prompt")
    user_prompt = st.text_area(
        "Modify the prompt below to customize your analysis:",
        default_prompt,
        height=300,
        key="prompt_input"
    )
    HCA_Section_1 = ""
    if st.button("Save promt"):
        if selected_phase == "Section 1":
            HCA_Section_1 = "HCA_Section_1"
        elif selected_phase == "Section 2":
            HCA_Section_1 = "HCA_Section_2"
        elif selected_phase == "Section 3":
            HCA_Section_1 = "HCA_Section_3"
        elif selected_phase == "Section 4":
            HCA_Section_1 = "HCA_Section_4"

            #st.session_state.user_prompt = default_prompt
        id = 1
        try:
            update_query = text(f"""
                UPDATE prompt_valuation_reports
                SET [{HCA_Section_1}] = :{HCA_Section_1}
                WHERE id = :id
            """)
            params = {
                f"{HCA_Section_1}": user_prompt,
                "id": id
            }
            execute_query(update_query, params)
            st.success("Data updated successfully!")
        except Exception as e:
            st.error(f"Update failed: {e}")
        st.success("Prompt reset to default!")
        st.rerun()

        try:
            query = text(f"SELECT [{HCA_Section_1}] FROM prompt_valuation_reports WHERE id = :id")
            params = {"id": 1}
            data = fetch_query(query, params)
            if data:
                st.write(f"{HCA_Section_1}:")
                st.write(data[0][f"{HCA_Section_1}"])
            else:
                st.warning("No report found.")
        except Exception as e:
            st.error(f"Error fetching data: {e}")


    st.markdown("----")



    # Analysis generation
    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("Generate Analysis"):
            if user_prompt and user_prompt != st.session_state.last_prompt:
                st.session_state.last_prompt = user_prompt
                
                with st.spinner("Generating analysis..."):
                    analysis = st.session_state.consultant.generate_analysis(
                        user_prompt, 
                        selected_phase, 
                        selected_task
                    )

                # Add to history
                st.session_state.analysis_history.append({
                    'timestamp': timestamp,
                    'Section': selected_phase,
                    'task': selected_task,
                    'prompt': user_prompt,
                    'analysis': analysis
                })

                # Display analysis
                st.subheader("Generated Analysis")
                st.markdown(analysis)

    with col2:
        if st.button("Clear History"):
            st.session_state.analysis_history = []
            st.session_state.last_prompt = None

    # Download options
    if st.session_state.analysis_history:
        # Prepare analysis history for download
        analysis_text = "\n\n---\n\n".join([
            f"Timestamp: {entry['timestamp']}\n"
            f"Section: {entry['phase']}\n"
            f"Task: {entry['task']}\n"
            f"Analysis:\n{entry['analysis']}"
            for entry in st.session_state.analysis_history
        ])
        
        st.download_button(
            label="Download Analysis History",
            data=analysis_text,
            file_name=f"mbb_analysis_{timestamp.replace(' ', '_').replace(':', '-')}.txt",
            mime="text/plain"
        )

    # View Analysis History
    if st.session_state.analysis_history:
        st.subheader("Analysis History")
        for i, entry in enumerate(st.session_state.analysis_history):
            with st.expander(f"Analysis {i+1} - {entry['phase']} - {entry['task']}"):
                st.markdown(f"**Timestamp:** {entry['timestamp']}")
                st.markdown(f"**Section:** {entry['phase']}")
                st.markdown(f"**Task:** {entry['task']}")
                st.markdown("**Analysis:**")
                st.markdown(entry['analysis'])

if __name__ == "__main__":
    main()