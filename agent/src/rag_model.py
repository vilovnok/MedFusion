from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from agent.src.utils import ModelName, get_system_prompt
from langchain_mistralai.chat_models import ChatMistralAI





class MedFusionLLM:
    def __init__(self, 
                model_name: str,
                api_key:str=None, 
                hf_token:str=None) -> None:
        
        self.api_key = api_key
        self.hf_token = hf_token
        self.model_name = model_name

        self._model = self._setup_model()
        self.system_prompt = get_system_prompt()


    def _setup_model(self):
        """Initialization for the model"""
        try:
            model = None 
            if self.model_name == ModelName.MICROSOFT.value:
                model = HuggingFaceEndpoint(
                    repo_id=ModelName.MICROSOFT.value,
                    task="text-generation",
                    do_sample=False,
                    repetition_penalty=1.03,
                    huggingfacehub_api_token=self.hf_token
                )          
            elif self.model_name == ModelName.MISTRAL.value:
                    model = ChatMistralAI(
                    model=ModelName.MISTRAL.value,
                    temperature=0.5,
                    max_retries=2,
                    api_key=self.api_key
                )
            return model
        except Exception as err:
            raise ValueError(f'Что-то не так с параметрами модели: {err}')

    def invoke(self, content: str):
        try:
            prompt = ChatPromptTemplate.from_messages([("system", self.system_prompt)])
            chain = prompt | self._model | StrOutputParser()
            output = chain.invoke({"content": content})
            return output
        except Exception as err:
            raise ValueError(f'Что-то не так с вызовом модели: {err}')