import os
import asyncio
import streamlit as st
import pandas as pd

from storage_service import StorageService
from news_service import NewsService
from nlp_service import NLPService
from rag_service import RAGService
from controller import NewsController

# Page configuration
st.set_page_config(
    page_title="AI News Summarizer & RAG System",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# تابع کمکی برای اجرای کدهای Async در استریم‌لیت بدون هیچ مشکل و Crash
def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    if loop.is_running():
        return asyncio.run_coroutine_threadsafe(coro, loop).result()
    else:
        return loop.run_until_complete(coro)

# Initialize Storage Service
storage_service = StorageService()

# Sidebar Configuration
with st.sidebar:
    st.image("https://img.icons8.com/color/96/news.png", width=70)
    st.title("Settings")
    
    default_news_key = os.getenv("NEWS_API_KEY", "")
    default_llm_key = os.getenv("LLM_API_KEY", "")
    
    news_api_key = st.text_input("NewsData.io API Key:", value=default_news_key, type="password")
    llm_api_key = st.text_input("LLM/Ollama API Key:", value=default_llm_key, type="password")
    
    st.divider()
    
    st.subheader("Fetch News")
    query_topic = st.text_input("Topic Query:", value="technology")
    fetch_limit = st.slider("Articles to Process:", min_value=1, max_value=5, value=3)
    
    fetch_btn = st.button("🔄 Fetch & Process News", use_container_width=True, type="primary")

# Process & Fetch Trigger
if fetch_btn:
    if not news_api_key or not llm_api_key:
        st.warning("Please provide both News API Key and LLM API Key in the sidebar.")
    else:
        with st.spinner("Fetching news and running AI analysis..."):
            try:
                news_service = NewsService(api_key=news_api_key)
                nlp_service = NLPService(api_key=llm_api_key)
                rag_service = RAGService(storage_service, api_key=llm_api_key)
                
                controller = NewsController(news_service, storage_service, nlp_service, rag_service)
                
                # استفاده از تابع run_async برای اجرای قطعی
                articles = run_async(controller.process_and_store_news(query=query_topic))
                
                if articles:
                    insights = run_async(controller.process_article_insights(limit=fetch_limit))
                    st.success(f"Successfully processed and stored {len(insights)} articles!")
                    st.rerun()
                else:
                    st.info("No articles found for the given topic query.")
            except Exception as e:
                st.error(f"Error processing news: {e}")

# Main UI Tabs
st.markdown('<div class="main-header">AI News Summarizer & RAG Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Fetch real-time news, generate AI summaries, and chat with your vector database.</div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📰 News & Insights", "🤖 RAG Assistant", "🗄️ Vector Database"])

# --- Tab 1: Articles ---
with tab1:
    st.subheader("Latest Analyzed News")
    
    articles = storage_service.get_articles(limit=10)
    
    if not articles:
        st.info("No articles found in the database. Use the sidebar to fetch new articles.")
    else:
        for idx, article in enumerate(articles, 1):
            summary = article.get('summary', 'No summary available.')
            topic = article.get('topic', article.get('title'))
            
            with st.expander(f"📌 {idx}. {topic}", expanded=(idx == 1)):
                st.markdown(f"**Original Title:** {article.get('title')}")
                if 'summary' in article and article['summary']:
                    st.info(f"**Generated Summary:**\n\n{summary}")
                
                with st.popover("View Full Content"):
                    st.write(article['content'])

# --- Tab 2: RAG Assistant ---
with tab2:
    st.subheader("RAG News Chatbot")
    st.write("Ask any question. The system will determine if it requires context from stored news articles or general knowledge.")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_query := st.chat_input("Ask a question (e.g., What is the latest update about AI?)..."):
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.chat_message("assistant"):
            if not llm_api_key:
                st.error("Please provide an LLM API Key in the sidebar.")
            else:
                with st.spinner("Analyzing query and generating response..."):
                    try:
                        rag_service = RAGService(storage_service, api_key=llm_api_key)
                        
                        intent = run_async(rag_service.classify_intent(user_query))
                        
                        if intent == "NEWS":
                            st.caption("🔍 **Source:** ChromaDB News Context")
                        else:
                            st.caption("🌐 **Source:** General Knowledge Model")
                        
                        response = run_async(rag_service.generate_response(user_query))
                        st.markdown(response)
                        
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    except Exception as e:
                        st.error(f"Error generating response: {e}")

# --- Tab 3: Database View ---
with tab3:
    st.subheader("Vector Store Status (ChromaDB)")
    
    all_docs = storage_service.get_all_articles()
    
    if all_docs and 'ids' in all_docs and all_docs['ids']:
        st.metric(label="Total Stored Articles", value=len(all_docs['ids']))
        
        data = []
        for i in range(len(all_docs['ids'])):
            meta = all_docs['metadatas'][i] if all_docs['metadatas'] else {}
            data.append({
                "ID": all_docs['ids'][i],
                "Title": meta.get('title', 'N/A'),
                "Topic": meta.get('topic', 'N/A'),
                "Has Summary": 'summary' in meta
            })
        
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Database is currently empty.")