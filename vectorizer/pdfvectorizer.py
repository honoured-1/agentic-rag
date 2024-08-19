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
