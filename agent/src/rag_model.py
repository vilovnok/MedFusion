from langchain_huggingface import HuggingFaceEndpoint
from langchain.agents import create_tool_calling_agent, AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain.tools import tool, Tool
from agent.database.retriever import Retriever, DenseModelType, SparseModelType
from agent.src.utils import ModelType
from agent.src.med_prompts import get_prompt
from langchain_mistralai import ChatMistralAI
from qdrant_client import models
import ast
import onnxruntime as ort
import numpy as np
import torch
from transformers import AutoTokenizer


# Загрузка ONNX модели
onnx_model_path = "./jina-reranker-v2-base-multilingual/model.onnx"
onnx_session = ort.InferenceSession(onnx_model_path)

# Токенайзер
tokenizer = AutoTokenizer.from_pretrained("jinaai/jina-reranker-v2-base-multilingual", trust_remote_code=True)


def rank_with_onnx(query, documents):
    """
    Ранжирование документов с использованием ONNX-модели.
    """
    # Токенизация пар (query, document)
    inputs = tokenizer(
        [[query, doc] for doc in documents],
        padding=True,
        truncation=True,
        max_length=512,
        return_tensors="np",
    )

    # Преобразование типов данных для ONNX (int32 -> int64)
    onnx_inputs = {
        "input_ids": inputs["input_ids"].astype(np.int64),
        "attention_mask": inputs["attention_mask"].astype(np.int64),
    }

    # Выполнение инференса ONNX
    logits = onnx_session.run(None, onnx_inputs)[0]

    # Ранжирование документов по убыванию логитов
    scores = np.squeeze(logits, axis=1)
    ranked_indices = np.argsort(-scores)

    # Возвращаем документы с оценками и индексами
    return [{"corpus_id": i, "text": documents[i], "score": scores[i]} for i in ranked_indices]


def medical_retriever_function(query, array):
    """
    Основная функция для поиска и ранжирования медицинской информации.
    """
    retriever = Retriever(
        model_type=DenseModelType.E5_LARGE,
        sparse_model_type=SparseModelType.BM42,
        localhost='77.234.216.100',
        device="cuda" if torch.cuda.is_available() else "cpu",
        dense_search=True,
        sparse_search=False,
    )
    coll_name = "medfusion"

    # Поиск документов
    replies = retriever.search(
        query=query,
        collection_name=coll_name,
        topk=30,
        score_threshold=0.7,
    )

    if replies:
        print('start ranking')
        documents = [doc[0].page_content for doc in replies]
        rankings = rank_with_onnx(query, documents)[:5]
        print('stop ranking')

        # Извлечение метаданных и формирование ответа
        array.extend([
            [
                v
                for k, v in replies[ranking['corpus_id']][0].metadata.items()
                if k in ['title', 'authors', 'publication_date', 'doi_link']
            ]
            for ranking in rankings
        ])

        # Формирование итогового ответа
        return '\n\n'.join([
            f"Metadata: {[v for k, v in replies[ranking['corpus_id']][0].metadata.items() if k in ['title', 'authors', 'publication_date', 'doi_link']]}, "
            f"Text: {ranking['text']}"
            for ranking in rankings
        ])

    else:
        return 'There is no information for your request in database.'
    
    
def medical_article_retriever_function(query, array):
    try:
        query = ast.literal_eval(query[query.find('{'):query.rfind('}')+1])
    except Exception as e:
        return 'Wrong query. Error with ast.literal_eval'
        
    retriever = Retriever(
        model_type=DenseModelType.E5_LARGE,
        sparse_model_type=SparseModelType.BM42,
        localhost='77.234.216.100',
        device=device,
        dense_search=True,
        sparse_search=False,#False
    )
    coll_name="medfusion"#"med_db_e5_large"#"med_db_e5_large_bm42"
    replies = retriever.search(
        query = '',
        collection_name=coll_name,
        topk=10,
        filter_options=models.Filter(
                    must=[
                        models.FieldCondition(key=f'metadata.{k}', match=models.MatchValue(value=v))
                        for k, v in query.items()
                    ]
                ),
        score_threshold=0,
    )

    if replies:
        array.extend([[v for k,v in reply[0].metadata.items() if k in ['title', 'authors', 'publication_date', 'doi_link']] for reply in replies])
        return '\n\n'.join([f"{reply[0].page_content}" for reply in replies])
    else:
        return 'There is no article for your request.'


class MedFusionLLM:
    def __init__(self, 
                model_type: ModelType,
                api_key:str=None, 
                max_tokens: int=None,
                model_name: str='mistral-large-latest',
                hf_token:str=None,
                token:str=None) -> None:
        

        print(f'Model Name: {model_name}')
        self.api_key = api_key
        self.hf_token = hf_token
        self._model_type = model_type 
        self.max_tokens = max_tokens
        self.model_name = model_name
        
        self.token = token
        self._agent_executor = self._setup_model()
        self.shared_array = []


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
                llm = ChatMistralAI(api_key=f'{self.token}', model=self.model_name, temperature=0.7, top_p=0.95, timeout=30, max_tokens=self.max_tokens)
                
            template = PromptTemplate.from_template(get_prompt())
            
            self.medical_retriever_tool = Tool(
                name="medical_retriever",
                func=lambda query: medical_retriever_function(query, self.shared_array),
                description="""Searches data by query in the database of medical documents from the cochrane library.
query must be in English. Call this tool again with different query to find more documents.
Some documents don't contain relevant information, you need to be smart and careful"""
            )
            
            self.medical_article_retriever_tool = Tool(
                name="medical_article_retriever",
                func=lambda query_with_filters: medical_article_retriever_function(query_with_filters, self.shared_array),
                description="""Search more information about specific medical article in the Cochrane Library.
Use when you need more deep specific information about the research presented in an article, or when you simply need the entire article.
The query must be either the exact title of the article in English or be a link to the article, e.g.:
{"doi_link": "https://doi.org/10.1002/14651858.CD0000.pub2"}
or
{"title": "Title of the article"}

You can't search using both filters at the same time. Only one!"""
            )
            
            tools = [self.medical_retriever_tool, self.medical_article_retriever_tool]
            agent = create_react_agent(llm, tools, template)
            _agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)
            return _agent_executor
        except Exception as err:
            raise ValueError(f'Что-то не так с параметрами модели: {err}')

    def test_retriever(self, query):
        return self.medical_retriever_tool(query)
    
    def test_article_retriever(self, query):
        return self.medical_article_retriever_tool(query)
    
    def invoke(self, user_input:str, chat_history=''):
        #try:
            self.shared_array = []
            response = self._agent_executor({"input": user_input, 'chat_history': chat_history})['output']
            metadata = self.shared_array
            print(metadata)

            return response, list(set(tuple(i) for i in metadata))
        # except Exception as e:
        #     return f"\nI'm sorry, I encountered an error while processing your request. Please try again.\nError: {e}\n", self.shared_array
