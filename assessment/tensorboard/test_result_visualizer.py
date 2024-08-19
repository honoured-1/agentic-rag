import os
import pandas as pd
import yaml
from torch.utils.tensorboard import SummaryWriter

# Load the test results folders
test_results_dir = 'database/test_results'
test_folders = [os.path.join(test_results_dir, d) for d in os.listdir(test_results_dir) if os.path.isdir(os.path.join(test_results_dir, d))]

# Initialize TensorBoard writer
log_dir = 'database/tensorboard/test_logs'
os.makedirs(log_dir, exist_ok=True)

# Define the keys to check in the CSV file
keys_to_check = ['bert_precision', 'bert_recall', 'bert_f1', 'time_taken']

# Iterate over each test results folder
for test_folder in test_folders:
    # Load the CSV file
    csv_path = os.path.join(test_folder, 'test.csv')
    if not os.path.exists(csv_path):
        continue
    
    df = pd.read_csv(csv_path)

    # Load the config.yaml file
    config_path = os.path.join(test_folder, 'config.yaml')
    with open(config_path, 'r') as config_file:
        config = yaml.safe_load(config_file)

    # Create a separate log directory for each test run
    test_log_dir = os.path.join(log_dir, os.path.basename(test_folder))
    if os.path.exists(test_log_dir):
        print(f"Skipping existing log directory: {test_log_dir}")
        continue
    
    writer = SummaryWriter(log_dir=test_log_dir)

    # Aggregate results for the test file
    hparams = {}
    metrics = {}

    for key in keys_to_check:
        if key in df.columns:
            hparams[key] = df[key].mean()
            metrics[f'hparam/{key}'] = hparams[key]
        else:
            hparams[key] = 0.0  # Set to 0.0 for TensorBoard visualization
            metrics[f'hparam/{key}'] = 0.0  # Set to 0.0 for TensorBoard visualization

    hparams['top_k'] = config.get('top_k', 5)  # Include top_k from config.yaml

    # Log aggregated results to TensorBoard
    writer.add_hparams(hparams, metrics)

    # Close the TensorBoard writer
    writer.close()
