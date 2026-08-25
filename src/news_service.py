import requests

"""news sevice class --> API & Fetch"""

class NewsService:
  def __init__(self, api_key):
    self.api_key = api_key
    self.base_url = "https://newsdata.io/api/1/news"

  def fetch_news(self, query='technology'):
    params = {
      'apikey':self.api_key,
      'q':query,
      'language':'en'
    }

    response = requests.get(self.base_url, params = params)
    response.raise_for_status()
    data = response.json()

    articles = []

    for article in data.get('results', [])[:5]:
      if article.get('content'):
        articles.append({
            'id':article.get('article_id'),
            'title':article.get('title'),
            'content':article.get('content'),
        })
    return articles