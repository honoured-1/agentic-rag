import yaml, sys
sys.path.append('models')
sys.path.append('chatbot/rag')
from langchain.agents import tool 
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import StrOutputParser
from geminillm import gemini #type: ignore 
from rag.rag import get_answer

# from langchain.prompts import PromptTemplate

with open('config.yaml') as config_file:
    config_file = yaml.safe_load(config_file)

llm = gemini()


class Input(BaseModel):
    query: str = Field(description="should be question")

class Output(BaseModel):
    response: str = Field(description="should be the answer")

parser = StrOutputParser(pydantic_object=Output)


@tool("querying", args_schema=Input, return_direct=True)
def querying(query: str) -> str:
    """
    Use this tool to provide detailed answers and insights across three main domains, including Yes/No responses:
    - Foundational: It addresses broad, overarching questions about a product, service, or concept, offering users a foundational understanding.
    - Feature Exploration: It delves into specific features, explaining their functions, benefits, and applications to give users a deeper appreciation of the product's capabilities.
    - Technical Details: It supplies in-depth technical information, such as spect fications, architecture, and engineering insights, catering to users with advanced knowledge or technical backgrounds.
    """
    response = get_answer(query)
    return parser.parse(response)
