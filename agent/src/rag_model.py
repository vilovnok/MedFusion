from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from agent.src.utils import ModelType, get_system_prompt
from langchain_mistralai.chat_models import ChatMistralAI


class MedFusionLLM:
    def __init__(self, 
                model_type: str,
                api_key:str=None, 
                hf_token:str=None) -> None:
        
        self.api_key = api_key
        self.hf_token = hf_token
        self.model_type = model_type

        self._model = self._setup_model()
        self.system_prompt = get_system_prompt()


    def _setup_model(self):
        """Initialization for the model"""
        try:
            model = None 
            if self.model_type == ModelType.MICROSOFT:
                model = HuggingFaceEndpoint(
                    repo_id=ModelType.MICROSOFT.value,
                    task="text-generation",
                    do_sample=False,
                    repetition_penalty=1.03,
                    huggingfacehub_api_token=self.hf_token
                )          
            elif self.model_type == ModelType.MISTRAL:
                    model = ChatMistralAI(
                    model=ModelType.MISTRAL.value,
                    temperature=0.5,
                    max_retries=2,
                    api_key=self.api_key
                )
            return model
        except Exception as err:
            raise ValueError(f'Что-то не так с параметрами модели: {err}')

    def invoke(self, content:str, messages:list=None):
        try:
            prompt = ChatPromptTemplate.from_messages([("system", self.system_prompt)])
            chain = prompt | self._model | StrOutputParser()
            output = chain.invoke({"content": content})
            return output
        except Exception as err:
            raise ValueError(f'Что-то не так с вызовом модели: {err}')