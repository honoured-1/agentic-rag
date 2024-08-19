import yaml, sys
sys.path.append('models')
sys.path.append('chatbot/rag')
from langchain.agents import tool 
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import StrOutputParser
from geminillm import gemini #type: ignore 
# from rag.rag import get_answer
from langchain.prompts import PromptTemplate

with open('config.yaml') as config_file:
    config_file = yaml.safe_load(config_file)

with open('config.yaml') as config_file:
    config_file = yaml.safe_load(config_file)

llm = gemini()

class Input(BaseModel):
    query: str = Field(description="should be question")

class Output(BaseModel):
    response: str = Field(description="should be the answer")

parser = StrOutputParser(pydantic_object=Output)


@tool("troubleshooter", args_schema=Input, return_direct=True)
def troubleshooter(query: str) -> str:
    """
    Use this tool to provide swift and accurate solutions to a wide array of troubleshooting queries like:
    - Offer step-by-step guidance to diagnose common and complex issues.
    - Provide actionable solutions and workarounds to resolve problems effectively.
    """
    template = config_file["toubleshooting_template"]
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke(query)
    return parser.parse(response)