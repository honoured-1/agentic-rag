import yaml

# Load the config.yaml file
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

development = config.get('development', False)

if development:


    import uuid, csv, os, uvicorn, sys, time
    sys.path.append('models')
    from fastapi import FastAPI, Request
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    from chatbot.agent.reactagent import answer

    # FastAPI app
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], 
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    class ChatRequest(BaseModel):
        message: str
        session_id: str

    class FeedbackRequest(BaseModel):
        session_id: str
        message: str
        feedback: str

    @app.post("/api/chatbot")
    async def chatbot_endpoint(request: ChatRequest, request_obj: Request):
        client_ip = request_obj.client.host
        
        # Start timing the request
        start_time = time.time()
        
        response = answer(request.message)
        
        # End timing the request
        end_time = time.time()
        duration = end_time - start_time
        
        # Log conversation to CSV
        directory = f"database/chat_history/{client_ip}"
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        # Check if a file with the same session ID already exists
        existing_file = None
        for file in os.listdir(directory):
            if file.endswith(".csv") and request.session_id in file:
                existing_file = file
                break
        
        if existing_file:
            file_path = f"{directory}/{existing_file}"
        else:
            # Use session_id as the file name
            file_path = f"{directory}/{request.session_id}.csv"
        
        file_exists = os.path.isfile(file_path)
        
        with open(file_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["client_ip", "message", "response", "feedback", "duration", "last_user_message"])  # Write header if file is new
            writer.writerow([client_ip, request.message, response, "neutral", duration, request.message])
        
        return {"response": response}

    @app.post("/api/feedback")
    async def feedback_endpoint(request: FeedbackRequest):
        # Find the directory based on session_id
        base_directory = "database/chat_history"
        session_directory = None
        file_path = None
        
        for root, dirs, files in os.walk(base_directory):
            for file in files:
                if file.endswith(".csv") and request.session_id in file:
                    file_path = f"{root}/{file}"
                    break
            if file_path:
                break
        
        if not file_path:
            return {"status": "error", "message": "Session not found"}
        
        # Read the existing rows
        rows = []
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            rows = list(reader)
        
        # Update the feedback for the specific message
        for row in rows:
            if row[1] == request.message:
                row[3] = request.feedback
                break
        
        # Write the updated rows back to the file
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(rows)
        
        return {"status": "success"}

    @app.get("/api/new_session")
    async def new_session():
        session_id = str(uuid.uuid4())
        return {"session_id": session_id}

    @app.get("/api/chat_history")
    async def chat_history(request_obj: Request):
        client_ip = request_obj.client.host
        directory = f"database/chat_history/{client_ip}"
        chat_history = []
        
        if os.path.exists(directory):
            for file in os.listdir(directory):
                if file.endswith(".csv"):
                    file_path = f"{directory}/{file}"
                    with open(file_path, mode='r', encoding='utf-8') as file:
                        reader = csv.DictReader(file)
                        rows = list(reader)
                        if rows:
                            last_row = rows[-1]
                            chat_history.append({
                                "session_id": file_path.split('/')[-1].replace('.csv', ''),
                                "last_user_message": last_row["last_user_message"]
                            })
        
        return {"chat_history": chat_history}

    @app.get("/api/chat_history/{session_id}")
    async def get_chat_history(session_id: str, request_obj: Request):
        client_ip = request_obj.client.host
        directory = f"database/chat_history/{client_ip}"
        chat_history = []

        if os.path.exists(directory):
            for file in os.listdir(directory):
                if file.endswith(".csv") and session_id in file:
                    file_path = f"{directory}/{file}"
                    with open(file_path, mode='r', encoding='utf-8') as file:
                        reader = csv.DictReader(file)
                        chat_history = list(reader)
                    break

        if not chat_history:
            return {"status": "error", "message": "Session not found"}

        return {"messages": chat_history}

    if __name__ == "__main__":
        uvicorn.run(app, host="0.0.0.0", port=8000)



else:
    
    import uuid, os, uvicorn, sys, time
    from fastapi import FastAPI, Request
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    from chatbot.agent.reactagent import answer
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


    # if __name__ == "__main__":
    #     uvicorn.run(app, host="0.0.0.0", port=8000)


