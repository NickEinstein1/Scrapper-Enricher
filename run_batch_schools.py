import sys
import os
import json
from datetime import datetime
import time
import logging
import argparse

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('batch_schools_run.log')
    ]
)
logger = logging.getLogger(__name__)

# Import the main module
from src.dbenc.main import run
from src.dbenc.tools.supabase_tool import SupabaseTool

# File to track processed schools
PROCESSED_SCHOOLS_FILE = "processed_schools.json"

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

def get_unprocessed_schools(limit=10):
    """Get schools that haven't been processed yet"""
    # Get the list of already processed schools
    processed_schools = load_processed_schools()
    processed_ids = set(processed_schools["processed_school_ids"])

    # Connect to Supabase
    supabase_tool = SupabaseTool()

    # Get schools needing enrichment
    all_schools = supabase_tool.get_schools_needing_enrichment(limit=limit)

    # Filter out already processed schools
    unprocessed_schools = [school for school in all_schools if school["school_id"] not in processed_ids]

    logger.info(f"Found {len(unprocessed_schools)} unprocessed schools out of {len(all_schools)} total schools")

    return unprocessed_schools

def process_batch(schools, batch_size, use_mock=False, timeout=300):
    """Process a batch of schools"""
    if not schools:
        logger.info("No schools to process in this batch")
        return []

    # Generate a timestamp for the output file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"batch_schools_{timestamp}.json"

    # Create a temporary file with just these schools
    temp_schools_file = f"temp_batch_{timestamp}.json"
    with open(temp_schools_file, 'w') as f:
        json.dump(schools, f, indent=2)
        logger.info(f"Created temporary schools file: {temp_schools_file}")

    # Log detailed information about each school
    logger.info(f"Processing batch of {len(schools)} schools")
    for i, school in enumerate(schools):
        logger.info(f"School {i+1}: {school.get('school_name', 'Unknown')} (ID: {school.get('school_id', 'Unknown')})")
        logger.info(f"  Address: {school.get('address', 'Unknown')}, {school.get('city', 'Unknown')}, {school.get('state', 'Unknown')} {school.get('zip', 'Unknown')}")
        logger.info(f"  Missing fields: {school.get('missing_fields', [])}")

    try:
        # Run the crew with retry mechanism
        start_time = time.time()
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                logger.info(f"Attempt {retry_count + 1} of {max_retries}")
                # Run the crew and save results directly to the output file
                logger.info(f"Running with parameters: batch_size={batch_size}, timeout={timeout}, use_mock={use_mock}")
                run(batch_size=batch_size, output_file=output_file, use_mock=use_mock, timeout=timeout, schools_file=temp_schools_file)
                logger.info(f"Run completed successfully on attempt {retry_count + 1}")
                # If we get here without an exception, break the retry loop
                break
            except Exception as e:
                retry_count += 1
                logger.warning(f"Attempt {retry_count} failed with error: {e}")
                # Log the stack trace for better debugging
                import traceback
                logger.warning(f"Stack trace: {traceback.format_exc()}")

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
        logger.info(f"Processed {len(schools)} schools")

        # Check if the results file exists
        if os.path.exists(output_file):
            logger.info(f"Results saved to {output_file}")

            # Display a summary of the results
            with open(output_file, 'r') as f:
                data = json.load(f)

                # Check for errors
                errors = [r for r in data.get('results', []) if isinstance(r, dict) and 'error' in r]
                if errors:
                    logger.warning(f"Found {len(errors)} batches with errors")
                    for i, error in enumerate(errors):
                        logger.warning(f"Error in batch {i+1}: {error.get('error')}")

                # Analyze the results and track successful schools
                successful_updates = 0
                failed_updates = 0
                successful_school_ids = []

                # First, check if there are any results
                if 'results' not in data or not data.get('results'):
                    logger.warning("No results found in the output file")
                    return []

                # Process each result
                for result in data.get('results', []):
                    if isinstance(result, dict):
                        # Check for explicit error field
                        if 'error' in result:
                            failed_updates += 1
                            logger.warning(f"Failed update: {result.get('error')}")
                            continue

                        # Check for school_id in the result
                        school_id = None
                        if 'school_id' in result:
                            school_id = result['school_id']
                        elif 'data' in result and isinstance(result['data'], list) and len(result['data']) > 0:
                            # Try to extract school_id from data array
                            for item in result['data']:
                                if isinstance(item, dict) and 'school_id' in item:
                                    school_id = item['school_id']
                                    break

                        # Check result text
                        if 'result' in result:
                            result_text = str(result.get('result', ''))
                            if 'successfully updated' in result_text.lower() or 'success' in result_text.lower():
                                successful_updates += 1
                                logger.info(f"Successful update detected in result")
                                if school_id:
                                    successful_school_ids.append(school_id)
                            elif 'failed' in result_text.lower() or 'error' in result_text.lower():
                                failed_updates += 1
                                logger.warning(f"Failed update detected in result: {result_text}")

                # If we couldn't determine success/failure from the results, assume success for all schools
                if successful_updates == 0 and failed_updates == 0:
                    logger.info("Could not determine success/failure from results, marking all schools as processed")
                    for school in schools:
                        save_processed_school(school["school_id"])
                else:
                    # Mark successful schools as processed
                    for school_id in successful_school_ids:
                        save_processed_school(school_id)

                    # If we have successful updates but no school_ids, mark all schools as processed
                    if successful_updates > 0 and not successful_school_ids:
                        logger.info("Successful updates detected but no school_ids found, marking all schools as processed")
                        for school in schools:
                            save_processed_school(school["school_id"])

                logger.info(f"Successful updates: {successful_updates}")
                logger.info(f"Failed updates: {failed_updates}")
                logger.info(f"Successful school IDs: {successful_school_ids}")

                return data.get('results', [])
        else:
            logger.error(f"Results file {output_file} not found")
            return []

    except Exception as e:
        logger.error(f"Error processing batch: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return []

def main(args):
    """Main function to process schools in batches"""
    logger.info("Starting Batch School Data Enrichment with MCP Server")
    logger.info(f"Parameters: batch_size={args.batch_size}, max_schools={args.max_schools}, use_mock={args.use_mock}, timeout={args.timeout}")

    # Get unprocessed schools
    unprocessed_schools = get_unprocessed_schools(limit=args.max_schools)

    if not unprocessed_schools:
        logger.info("No unprocessed schools found. All schools have been processed.")
        return

    logger.info(f"Found {len(unprocessed_schools)} unprocessed schools")

    # Process schools in batches
    batch_size = min(args.batch_size, 3)  # Limit batch size to prevent context window issues

    # Split schools into smaller batches
    batches = []
    for i in range(0, len(unprocessed_schools), batch_size):
        batches.append(unprocessed_schools[i:i + batch_size])

    logger.info(f"Split {len(unprocessed_schools)} schools into {len(batches)} batches of size {batch_size}")

    # Process each batch
    all_results = []
    for i, batch in enumerate(batches):
        logger.info(f"Processing batch {i+1} of {len(batches)}")
        batch_results = process_batch(batch, batch_size, use_mock=args.use_mock, timeout=args.timeout)
        all_results.extend(batch_results)

        # Wait between batches to avoid rate limiting
        if i < len(batches) - 1:
            wait_time = 5
            logger.info(f"Waiting {wait_time} seconds before processing next batch...")
            time.sleep(wait_time)

    logger.info(f"Completed processing {len(unprocessed_schools)} schools in {len(batches)} batches")
    logger.info(f"Total results: {len(all_results)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process schools in batches')
    parser.add_argument('--batch_size', type=int, default=1, help='Number of schools to process in each batch')
    parser.add_argument('--max_schools', type=int, default=10, help='Maximum number of schools to process in total')
    parser.add_argument('--use_mock', action='store_true', help='Use mock data instead of real data')
    parser.add_argument('--timeout', type=int, default=300, help='Timeout in seconds for each batch')
    args = parser.parse_args()

    main(args)
