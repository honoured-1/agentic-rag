import os
import csv
import time
from tensorboardX import SummaryWriter

# Directory containing chat history CSV files
base_directory = "database/chat_history"

# Dictionary to store the last processed message count for each CSV file
last_processed_counts = {}

def process_csv(file_path):
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        rows = list(reader)
        header = rows[0]
        data = rows[1:]

    # Check if the CSV file has new messages
    if file_path in last_processed_counts:
        last_count = last_processed_counts[file_path]
        if len(data) == last_count:
            return  # No new messages, skip processing
    else:
        last_processed_counts[file_path] = 0

    # Update the last processed count
    last_processed_counts[file_path] = len(data)

    # Extract data for TensorBoard logging
    for row in data:
        client_ip, message, response, feedback, duration = row
        log_dir = f"database/tensorboard_logs/{os.path.basename(file_path).replace('.csv', '')}"
        
        # Delete previous logs if they exist
        if os.path.exists(log_dir):
            for file in os.listdir(log_dir):
                try:
                    os.remove(os.path.join(log_dir, file))
                except PermissionError:
                    print(f"PermissionError: Unable to delete {os.path.join(log_dir, file)}. Skipping.")
                    continue
        
        # Initialize TensorBoard writer
        writer = SummaryWriter(logdir=log_dir)
        
        # Log hparams
        writer.add_hparams(
            {
                'client_ip': client_ip,
                'message': message,
                'response': response,
                'feedback': feedback,
                'duration': duration
            },
            {}
        )
        
        writer.close()

def main():
    while True:
        for root, dirs, files in os.walk(base_directory):
            for file in files:
                if file.endswith(".csv"):
                    file_path = os.path.join(root, file)
                    process_csv(file_path)
        time.sleep(600)  # Check for new messages every 10 minutes

if __name__ == "__main__":
    main()
