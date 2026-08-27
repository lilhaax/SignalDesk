# import required libraries

from transformers import pipeline

# rag service class --> prompt / RAG or GENERAL GENERATION

class RAGService:
  def __init__(self, storage_service):
    self.storage_service = storage_service
    self.llm = pipeline('text2text-generation', model='google/flan-t5-large')

  def classify_intent(self, user_query):
    prompt = f"Determine if this query needs news database search or general knowledge. Answer only 'NEWS' or 'GENERAL'. Query: {user_query}"
    result = self.llm(prompt, max_length=10)
    intent = result[0]['generated_text'].strip().upper()
    return "NEWS" if 'NEWS' in intent else 'GENERAL'

  def generate_response(self, user_query):
    intent = self.classify_intent(user_query)

    if intent == 'NEWS':
      docs = self.storage_service.collection.query(query_texts=[user_query], n_results = 2)
      context = " ".join(docs["documents"][0]) if docs["documents"] else ""
      prompt = f"Answer the user query based ONLY on this news context:\n{context}\n\nQuery: {user_query}"
    else:
      prompt = f"Answer this query directly:\n{user_query}"

    result = self.llm(prompt, max_length=200)
    return result[0]['generated_text'].strip()