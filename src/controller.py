"""controller class"""

class NewsController:
  def __init__(self, news_service, storage_service, nlp_service=None, rag_service=None):
    self.news_service = news_service
    self.storage_service = storage_service
    self.nlp_service = nlp_service
    self.rag_service = rag_service

  async def process_and_store_news(self, query='technology'):
    articles = await self.news_service.fetch_news(query)
    if articles:
      self.storage_service.save_articles(articles)
    return articles

  async def process_article_insights(self, limit=10):
    if not self.nlp_service:
      return []

    articles = self.storage_service.get_articles(limit=limit)
    results = []

    for article in articles:
      summary = await self.nlp_service.summarize_text(article['content'])
      generated_title = await self.nlp_service.extract_topic(article['content'])

      self.storage_service.update_article_analysis(article['id'], summary, generated_title)

      results.append({
          'id': article['id'],
          'original_title': article['title'],
          'generated_title': generated_title,
          'summary': summary,
      })
    return results
  
  async def answer_user_query(self, query):
    if not self.rag_service:
      return ''
    return await self.rag_service.generate_response(query)