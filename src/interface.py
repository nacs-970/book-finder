"""
Chat Application with RAG (Retrieval Augmented Generation)
Demonstrates document-based question answering with vector search
"""

import json
import streamlit as st
import sys
import os
from pathlib import Path
import tempfile

# Add project root to path
project_root = Path(__file__).parent.parent 
sys.path.insert(0, str(project_root))
 
from utils import LLMClient, SimpleRAGSystem, get_available_models

Recommeded_books = set()

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
    if "books" not in st.session_state:
        st.session_state.books = set()


def display_chat_messages():
    """Display chat messages"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message.get("context_used", False):
                st.markdown("📑 *Used document context*")
            st.markdown(message["content"])

def main():
    st.set_page_config(
        page_title="Chat with RAG",
        page_icon="📚",
        layout="wide"
    )

    st.title("📚 BOOK FINDER")
    st.markdown(
        "Discover books you’ll love with just a few words, and let every search lead you to new adventures")
    
    init_session_state()

    # Auto initialize LLM model (no sidebar config)
    if st.session_state.llm_client is None:
        st.session_state.llm_client = LLMClient(
            model="gpt-4o-mini",  # หรือเปลี่ยนเป็น default model ของคุณ
            temperature=0.7,
            max_tokens=2000
        )

    # Auto initialize RAG system (with sample docs)
    if st.session_state.rag_system is None:
        st.session_state.rag_system = SimpleRAGSystem()
        if not st.session_state.rag_initialized:
            st.session_state.rag_initialized = True


    with st.sidebar:
        st.markdown("### 📚 About")
        st.markdown("""
        **Features:**
        - Displays the title of the recommended book
        - Shows average reader rating or review score
        - Shows the official publication date of the book
        - Provides the total number of pages for quick reference
        - Highlights the main categories or themes
        - Indicates the overall tone or emotional atmosphere of the book
        - A concise summary or blurb giving you the essence of the book
                
        **How to use:**
        - Enter a genre or theme, for example romantic sci-fi, classic mystery, or self-help.
        - Provide a short summary or blurb that describes the type of story or topic you’re looking for.
        - The system will then suggest similar books most closely related to your input.
        """)

        st.divider()
        # Clear chat button
        if st.button("🗑️ Clear Chat", type="secondary"):
            st.session_state.messages = []
            st.session_state.books = set()
            st.rerun()

    # Main chat interface
    if not st.session_state.llm_client or not st.session_state.rag_system:
        st.warning(
            "⚠️ Please initialize both Model and RAG system in the sidebar first!")
        return

    # Display existing chat messages
    display_chat_messages()

    # Chat input
    prompt = st.chat_input("Ask me anything about the documents...")

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
            with st.spinner("Please enter your request about the book..."):
                # Get relevant context from RAG system
                context = st.session_state.rag_system.get_context_for_query(
                    prompt + f"that isn't {list(st.session_state.books)}", max_context_length=2000)

                # Create enhanced prompt with context
                enhanced_prompt = f"""

                {context}

                User Question: {prompt} that isn't {list(st.session_state.books)}

                Based on the following information from the knowledge base, please answer the user's question:
                Your job is to give a review or introducing a new book to user with given exist data
                if the book already been recommended, don't mention it again.

                Sort it out by rating (max is 5)
                3 to 10 books Recommendation 
                (if i didn't said any before)

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

                answer=""
                response = json.loads(response)
                Books_info = response.get("books_info", [])
                messages = response.get("dupe_messages", "")

                if messages:
                    answer += f"{messages}\n\n"

                if Books_info:
                    for idx, book in enumerate(Books_info, 1):
                        genres = ", ".join(list(book.get('genres', ['N/A'])))
                        moods = ", ".join(list(book.get('moods', ['N/A'])))

                        title = book.get('title', 'N/A')
                        if title in st.session_state.books:
                            answer += f"**{title}** has already been recommended\n\n"
                            continue

                        st.session_state.books.add(title)
                        answer += f"### {idx}. {title} \n"
                        answer += f"- **Average Rating:** {book.get('rating', 'N/A')}\n"
                        answer += f"- **release_date:** {book.get('release_date', 'N/A')} \n"
                        answer += f"- **Genres:** {genres}\n"
                        answer += f"- **Moods:** {moods}\n"
                        answer += f"- **Pages:** {book.get('page_count', 'N/A')}\n"
                        answer += f"- **Summary:** {book.get('summary', 'N/A')}\n\n"
                        answer += "---\n"

                # Display response
                st.markdown(answer)

                # Show retrieved context in expander
                with st.expander("📄 Retrieved Context"):
                    st.markdown(context)

                # Add assistant response to chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "context_used": True
                })
     # Example queries
    st.markdown("### 📁 Start your journey with these book queries:")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if st.button("💥ACTION"):
            st.session_state.example_query = "Recommend some action books."
            st.rerun()
    with col2:
        if st.button("🎭DRAMA"):
            st.session_state.example_query = "Recommend some drama books."
            st.rerun()
    with col3:
        if st.button("🏜️FANTASY"):
            st.session_state.example_query = "Recommend some fantasy books."
            st.rerun()
    with col4:
        if st.button("👻HORROR"):
            st.session_state.example_query = "Recommend some horror books."
            st.rerun()
    with col5:
        if st.button("💋ROMANTIC"):
            st.session_state.example_query = "Recommend some romantic books."
            st.rerun()

    
if __name__ == "__main__":
    main()
