import yaml
from enum import Enum

class ModelType(Enum):
    MISTRAL = "mistral-large-latest"
    MICROSOFT = "microsoft/Phi-3-mini-4k-instruct"

def get_model_info(model_name):
    with open('agent/config/env.yaml', 'r') as file:
        config = yaml.safe_load(file)
    for model in config['models']:
        if model['name'] == model_name:
            return model  
    return None  