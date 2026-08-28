from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from news_service import NewsService
from storage_service import StorageService
from controller import NewsController
from nlp_service import NLPService
from rag_service import RAGService

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = 'YOUR_NEWS_DATA_API_KEY'  
news_service = NewsService(api_key=API_KEY)
storage_service = StorageService()
nlp_service = NLPService()
rag_service = RAGService(storage_service)

controller = NewsController(
    news_service,
    storage_service,
    nlp_service,
    rag_service
)

class QueryRequest(BaseModel):
    query: str

@app.get("/api/fetch-news")
def fetch_news():
    try:
        controller.process_and_store_news(query='technology')
        insights = controller.process_article_insights(limit=5)
        return {"status": "success", "articles": insights}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
def chat(request: QueryRequest):
    try:
        response = controller.answer_user_query(request.query)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))