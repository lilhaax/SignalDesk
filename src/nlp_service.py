from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
import asyncio

"""Nlp service class --> summarization and topic generation"""

class NLPService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.llm = init_chat_model(
            model="gpt-oss:20b-cloud",
            api_key=api_key,
            base_url="https://ollama.com/v1",
        )

        self.summarizer_agent = create_agent(
            model=self.llm,
            system_prompt="Summarize the article accurately and concisely. Use only information from the article. Do not add opinions, assumptions, or facts. Write in clear, neutral English."
        )

        self.topicgenerator_agent = create_agent(
            model=self.llm,
            system_prompt="Generate one short headline for this article. Keep it clear, professional, and under 5 words."
        )

    def _summarize_sync(self, text):
        truncated_text = ' '.join(text.split()[:500])
        result = self.summarizer_agent.invoke({
            "messages": [
                {"role": "user", "content": truncated_text}
            ]
        })
        return result["messages"][-1].content

    def _extract_topic_sync(self, text):
        truncated_text = ' '.join(text.split()[:200])
        result = self.topicgenerator_agent.invoke({
            "messages": [
                {"role": "user", "content": truncated_text}
            ]
        })
        return result["messages"][-1].content
    
    async def summarize_text(self, text):
        return await asyncio.to_thread(self._summarize_sync, text)
    
    async def extract_topic(self, text):
        return await asyncio.to_thread(self._extract_topic_sync, text)