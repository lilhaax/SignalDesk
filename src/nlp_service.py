#!pip install "numpy==2.2.6" "transformers==4.57.1" "sentencepiece"
from transformers import pipeline

"""Nlp service class --> summarization and topic generation"""

class NLPService:
  def __init__(self):
    self.summarizer = pipeline('summarization', model='facebook/bart-large-cnn')
    self.topic_generator = pipeline('text2text-generation', model='google/flan-t5-base')

  def summarize_text(self, text):
    truncated_text = text[:1024]
    summary = self.summarizer(truncated_text, max_length=250, min_length=120, do_sample=False)
    return summary[0]['summary_text']

  def extract_topic(self, text):
    truncated_text = text[:512]
    prompt = f"Write a short, catchy title for this news article:\n\n{truncated_text}"
    result = self.topic_generator(prompt, max_length=20, clean_up_tokenization_spaces=True)
    return result[0]['generated_text'].strip()