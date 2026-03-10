import os
import sys
import json
import sqlite3
import importlib.util
from datetime import datetime

# Add the current directory to the Python path
sys.path.append('.')

# Function to dynamically import the SupabaseTool
def import_supabase_tool():
    try:
        # Try to import directly
        from src.dbenc.tools.supabase_tool import SupabaseTool
        return SupabaseTool
    except ImportError:
        try:
            # Try to import using spec
            spec = importlib.util.spec_from_file_location(
                "supabase_tool",
                os.path.join("src", "dbenc", "tools", "supabase_tool.py")
            )
            if spec is None:
                raise ImportError("Could not find supabase_tool.py")

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module.SupabaseTool
        except Exception as e:
            print(f"Error importing SupabaseTool: {e}")
            return None

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

def get_schools_from_supabase(batch_size=5):
    """Get schools from Supabase"""
    # Import the SupabaseTool
    SupabaseTool = import_supabase_tool()

    if SupabaseTool is None:
        print("Failed to import SupabaseTool. Using sample data instead.")
        # Return sample data as fallback
        return [
            {
                "school_id": "sample1-uuid-1234-5678-90abcdef",
                "school_name": "SAMPLE SCHOOL 1",
                "address": "123 Sample St",
                "city": "Sample City",
                "zip": 12345,
                "total_student_enrollment": 500
            },
            {
                "school_id": "sample2-uuid-1234-5678-90abcdef",
                "school_name": "SAMPLE SCHOOL 2",
                "address": "456 Sample Ave",
                "city": "Sample Town",
                "zip": 67890,
                "total_student_enrollment": 750
            }
        ]

    try:
        # Initialize the Supabase tool
        supabase_tool = SupabaseTool()

        # Get schools from Supabase
        print("Getting schools from Supabase...")
        result = supabase_tool._run(action="get_schools", limit=50)

        if not result or 'schools' not in result:
            print("Failed to get schools from Supabase")
            return []

        schools = result['schools']
        print(f"Retrieved {len(schools)} schools from Supabase")
        return schools

    except Exception as e:
        print(f"Error getting schools from Supabase: {e}")
        return []

def process_schools(batch_size=5):
    """Process schools from Supabase"""
    # Initialize the database connection
    conn = init_processed_schools_db()

    # Get schools from Supabase
    all_schools = get_schools_from_supabase(batch_size)

    if not all_schools:
        print("No schools found in Supabase")
        return

    print(f"Found {len(all_schools)} schools")

    # Filter out schools that have already been processed
    unprocessed_schools = []
    for school in all_schools:
        school_id = school.get('school_id')
        if school_id and not is_school_processed(conn, school_id):
            unprocessed_schools.append(school)

    print(f"Found {len(unprocessed_schools)} unprocessed schools")

    if not unprocessed_schools:
        print("No unprocessed schools found")
        return

    # Limit to batch size
    unprocessed_schools = unprocessed_schools[:batch_size]

    # Save the unprocessed schools to a file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    os.makedirs("school_output", exist_ok=True)
    schools_file = os.path.join("school_output", f"schools_to_process_{timestamp}.json")

    with open(schools_file, 'w') as f:
        json.dump(unprocessed_schools, f, indent=2)

    print(f"Saved {len(unprocessed_schools)} schools to {schools_file}")

    # Create the repaired JSON format
    repaired_json = []
    for school in unprocessed_schools:
        school_id = school.get('school_id')
        school_name = school.get('school_name')

        if not school_id or not school_name:
            continue

        # Create a data object with the school fields
        data = {k: v for k, v in school.items() if k != 'school_id'}

        # Add to repaired JSON
        repaired_json.append({
            "school_id": school_id,
            "data": data
        })

        # Mark this school as processed
        mark_school_as_processed(conn, school_id, school_name, schools_file)

        print(f"School {school_name} marked as processed")

    # Save the repaired JSON
    os.makedirs("repair_output", exist_ok=True)
    repaired_file = os.path.join("repair_output", f"repaired_school_updates_{timestamp}.json")
    with open(repaired_file, 'w') as f:
        json.dump(repaired_json, f, indent=2)

    print(f"Saved repaired JSON to {repaired_file}")
    print("\nAll schools processed successfully")

    return repaired_file

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Process schools from Supabase")
    parser.add_argument("--batch_size", type=int, default=5, help="Number of schools to process")
    parser.add_argument("--view-processed", action="store_true", help="View all processed schools")
    args = parser.parse_args()

    if args.view_processed:
        view_processed_schools()
    else:
        process_schools(args.batch_size)
