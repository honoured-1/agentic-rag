import os, yaml, sys, time
sys.path.append('chatbot')
from rag.rag import get_answer #type: ignore
import pandas as pd
from datetime import datetime
from bert_score import score as bert_score

# Set environment variable to avoid OpenMP runtime conflict
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

# Load existing config.yaml if it exists
config_path = 'config.yaml'
if os.path.exists(config_path):
    with open(config_path, 'r') as config_file:
        config = yaml.safe_load(config_file)
else:
    # Configuration dictionary to store relevant settings
    config = {
        'bert_score_lang': 'en'
    }

# Create a folder named with the current datetime
current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
folder_path = f'database/test_results/{current_time}'
os.makedirs(folder_path, exist_ok=True)

# Save config.yaml in the folder
new_config_path = os.path.join(folder_path, 'config.yaml')
with open(new_config_path, 'w') as config_file:
    yaml.dump(config, config_file)

# Load the CSV file
df = pd.read_csv('database/python_theoretical_qa.csv')

# Initialize lists to store individual scores (optional if needed later)
bert_precision_scores = []
bert_recall_scores = []
bert_f1_scores = []
time_taken_list = []

# Iterate over each row in the CSV
for index, row in df.iterrows():
    query = row['message']
    expected_response = row['response']
    
    # Record the start time
    start_time = time.time()
    
    # Get the actual response from your function
    actual_response = get_answer(query)
    
    # Record the end time
    end_time = time.time()
    
    # Calculate the time taken
    time_taken = end_time - start_time
    time_taken_list.append(time_taken)
    
    # Calculate BERTScore
    P, R, F1 = bert_score([actual_response], [expected_response], lang=config['bert_score_lang'], rescale_with_baseline=True)
    
    # Update the DataFrame with the computed scores and time taken
    df.at[index, 'actual_response'] = actual_response
    df.at[index, 'bert_precision'] = P.item()
    df.at[index, 'bert_recall'] = R.item()
    df.at[index, 'bert_f1'] = F1.item()
    df.at[index, 'time_taken'] = time_taken
    
    # Optional: Append scores to lists if you want to use them later
    bert_precision_scores.append(P.item())
    bert_recall_scores.append(R.item())
    bert_f1_scores.append(F1.item())

# Save the updated DataFrame to the CSV
df.to_csv(os.path.join(folder_path, 'test.csv'), index=False)
