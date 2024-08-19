import sys, yaml
sys.path.append('models')
from geminillm import gemini #type: ignore
from geminiembed import embeddings #type: ignore
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_community.vectorstores import FAISS

# from langchain.globals import set_debug
# set_debug(True)

with open('config.yaml') as config_file:
    config_file = yaml.safe_load(config_file)

embeddings_model = embeddings()
llm = gemini()

top_k = config_file['top_k']

# template = """
# You are a professional customer care executive of State Bank of India. Generate a response that stays ture to the {context} and user's query {question} aiming for high precision and recall.
# """

def get_answer(query):
    load_directory = "vectordb"
    vectorstore = FAISS.load_local(load_directory, embeddings_model, allow_dangerous_deserialization=True)
    template = config_file["rag_template"]
    relevant_passage = vectorstore
    prompt = PromptTemplate(input_variable=["relevant_passage", "query"], template=template)
    retriever = vectorstore.as_retriever(search_type = "mmr", search_kwargs={'k':top_k})
    retrieval = RunnableParallel(
        {"relevant_passage": retriever, "query": RunnablePassthrough()}
    )
    chain = retrieval | prompt | llm | StrOutputParser()
    response = chain.invoke(query)
    return response

def main():
    print("Type 'exit' to end the conversation.")
    while True:
        query = input("Enter your question: ")
        if query.lower() == 'exit':
            print("Ending the conversation. Goodbye!")
            break
        answer = get_answer(query)
        print(f"Answer: {answer}")

if __name__ == "__main__":
    main()