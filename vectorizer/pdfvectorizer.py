import yaml
import sys, os, time, getpass
sys.path.append('models')
from uuid import uuid4
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from geminiembed import embeddings  # type: ignore
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore

# Load the config.yaml file
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

development = config.get('development', False)

def process_pdf(file, faissDIR=None, pinecone_index=None):
    loader = PyPDFLoader(file, extract_images=False)
    data = loader.load()
    embedding_model = embeddings()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=48)
    chunks = text_splitter.split_documents(data)
    chunk_texts = [chunk.page_content for chunk in chunks]

    if faissDIR:
        vectorstore = FAISS.from_texts(chunk_texts, embedding_model)
        vectorstore.save_local(faissDIR)
        print(f"Created FAISS vectorDB for {file}")

    if pinecone_index:
        uuids = [str(uuid4()) for _ in range(len(chunks))]
        vector_store = PineconeVectorStore(index=pinecone_index, embedding=embedding_model)
        vector_store.add_documents(documents=chunks, ids=uuids)
        print(f"Created Pinecone vectorDB for {file}")

if development:
    sys.path.append('models')
    process_pdf('database/Learning_Python.pdf', faissDIR="vectordb/pythondb")
    process_pdf('database/Sumit_Kumar_GenAI_Resume.pdf', faissDIR="vectordb/aboutme")
else:
    sys.path.append('models')
    load_dotenv()
    if not os.getenv("PINECONE_API_KEY"):
        os.environ["PINECONE_API_KEY"] = getpass.getpass("Enter your Pinecone API key: ")
    pinecone_api_key = os.environ.get("PINECONE_API_KEY")
    pc = Pinecone(api_key=pinecone_api_key)

    def get_or_create_index(index_name):
        existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
        if index_name not in existing_indexes:
            pc.create_index(
                name=index_name,
                dimension=768,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )
            while not pc.describe_index(index_name).status["ready"]:
                time.sleep(1)
        return pc.Index(index_name)

    process_pdf('database/Learning_Python.pdf', pinecone_index=get_or_create_index("python-db"))
    process_pdf('database/Sumit_Kumar_GenAI_Resume.pdf', pinecone_index=get_or_create_index("about-me"))
