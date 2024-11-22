import argparse

from agent.database.retriever import Retriever, ModelType
from agent.database.utils import ensure_directory_exists


ensure_directory_exists("dataset")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--act", type=str, required=True)
    parser.add_argument("--coll_name", type=str, required=True)
    args = parser.parse_args()

    act = args.act
    coll_name = args.coll_name
    
    retriever = Retriever(
        model_type=ModelType.DEEPVK_USER, 
        localhost='77.234.216.100',
        device=0)

    if act == "create":
        embedding = retriever.encode(text='Hello, world')
        retriever.create_database(collection_name=coll_name, embedding=embedding)    
        print("Коллекция создана!")    
    elif act == "delete":
        retriever.delete_database(collection_name=coll_name)
        print("Коллекция удалена!")    
    elif act == "upload":
        retriever.upload_database(collection_name=coll_name)
        print("Коллекция обновилась!")  
    elif act == "search":
        result = retriever.search(
        query = """What is cranberry juice used for the prevention of urinary tract infections?""",
        collection_name=coll_name,
        topk=1)

        for i in result:
            print(i)         