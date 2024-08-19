from dotenv import load_dotenv
import os, getpass
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Provide your Google API Key")

def embeddings():
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    return embeddings



# vector = embeddings.embed_query("hello, world!")
# print(vector[:5])