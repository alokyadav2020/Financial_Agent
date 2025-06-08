import streamlit as st
from huggingface_hub import InferenceClient
from datetime import datetime
import json

class MBBConsultant:
    def __init__(self):
        self.client = InferenceClient(
            provider="hf-inference",
            api_key=st.secrets["hf_token"]
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
            response = self.client.chat_completion(
                model=st.secrets["hf_model"],
                messages=messages,
                max_tokens=8000,
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

def hc_reports(selected_phase,selected_task):
   

    # Initialize session state
    initialize_session_state()

    # Phase selection
    # phases = {
    #     "Phase 1": "Organizational Structure and Workforce Analysis",
    #     "Phase 2": "Compensation, Benefits, and Talent Development",
    #     "Phase 3": "Human Capital Risks and Strategic Alignment",
    #     "Phase 4": "Synthesis and Output"
    # }

    # selected_phase = st.sidebar.selectbox(
    #     "Select Analysis Phase",
    #     list(phases.keys()),
    #     format_func=lambda x: f"{x}: {phases[x]}"
    # )

    # # Task selection based on phase
    # tasks = {
    #     "Phase 1": ["Task 1: Analyze Organizational Structure", 
    #                 "Task 2: Analyze Employee Metrics"],
    #     "Phase 2": ["Task 3: Analyze Compensation and Benefits", 
    #                 "Task 4: Evaluate Talent Development and Training"],
    #     "Phase 3": ["Task 5: Identify Human Capital Risks", 
    #                 "Task 6: Assess Strategic Alignment"],
    #     "Phase 4": ["Task 7: Synthesize Findings", 
    #                 "Task 8: Develop Strategic Moves", 
    #                 "Task 9: Create Assessment Report"]
    # }

    # selected_task = st.sidebar.select_slider(
    #     "Select Task",
    #     tasks[selected_phase]
    # )

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


    analysis = st.session_state.consultant.generate_analysis(
                        default_prompt, 
                        selected_phase, 
                        selected_task
                    )


    return analysis
# if __name__ == "__main__":
#     hc_reports(selected_phase,selected_task)