# !pip install chromadb
import chromadb

# !pip install "numpy==2.2.6" "transformers==4.57.1" "sentencepiece"
from news_service import NewsService
from storage_service import StorageService
from controller import NewsController
from nlp_service import NLPService
from rag_service import RAGService

if __name__ == '__main__':
  API_KEY = ''

  news_service = NewsService(api_key = API_KEY)
  storage_service = StorageService()
  nlp_service = NLPService()
  rag_service = RAGService(storage_service)

  controller = NewsController(news_service, storage_service, nlp_service, rag_service)
  controller.process_and_store_news()
  insights = controller.process_article_insights(limit=5)
  response = controller.answer_user_query("What is the latest update about AI?")


for i, article in enumerate(insights, 1):
    print(f"\n{'=' * 60}")
    print(f"NEWS {i}")
    print(f"{'=' * 60}")
    print(f"Original Title: {article['original_title']}")
    print(f"Generated Title: {article['generated_title']}")
    print(f"Summary: {article['summary']}")
