import streamlit as st
from huggingface_hub import InferenceClient
from datetime import datetime
import json

class OperationalAssessment:
    def __init__(self):
        self.client = InferenceClient(
            provider="hf-inference",
            api_key=st.secrets["hf_token"]
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
            response = self.client.chat_completion(
                model=st.secrets["hf_model"],
                messages=[
                    {"role": "system", "content": "You are an experienced MBB consultant specializing in operational strategy."},
                    {"role": "user", "content": formatted_prompt}
                ],
                max_tokens=8000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating analysis: {str(e)}"

def operationassessment(selected_phase,selected_task,industry_context):
    
    assessment = OperationalAssessment()

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

    analysis =assessment.generate_analysis(
                    default_prompt,
                    selected_phase,
                    selected_task,
                    industry_context
                )
    return analysis
