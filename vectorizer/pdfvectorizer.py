import sys
sys.path.append('models')
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from geminiembed import embeddings #type: ignore

file = 'database/Learning_Python.pdf'
faissDIR = "vectordb"
loader = PyPDFLoader(file, extract_images=False)
data = loader.load()

embedding_model = embeddings()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=48)
chunks = text_splitter.split_documents(data)

# Extract text content from chunked Document objects
chunk_texts = [chunk.page_content for chunk in chunks]

vectorstore = FAISS.from_texts(chunk_texts, embedding_model)
vectorstore.save_local(faissDIR)
print("Created FAISS vectorDB")

# import sys
# sys.path.append('models')
# from langchain_community.document_loaders import PyPDFLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from geminiembed import embeddings # type: ignore
# from elasticsearch import Elasticsearch
# from elasticsearch.helpers import bulk
# from elasticsearch_dsl import Document, Text, connections

# file = 'database/Learning_Python.pdf'
# loader = PyPDFLoader(file, extract_images=False)
# data = loader.load()

# embedding_model = embeddings()

# text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=48)
# chunks = text_splitter.split_documents(data)

# # Extract text content from chunked Document objects
# chunk_texts = [chunk.page_content for chunk in chunks]

# # Connect to Elasticsearch
# es = Elasticsearch(hosts=["http://localhost:9200"])  # Update this with your Elasticsearch host

# # Define the connection
# connections.create_connection(alias='default', hosts=["http://localhost:9200"])

# # Define the Elasticsearch document structure
# class TextDocument(Document):
#     content = Text()

#     class Index:
#         name = 'documents'

# # Create the index
# TextDocument.init()

# # Index the documents
# def index_documents(docs):
#     actions = [
#         {
#             "_index": "documents",
#             "_source": {"content": doc}
#         }
#         for doc in docs
#     ]
#     bulk(es, actions)

# index_documents(chunk_texts)
# print("Created Elastic Vector DB")