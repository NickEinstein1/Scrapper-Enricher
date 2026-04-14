import sys
import os

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

# Import the main module
from src.dbenc.main import test_db

# Run the test_db function
if __name__ == "__main__":
    test_db()
