import json
import logging
import os
import requests
import time
import random
import sys

# Add the current directory to the Python path
sys.path.append('.')

from dotenv import load_dotenv
from src.error_handling import retry_with_exponential_backoff, safe_execute, batch_with_error_handling

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get Supabase credentials from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

@retry_with_exponential_backoff(max_retries=3, initial_delay=2.0)
def update_school(school_id, data):
    """Update a single school with retry mechanism"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Supabase credentials not found in environment variables")

    if not school_id:
        raise ValueError(f"Missing school_id in update")

    # Update the school in the database using Supabase REST API
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

    url = f"{SUPABASE_URL}/rest/v1/schools?school_id=eq.{school_id}"
    response = requests.patch(url, headers=headers, json=data)

    if response.status_code == 200 or response.status_code == 204:
        logger.info(f"Successfully updated school {school_id}")
        return {"school_id": school_id, "status": "success"}
    else:
        error_message = f"Failed to update school {school_id}: {response.text}"
        logger.error(error_message)
        raise Exception(error_message)

def update_schools_from_json(json_file_path):
    """Update schools in the database using the repaired JSON file with robust error handling"""
    try:
        # Load the JSON file
        with open(json_file_path, 'r') as f:
            updates = json.load(f)

        logger.info(f"Loaded {len(updates)} school updates from {json_file_path}")

        # Check if Supabase credentials are available
        if not SUPABASE_URL or not SUPABASE_KEY:
            logger.error("Supabase credentials not found in environment variables")
            return {"error": "Supabase credentials not found"}

        logger.info("Connected to Supabase")

        # Process updates with batch error handling
        results = batch_with_error_handling(
            items=updates,
            process_func=lambda update: update_school(update.get('school_id'), update.get('data', {})),
            batch_size=5
        )

        # Print summary
        logger.info(f"Update complete: {results['success_count']} successful, {results['error_count']} failed")
        return {
            "success_count": results['success_count'],
            "error_count": results['error_count'],
            "total": len(updates),
            "results": results['results'],
            "errors": results['errors']
        }

    except Exception as e:
        logger.error(f"Error in update_schools_from_json: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Update schools in the database using a JSON file')
    parser.add_argument('json_file', help='Path to the JSON file with school updates')
    args = parser.parse_args()

    result = update_schools_from_json(args.json_file)
    print(f"Update result: {json.dumps(result, indent=2)}")
