import yaml
import sys, getpass, os
from dotenv import load_dotenv

# Load the config.yaml file
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

development = config.get('development', False)

sys.path.append('models')
from geminillm import gemini  # type: ignore
from geminiembed import embeddings  # type: ignore
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

if development:
    from langchain_community.vectorstores import FAISS
else:
    from pinecone import Pinecone
    from langchain_pinecone import PineconeVectorStore

    load_dotenv()
    if not os.getenv("PINECONE_API_KEY"):
        os.environ["PINECONE_API_KEY"] = getpass.getpass("Enter your Pinecone API key: ")

    pinecone_api_key = os.environ.get("PINECONE_API_KEY")
    pc = Pinecone(api_key=pinecone_api_key)
    index_name = "python-db"  # Change if desired
    index = pc.Index(index_name)

with open('config.yaml') as config_file:
    config_file = yaml.safe_load(config_file)

embeddings_model = embeddings()
llm = gemini()
top_k = config_file['top_k']

def get_answer(query):
    if development:
        load_directory = "vectordb"
        vector_store = FAISS.load_local(load_directory, embeddings_model, allow_dangerous_deserialization=True)
    else:
        vector_store = PineconeVectorStore(index=index, embedding=embeddings_model)

    template = config_file["rag_template"]
    prompt = PromptTemplate(input_variable=["relevant_passage", "query"], template=template)
    retriever = vector_store.as_retriever(search_type="mmr", search_kwargs={'k': top_k})
    retrieval = RunnableParallel({"relevant_passage": retriever, "query": RunnablePassthrough()})
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
