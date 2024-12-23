import os
from agent.src import *
from agent.src.utils import ModelType

os.environ['MISTRAL_TOKEN'] = '<your token>'
agent = MedFusionLLM(model_type=ModelType.MISTRAL, token=os.environ.get("MISTRAL_TOKEN"))

def main():
    print("Welcome to the MedFusion Bot! Type 'exit' to quit.\n")
    while True:
        user_input = input("User: ")
        
        chat_history = '' #"Human: Hi! My name is Bob\nAI: Hello Bob! Nice to meet you",
        
        if user_input.lower() == 'exit':
            print("\nBot: Goodbye!")
            break
        
        #response = agent.test_retriever(user_input)
        response, metadata = agent.invoke(user_input, chat_history)
        #response = agent.test_article_retriever(user_input)
        print(response)
        for i, meta in enumerate(metadata):
            print(f'Links {i+1}:\n{meta}')

if __name__ == '__main__':
    main()