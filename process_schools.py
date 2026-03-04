import os
import sys
import json
import sqlite3
import subprocess
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
    """Get schools directly from Supabase"""
    # Create a temporary script to get schools
    temp_script = """
import os
import json
import sys
from dotenv import load_dotenv
from dbenc.tools.supabase_tool import SupabaseTool

# Load environment variables
load_dotenv()

# Get batch size from command line
batch_size = int(sys.argv[1]) if len(sys.argv) > 1 else 5

# Initialize Supabase tool
supabase_tool = SupabaseTool()

# Get schools from Supabase
result = supabase_tool._run(action="get_schools", limit=50)

if not result or 'schools' not in result:
    print(json.dumps({"error": "Failed to get schools from Supabase"}))
    sys.exit(1)

# Get the first batch_size schools
schools = result['schools'][:batch_size]

# Print the schools as JSON
print(json.dumps(schools))
"""
    
    # Save the temporary script
    with open('get_schools_temp.py', 'w') as f:
        f.write(temp_script)
    
    # Run the script
    try:
        result = subprocess.run(
            ["python", "get_schools_temp.py", str(batch_size)],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse the JSON output
        schools = json.loads(result.stdout)
        return schools
    except subprocess.CalledProcessError as e:
        print(f"Error getting schools from Supabase: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        # Clean up the temporary script
        if os.path.exists('get_schools_temp.py'):
            os.remove('get_schools_temp.py')

def process_schools(batch_size=5):
    """Process schools from Supabase"""
    # Initialize the database connection
    conn = init_processed_schools_db()
    
    # Get schools from Supabase
    print(f"Getting schools from Supabase (batch size: {batch_size})...")
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
    
    # Save the unprocessed schools to a file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    schools_file = f"schools_to_process_{timestamp}.json"
    
    with open(schools_file, 'w') as f:
        json.dump(unprocessed_schools, f, indent=2)
    
    print(f"Saved {len(unprocessed_schools)} schools to {schools_file}")
    
    # Process each school
    for school in unprocessed_schools:
        school_id = school.get('school_id')
        school_name = school.get('school_name')
        
        if not school_id or not school_name:
            continue
        
        print(f"\nProcessing school: {school_name} (ID: {school_id})")
        
        # Create a JSON file for this school
        school_file = f"school_{school_id}_{timestamp}.json"
        with open(school_file, 'w') as f:
            json.dump([school], f, indent=2)
        
        # Mark this school as processed
        mark_school_as_processed(conn, school_id, school_name, school_file)
        
        # TODO: Add code to process the school using your existing tools
        # For now, we'll just print a message
        print(f"School {school_name} marked as processed")
    
    print("\nAll schools processed successfully")

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
