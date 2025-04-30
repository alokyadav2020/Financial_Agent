import streamlit as st
from huggingface_hub import InferenceClient
import PyPDF2
import io
from datetime import datetime

class PDFChatbot:
    def __init__(self):
        self.client = InferenceClient(
            provider="hf-inference",
            api_key=st.secrets["hf_token"]
        )
        self.pdf_text = ""
        self.chat_history = []

    def extract_text_from_pdf(self, pdf_file):
        """Extract text from uploaded PDF file."""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            st.error(f"Error extracting text from PDF: {str(e)}")
            return None

    def generate_response(self, user_question):
        """Generate response using HuggingFace model."""
        prompt = f"""
        You are an expert in financial reporting and business valuation and analysis from top tier consulting firms (McKinsey, BCG and Bain)  and known for producing concise, insightful, and action-oriented Answers.
        Based on the following document, please answer the question.
        
        Document content:
        {self.pdf_text}  # Limiting context window to first 2000 characters
        
        Question: {user_question}
        
        Please provide a clear and concise answer based only on the information available in the document.
        If the answer cannot be found in the document, please say so.
        """

        messages = [
            {"role": "system", "content": "You are a helpful assistant that answers questions about PDF documents."},
            {"role": "user", "content": prompt}
        ]

        try:
            response = self.client.chat_completion(
                model=st.secrets["hf_model"],
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {str(e)}"

def initialize_session_state():
    """Initialize session state variables."""
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = PDFChatbot()
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'pdf_uploaded' not in st.session_state:
        st.session_state.pdf_uploaded = False

def main():
    st.title("Delivery Assurance Chatbot")

    # Display session information
    st.sidebar.markdown("### Session Information")
    current_time = "2025-04-30 18:00:15"  # Fixed timestamp as per requirement
    username = "alokyadav2020"  # Fixed username as per requirement
    st.sidebar.info(f"Current Date and Time (UTC): {current_time}")
    st.sidebar.info(f"Current User: {username}")

    # Initialize session state
    initialize_session_state()

    # File upload section
    st.subheader("Upload PDF Document")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file is not None and not st.session_state.pdf_uploaded:
        with st.spinner("Processing PDF..."):
            # Extract text from PDF
            pdf_text = st.session_state.chatbot.extract_text_from_pdf(uploaded_file)
            if pdf_text:
                st.session_state.chatbot.pdf_text = pdf_text
                st.session_state.pdf_uploaded = True
                st.success("PDF processed successfully!")

                # Display PDF content in expander
                with st.expander("View PDF Content"):
                    st.text_area("Extracted Text", pdf_text, height=200)

    # Chat interface
    if st.session_state.pdf_uploaded:
        st.subheader("Chat with Agent")
        st.markdown("Ask questions about the document you uploaded.")
        
        # Display chat history
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.info(f"**You:** {message['content']}")
            else:
                st.markdown(f"**Assistant:** {message['content']}")

        # Chat input
        user_question = st.text_input("Ask a question about the document:")
        
        if st.button("Send"):
            if user_question:
                # Add user message to chat history
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": user_question
                })

                # Generate response
                with st.spinner("Generating response..."):
                    response = st.session_state.chatbot.generate_response(user_question)
                
                # Add assistant response to chat history
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response
                })

                # Clear input
                st.rerun()

        # Clear chat history button
        if st.button("Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()

    # Download chat history
    if st.session_state.chat_history:
        chat_text = "\n\n".join([
            f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
            for msg in st.session_state.chat_history
        ])
        
        st.download_button(
            label="Download Chat History",
            data=chat_text,
            file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )

if __name__ == "__main__":
    main()