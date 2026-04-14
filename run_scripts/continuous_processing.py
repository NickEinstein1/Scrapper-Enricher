#!/usr/bin/env python3
"""
Continuous School Data Enrichment Processing
This script will continuously process schools until all are processed.
It uses real data from the Supabase database via the MCP server.

Usage:
    python continuous_processing.py [options]

Options:
    --batch_size=N        Number of schools to process in each batch (default: 2)
    --max_schools=N       Maximum number of schools to process in each run (default: 50)
    --timeout=N           Timeout in seconds for each batch (default: 600)
    --wait=N              Wait time in seconds between runs (default: 60)
    --max_runs=N          Maximum number of runs (default: 100, use 0 for unlimited)
    --help                Show this help message and exit
"""

import subprocess
import time
import logging
import json
import os
import sys
from datetime import datetime

os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join('logs', 'continuous_processing.log'))
    ]
)
logger = logging.getLogger(__name__)

# Default configuration
BATCH_SIZE = 2
MAX_SCHOOLS_PER_RUN = 50
TIMEOUT = 600
WAIT_BETWEEN_RUNS = 60  # seconds
MAX_RUNS = 100  # Set to 0 for unlimited runs
PROCESSED_SCHOOLS_FILE = os.path.join("school_output", "processed_schools.json")

# Parse command line arguments
def parse_args():
    """Parse command line arguments"""
    args = {}
    for arg in sys.argv[1:]:
        if arg == "--help":
            print(__doc__)
            sys.exit(0)
        elif arg.startswith("--"):
            try:
                key, value = arg.split("=", 1)
                key = key[2:]  # Remove the -- prefix
                args[key] = value
            except ValueError:
                logger.warning(f"Ignoring invalid argument: {arg}")
    return args

# Apply command line arguments
args = parse_args()
BATCH_SIZE = int(args.get("batch_size", BATCH_SIZE))
MAX_SCHOOLS_PER_RUN = int(args.get("max_schools", MAX_SCHOOLS_PER_RUN))
TIMEOUT = int(args.get("timeout", TIMEOUT))
WAIT_BETWEEN_RUNS = int(args.get("wait", WAIT_BETWEEN_RUNS))
MAX_RUNS = int(args.get("max_runs", MAX_RUNS))

# Set MAX_RUNS to None if it's 0 (unlimited)
if MAX_RUNS == 0:
    MAX_RUNS = None

def get_processed_count():
    """Get the number of processed schools"""
    if os.path.exists(PROCESSED_SCHOOLS_FILE):
        with open(PROCESSED_SCHOOLS_FILE, 'r') as f:
            data = json.load(f)
            return len(data.get("processed_school_ids", []))
    return 0

def main():
    """Main function to continuously process schools"""
    logger.info("Starting Continuous School Data Enrichment Processing")
    logger.info(f"Configuration: batch_size={BATCH_SIZE}, max_schools_per_run={MAX_SCHOOLS_PER_RUN}, timeout={TIMEOUT}")

    # Make sure the MCP server is running
    logger.info("Checking if MCP server is running...")
    try:
        # Simple check to see if the test_mcp_connection.js file exists
        if os.path.exists("test_mcp_connection.js"):
            logger.info("Running MCP connection test...")
            subprocess.run("node tests/test_mcp_connection.js", shell=True, check=False)
        else:
            logger.warning("test_mcp_connection.js not found. Make sure the MCP server is running.")
            logger.info("You can start the MCP server with: npx -y @supabase/mcp-server-supabase@latest --access-token=your_access_token")
    except Exception as e:
        logger.warning(f"Error checking MCP server: {e}")
        logger.warning("Continuing anyway, but you may encounter errors if the MCP server is not running.")

    run_count = 0
    start_time = datetime.now()

    while True:
        # Check if we've reached the maximum number of runs
        if MAX_RUNS is not None and run_count >= MAX_RUNS:
            logger.info(f"Reached maximum number of runs ({MAX_RUNS}). Stopping.")
            break

        # Get the current number of processed schools
        processed_before = get_processed_count()
        logger.info(f"Run {run_count + 1}: {processed_before} schools processed so far")

        # Run the batch processing script
        logger.info(f"Starting batch processing run {run_count + 1}")
        cmd = f"python run_scripts/run_batch_schools.py --batch_size={BATCH_SIZE} --max_schools={MAX_SCHOOLS_PER_RUN} --timeout={TIMEOUT}"
        logger.info(f"Running command: {cmd}")

        try:
            subprocess.run(cmd, shell=True, check=True)
            logger.info(f"Batch processing run {run_count + 1} completed successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"Batch processing run {run_count + 1} failed with error: {e}")
            logger.error("Continuing to the next run...")

        # Get the new number of processed schools
        processed_after = get_processed_count()
        schools_processed = processed_after - processed_before
        logger.info(f"Run {run_count + 1} processed {schools_processed} new schools")

        # If no new schools were processed, we're done
        if schools_processed == 0:
            consecutive_zero_runs = getattr(main, 'consecutive_zero_runs', 0) + 1
            main.consecutive_zero_runs = consecutive_zero_runs
            logger.warning(f"No new schools were processed in this run. Consecutive zero runs: {consecutive_zero_runs}")

            # If we've had 3 consecutive runs with no new schools, we're probably done
            if consecutive_zero_runs >= 3:
                logger.info("No new schools were processed in 3 consecutive runs. All schools may be processed or there was an error.")
                break
        else:
            # Reset the consecutive zero runs counter
            main.consecutive_zero_runs = 0

        # Increment the run count
        run_count += 1

        # Calculate and log progress
        elapsed_time = (datetime.now() - start_time).total_seconds() / 60  # minutes
        schools_per_minute = processed_after / elapsed_time if elapsed_time > 0 else 0
        logger.info(f"Progress: {processed_after} schools processed in {elapsed_time:.2f} minutes ({schools_per_minute:.2f} schools/minute)")

        # Estimate time remaining
        if schools_per_minute > 0:
            # Assuming we have about 22,833 schools in total (based on earlier tests)
            total_schools = 22833
            remaining_schools = total_schools - processed_after
            estimated_minutes_remaining = remaining_schools / schools_per_minute
            logger.info(f"Estimated time remaining: {estimated_minutes_remaining:.2f} minutes ({estimated_minutes_remaining/60:.2f} hours)")

        # Wait before the next run
        logger.info(f"Waiting {WAIT_BETWEEN_RUNS} seconds before the next run...")
        time.sleep(WAIT_BETWEEN_RUNS)

    # Log final statistics
    total_elapsed_time = (datetime.now() - start_time).total_seconds() / 60  # minutes
    total_processed = get_processed_count()
    logger.info(f"Continuous processing completed after {run_count} runs")
    logger.info(f"Total schools processed: {total_processed}")
    logger.info(f"Total elapsed time: {total_elapsed_time:.2f} minutes")
    logger.info(f"Overall processing rate: {total_processed / total_elapsed_time:.2f} schools/minute")

if __name__ == "__main__":
    main()
