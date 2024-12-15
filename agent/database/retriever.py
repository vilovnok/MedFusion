from typing import List, Union
from enum import Enum

from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain_qdrant import QdrantVectorStore
from langchain_qdrant import FastEmbedSparse, RetrievalMode
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from qdrant_client import QdrantClient, models
import requests

from torch.cuda import is_available
from mistralai import Mistral
from uuid import uuid4

import json

from tqdm import tqdm


class DenseModelType(Enum):
    MISTRAL = "mistral-embed"
    DEEPVK_USER = "deepvk/USER-bge-m3"
    MiniLM_L6 = 'sentence-transformers/multi-qa-MiniLM-L6-cos-v1'
    E5_LARGE = "intfloat/multilingual-e5-large"
    E5_LARGE2 = "intfloat/e5-large-v2"
    E5_BASE = "intfloat/multilingual-e5-base"

class SparseModelType(Enum):
    BM25 = "Qdrant/bm25"
    BM42 = "Qdrant/bm42-all-minilm-l6-v2-attentions"

class Retriever:
    """ Retrieves information about the specified resource and its associated services """
    
    def __init__(self,                  
                 model_type: DenseModelType,
                 sparse_model_type: SparseModelType,
                 localhost: str='0.0.0.0',
                 port: int=6333,
                 grpc_port: int=6334,
                 api_key: str=None,
                 dataset_dir: str='C:\\Users\\Maxim\\Desktop\\hw\\LLM_basic\\project\\code\\qdrant\\MedFusion\\dataset\\dataset.jsonl',
                 device: int = 0,
                 dense_search=True,
                 sparse_search=True,
        ):

        self.api_key = api_key
        self.dataset_dir = dataset_dir
        self._model_type = model_type
        self._sparse_model_type = sparse_model_type  
        self._device = 0 if (device is None and is_available()) else device
        
        self.dense_search = dense_search
        self.sparse_search = sparse_search

        self._model = self._setup_model()
        self._sparse_model = self._setup_sparse_model()
        self._client = self._setup_database(localhost=localhost, port=port, grpc_port=grpc_port)

    
    def _setup_model(self):
        """Initialization for the model"""
        if self._model_type == DenseModelType.MISTRAL:
            model = Mistral(api_key=self.api_key)
        else:
            model = HuggingFaceEmbeddings(
                model_name = self._model_type.value,
                model_kwargs = {'device': self._device},
                encode_kwargs = {'normalize_embeddings': True}
            )

        return model

    def _setup_sparse_model(self):
        """Initialization for the sparse model"""
        sparse_model = FastEmbedSparse(
            model_name=self._sparse_model_type.value,
            model_kwargs={'device': self._device},
        )
        
        return sparse_model
        
    def _setup_database(self, localhost: str, port: int, grpc_port: int):     
        """ Initialization for the database """   
        if not requests.get(f'http://{localhost}:{port}'):
            raise Exception(f'Qdrant server is not running at http://{localhost}:{port}')
            
        client = QdrantClient(
            location=localhost, 
            port=port,
            #grpc_port=grpc_port,
            #prefer_grpc=True,
            timeout=300)
        
        return client


    def encode(self,  text: Union[List[str], str]):
        """ Encoder for text """
        if self._model_type == DenseModelType.MISTRAL:        
            embeddings = self._model.embeddings.create(
                model=self.model_type,
                inputs=text
            )        
        else:
            embeddings = self._model.embed_query(text)
        
        return embeddings
    
    
    def create_database(self, embedding: list, collection_name: str=None):
        """ Create the database """
        try:
            if self._client.collection_exists(collection_name=collection_name):
                return

            self._client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=len(embedding),
                    distance=models.Distance.COSINE
                ) if self.dense_search else None,
                sparse_vectors_config={
                    "sparse_vector": models.SparseVectorParams(
                        index=models.SparseIndexParams(on_disk=False)
                    )
                } if self.sparse_search else None
            )
            
        finally:
            if hasattr(self._client, 'close'):
                self._client.close() 


    def delete_database(self, collection_name: str):
        """ Delete the database """
        try:
            self._client.delete_collection(collection_name=collection_name)
        finally:
            if hasattr(self._client, 'close'):
                self._client.close() 


    def read_dataset(self):
        """ Read the file """
        with open(self.dataset_dir, 'r', encoding='utf-8') as file:
            data = [json.loads(line) for line in file]

        return data


    def splitter(self, content):    
        """ Splits the text into chunks """
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, 
                                                       chunk_overlap=200, 
                                                       add_start_index=True)
        chunks = text_splitter.split_text(content)
        chunks = [chank for chank in chunks if len(chank)>200]
        return chunks



    def upload_database(self, collection_name: str):
        """ Upload data to database """
        dataset = self.read_dataset()
        count = -1
        
        self.setup_vector_store(collection_name)
        
        try:
            length = len(dataset)
            for i in tqdm(range(length)):
                content = dataset[i]['content']
                metadata = dataset[i]['metadata']
                
                chunks = self.splitter(content=content)
                uuids = [str(uuid4()) for _ in range(len(chunks))]
                self.vector_store.add_texts(texts=chunks, metadatas=[metadata for _ in range(len(chunks))], ids=uuids, batch_size=1000)
        finally:
            if hasattr(self._client, 'close'):
                self._client.close()

    def setup_vector_store(
            self, 
            collection_name
        ):
        """Setup vector store"""
        if self.sparse_search and self.dense_search:
            retrieval_mode=RetrievalMode.HYBRID
        elif self.sparse_search:
            retrieval_mode=RetrievalMode.SPARSE
        else:
            retrieval_mode=RetrievalMode.DENSE
            
        self.vector_store = QdrantVectorStore(
            client=self._client,
            collection_name=collection_name,
            embedding=self._model if self.dense_search else None,
            retrieval_mode=retrieval_mode,
            sparse_embedding=self._sparse_model if self.sparse_search else None,
            sparse_vector_name='sparse_vector' if self.sparse_search else None,
        )
    
    def search(
            self,
            query: str,
            collection_name: str,
            topk: int = 5,
            filter_options: dict = None,
            score_threshold: float = 0.5,
        ):
        """ Search for a similar context """
        try:
            self.setup_vector_store(collection_name)
            
            results = self.vector_store.similarity_search_with_score(
                query=query,
                k=topk,
                filter=filter_options,
                score_threshold=score_threshold,
            )
            return results
        finally:
            if hasattr(self._client, 'close'):
                self._client.close()