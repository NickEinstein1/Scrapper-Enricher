import os
import subprocess
import time
import json
import sqlite3
from datetime import datetime
# Fix import path
import sys
sys.path.append('.')
from src.get_schools_for_processing import get_unprocessed_schools, save_schools_to_file

def prepare_schools_for_processing(batch_size=5):
    """Get unprocessed schools from Supabase and prepare them for processing"""
    print(f"Getting {batch_size} unprocessed schools from Supabase...")
    schools = get_unprocessed_schools(batch_size)

    if not schools:
        print("No unprocessed schools found in Supabase.")
        return None

    # Save schools to a file for processing
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    os.makedirs("school_output", exist_ok=True)
    schools_file = os.path.join("school_output", f"schools_to_process_{timestamp}.json")
    save_schools_to_file(schools, schools_file)

    return schools_file

def run_batch(batch_size=5, timeout=180):
    """Run a batch of schools through the enrichment process"""
    # Get unprocessed schools from Supabase
    schools_file = prepare_schools_for_processing(batch_size)

    if not schools_file:
        print("No schools to process. Exiting.")
        return False

    # Run the main process
    print(f"Running batch with size {batch_size} and timeout {timeout}...")
    # Use the correct path to the main.py script
    subprocess.run(["python", "-m", "dbenc.main", "run", "--batch_size", str(batch_size), "--timeout", str(timeout)])

    # Extract school data
    print("Extracting school data...")
    subprocess.run(["python", "src/extract_school_data.py"])

    # Find the latest repaired JSON file in repair_output/
    repair_dir = "repair_output" if os.path.isdir("repair_output") else "."
    repaired_files = [
        os.path.join(repair_dir, f)
        for f in os.listdir(repair_dir)
        if f.startswith("repaired_school_updates_") and f.endswith(".json")
    ]
    if not repaired_files:
        print("No repaired JSON files found")
        return False

    # Sort by modification time (newest first)
    repaired_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    latest_file = repaired_files[0]

    # Update the database
    print(f"Updating database with {latest_file}...")
    subprocess.run(["python", "src/update_db_schools.py", latest_file])

    # View the enriched data
    print("Viewing enriched data...")
    subprocess.run(["python", "src/view_enriched_schools.py"])

    return True

def view_processed_schools():
    """View all processed schools"""
    print("Viewing all processed schools...")
    subprocess.run(["python", "src/extract_school_data.py", "--view-processed"])

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Batch process schools")
    parser.add_argument("--batch_size", type=int, default=5, help="Number of schools to process in each batch")
    parser.add_argument("--timeout", type=int, default=180, help="Timeout in seconds for crew execution")
    parser.add_argument("--batches", type=int, default=1, help="Number of batches to process")
    parser.add_argument("--view-processed", action="store_true", help="View all processed schools")
    args = parser.parse_args()

    if args.view_processed:
        view_processed_schools()
        exit(0)

    for i in range(args.batches):
        print(f"\n{'=' * 80}")
        print(f"BATCH {i+1} of {args.batches}")
        print(f"{'=' * 80}\n")

        success = run_batch(batch_size=args.batch_size, timeout=args.timeout)

        if not success:
            print(f"Batch {i+1} failed, stopping")
            break

        if i < args.batches - 1:
            print(f"Waiting 10 seconds before next batch...")
            time.sleep(10)

    print("\nBatch processing complete")
