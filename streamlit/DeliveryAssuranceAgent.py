import streamlit as st
from huggingface_hub import InferenceClient
import PyPDF2
import io
from datetime import datetime

# --- Configuration & Secrets ---
# Ensure these secrets are set in your Streamlit Cloud environment or locally
try:
    HF_TOKEN = st.secrets["hf_token"]
    HF_MODEL = st.secrets["hf_model"]
except KeyError:
    st.error("Please provide 'hf_token' and 'hf_model' in your Streamlit secrets.")
    st.stop() # Stop execution if secrets are missing

# --- PDF Chatbot Class ---
class PDFChatbot:
    def __init__(self, api_key, model_name):
        """Initialize the InferenceClient."""
        try:
            self.client = InferenceClient(
                provider="hf-inference", # Or specify your provider if different
                model=model_name,
                token=api_key
            )
            self.model_name = model_name
        except Exception as e:
            st.error(f"Failed to initialize HuggingFace client: {e}")
            st.stop()
        self.pdf_text = ""

    def extract_text_from_pdf(self, pdf_file):
        """Extract text from uploaded PDF file."""
        try:
            # Use BytesIO to handle the uploaded file in memory
            pdf_file_bytes = io.BytesIO(pdf_file.getvalue())
            pdf_reader = PyPDF2.PdfReader(pdf_file_bytes)
            text = ""
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text: # Add text only if extraction was successful
                    text += f"--- Page {page_num+1} ---\n{page_text}\n\n"
            return text if text else "Could not extract text from the PDF."
        except Exception as e:
            st.error(f"Error extracting text from PDF: {str(e)}")
            return None

    def generate_response(self, user_question, chat_history):
        """Generate response using HuggingFace model, including chat history."""
        system_prompt = """
        You are a value assurance expert in financial reporting, business valuation , M&A and known for understanding and interpreting Economics from top tier consulting firms (McKinsey, BCG and Bain)  and known for producing concise, insightful, and action-oriented Answers.

        Based ONLY on the provided Document Content, please answer the User's Question.
        Provide a clear and concise answer.
        If the answer cannot be found in the document, state that clearly. Do not make up information.
        """

        # Construct messages for the API call, including history
        messages = [{"role": "system", "content": system_prompt}]

        # Add limited document context (e.g., first 4000 chars) to avoid exceeding limits
        # A more robust solution would involve chunking/embeddings for large docs
        context_limit = 8000
        limited_pdf_text = self.pdf_text[:context_limit]
        if len(self.pdf_text) > context_limit:
             limited_pdf_text += "\n... [Document Content Truncated]"

        messages.append({"role": "user", "content": f"Document Content:\n{limited_pdf_text}"})

        # Add previous chat history
        for message in chat_history:
             messages.append({"role": message["role"], "content": message["content"]})

        # Add the current user question
        messages.append({"role": "user", "content": f"User's Question: {user_question}"})


        try:
            # Using chat_completion for conversational models
            response_stream = self.client.chat_completion(
                messages=messages,
                max_tokens=500,
                temperature=0.7,
                stream=False # Set to False unless you want to handle streaming
            )
            # Accessing the response content correctly
            if response_stream.choices and len(response_stream.choices) > 0:
                 return response_stream.choices[0].message.content
            else:
                 return "Error: Received an empty response from the model."

        except Exception as e:
            st.error(f"Error generating response from HF API: {str(e)}")
            return "Sorry, I encountered an error while generating the response."

# --- Session State Initialization ---
def initialize_session_state():
    """Initialize session state variables if they don't exist."""
    if 'chatbot' not in st.session_state:
        # Pass secrets safely during initialization
        st.session_state.chatbot = PDFChatbot(api_key=HF_TOKEN, model_name=HF_MODEL)
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = [] # Store as list of dicts: {"role": "user/assistant", "content": "..."}
    if 'pdf_uploaded' not in st.session_state:
        st.session_state.pdf_uploaded = False
    if 'pdf_text' not in st.session_state:
        st.session_state.pdf_text = ""
    if 'pdf_filename' not in st.session_state:
        st.session_state.pdf_filename = ""

