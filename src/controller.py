class NewsController:
  def __init__(self, news_service, storage_service, nlp_service=None):
    self.news_service = news_service
    self.storage_service = storage_service
    self.nlp_service = nlp_service

  def process_and_store_news(self):
    articles = self.news_service.fetch_news()
    if articles:
      self.storage_service.save_articles(articles)
    return articles

  def process_article_insights(self, limit=5):
    if not self.nlp_service:
      return []

    articles = self.storage_service.get_articles(limit=limit)
    results = []

    for article in articles:
      summary = self.nlp_service.summarize_text(article['content'])
      generated_title = self.nlp_service.extract_topic(article['content'])

      self.storage_service.update_article_analysis(article['id'], summary, generated_title)

      results.append({
          'id': article['id'],
          'original_title': article['title'],
          'generated_title': generated_title,
          'summary': summary,
      })
    return results