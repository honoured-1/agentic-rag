import os, csv, schedule, time
from textblob import TextBlob
# from transformers import pipeline

# Disable SSL verification
os.environ['CURL_CA_BUNDLE'] = ''

# Initialize the emotion detection pipeline
# emotion_classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", top_k=None, use_auth_token=False, trust_remote_code=True)

def analyze_emotions(base_directory="database/chat_history"):
    print(f"Starting emotion analysis in directory: {base_directory}")
    for root, dirs, files in os.walk(base_directory):
        for file in files:
            if file.endswith(".csv"):
                file_path = os.path.join(root, file)
                print(f"Analyzing file: {file_path}")
                analyze_emotions_in_file(file_path)

def analyze_emotions_in_file(file_path):
    rows = []
    updated = False

    try:
        # Read the existing rows
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            header = next(reader)
            rows = list(reader)

        # Check if the emotion column exists
        if "emotion" not in header:
            header.append("emotion")
            updated = True
            print(f"Added 'emotion' column to header in file: {file_path}")

        # Analyze emotions for each message
        # for row in rows:
        #     if len(row) < len(header):  # If the emotion column is missing
        #         message = row[1]
        #         print(f"Analyzing message: {message}")
        #         try:
        #             emotions = emotion_classifier(message)
        #             dominant_emotion = max(emotions[0], key=lambda x: x['score'])['label']
        #             row.append(dominant_emotion)
        #             updated = True
        #         except RuntimeError as e:
        #             print(f"Skipping message due to error: {e}")
        #     else:
        #         print(f"Skipping message: {row[1]} (already analyzed)")
        for row in rows:
            if len(row) < len(header):  # If the emotion column is missing
                message = row[1]
                print(f"Analyzing message: {message}")
                try:
                    blob = TextBlob(message)
                    sentiment = blob.sentiment
                    emotion = "positive" if sentiment.polarity > 0 else "negative" if sentiment.polarity < 0 else "neutral"
                    row.append(emotion)
                    updated = True
                except Exception as e:
                    print(f"Skipping message due to error: {e}")
            else:
                print(f"Skipping message: {row[1]} (already analyzed)")

        # Write the updated rows back to the file if there were any updates
        if updated:
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(header)
                writer.writerows(rows)
            print(f"Updated file: {file_path}")

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")

def job():
    analyze_emotions()

# Schedule the job every 10 minutes
schedule.every(10).minutes.do(job)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)
