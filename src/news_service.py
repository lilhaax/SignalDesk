import httpx

class NewsService:
  def __init__(self, api_key):
    self.api_key = api_key
    self.base_url = "https://api.thenewsapi.com/v1/news/top"

  async def fetch_news(self, query='technology'):
    params = {
      'api_token':self.api_key,
      'search':query,
      'language':'en',
      'limit':3
    }

    async with httpx.AsyncClient() as client:
      response = await client.get(self.base_url, params=params, timeout=10.0)
      response.raise_for_status()
      data = response.json()

    articles = []

    for article in data.get('data', [])[:3]:
      if article.get('description'):
        articles.append({
            'id':article.get('uuid'),
            'title':article.get('title'),
            'content':article.get('description'),
        })
    return articles