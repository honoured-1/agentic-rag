import os, schedule, time
from textblob import TextBlob
import motor.motor_asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MongoDB client setup
MONGODB_CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_CONNECTION_STRING)
db = client.chatbot
chat_collection = db.chat_history

async def analyze_emotions():
    print("Starting emotion analysis in MongoDB")
    async for document in chat_collection.find():
        await analyze_emotions_in_document(document)

async def analyze_emotions_in_document(document):
    updated = False
    message = document.get("message", "")
    emotion = document.get("emotion", None)

    if not emotion:
        print(f"Analyzing message: {message}")
        try:
            blob = TextBlob(message)
            sentiment = blob.sentiment
            emotion = "positive" if sentiment.polarity > 0 else "negative" if sentiment.polarity < 0 else "neutral"
            await chat_collection.update_one(
                {"_id": document["_id"]},
                {"$set": {"emotion": emotion}}
            )
            updated = True
        except Exception as e:
            print(f"Skipping message due to error: {e}")
    else:
        print(f"Skipping message: {message} (already analyzed)")

    if updated:
        print(f"Updated document: {document['_id']}")

def job():
    import asyncio
    asyncio.run(analyze_emotions())

# Schedule the job every 10 minutes
schedule.every(120).minutes.do(job)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)
