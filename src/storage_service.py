import chromadb

"""storage service class --> chromadb (vectore database)"""

class StorageService:
  def __init__(self, collection_name='news_collection'):
    self.client = chromadb.PersistentClient()
    self.collection = self.client.get_or_create_collection(name=collection_name)

  def save_articles(self, articles):
    ids = [article['id'] for article in articles]
    documents = [article['content'] for article in articles]
    metadatas = [{'title': article['title']} for article in articles]

    self.collection.upsert(ids=ids, documents=documents, metadatas=metadatas)

  def get_all_articles(self):
    return self.collection.get()

  def get_articles(self, limit=5):
    result = self.collection.get()
    articles = []

    for i in range(min(limit, len(result['ids']))):
      articles.append({
        'id': result['ids'][i],
        'content': result['documents'][i],
        'title': result['metadatas'][i]['title'],
      })

    return articles

  def update_article_analysis(self, article_id, summary, topic):
    existing = self.collection.get(ids=[article_id])
    if existing['ids']:
      metadata = existing['metadatas'][0]
      metadata['summary'] = summary
      metadata['topic'] = topic
      self.collection.update(ids=[article_id], metadatas=[metadata])