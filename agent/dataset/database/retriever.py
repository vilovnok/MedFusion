from typing import List, Union
from enum import Enum

from qdrant_client import QdrantClient, models
from torch.cuda import is_available
from mistralai import Mistral
import requests



class ModelType(Enum):
    MISTRAL = "mistral-embed"


class Retriever:
    """ Retrieves information about the specified resource and its associated services """
    
    def __init__(self, 
                 api_key: str, 
                 model_type: ModelType, 
                 localhost: str='0.0.0.0',
                 port: int=6654,
                 device=0
        ):

        self.api_key = api_key
        self.model_type = model_type
        self.localhost = localhost
        self.port = port

        if not device:
            self._device = 0 if is_available() else -1
        else:
            self._device = device

        self._model = self._setup_model()
        self._client = self._setup_database()


    def _setup_model(self):
        if self.model_type == ModelType.MISTRAL:
            model = Mistral(api_key=self.api_key)
        else:
            raise NotImplementedError()
        
        return model
    
    def _setup_database(self):        
        if requests.get(f'http://{self.localhost}:{self.port}'):
            client = QdrantClient(location=self.localhost, port=self.port)
        else:
            raise Exception(f'Qdrant server is not running at http://{self.localhost}:{self.port}')

        return client

    def encode(self,  text: Union[List[str], str]):

        if self.model_type == ModelType.MISTRAL:
        
            embeddings = self._model.embeddings.create(
                model=self.model_type,
                inputs=text
            )        
        else:
            raise NotImplementedError()
        
        return embeddings
    

    def _fill_database(self, embeddings, collection_name):

        self._client.create_collection(
            collection_name=collection_name,
                vectors_config=models.VectorParams(
                size=len(embeddings.data[0].embedding),
                distance=models.Distance.COSINE
            ),
        )