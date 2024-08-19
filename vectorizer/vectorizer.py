import sys
sys.path.append('models')
from splitter import markdown_splitter
from rich import print
from langchain_community.vectorstores import FAISS
from geminiembed import embeddings #type: ignore

input_file = 'database/APIs.txt'
documents = markdown_splitter(input_file)

# Debug: Print the type and content of documents
# print(f"Type of documents: {type(documents)}")
# print(f"Content of documents: {documents}")

faissDIR = "vectordb"

embedding_model = embeddings()

# Ensure documents is a list of strings
if isinstance(documents, list) and all(isinstance(doc, str) for doc in documents):
    vectorstore = FAISS.from_texts(documents, embedding_model)
    vectorstore.save_local(faissDIR)
    print("Created FAISS vectorDB")
else:
    print("Error: documents should be a list of strings")




# # Access and print specific splits by their index
# index_to_print = 0  # Change this to the index you want to print
# if 0 <= index_to_print < len(documents):
#     print(documents[index_to_print])
# else:
#     print("Index out of range")