# --- Main App Logic ---
def main():
    st.set_page_config(page_title="Delivery Assurance Chatbot", layout="wide")
    st.title("📄 Delivery Assurance Chatbot")

    # Initialize session state
    initialize_session_state()

    # --- Sidebar ---
    with st.sidebar:
        st.markdown("### Session Information")
        # Use datetime.utcnow() for current UTC time, but format it
        # current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S") # Use actual current time
        fixed_time = "2025-04-30 18:00:15" # Fixed timestamp as per requirement
        username = "alokyadav2020"  # Fixed username as per requirement
        st.info(f"Current Date and Time (UTC): {fixed_time}")
        st.info(f"Current User: {username}")

        st.markdown("---")
        st.subheader("Upload PDF Document")
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf", key="pdf_uploader")

        if uploaded_file is not None:
            # Process PDF only if it's a new file or hasn't been processed yet
            if not st.session_state.pdf_uploaded or st.session_state.pdf_filename != uploaded_file.name:
                with st.spinner("Processing PDF..."):
                    pdf_text = st.session_state.chatbot.extract_text_from_pdf(uploaded_file)
                    if pdf_text:
                        st.session_state.chatbot.pdf_text = pdf_text # Store in chatbot instance
                        st.session_state.pdf_text = pdf_text         # Also store in session_state for display
                        st.session_state.pdf_uploaded = True
                        st.session_state.pdf_filename = uploaded_file.name
                        st.session_state.chat_history = [] # Reset chat history on new PDF upload
                        st.success(f"Processed '{uploaded_file.name}'")
                    else:
                        # Handle extraction failure
                        st.session_state.pdf_uploaded = False
                        st.session_state.pdf_text = ""
                        st.session_state.pdf_filename = ""
                        st.error("Failed to extract text from the PDF.")
        elif st.session_state.pdf_uploaded:
             # If a file was previously uploaded, show its name
             st.info(f"Currently loaded: '{st.session_state.pdf_filename}'")


        # Display PDF content if uploaded
        if st.session_state.pdf_uploaded:
            with st.expander("View PDF Content (First 4000 Chars)"):
                st.text_area("Extracted Text", st.session_state.pdf_text[:4000], height=200, disabled=True)

        st.markdown("---")
        # Clear chat history button
        if st.button("Clear Chat History"):
            st.session_state.chat_history = []
            st.toast("Chat history cleared!") # Use toast for less intrusive feedback
            # No rerun needed, Streamlit handles it

    # --- Main Chat Area ---
    if not st.session_state.pdf_uploaded:
        st.warning("Please upload a PDF document using the sidebar to start chatting.")
    else:
        st.subheader(f"Chat about: {st.session_state.pdf_filename}")

        # Display chat history
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input - using st.chat_input
        # The prompt variable will contain the user's input when they press Enter/Send
        if user_question := st.chat_input("Ask a question about the document..."):
            # Add user message to chat history immediately
            st.session_state.chat_history.append({"role": "user", "content": user_question})
            # Display user message
            with st.chat_message("user"):
                st.markdown(user_question)

            # Generate and display assistant response
            with st.spinner("Generating response..."):
                 # Pass relevant history to the generation function if needed
                 response = st.session_state.chatbot.generate_response(
                     user_question,
                     st.session_state.chat_history[:-1] # Pass history *before* the latest user question
                 )

            # Add assistant response to chat history
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            # Display assistant response
            with st.chat_message("assistant"):
                st.markdown(response)
            # No explicit rerun needed here either

        # Download chat history button (consider placing in sidebar or below chat)
        if st.session_state.chat_history:
            chat_text = "\n\n".join([
                f"{msg['role'].capitalize()}: {msg['content']}"
                for msg in st.session_state.chat_history
            ])
            # Use a consistent file name format
            download_filename = f"chat_history_{st.session_state.pdf_filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            st.download_button(
                label="Download Chat History",
                data=chat_text.encode('utf-8'), # Encode to bytes
                file_name=download_filename,
                mime="text/plain"
            )

# --- Run the App ---
if __name__ == "__main__":
    main()