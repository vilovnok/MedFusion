from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from agent.utils import get_system_prompt


class MedFusionLLM:
    def __init__(self, 
                api_key:str=None, 
                hf_token:str=None, 
                model:str=None) -> None:
        
        self.api_key = api_key
        self.hf_token = hf_token
        self.model = model
        
        self._init_prompts()
        self._init_model()


    def _init_prompts(self):
        self.system_prompt = get_system_prompt()
    
    def _init_model(self):
        try:
            self._model_hf = HuggingFaceEndpoint(
                repo_id=self.model,
                task="text-generation",
                do_sample=False,
                repetition_penalty=1.03,
                huggingfacehub_api_token=self.hf_token
            )           
            self._model_other = None
        except Exception as err:
            raise ValueError(f'Что-то не так с параметрами модели: {err}')

    def invoke(self, context: str):
        prompt = ChatPromptTemplate.from_messages([("system", self.system_prompt)])
        map_chain = prompt | self._model_hf | StrOutputParser()
        output = map_chain.invoke({"context": context}).split('topic:')[-1]
        return output