import argparse

from agent.database.retriever import Retriever, DenseModelType, SparseModelType
from agent.database.utils import ensure_directory_exists


ensure_directory_exists("C:\\Users\\Maxim\\Desktop\\hw\\LLM_basic\\project\\code\\qdrant\\MedFusion\\dataset")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--act", type=str, required=True)
    parser.add_argument("--coll_name", type=str, required=True)
    parser.add_argument("--dense", type=bool, required=False, default=True)
    parser.add_argument("--sparse", type=bool, required=False, default=False)
    args = parser.parse_args()

    act = args.act
    coll_name = args.coll_name
    dense_search = args.dense
    sparse_search = args.sparse
    
    retriever = Retriever(
        model_type=DenseModelType.E5_LARGE,
        sparse_model_type=SparseModelType.BM42,
        localhost="localhost",#'77.234.216.100',
        device=0,
        dense_search=dense_search,
        sparse_search=sparse_search,#False
    )

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
            query = """Is cranberries helpfull for women?""",
            collection_name=coll_name,
            topk=5,
            score_threshold=0,
        )

        for i in result:
            print(i[1], i[0].metadata['title'])
            print(i[0].page_content)
            print('\n\n')         