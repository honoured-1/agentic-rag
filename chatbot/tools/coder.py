import yaml, sys, re, os
# from threading import Thread
sys.path.append('models')
sys.path.append('chatbot/rag')
from langchain.agents import tool 
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import StrOutputParser
from geminillm import gemini #type: ignore 
# from rag.rag import get_answer
# from flask import Flask, send_file
# from werkzeug.serving import make_server
from langchain.prompts import PromptTemplate

with open('config.yaml') as config_file:
    config_file = yaml.safe_load(config_file)

class Input(BaseModel):
    query: str = Field(description="should be question")

class Output(BaseModel):
    response: str = Field(description="should be the answer")

parser = StrOutputParser(pydantic_object=Output)
llm = gemini()

# app = Flask(__name__)

# @app.route('/download/<filename>')
# def download_file(filename):
#     file_path = os.path.join(os.getcwd(), filename)
#     return send_file(file_path, as_attachment=True, attachment_filename=filename, mimetype='text/x-python')

# class ServerThread(Thread):
#     def __init__(self, app):
#         Thread.__init__(self)
#         self.srv = make_server('localhost', 5000, app)
#         self.ctx = app.app_context()
#         self.ctx.push()

#     def run(self):
#         self.srv.serve_forever()

#     def shutdown(self):
#         self.srv.shutdown()

# # Start the Flask app in a separate thread
# server = ServerThread(app)
# server.start()

@tool("coder", args_schema=Input, return_direct=True)
def coder(query: str) -> str:
    """
    Use this tool to facilitate the generation of code snippets and provide solutions to coding-related queries.
    - Generate concise and functional code snippets based on user-provided specifications and requirements.
    - Offer guidance on best coding practices, design patterns, and algorithm optimization.
    """
    template = config_file["code_template"]
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke(query)

    # def detect_code(response):
    #     code_pattern = re.compile(r'```(.*?)```', re.DOTALL)
    #     match = code_pattern.search(response)
    #     if match:
    #         code = match.group(1)
    #         return code
    #     return None

    # def determine_extension(code):
    #     return 'py'

    # def save_code_to_file(code, extension):
    #     filename = f'code.{extension}'
    #     with open(filename, 'w') as file:
    #         file.write(code)
    #     return filename

    # def process_response(response):
    #     code = detect_code(response)
    #     if code:
    #         extension = determine_extension(code)
    #         filename = save_code_to_file(code, extension)
    #         download_url = f'http://localhost:5000/download/{filename}'
    #         return download_url
    #     return None

    # download_url = process_response(response)
    # final_response = f"{response}\nYou can download the code from the following URL: {download_url}"
    return parser.parse(response)
