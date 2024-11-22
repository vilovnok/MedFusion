from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from agent.src.utils import ModelType, get_system_prompt

from mistralai import Mistral




class MedFusionLLM:
    def __init__(self, 
                model_type: ModelType,
                api_key:str=None, 
                hf_token:str=None) -> None:
        
        self.api_key = api_key
        self.hf_token = hf_token
        self._model_type = model_type  

        self._model = self._setup_model()
        self.system_prompt = get_system_prompt()


    def _setup_model(self):
        """Initialization for the model"""
        try:
            if self._model_type == ModelType.MICROSOFT:
                model = HuggingFaceEndpoint(
                    repo_id=ModelType.MICROSOFT.value,
                    task="text-generation",
                    do_sample=False,
                    repetition_penalty=1.03,
                    huggingfacehub_api_token=self.hf_token
                )          
            elif self._model_type == ModelType.MISTRAL:
                model = Mistral(api_key=self.api_key)

            return model
        except Exception as err:
            raise ValueError(f'Что-то не так с параметрами модели: {err}')

    def invoke(self, context: str):
        prompt = ChatPromptTemplate.from_messages([("system", self.system_prompt)])
        chain = prompt | self._model | StrOutputParser()
        output = chain.invoke({"context": context}).split('topic:')[-1]
        return output