from langchain.tools import tool
from agent.src.med_prompts import get_prompt
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.prompts import ChatPromptTemplate
from agent.src.utils import ModelType, get_system_prompt
from langchain_core.output_parsers import StrOutputParser
from agent.database.retriever import Retriever, DenseModelType, SparseModelType
from langchain.agents import create_tool_calling_agent, AgentExecutor, create_react_agent



# @tool
# def medical_retriever(query) -> str:
#     """Searches data by query in the database of medical documents from the cochrane library.
# query must be in English. Call this tool again with different query to find more documents"""

#     #call retriever
#     reply = None

#     if reply is not None:
#         return reply
#     else:
#         return 'There is no information for your request in database.'

@tool
def medical_retriever(query) -> str:
    """Searches data by query in the database of medical documents from the cochrane library.
query must be in English. Call this tool again with different query to find more documents.
Some documents don't contain relevant information, you need to be smart and careful"""
    
    retriever = Retriever(
        model_type=DenseModelType.E5_LARGE,
        sparse_model_type=SparseModelType.BM42,
        localhost="localhost",#'77.234.216.100',
        device=0,
        dense_search=True,
        sparse_search=False,#False
    )
    
    coll_name="med_db_e5_large"#"med_db_e5_large_bm42"
    
    replies = retriever.search(
        query = query,
        collection_name=coll_name,
        topk=3,
        score_threshold=0,
    )

    if replies:
        return '\n\n'.join([f'Text {i+1}: '+reply[0].page_content for i, reply in enumerate(replies)]) #, [reply[0].metadata for reply in replies]
    else:
        return 'There is no information for your request in database.'


class MedFusionLLM:
    def __init__(self, 
                model_type: ModelType,
                api_key:str=None, 
                hf_token:str=None) -> None:
        
        self.api_key = api_key
        self.hf_token = hf_token
        self._model_type = model_type 
    
        self._agent_executor = self._setup_model()
        self.system_prompt = get_system_prompt()


    def _setup_model(self):
        """Initialization for the model"""
        try:
            if self._model_type == ModelType.MICROSOFT:
                llm = HuggingFaceEndpoint(
                    repo_id=ModelType.MICROSOFT.value,
                    task="text-generation",
                    do_sample=False,
                    repetition_penalty=1.03,
                    huggingfacehub_api_token=self.hf_token
                )          
            elif self._model_type == ModelType.MISTRAL:
                llm = ChatMistralAI(api_key=self.api_key, model="mistral-large-latest", timeout=30)
                
            template = PromptTemplate.from_template(get_prompt())
            tools = [medical_retriever] #query_paraphraze
            agent = create_react_agent(llm, tools, template)
            agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)
            return agent_executor
        except Exception as err:
            raise ValueError(f'Что-то не так с параметрами модели: {err}')

    def test_retriever(self, query):
        return medical_retriever(query)
    
    def invoke(self, user_input, chat_history=''):
        try:
            response = self._agent_executor({"input": user_input, 'chat_history': chat_history})['output']
            return response
        except Exception as e:
            return f"\nI'm sorry, I encountered an error while processing your request. Please try again.\nError: {e}\n"
    
    def healthcheck(self, content:str):
        try:
            llm = ChatMistralAI(api_key=self.api_key, model="mistral-large-latest", timeout=30)
            prompt = ChatPromptTemplate.from_messages([("system", 'none')])
            chain = prompt | llm | StrOutputParser()
            output = chain.invoke({"content": content})
            return output
        except Exception as err:
            raise ValueError(f'Что-то не так с вызовом модели: {err}')
        