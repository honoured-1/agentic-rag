import os
import csv
import motor.motor_asyncio
from dotenv import load_dotenv
from bson import ObjectId

# Load environment variables
load_dotenv()

# MongoDB client setup
MONGODB_CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_CONNECTION_STRING)
db = client.chatbot
chat_collection = db.chat_history

async def fetch_all_documents():
    documents = await chat_collection.find().to_list(length=None)
    return documents

def convert_objectid(data):
    if isinstance(data, list):
        for item in data:
            if '_id' in item:
                item['_id'] = str(item['_id'])
    elif isinstance(data, dict):
        if '_id' in data:
            data['_id'] = str(data['_id'])
    return data

def read_existing_csv(csv_file_path):
    existing_ids = set()
    if os.path.isfile(csv_file_path):
        with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if '_id' in row:
                    existing_ids.add(row['_id'])
    return existing_ids

async def dump_to_csv():
    documents = await fetch_all_documents()
    documents = convert_objectid(documents)
    
    # Define the CSV file path
    csv_file_path = "database/mongodb_dump/dump.csv"
    
    # Read existing CSV to get already saved IDs
    existing_ids = read_existing_csv(csv_file_path)
    
    # Filter out documents that are already in the CSV
    new_documents = [doc for doc in documents if doc['_id'] not in existing_ids]
    
    # Define the column names
    column_names = ["_id", "client_ip", "message", "response", "feedback", "duration", "last_user_message", "session_id"]
    
    # Write to CSV file
    file_exists = os.path.isfile(csv_file_path)
    with open(csv_file_path, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=column_names)
        
        # Write header if the file doesn't exist or is empty
        if not file_exists or os.stat(csv_file_path).st_size == 0:
            writer.writeheader()
        
        # Write new documents to the CSV
        writer.writerows(new_documents)
    
    print(f"Data successfully dumped to {csv_file_path}")

# Run the dump_to_csv function
import asyncio
asyncio.run(dump_to_csv())
