import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from logs.logger import logger  # Import the logger

# Log test message
logger.info("This is a test log entry!")

# Verify log file location
log_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs", "crew_logs.log"))
print(f"Logger is writing to: {log_file_path}")

# Check if the log file was created
if os.path.exists(log_file_path):
    print("Log file exists. Logging is working correctly!")
    with open(log_file_path, "r", encoding="utf-8") as log_file:
        print("Log file content:")
        print(log_file.read())
else:
    print("❌ Log file not found! Logging is not working correctly.")
