import sys
import os
import json
from datetime import datetime
import time
import logging

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join('logs', 'real_data_run.log'))
    ]
)
logger = logging.getLogger(__name__)

# Import the main module
from src.dbenc.main import run

if __name__ == "__main__":
    # Set parameters for the run
    batch_size = 2  # Start with a small batch for real data testing
    use_mock = False  # Use real mode for actual data enrichment
    timeout = 600    # Set a longer timeout (10 minutes) for real operations
    
    # Generate a timestamp for the output file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    os.makedirs("school_output", exist_ok=True)
    output_file = os.path.join("school_output", f"real_results_{timestamp}.json")
    
    logger.info(f"Starting School Data Enrichment with REAL DATA")
    logger.info(f"Parameters: batch_size={batch_size}, use_mock={use_mock}, timeout={timeout}")
    logger.info(f"Results will be saved to {output_file}")
    
    try:
        # Run the crew
        start_time = time.time()
        results = run(batch_size=batch_size, output_file=output_file, use_mock=use_mock, timeout=timeout)
        end_time = time.time()
        
        # Log the results
        logger.info(f"Execution completed in {end_time - start_time:.2f} seconds")
        logger.info(f"Processed {len(results)} batches")
        
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
