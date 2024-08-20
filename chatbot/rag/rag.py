import sys, yaml, getpass, os
sys.path.append('models')
from geminillm import gemini #type: ignore
from geminiembed import embeddings #type: ignore
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
# from langchain_community.vectorstores import FAISS
from pinecone import Pinecone
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore

load_dotenv()

# Get Pinecone API key
if not os.getenv("PINECONE_API_KEY"):
    os.environ["PINECONE_API_KEY"] = getpass.getpass("Enter your Pinecone API key: ")

pinecone_api_key = os.environ.get("PINECONE_API_KEY")

# Initialize Pinecone
pc = Pinecone(api_key=pinecone_api_key)

index_name = "python-db"  # Change if desired
index = pc.Index(index_name)
embedding_model = embeddings() 
vector_store = PineconeVectorStore(index=index, embedding=embedding_model)



with open('config.yaml') as config_file:
    config_file = yaml.safe_load(config_file)

embeddings_model = embeddings()
llm = gemini()

top_k = config_file['top_k']


def get_answer(query):
    # load_directory = "vectordb"
    # vectorstore = FAISS.load_local(load_directory, embeddings_model, allow_dangerous_deserialization=True)
    template = config_file["rag_template"]
    relevant_passage = vector_store
    prompt = PromptTemplate(input_variable=["relevant_passage", "query"], template=template)
    retriever = vector_store.as_retriever(search_type = "mmr", search_kwargs={'k':top_k})
    retrieval = RunnableParallel(
        {"relevant_passage": retriever, "query": RunnablePassthrough()}
    )
    chain = retrieval | prompt | llm | StrOutputParser()
    response = chain.invoke(query)
    return response



if __name__ == "__main__":
    def main():
        print("Type 'exit' to end the conversation.")
        while True:
            query = input("Enter your question: ")
            if query.lower() == 'exit':
                print("Ending the conversation. Goodbye!")
                break
            answer = get_answer(query)
            print(f"Answer: {answer}")
    main()