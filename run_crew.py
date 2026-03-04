import sys
import os

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

# Import the main module
from src.dbenc.main import run

# Run the crew with a batch of 3 schools
if __name__ == "__main__":
    run(batch_size=3, use_mock=True, timeout=300)
