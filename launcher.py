import subprocess
import time
import os

def run_script(script_path):
  """Runs a Python script using subprocess.Popen.

  Args:
    script_path: The path to the Python script to run.

  Returns:
    A subprocess.Popen object representing the running process.
  """
  try:
    # Construct the command to run the script
    command = ["python", script_path]
    # Start the process
    process = subprocess.Popen(command)
    # Return the process object
    return process
  except FileNotFoundError:
    print(f"Error: Script not found: {script_path}")
    return None

def main():
  """Starts two Python scripts simultaneously using subprocess.Popen."""

  # Define the paths to the scripts
  main_script_path = "main.py"
  emotion_analysis_script_path = "assessment/analysis/emotion_analysis.py"

  # Start the main script
  main_process = run_script(main_script_path)

  # Start the emotion analysis script
  emotion_analysis_process = run_script(emotion_analysis_script_path)

  # Check if both scripts were started successfully
  if main_process is not None and emotion_analysis_process is not None:
    print("Both main.py and emotion_analysis.py have been started.")
  else:
    print("Error starting one or both scripts.")

  # Keep the main process running to prevent the scripts from being terminated
  while True:
    time.sleep(1)
    # Check if either script has exited
    if main_process.poll() is not None or emotion_analysis_process.poll() is not None:
      print("One or both scripts have exited.")
      break

if __name__ == "__main__":
  main()