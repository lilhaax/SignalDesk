from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from langchain_core.prompts import PromptTemplate
from langchain.chat_models import init_chat_model

class RAGState(TypedDict):
    question: str
    intent: str
    content: str 
    response: str

class RAGService:
    def __init__(self, storage_service, api_key:str):
        self.storage_service = storage_service 
        self.llm = init_chat_model(
            model='Qwen/Qwen3-32B',
            api_key = api_key,
            base_url = 'https://router.huggingface.co/v1',
            model_provider='huggingface',
        )
        self.graph = self._build_graph()
    
    def _classify_intent(self, state: RAGState) -> dict:
        prompt = f"Determine if this query needs news database search or general knowledge. Answer ONLY 'NEWS' or 'GENERAL'.\nQuery: {state['question']}"
        result = self.llm.invoke(prompt)
        intent = 'NEWS' if 'NEWS' in result.content.upper() else 'GENERAL'
        return {'intent': intent}
    
    def _retrieve_news(self, state:RAGState) -> dict:
        docs = self.storage_service.collection.query(
            query_texts = [state['question']],
            n_results = 2
        )
        context = " ".join(docs['documents'][0]) if docs['documents'] else ''
        return {'content': context}
    
    def _generate_answer(self, state:RAGState) -> dict:
        if state['intent'] == 'NEWS':
            prompt = f"Answer the user query based ONLY on this news context:\n{state['content']}\n\nQuery: {state['question']}"
        else:
            prompt = f'Answer this query directly:\n{state["question"]}'
        
        result = self.llm.invoke(prompt)
        return {'response': result.content}
    
    def _route_intent(self, state:RAGState) -> Literal['retrieve_news', 'generate_answer']:
        if state['intent'] == 'NEWS':
            return 'retrieve_news'
        return 'generate_answer'
    
    def _build_graph(self):
        workflow = StateGraph(RAGState)

        workflow.add_node('classifier', self._classify_intent)
        workflow.add_node('news_retriever', self._retrieve_news)
        workflow.add_node('answer_generator', self._generate_answer)

        workflow.set_entry_point('classifier')

        workflow.add_conditional_edges(
            'classifier',
            self._route_intent,
            {
                'retrieve_news': 'news_retriever',
                'generate_answer': 'answer_generator',
            }
        )

        workflow.add_edge('news_retriever', 'answer_generator')
        workflow.add_edge('answer_generator', END)

        return workflow.compile()
    
    async def run(self, question:str) -> str:
        initial_state = {'question':question, 'intent':'', 'content':'', 'response':''}
        final_state = await self.graph.ainvoke(initial_state)
        return final_state['response']