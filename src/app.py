import asyncio
import streamlit as st
from news_service import NewsService
from storage_service import StorageService
from nlp_service import NLPService
from rag_graph import RAGService
from controller import NewsController

st.title("News AI & RAG Dashboard")

# Sidebar for credentials
NEWS_API_KEY = st.sidebar.text_input("News API Key", type="password")
HF_API_KEY = st.sidebar.text_input("Hugging Face API Key", type="password")

# Initialize Storage
if "storage_service" not in st.session_state:
    st.session_state.storage_service = StorageService()

storage_service = st.session_state.storage_service

# Section 1: Process News
st.header("1. Fetch & Analyze News")
topic = st.text_input("Search Topic", "technology")

if st.button("Fetch and Process"):
    if not NEWS_API_KEY or not HF_API_KEY:
        st.warning("Please provide both API keys.")
    else:
        news_service = NewsService(NEWS_API_KEY)
        nlp_service = NLPService(HF_API_KEY)
        controller = NewsController(news_service, storage_service, nlp_service)

        with st.spinner("Fetching & Analyzing..."):
            asyncio.run(controller.process_and_store_news(topic))
            insights = asyncio.run(controller.process_article_insights(limit=3))
            st.success("Done!")

            for item in insights:
                st.write(f"**Original Title:** {item['original_title']}")
                st.write(f"**Generated Headline:** {item['generated_title']}")
                st.write(f"**Summary:** {item['summary']}")
                st.divider()

# Section 2: Ask RAG
st.header("2. Ask Question (RAG)")
user_query = st.text_input("Ask something about the news or general knowledge:")

if st.button("Get Answer"):
    if not HF_API_KEY:
        st.warning("Please provide Hugging Face API Key.")
    elif not user_query:
        st.warning("Please enter a query.")
    else:
        rag_service = RAGService(storage_service, HF_API_KEY)
        controller = NewsController(None, storage_service, rag_service=rag_service)

        with st.spinner("Thinking..."):
            response = asyncio.run(controller.answer_user_query(user_query))
            st.write("**Answer:**")
            st.write(response)