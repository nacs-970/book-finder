"""
Chat Application with RAG (Retrieval Augmented Generation)
Demonstrates document-based question answering with vector search
"""


import streamlit as st
import sys
import os
from pathlib import Path
import tempfile

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
 
from utils import LLMClient, SimpleRAGSystem, get_available_models, load_sample_documents, load_sample_documents_for_demo

def init_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "llm_client" not in st.session_state:
        st.session_state.llm_client = None
    if "rag_system" not in st.session_state:
        st.session_state.rag_system = None
    if "rag_initialized" not in st.session_state:
        st.session_state.rag_initialized = False


def display_chat_messages():
    """Display chat messages"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message.get("context_used", False):
                st.markdown("📚 *Used document context*")
            st.markdown(message["content"])


# def display_documents():
#     """Display documents in the RAG system"""
#     if st.session_state.rag_system:
#         docs = st.session_state.rag_system.list_documents()

#         if docs and not any("error" in doc for doc in docs):
#             st.subheader("📄 Documents in Knowledge Base")
#             for doc in docs:
#                 with st.expander(f"📄 {doc.get('doc_id', 'Unknown')} ({doc.get('chunks', 0)} chunks)"):
#                     st.json(doc.get('metadata', {}))
#                     if st.button(f"Delete {doc['doc_id']}", key=f"delete_{doc['doc_id']}"):
#                         result = st.session_state.rag_system.delete_document(
#                             doc['doc_id'])
#                         st.success(result)
#                         st.rerun()
#         else:
#             st.info("No documents in knowledge base yet.")


def main():
    st.set_page_config(
        page_title="Chat with RAG",
        page_icon="📚",
        layout="wide"
    )

    st.title("📚 Book Finder")
    st.markdown(
        "AI chat with document-based knowledge retrieval - Enterprise-ready starter code!")

    # Initialize session state
    init_session_state()

    # Sidebar configuration
    with st.sidebar:
        # st.header("⚙️ CHANGE")


        
        st.markdown("### 📚 About")
        st.markdown("""
        This RAG-enabled chat app demonstrates:
        - Document ingestion and vectorization
        - Semantic search and retrieval
        - Context-aware responses
        - Knowledge base management
        
        **Features:**
        - Upload PDF and text files
        - Semantic search across documents
        - Contextual AI responses
        - Document management
        
        **For Students:**
        - Experiment with different embedding models
        - Implement advanced chunking strategies
        - Add metadata filtering
        - Create document summarization
        - Build citation systems
        """)
        
        st.divider()

        # Clear chat button
        if st.button("🗑️ Clear Chat", type="secondary"):
            st.session_state.messages = []
            st.rerun()

                
        

    # Main interface - Two tabs
    tab1, = st.tabs(["💬 Chat"])

    with tab1:
        
        # Main chat interface
        # if not st.session_state.llm_client or not st.session_state.rag_system:
        #     st.warning(
        #         "⚠️ Please initialize both Model and RAG system in the sidebar first!")
        #     return

        # Display existing chat messages
        display_chat_messages()

        # Example queries
        st.markdown("### 💡 Try these example queries:")
        col1, col2, col3, col4, col5 = st.columns(5)
        # เหลือแก้ st.session_state.example_query

        with col1:
            if st.button("Romantic 💖"):
                st.session_state.example_query = "romantic"

        with col2:
            if st.button("Horror 👻"):
                st.session_state.example_query = "horror"

        with col3:
            if st.button("Drama 🥺"):
                st.session_state.example_query = "drama"

        with col4:
            if st.button("Fantasy 👽"):
                st.session_state.example_query = "fantasy"

        with col5:
            if st.button("Action 💥"):
                st.session_state.example_query = "action"

            

        # Chat input
        prompt = st.chat_input("Please enter your request about the book...")

        # Handle example query
        if hasattr(st.session_state, 'example_query'):
            prompt = st.session_state.example_query
            delattr(st.session_state, 'example_query')

        if prompt:
            # Add user message to chat history
            st.session_state.messages.append(
                {"role": "user", "content": prompt})

            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)

            # Generate and display assistant response
            with st.chat_message("assistant"):
                with st.spinner("Searching documents and generating response..."):
                    # Get relevant context from RAG system
                    context = st.session_state.rag_system.get_context_for_query(
                        prompt, max_context_length=2000)

                    # Create enhanced prompt with context
                    enhanced_prompt = f"""
                    Based on the following information from the knowledge base, please answer the user's question:

                    {context}

                    User Question: {prompt}

                    Please provide a comprehensive answer based on the information provided above. If the information is not sufficient or not found in the knowledge base, please mention that clearly.
                    """

                    # Prepare messages for LLM
                    messages = []
                    # Add conversation history (excluding current question)
                    for msg in st.session_state.messages[:-1]:
                        messages.append(
                            {"role": msg["role"], "content": msg["content"]})

                    # Add the enhanced prompt
                    messages.append(
                        {"role": "user", "content": enhanced_prompt})

                    # Get response from LLM
                    response = st.session_state.llm_client.chat(messages)

                    # Display response
                    st.markdown(response)

                    # Show retrieved context in expander
                    with st.expander("📄 Retrieved Context"):
                        st.markdown(context)

                    # Add assistant response to chat history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response,
                        "context_used": True
                    })


if __name__ == "__main__":
    main()