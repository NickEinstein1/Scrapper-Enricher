import os
from dotenv import load_dotenv
import json
import argparse
from datetime import datetime
from typing import Dict, Any, List
import logging
import sys

# Configure logging to output to console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

from src.dbenc.crew import SchoolEnrichmentCrew
from src.dbenc.tools.supabase_tool import SupabaseTool

load_dotenv()

def initialize_database() -> Dict[str, Any]:
    supabase_tool = SupabaseTool()
    return supabase_tool.initialize_database()

def run(batch_size: int = 1, output_file: str = None, use_mock: bool = True, timeout: int = 300, schools_file: str = None) -> List[Any]:
    try:
        logger.info("Starting run function")
        init_result = initialize_database()
        logger.info(f"Database initialization result: {init_result}")
        if "error" in init_result:
            raise Exception(f"Database initialization failed: {init_result['error']}")

        logger.info(f"Creating SchoolEnrichmentCrew with mock_mode={use_mock} and timeout={timeout}")
        try:
            crew = SchoolEnrichmentCrew(use_mock=use_mock, timeout=timeout)
            logger.info("SchoolEnrichmentCrew created successfully")
        except Exception as e:
            logger.error(f"Error creating SchoolEnrichmentCrew: {e}")
            raise

        logger.info("Creating SupabaseTool")
        supabase_tool = SupabaseTool()
        logger.info("Getting schools needing enrichment")

        # Check if a specific schools file was provided
        if schools_file and os.path.exists(schools_file):
            logger.info(f"Using provided schools file: {schools_file}")
            with open(schools_file, 'r') as f:
                all_schools = json.load(f)
        else:
            # Check if there's a schools_to_process file
            schools_files = [f for f in os.listdir() if f.startswith("schools_to_process_") and f.endswith(".json")]

            if schools_files:
                # Sort by modification time (newest first)
                schools_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
                latest_file = schools_files[0]
                logger.info(f"Found schools file: {latest_file}")

                # Load schools from file
                with open(latest_file, 'r') as f:
                    all_schools = json.load(f)
            else:
                # Get schools from Supabase
                all_schools = supabase_tool.get_schools_needing_enrichment()

        logger.info(f"Found {len(all_schools)} schools needing enrichment")

        # Print the schools for debugging
        for i, school in enumerate(all_schools):
            logger.info(f"School {i+1}: {school}")

        max_schools = 10
        if len(all_schools) > max_schools:
            logger.warning(f"Limiting to {max_schools} schools")
            all_schools = all_schools[:max_schools]

        results = []
        for i in range(0, len(all_schools), batch_size):
            batch = all_schools[i:i + batch_size]
            input_data = {
                "schools": batch,
                "current_year": str(datetime.now().year)
            }

            logger.info(f"Processing batch {i // batch_size + 1} with {len(batch)} schools")
            try:
                result = crew.run_crew(input_data)
                # Convert CrewOutput to a serializable dictionary
                serializable_result = {
                    "result": result.result if hasattr(result, 'result') else str(result),
                    "raw_output": result.raw_output if hasattr(result, 'raw_output') else None,
                    "task_outputs": [str(task_output) for task_output in result.task_outputs] if hasattr(result, 'task_outputs') else []
                }
                results.append(serializable_result)
                logger.info(f"Successfully processed batch {i // batch_size + 1}")
                logger.info(f"Result for batch {i // batch_size + 1}: {json.dumps(serializable_result, indent=2)}")
            except Exception as batch_error:
                logger.error(f"Error in batch {i // batch_size + 1}: {batch_error}")
                continue

        # Save results to a file
        if not output_file:
            output_file = f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(output_file, 'w') as f:
            json.dump({"results": results, "total_batches": len(results)}, f, indent=2)
        logger.info(f"Results saved to {output_file}")

        return results

    except Exception as e:
        logger.error(f"Error during run: {e}")
        raise

def test_db() -> None:
    print("Starting test_db function")
    try:
        supabase_tool = SupabaseTool()
        print("SupabaseTool created")
        result = supabase_tool.test_connection()
        print("Test connection result:", json.dumps(result, indent=2))
        if result["data"] is None:
            print("Initializing database...")
            init_result = initialize_database()
            print("Initialization result:", json.dumps(init_result, indent=2))
    except Exception as e:
        print(f"Error in test_db: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='School data enrichment')
    parser.add_argument('command', choices=['run', 'test_db'], help='Command to run')
    parser.add_argument('--output_file', type=str, help='File to save results')
    parser.add_argument('--batch_size', type=int, default=5, help='Schools per batch (default: 5)')
    parser.add_argument('--no-mock', action='store_true', help='Disable mock mode for scraping')
    parser.add_argument('--timeout', type=int, default=60, help='Timeout in seconds for crew execution (default: 60)')
    parser.add_argument('--schools_file', type=str, help='JSON file containing schools to process')
    args = parser.parse_args()

    if args.command == "run":
        run(batch_size=args.batch_size, output_file=args.output_file, use_mock=not args.no_mock, timeout=args.timeout, schools_file=args.schools_file)
    elif args.command == "test_db":
        test_db()