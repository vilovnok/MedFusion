from typing import List, Union
from enum import Enum

from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter

from qdrant_client import QdrantClient, models
import requests

from torch.cuda import is_available
from mistralai import Mistral

import json

from tqdm import tqdm



class ModelType(Enum):
    MISTRAL = "mistral-embed"
    DEEPVK_USER = "deepvk/USER-bge-m3"

class Retriever:
    """ Retrieves information about the specified resource and its associated services """
    
    def __init__(self,                  
                 model_type: ModelType, 
                 localhost: str='0.0.0.0',
                 port: int=6333,
                 grpc_port: int=6334,
                 api_key: str=None,
                 dataset_dir: str='./dataset/dataset.jsonl',
                 device: int = 0                 
        ):

        self.api_key = api_key
        self.dataset_dir = dataset_dir
        self._model_type = model_type   
        self._device = 0 if (device is None and is_available()) else device

        self._model = self._setup_model()        
        self._client = self._setup_database(localhost=localhost, port=port, grpc_port=grpc_port)        

    

    def _setup_model(self):
        
        if self._model_type == ModelType.DEEPVK_USER:
            model = SentenceTransformer(
                ModelType.DEEPVK_USER.value,
                device=self._device
            )
        elif self._model_type == ModelType.MISTRAL:
            model = Mistral(api_key=self.api_key)
        else:
            raise NotImplementedError()

        return model
        
    def _setup_database(self, localhost: str, port: int, grpc_port: int):        
        if not requests.get(f'http://{localhost}:{port}'):
            raise Exception(f'Qdrant server is not running at http://{localhost}:{port}')
            
        client = QdrantClient(
            location=localhost, 
            port=port,
            grpc_port=grpc_port,
            prefer_grpc=True,
            timeout=300)

        return client


    def encode(self,  text: Union[List[str], str]):

        if self._model_type == ModelType.MISTRAL:        
            embeddings = self._model.embeddings.create(
                model=self.model_type,
                inputs=text
            )        

        elif self._model_type == ModelType.DEEPVK_USER:
            embeddings = self._model.encode(text, normalize_embeddings=True)

        else:
            raise NotImplementedError()
        
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
                )
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

        with open(self.dataset_dir, 'r') as file:
            data = [json.loads(line) for line in file]

        return data



    def splitter(self, content):    
        """ Разбивает текст на части """

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, 
                                                       chunk_overlap=200, 
                                                       add_start_index=True)
        chunks = text_splitter.split_text(content)            
        
        return chunks


    def upload_database(self, collection_name: str):
        """ Upload data to database """

        dataset = self.read_dataset()
        count = -1

        try:
            length = len(dataset)

            for i in tqdm(range(length)):

                content = dataset[i]['content']
                metadata = dataset[i]['metadata']
                
                chunks = self.splitter(content=content)
                embeddings = self.encode(chunks)

                for embedding, chunk in zip(embeddings, chunks):
                    count+=1
                    self._client.upsert(
                        collection_name=collection_name,
                        points=[
                            models.PointStruct(
                                id=count,
                                vector=embedding,
                                payload={
                                    "link": metadata['doi_link'],
                                    "title": metadata['title'],
                                    "content": chunk
                                }
                            )
                        ]
                    )            
        finally:
            if hasattr(self._client, 'close'):
                self._client.close()


    def search(
            self,
            query: str,
            collection_name: str,
            topk: int = 1,
            filter_options: dict = None,
            score_threshold: float = None
        ):
        try:
            embedding = self.encode(query)
            results = self._client.search(
                collection_name,
                embedding,
                limit=topk,
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(key=k, match=models.MatchValue(value=v))
                        for k, v in filter_options.items()
                    ]
                ) if filter_options else None,
                score_threshold=score_threshold
            )

            return results
        finally:
            if hasattr(self._client, 'close'):
                self._client.close() 