import yaml

def get_model_info(model_name):
    with open('agent/config/env.yaml', 'r') as file:
        config = yaml.safe_load(file)
    for model in config['models']:
        if model['name'] == model_name:
            return model  
    return None  

def get_system_prompt():
    with open('agent/prompts/system_prompt.txt', 'r') as file:
        prompt = file.read()
    return prompt