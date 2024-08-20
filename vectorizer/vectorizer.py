import sys
sys.path.append('models')
from splitter import markdown_splitter
from rich import print
from langchain_community.vectorstores import FAISS
from geminiembed import embeddings #type: ignore

input_file = 'database/APIs.txt'
documents = markdown_splitter(input_file)


faissDIR = "vectordb"

embedding_model = embeddings()

# Ensure documents is a list of strings
if isinstance(documents, list) and all(isinstance(doc, str) for doc in documents):
    vectorstore = FAISS.from_texts(documents, embedding_model)
    vectorstore.save_local(faissDIR)
    print("Created FAISS vectorDB")
else:
    print("Error: documents should be a list of strings")




# import sys, os, time, getpass
# sys.path.append('models')
# from splitter import markdown_splitter
# from langchain_pinecone import PineconeVectorStore
# from geminiembed import embeddings #type: ignore
# import getpass
# from dotenv import load_dotenv
# from pinecone import Pinecone, ServerlessSpec
# from uuid import uuid4
 
# load_dotenv()
# if not os.getenv("PINECONE_API_KEY"):
#     os.environ["PINECONE_API_KEY"] = getpass.getpass("Enter your Pinecone API key: ")
 
# pinecone_api_key = os.environ.get("PINECONE_API_KEY")
 
# pc = Pinecone(api_key=pinecone_api_key)
 
 
# index_name = "python-db"  # change if desired
 
# existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
 
# if index_name not in existing_indexes:
#     pc.create_index(
#         name=index_name,
#         dimension=768,
#         metric="cosine",
#         spec=ServerlessSpec(cloud="aws", region="us-east-1"),
#     )
#     while not pc.describe_index(index_name).status["ready"]:
#         time.sleep(1)
 
# index = pc.Index(index_name)
 
# input_file = 'database/APIs.txt'
# documents = markdown_splitter(input_file)
 
 
# # index = pc.Index(index_name)
# embedding_model = embeddings()
# vector_store = PineconeVectorStore(index=index, embedding=embedding_model)
 
# uuids = [str(uuid4()) for _ in range(len(documents))]
 
# vector_store.add_documents(documents=documents, ids=uuids)