import asyncio
from news_service import NewsService
from storage_service import StorageService
from controller import NewsController
from nlp_service import NLPService
from rag_service import RAGService

async def main():
    NEWS_API_KEY = ''
    API_KEY = ''

    news_service = NewsService(api_key=NEWS_API_KEY)
    storage_service = StorageService()
    nlp_service = NLPService(API_KEY)
    rag_service = RAGService(storage_service, API_KEY)

    controller = NewsController(news_service, storage_service, nlp_service, rag_service)

    print("Fetching and storing news...")
    await controller.process_and_store_news('technology')

    print("Generating summaries and insights...")
    insights = await controller.process_article_insights(limit=3)

    print("\nAnswering query with RAG...")
    response = await controller.answer_user_query("What is the latest update about AI?")
    print(f"\nRAG Answer: {response}")

    for i, article in enumerate(insights, 1):
        print(f"\n{'=' * 60}")
        print(f"NEWS {i}")
        print(f"{'=' * 60}")
        print(f"Original Title: {article['original_title']}")
        print(f"Generated Title: {article['generated_title']}")
        print(f"Summary: {article['summary']}")

if __name__ == '__main__':
    asyncio.run(main())