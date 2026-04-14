import sys
import os
import json
from datetime import datetime
import time
import logging
import uuid

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join('logs', 'real_school_run.log'))
    ]
)
logger = logging.getLogger(__name__)

# Import the main module
from src.dbenc.main import run
from src.dbenc.tools.supabase_tool import SupabaseTool

# File to track processed schools
PROCESSED_SCHOOLS_FILE = os.path.join("school_output", "processed_schools.json")

def load_processed_schools():
    """Load the list of already processed schools"""
    if os.path.exists(PROCESSED_SCHOOLS_FILE):
        try:
            with open(PROCESSED_SCHOOLS_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.warning(f"Error reading {PROCESSED_SCHOOLS_FILE}, starting with empty list")
    return {"processed_school_ids": []}

def save_processed_school(school_id):
    """Save a school ID to the processed schools list"""
    processed_schools = load_processed_schools()
    if school_id not in processed_schools["processed_school_ids"]:
        processed_schools["processed_school_ids"].append(school_id)
        with open(PROCESSED_SCHOOLS_FILE, 'w') as f:
            json.dump(processed_schools, f, indent=2)
        logger.info(f"Added school {school_id} to processed schools list")
    else:
        logger.info(f"School {school_id} already in processed schools list")

def get_next_unprocessed_school():
    """Get the next school that hasn't been processed yet"""
    # Get the list of already processed schools
    processed_schools = load_processed_schools()
    processed_ids = set(processed_schools["processed_school_ids"])

    # Connect to Supabase
    supabase_tool = SupabaseTool()

    # Get schools needing enrichment
    schools = supabase_tool.get_schools_needing_enrichment(limit=10)

    # Find the first school that hasn't been processed yet
    for school in schools:
        if school["school_id"] not in processed_ids:
            return school

    return None

if __name__ == "__main__":
    logger.info("Starting Real-Time School Data Enrichment with MCP Server")

    # Get the next unprocessed school
    school = get_next_unprocessed_school()

    if not school:
        logger.info("No unprocessed schools found. All schools have been processed.")
        sys.exit(0)

    logger.info(f"Selected school: {school['school_name']} (ID: {school['school_id']})")

    # Set parameters for the run
    use_mock = False  # Use real mode for actual data enrichment
    timeout = 600     # Set a longer timeout (10 minutes) for real operations

    # Generate a timestamp for the output file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    os.makedirs("school_output", exist_ok=True)
    output_file = os.path.join("school_output", f"real_school_{timestamp}.json")

    logger.info(f"Starting School Data Enrichment with REAL DATA")
    logger.info(f"School: {school['school_name']}")
    logger.info(f"Parameters: use_mock={use_mock}, timeout={timeout}")
    logger.info(f"Results will be saved to {output_file}")

    try:
        # Create a temporary file with just this school
        temp_schools_file = os.path.join("school_output", f"temp_school_{timestamp}.json")
        with open(temp_schools_file, 'w') as f:
            json.dump([school], f, indent=2)

        # Run the crew with retry mechanism
        start_time = time.time()
        max_retries = 3
        retry_count = 0
        results = None

        while retry_count < max_retries:
            try:
                logger.info(f"Attempt {retry_count + 1} of {max_retries}")
                results = run(batch_size=1, output_file=output_file, use_mock=use_mock, timeout=timeout, schools_file=temp_schools_file)
                # If we get here without an exception, break the retry loop
                break
            except Exception as e:
                retry_count += 1
                logger.warning(f"Attempt {retry_count} failed with error: {e}")
                if retry_count < max_retries:
                    # Wait before retrying (exponential backoff)
                    wait_time = 2 ** retry_count
                    logger.info(f"Waiting {wait_time} seconds before retrying...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"All {max_retries} attempts failed")
                    raise

        end_time = time.time()

        # Clean up the temporary file
        if os.path.exists(temp_schools_file):
            os.remove(temp_schools_file)

        # Log the results
        logger.info(f"Execution completed in {end_time - start_time:.2f} seconds")
        logger.info(f"Processed 1 school")

        # Check if the results file exists
        if os.path.exists(output_file):
            logger.info(f"Results saved to {output_file}")

            # Display a summary of the results
            with open(output_file, 'r') as f:
                data = json.load(f)
                logger.info(f"Total batches: {data.get('total_batches', 0)}")

                # Check for errors
                errors = [r for r in data.get('results', []) if isinstance(r, dict) and 'error' in r]
                if errors:
                    logger.warning(f"Found {len(errors)} batches with errors")
                    for i, error in enumerate(errors):
                        logger.warning(f"Error in batch {i+1}: {error.get('error')}")
                else:
                    logger.info("No errors found in the results")
                    # Mark the school as processed only if there were no errors
                    save_processed_school(school["school_id"])

                # Analyze the results
                successful_updates = 0
                failed_updates = 0

                for result in data.get('results', []):
                    if isinstance(result, dict):
                        # Check for explicit error field
                        if 'error' in result:
                            failed_updates += 1
                            logger.warning(f"Failed update: {result.get('error')}")
                            continue

                        # Check result text
                        if 'result' in result:
                            result_text = str(result.get('result', ''))
                            if 'successfully updated' in result_text.lower() or 'success' in result_text.lower():
                                successful_updates += 1
                                logger.info(f"Successful update detected in result")
                            elif 'failed' in result_text.lower() or 'error' in result_text.lower():
                                failed_updates += 1
                                logger.warning(f"Failed update detected in result: {result_text}")

                logger.info(f"Successful updates: {successful_updates}")
                logger.info(f"Failed updates: {failed_updates}")
        else:
            logger.error(f"Results file {output_file} not found")

    except Exception as e:
        logger.error(f"Error running the crew: {e}")
        import traceback
        logger.error(traceback.format_exc())
