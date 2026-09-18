from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class NLPService:
    def __init__(self, api_key: str):
        self.llm = init_chat_model(
            model='Qwen/Qwen3-32B',
            api_key = api_key,
            base_url = 'https://router.huggingface.co/v1',
            model_provider='huggingface',
        )

        summarize_prompt = ChatPromptTemplate.from_messages([
            ('system', 'Summarize the article accurately and concisely. Use only information from the article.'),
            ('user', '{text}')
        ])

        topic_prompt = ChatPromptTemplate.from_messages([
            ("system", "Generate one short headline for this article under 5 words."),
            ("user", "{text}")
        ])

        self.summarize_chain = summarize_prompt | self.llm | StrOutputParser()
        self.topic_chain = topic_prompt | self.llm | StrOutputParser()
    
    async def summarize_text(self, text: str) -> str:
        truncated_text = ' '.join(text.split()[:500])
        return await self.summarize_chain.ainvoke({"text": truncated_text})

    async def extract_topic(self, text: str) -> str:
        truncated_text = ' '.join(text.split()[:200])
        return await self.topic_chain.ainvoke({"text": truncated_text})