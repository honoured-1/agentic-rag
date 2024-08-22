import yaml

# Load the config.yaml file
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

development = config.get('development', False)

if development:
    # Code to run when development is True
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

else:
    # Code to run when development is False
    import sys, os, time, getpass
    sys.path.append('models')
    from langchain_community.document_loaders import PyPDFLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from geminiembed import embeddings  #type: ignore
    from dotenv import load_dotenv
    from pinecone import Pinecone, ServerlessSpec
    from langchain_pinecone import PineconeVectorStore
    from uuid import uuid4

    # Load environment variables
    load_dotenv()

    # Get Pinecone API key
    if not os.getenv("PINECONE_API_KEY"):
        os.environ["PINECONE_API_KEY"] = getpass.getpass("Enter your Pinecone API key: ")

    pinecone_api_key = os.environ.get("PINECONE_API_KEY")

    # Initialize Pinecone
    pc = Pinecone(api_key=pinecone_api_key)

    index_name = "python-db"  # Change if desired

    # Check if the index exists, if not, create it
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

    index = pc.Index(index_name)

    # Load and split the PDF document
    file = 'database/Learning_Python.pdf'
    loader = PyPDFLoader(file, extract_images=False)
    data = loader.load()

    embedding_model = embeddings()  # Call the function to get the instance

    # Create Pinecone vector store and add documents
    vector_store = PineconeVectorStore(index=index, embedding=embedding_model)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=48)
    chunks = text_splitter.split_documents(data)

    uuids = [str(uuid4()) for _ in range(len(chunks))]

    vector_store.add_documents(documents=chunks, ids=uuids)

    print("Created Pinecone vectorDB")
