import json
import os
import re
import sqlite3
from datetime import datetime

def init_processed_schools_db():
    """Initialize the database to track processed schools"""
    conn = sqlite3.connect('processed_schools.db')
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS processed_schools (
        school_id TEXT PRIMARY KEY,
        school_name TEXT,
        processed_date TEXT,
        batch_file TEXT
    )
    ''')

    conn.commit()
    return conn

def is_school_processed(conn, school_id):
    """Check if a school has already been processed"""
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM processed_schools WHERE school_id = ?', (school_id,))
    return cursor.fetchone() is not None

def mark_school_as_processed(conn, school_id, school_name, batch_file):
    """Mark a school as processed"""
    cursor = conn.cursor()
    processed_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute(
        'INSERT OR REPLACE INTO processed_schools (school_id, school_name, processed_date, batch_file) VALUES (?, ?, ?, ?)',
        (school_id, school_name, processed_date, batch_file)
    )
    conn.commit()

def find_latest_results_file():
    """Find the most recent results file"""
    result_files = [f for f in os.listdir() if f.startswith('results_') and f.endswith('.json')]
    if not result_files:
        return None

    # Sort by modification time (newest first)
    result_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return result_files[0]

def extract_school_data(input_file):
    """Extract school data from the results file"""
    # Initialize the database connection
    conn = init_processed_schools_db()

    # Load the results
    with open(input_file, 'r') as f:
        results = json.load(f)

    # Get the school data from the first batch
    schools = []
    skipped_schools = []

    print(f"Processing results from {input_file}")

    # Try to find school data in the results
    for batch in results.get("results", []):
        batch_result = batch.get("result", "")

        # Look for school IDs in the result
        school_ids = re.findall(r"'school_id':\s*'([^']+)'", batch_result)
        school_names = re.findall(r"'school_name':\s*'([^']+)'", batch_result)

        # If we found school IDs and names, create school objects
        if school_ids and school_names and len(school_ids) == len(school_names):
            for i in range(len(school_ids)):
                school_id = school_ids[i]
                school_name = school_names[i]

                # Check if this school has already been processed
                if is_school_processed(conn, school_id):
                    print(f"Skipping already processed school: {school_name} (ID: {school_id})")
                    skipped_schools.append({
                        "school_id": school_id,
                        "school_name": school_name
                    })
                    continue

                school = {
                    "school_id": school_id,
                    "school_name": school_name
                }

                # Look for other fields
                for field in ["address", "city", "zip", "total_student_enrollment", "latitude", "longitude"]:
                    pattern = f"'{field}':\\s*'?([^',}}]+)'?"
                    matches = re.findall(pattern, batch_result)
                    if matches and i < len(matches):
                        try:
                            # Try to convert to appropriate type
                            if field in ["zip", "total_student_enrollment"]:
                                school[field] = int(matches[i])
                            elif field in ["latitude", "longitude"]:
                                school[field] = float(matches[i])
                            else:
                                school[field] = matches[i]
                        except:
                            school[field] = matches[i]

                schools.append(school)

                # Mark this school as processed
                mark_school_as_processed(conn, school_id, school_name, input_file)

    # If we didn't find any schools, try to get them directly from Supabase
    if not schools:
        try:
            # Import here to avoid circular imports
            import sys
            sys.path.append('.')
            from src.get_schools_for_processing import get_unprocessed_schools

            print("No schools found in results file. Getting schools directly from Supabase...")
            unprocessed_schools = get_unprocessed_schools(batch_size=5)

            if unprocessed_schools:
                for school in unprocessed_schools:
                    school_id = school.get("school_id")
                    school_name = school.get("school_name")

                    if school_id and school_name:
                        schools.append(school)
                        # Mark this school as processed
                        mark_school_as_processed(conn, school_id, school_name, input_file)
                        print(f"Added school from Supabase: {school_name} (ID: {school_id})")
            else:
                print("No unprocessed schools found in Supabase.")
        except Exception as e:
            print(f"Error getting schools from Supabase: {e}")
            print("Falling back to empty schools list.")

    # Create the repaired JSON
    repaired_json = []
    for school in schools:
        repaired_json.append({
            "action": "update_school",
            "school_id": school.get("school_id"),
            "data": {
                "total_student_enrollment": school.get("total_student_enrollment"),
                "address": school.get("address"),
                "city": school.get("city"),
                "zip": school.get("zip"),
                "latitude": school.get("latitude"),
                "longitude": school.get("longitude")
            }
        })

    # Save the repaired JSON
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"repaired_school_updates_{timestamp}.json"

    with open(output_file, 'w') as f:
        json.dump(repaired_json, f, indent=2)

    print(f"Repaired school updates saved to {output_file}")

    # Print information about skipped schools
    if skipped_schools:
        print(f"\nSkipped {len(skipped_schools)} already processed schools:")
        for i, school in enumerate(skipped_schools, 1):
            print(f"  {i}. {school['school_name']} (ID: {school['school_id']})")

    return output_file

def view_processed_schools():
    """View all processed schools"""
    conn = init_processed_schools_db()
    cursor = conn.cursor()
    cursor.execute('SELECT school_id, school_name, processed_date, batch_file FROM processed_schools ORDER BY processed_date DESC')
    schools = cursor.fetchall()

    if not schools:
        print("No processed schools found in the database")
        return

    print(f"\nProcessed Schools ({len(schools)} total):")
    print("-" * 80)
    print(f"{'School ID':<40} {'School Name':<40} {'Processed Date':<20} {'Batch File':<30}")
    print("-" * 80)

    for school in schools:
        school_id, school_name, processed_date, batch_file = school
        print(f"{school_id:<40} {school_name[:38]:<40} {processed_date:<20} {os.path.basename(batch_file):<30}")

    conn.close()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Extract school data from results file')
    parser.add_argument('--view-processed', action='store_true', help='View all processed schools')
    args = parser.parse_args()

    if args.view_processed:
        view_processed_schools()
    else:
        # Find the latest results file
        latest_file = find_latest_results_file()
        if not latest_file:
            print("No results files found")
            exit(1)

        print(f"Extracting school data from {latest_file}")
        output_file = extract_school_data(latest_file)

        # Print the repaired JSON
        with open(output_file, 'r') as f:
            repaired_json = json.load(f)

        print(f"\nExtracted {len(repaired_json)} schools:")
        for i, school in enumerate(repaired_json, 1):
            print(f"\nSchool #{i}:")
            print(f"  School ID: {school['school_id']}")
            print(f"  Data: {json.dumps(school['data'], indent=2)}")
