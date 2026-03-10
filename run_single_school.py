import sys
import os
import json
from datetime import datetime
import time
import logging
import uuid

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('single_school_run.log')
    ]
)
logger = logging.getLogger(__name__)

# Import the main module
from src.dbenc.main import run

# Sample school data for testing
SAMPLE_SCHOOLS = [
    {
        "school_id": str(uuid.uuid4()),
        "school_name": "SACRED HEART CATHOLIC HIGH SCHOOL",
        "address": "106 N. St. Joseph",
        "city": "Morrilton",
        "state": "AR",
        "zip": 72110,
        "total_student_enrollment": None,
        "latitude": None,
        "longitude": None
    },
    {
        "school_id": str(uuid.uuid4()),
        "school_name": "LITTLE FISHERS PRESCHOOL",
        "address": "2011 AUSTIN PKWY",
        "city": "SUGAR LAND",
        "state": "TX",
        "zip": 77479,
        "total_student_enrollment": None,
        "latitude": None,
        "longitude": None
    }
]

if __name__ == "__main__":
    # Get the school index from command line arguments
    school_index = 0
    if len(sys.argv) > 1:
        try:
            school_index = int(sys.argv[1])
        except ValueError:
            logger.error(f"Invalid school index: {sys.argv[1]}")
            sys.exit(1)

    # Validate the school index
    if school_index < 0 or school_index >= len(SAMPLE_SCHOOLS):
        logger.error(f"School index out of range: {school_index}")
        sys.exit(1)

    # Get the selected school
    selected_school = SAMPLE_SCHOOLS[school_index]
    logger.info(f"Selected school: {selected_school['school_name']}")

    # Set parameters for the run
    use_mock = False  # Use real mode for actual data enrichment
    timeout = 600    # Set a longer timeout (10 minutes) for real operations

    # Generate a timestamp for the output file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    os.makedirs("school_output", exist_ok=True)
    output_file = os.path.join("school_output", f"single_school_{timestamp}.json")

    logger.info(f"Starting School Data Enrichment with a SINGLE SCHOOL")
    logger.info(f"School: {selected_school['school_name']}")
    logger.info(f"Parameters: use_mock={use_mock}, timeout={timeout}")
    logger.info(f"Results will be saved to {output_file}")

    try:
        # Monkey patch the get_schools_needing_enrichment function in SupabaseTool
        from src.dbenc.tools.supabase_tool import SupabaseTool
        original_get_schools = SupabaseTool.get_schools_needing_enrichment

        def mock_get_schools_needing_enrichment(self, *args, **kwargs):
            logger.info(f"Using mock get_schools_needing_enrichment with single school: {selected_school['school_name']}")
            return [selected_school]

        # Apply the monkey patch
        SupabaseTool.get_schools_needing_enrichment = mock_get_schools_needing_enrichment

        # Run the crew
        start_time = time.time()
        results = run(batch_size=1, output_file=output_file, use_mock=use_mock, timeout=timeout)
        end_time = time.time()

        # Restore the original function
        SupabaseTool.get_schools_needing_enrichment = original_get_schools

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

                # Analyze the results
                successful_updates = 0
                failed_updates = 0

                for result in data.get('results', []):
                    if isinstance(result, dict) and 'result' in result:
                        result_text = result.get('result', '')
                        if 'successfully updated' in result_text.lower():
                            successful_updates += 1
                        elif 'failed' in result_text.lower() or 'error' in result_text.lower():
                            failed_updates += 1

                logger.info(f"Successful updates: {successful_updates}")
                logger.info(f"Failed updates: {failed_updates}")
        else:
            logger.error(f"Results file {output_file} not found")

    except Exception as e:
        logger.error(f"Error running the crew: {e}")
        import traceback
        logger.error(traceback.format_exc())
