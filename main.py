from agent.src import *#MedFusionLLM
from agent.src.utils import ModelType

import os
os.environ['MISTRAL_TOKEN'] = 'gUuOZlGmF6xZZoDDNT8L7oteKUjEoVsX'


agent = MedFusionLLM(model_type=ModelType.MISTRAL, token=os.environ.get("MISTRAL_TOKEN"))

def main():
    print("Welcome to the Paphos City Information Bot! Type 'exit' to quit.\n")
    while True:
        user_input = input("User: ")
        
        # Notice that chat_history is a string, since this prompt is aimed at LLMs, not chat models
        chat_history = '' #"Human: Hi! My name is Bob\nAI: Hello Bob! Nice to meet you",
        
        if user_input.lower() == 'exit':
            print("\nBot: Goodbye!")
            break
        
        #response = agent.test_retriever(user_input)
        response = agent.invoke(user_input, chat_history)
        print(response)

if __name__ == '__main__':
    main()
