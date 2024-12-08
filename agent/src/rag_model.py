from langchain_huggingface import HuggingFaceEndpoint
from langchain.agents import create_tool_calling_agent, AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain.tools import tool

from agent.database.retriever import Retriever, DenseModelType, SparseModelType
from agent.src.utils import ModelType, get_system_prompt
from agent.src.med_prompts import get_prompt

from langchain_mistralai import ChatMistralAI

from sentence_transformers import CrossEncoder

model = CrossEncoder(
    "jinaai/jina-reranker-v2-base-multilingual",
    automodel_args={"torch_dtype": "auto"},
    trust_remote_code=True,
)

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
    
    coll_name="med_db_e5_large_longer200"#"med_db_e5_large"#"med_db_e5_large_bm42"
    
    replies = retriever.search(
        query = query,
        collection_name=coll_name,
        topk=30,
        score_threshold=0.7,
    )

    if replies:
        # sentence_pairs = [[query, doc[0].page_content] for doc in replies]
        # scores = model.predict(sentence_pairs, convert_to_tensor=True).tolist()
        
        rankings = model.rank(query, [doc[0].page_content for doc in replies], return_documents=True, convert_to_tensor=True)[:3]
        
        return '\n\n'.join([f"Score: {ranking['score']:.4f}, Metadata: {[v for k,v in replies[ranking['corpus_id']][0].metadata.items() if k in ['title', 'authors', 'publication_date', 'doi_link']]}, Text: {ranking['text']}" for ranking in rankings])
        #return '\n\n'.join([f'Text {i+1}: '+reply[0].page_content for i, reply in enumerate(replies)]) #, [reply[0].metadata for reply in replies]
    else:
        return 'There is no information for your request in database.'


class MedFusionLLM:
    def __init__(self, 
                model_type: ModelType,
                api_key:str=None, 
                hf_token:str=None,
                token:str=None) -> None:
        
        self.api_key = api_key
        self.hf_token = hf_token
        self._model_type = model_type 
        
        self.token = token
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
                llm = ChatMistralAI(api_key=self.token, model="mistral-large-latest", timeout=30)
                
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
        
        