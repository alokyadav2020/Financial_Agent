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
        You are a value assurance expert in financial reporting, business valuation , M&A and known for understanding and interpreting Economics from top tier consulting firms (McKinsey, BCG and Bain)  and known for producing concise, insightful, and action-oriented Answers.

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
                # st.rerun()

        # Clear chat history button
        if st.button("Clear Chat History"):
            st.session_state.chat_history = []
            # st.rerun()

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

# if __name__ == "__main__":
#     main()
# import streamlit as st
# from huggingface_hub import InferenceClient
# import PyPDF2
# from datetime import datetime

# class PDFChatbot:
#     def __init__(self):
#         # Initialize authenticated Hugging Face Inference client
#         self.client = InferenceClient(token=st.secrets['hf_token'])
#         self.pdf_text = ''

#     def extract_text_from_pdf(self, pdf_file):
#         """Extract text from uploaded PDF file."""
#         try:
#             reader = PyPDF2.PdfReader(pdf_file)
#             text = ''
#             for page in reader.pages:
#                 text += (page.extract_text() or '') + "\n"
#             return text
#         except Exception as e:
#             st.error(f"Error extracting text from PDF: {e}")
#             return ''

#     def generate_response(self, question):
#         """Generate response using Hugging Face chat endpoint."""
#         prompt = f"""
# You are an expert in financial reporting and business valuation from top consulting firms.
# Based on the document below, answer the question concisely.

# Document:
# {self.pdf_text[:2000]}

# Question: {question}
# """
#         messages = [
#             {"role": "system", "content": "You are a helpful assistant answering questions about PDF content."},
#             {"role": "user", "content": prompt}
#         ]
#         try:
#             resp = self.client.chat_completion(
#                 model=st.secrets['hf_model'],
#                 messages=messages,
#                 max_tokens=500,
#                 temperature=0.7
#             )
#             return resp.choices[0].message.content
#         except Exception as e:
#             return f"Error generating response: {e}"

# # --- Session Initialization ---
# def init_state():
#     if 'chatbot' not in st.session_state:
#         st.session_state.chatbot = PDFChatbot()
#     if 'chat_history' not in st.session_state:
#         st.session_state.chat_history = []
#     if 'pdf_uploaded' not in st.session_state:
#         st.session_state.pdf_uploaded = False

# # --- Main App ---
# def main():
#     st.title("Delivery Assurance Chatbot")

#     # Sidebar session info
#     st.sidebar.markdown("### Session Information")
#     st.sidebar.info(f"Current Date and Time (UTC): 2025-04-30 18:00:15")
#     st.sidebar.info(f"Current User: alokyadav2020")

#     init_state()

#     # PDF upload
#     st.subheader("Upload PDF Document")
#     uploaded = st.file_uploader("Choose a PDF file", type="pdf")
#     if uploaded and not st.session_state.pdf_uploaded:
#         with st.spinner("Processing PDF..."):
#             text = st.session_state.chatbot.extract_text_from_pdf(uploaded)
#             if text:
#                 st.session_state.chatbot.pdf_text = text
#                 st.session_state.pdf_uploaded = True
#                 st.success("PDF processed successfully!")
#                 with st.expander("View PDF Content"):
#                     st.text_area("Extracted Text", text, height=200)

#     # Chat interface
#     if st.session_state.pdf_uploaded:
#         st.subheader("Chat with Agent")
#         # Display chat history
#         for msg in st.session_state.chat_history:
#             if msg['role'] == 'user':
#                 st.info(f"**You:** {msg['content']}")
#             else:
#                 st.markdown(f"**Assistant:** {msg['content']}")

#         # Use a form to clear input on submit
#         with st.form(key='chat_form', clear_on_submit=True):
#             user_input = st.text_input("Ask a question about the document:")
#             submitted = st.form_submit_button("Send")
#         if submitted and user_input:
#             # Append user question and generate response
#             st.session_state.chat_history.append({"role": "user", "content": user_input})
#             with st.spinner("Generating response..."):
#                 answer = st.session_state.chatbot.generate_response(user_input)
#             st.session_state.chat_history.append({"role": "assistant", "content": answer})

#         if st.button("Clear Chat History"):
#             st.session_state.chat_history = []

#     # Download history
#     if st.session_state.chat_history:
#         chat_text = "\n\n".join([
#             f"User: {m['content']}" if m['role']=='user' else f"Assistant: {m['content']}"
#             for m in st.session_state.chat_history
#         ])
#         st.download_button(
#             "Download Chat History",
#             data=chat_text,
#             file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
#             mime="text/plain"
#         )

# if __name__ == '__main__':
#     main()
