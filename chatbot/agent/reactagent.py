import yaml, sys
sys.path.append('models')
sys.path.append('chatbot')
from geminillm import gemini #type: ignore
from langchain.chains.conversation.memory import ConversationSummaryBufferMemory
from tools.query import querying
from tools.coder import coder
from tools.interactionhandler import interactionhandler
from tools.troubleshooter import troubleshooter
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate

with open('config.yaml') as config_file:
    config_file = yaml.safe_load(config_file)

llm = gemini()
agent_template = config_file['react_agent']

tools=[querying, coder, interactionhandler, troubleshooter]
memory = ConversationSummaryBufferMemory(llm=llm, memory_key="chat_history", return_messages=True, max_token_limit=512)
prompt = PromptTemplate.from_template(agent_template)

agent = create_react_agent(
    llm=llm,
    prompt=prompt,
    tools=tools
)

agent_executor = AgentExecutor(
    agent=agent,
    verbose=True,
    tools=tools,
    memory=memory,
    handle_parsing_errors=True
)

def answer(query, chat_history=[]):
    return agent_executor.invoke({"input": query})['output']
