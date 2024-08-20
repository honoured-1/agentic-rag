import uuid, os, uvicorn, sys, time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent.reactagent import answer
import motor.motor_asyncio
from dotenv import load_dotenv
from bson import ObjectId

# Load environment variables from .env file
load_dotenv()

# FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB client setup
MONGODB_CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_CONNECTION_STRING)
db = client.chatbot
chat_collection = db.chat_history

class ChatRequest(BaseModel):
    message: str
    session_id: str

class FeedbackRequest(BaseModel):
    session_id: str
    message: str
    feedback: str

def convert_objectid(data):
    if isinstance(data, list):
        for item in data:
            if '_id' in item:
                item['_id'] = str(item['_id'])
    elif isinstance(data, dict):
        if '_id' in data:
            data['_id'] = str(data['_id'])
    return data

@app.post("/api/chatbot")
async def chatbot_endpoint(request: ChatRequest, request_obj: Request):
    client_ip = request_obj.client.host
    
    # Start timing the request
    start_time = time.time()
    
    response = answer(request.message)
    
    # End timing the request
    end_time = time.time()
    duration = end_time - start_time
    
    # Log conversation to MongoDB
    chat_data = {
        "client_ip": client_ip,
        "message": request.message,
        "response": response,
        "feedback": "neutral",
        "duration": duration,
        "last_user_message": request.message,
        "session_id": request.session_id
    }
    await chat_collection.insert_one(chat_data)
    
    return {"response": response}

@app.post("/api/feedback")
async def feedback_endpoint(request: FeedbackRequest):
    # Update the feedback for the specific message
    result = await chat_collection.update_one(
        {"session_id": request.session_id, "message": request.message},
        {"$set": {"feedback": request.feedback}}
    )
    
    if result.modified_count == 0:
        return {"status": "error", "message": "Session not found"}
    
    return {"status": "success"}

@app.get("/api/new_session")
async def new_session():
    session_id = str(uuid.uuid4())
    return {"session_id": session_id}

@app.get("/api/chat_history")
async def chat_history(request_obj: Request):
    client_ip = request_obj.client.host
    pipeline = [
        {"$match": {"client_ip": client_ip}},
        {"$sort": {"_id": -1}},  # Sort by _id in descending order to get the latest entries first
        {"$group": {
            "_id": "$session_id",
            "latest_entry": {"$first": "$$ROOT"}
        }},
        {"$replaceRoot": {"newRoot": "$latest_entry"}}
    ]
    chat_history = await chat_collection.aggregate(pipeline).to_list(length=100)
    chat_history = convert_objectid(chat_history)
    
    return {"chat_history": chat_history}


@app.get("/api/chat_history/{session_id}")
async def get_chat_history(session_id: str, request_obj: Request):
    client_ip = request_obj.client.host
    chat_history = await chat_collection.find({"client_ip": client_ip, "session_id": session_id}).to_list(length=100)
    chat_history = convert_objectid(chat_history)

    if not chat_history:
        return {"status": "error", "message": "Session not found"}

    return {"messages": chat_history}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
