import yaml, sys
sys.path.append('models')
sys.path.append('chatbot/rag')
from langchain.agents import tool 
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import StrOutputParser
from geminillm import gemini #type: ignore 
from rag.rag import me_func

# from langchain.prompts import PromptTemplate

with open('config.yaml') as config_file:
    config_file = yaml.safe_load(config_file)

llm = gemini()


class Input(BaseModel):
    query: str = Field(description="should be question")

class Output(BaseModel):
    response: str = Field(description="should be the answer")

parser = StrOutputParser(pydantic_object=Output)


@tool("aboutme", args_schema=Input, return_direct=True)
def aboutme(query: str) -> str:
    """
    Use this tool to answer questions related to identity, such as Who is Sumit Kumar?, Who built you?, Who is your Owner?.
    """
    response = me_func(query)
    return parser.parse(response)
