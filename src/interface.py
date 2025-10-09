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

    #C3E8EB
    st.markdown("""
    <h1 style="text-align:center;
    background: -webkit-linear-gradient(#2962FF, #5ACAF9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;">
    ✨ BOOK FINDER
    </h1>
    """, unsafe_allow_html=True)

    st.markdown(
    """
    <p style='text-align: center; font-size:20px; color:#1565C0; font-weight:500;'>
        Discover books you’ll love with just a few words, and let every search lead you to new adventures
    </p>
    """,
    unsafe_allow_html=True
    )

    st.markdown("""
    <style>
    # div.stButton > button {
    #     border-radius: 12px;
    #     padding: 12px 24px;
    #     font-size: 16px;
    #     font-weight: bold;
    #     background-color: #f0f2f6;
    #     color: #2962FF;
    #     border: 1px solid #2962FF;
    #     box-shadow: 0px 3px 8px rgba(0,0,0,0.1);
    #     transition: all 0.2s ease-in-out;
    # }
    div.stButton > button:hover {
        background-color: #2962FF; 
        color: white;
        border: none;
        transform: translateY(-2px);
        box-shadow: 0px 5px 15px rgba(0,0,0,0.2);
    }
    </style>
    """, unsafe_allow_html=True)

    #EDF6F9
    #659BB9
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] {
        background-color: #FFFCEF;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
    }
    section[data-testid="stSidebar"] {
        color: #659BB9;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #659BB9;
    }
                
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <style>
    div[data-testid="stChatInput"] > div {
        border: 2px solid #FFFFFF; 
        border-radius: 30px !important;           
        padding: 20px !important;
    }

    div[data-testid="stChatInput"] > div:focus-within {
        border: 2px solid #0082FB !important;       
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <style>
    [data-testid="stChatMessage"] [data-testid="stChatMessageAvatarUser"] {
        background-color: #00BECD !important;   
        color: white !important;                
        border-radius: 50% !important;          
        padding: 8px !important;
    }

    [data-testid="stChatMessage"] [data-testid="stChatMessageAvatarAssistant"] {
        background-color: #C4E81D !important;    
        color: white !important;              
        border-radius: 50% !important;
        padding: 8px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    init_session_state()

    with st.spinner("Preparing model..."):
        # Auto initialize LLM model (no sidebar config)
        if st.session_state.llm_client is None:
            st.session_state.llm_client = LLMClient(
                model="gpt-4o-mini", 
                temperature=0.6,
                max_tokens=3500
            )

    with st.spinner("Preparing rag..."):
        # Auto initialize RAG system (with sample docs)
        if st.session_state.rag_system is None:
            st.session_state.rag_system = SimpleRAGSystem()
            if not st.session_state.rag_initialized:
                st.session_state.rag_initialized = True

    with st.sidebar:

        st.markdown("### 📖 ABOUT")
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
    prompt = st.chat_input("Ask me anything about the books...")

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
            with st.spinner("Looking for the book you want..."):
                # Get relevant context from RAG system
                #context = st.session_state.rag_system.get_context_for_query(prompt + f"that isn't {list(st.session_state.books)}", max_context_length=20000)
                context = st.session_state.rag_system.get_context_for_query(prompt)

                # Create enhanced prompt with context
                enhanced_prompt = f"""
                {context}

                Based on the following information from the knowledge base, please answer the user's question:
                Your job is to give a review or introducing a new book to user with given exist data
                if the book already been recommended, don't mention it again.

                Sort it out by rating (max is 5)
                up to 5 books Recommendation if user didn't mention about it

                User Question: {prompt} that isn't {list(st.session_state.books)}

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
                
                # sort by rating, title (highest first)
                if "books_info" in response:
                    response["books_info"].sort(key=lambda x: x.get("title"))
                    response["books_info"].sort(key=lambda x: x.get("rating", 0), reverse=True)
                
                Books_info = response.get("books_info", [])[:5]

                answer += f"{response.get('comments', '')}\n"
                if Books_info:
                    for idx, book in enumerate(Books_info, 1):
                        genres = ", ".join(list(book.get('genres', ['N/A'])))
                        moods = ", ".join(list(book.get('moods', ['N/A'])))

                        title = book.get('title', 'N/A')
                        answer += f"### {idx}. {title} \n"

                        if title in st.session_state.books:
                            answer += f"###### *(already been recommended)*\n"

                        st.session_state.books.add(title)
                        rate = 0
                        if (rate != "N/A"):
                            rate = int(book.get("rating", "N/A"))
                            
                        answer += f"- **Average Rating:** {'⭐'*rate} ({book.get('rating', 'N/A')} / 5)\n"
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
        if st.button("🗺️ADVANTURE"):
            st.session_state.example_query = "Recommend some adventure books."
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
        if st.button("💋ROMANCE"):
            st.session_state.example_query = "Recommend some romance books."
            st.rerun()

if __name__ == "__main__":
    main()
