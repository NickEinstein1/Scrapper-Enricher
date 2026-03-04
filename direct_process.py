import os
import json
import sqlite3
from datetime import datetime

# Sample school data (replace with your actual data)
SAMPLE_SCHOOLS = [
    {
        "school_id": "a1b2c3d4-e5f6-4a5b-9c8d-7e6f5a4b3c2d",
        "school_name": "GRACE CHRISTIAN ACADEMY",
        "address": "123 Faith Avenue",
        "city": "Portland",
        "zip": 97201,
        "total_student_enrollment": 350,
        "latitude": 45.523064,
        "longitude": -122.676483
    },
    {
        "school_id": "b2c3d4e5-f6a7-5b6c-0d1e-8f7g6h5j4k3l",
        "school_name": "LINCOLN HIGH SCHOOL",
        "address": "456 Education Drive",
        "city": "Chicago",
        "zip": 60601,
        "total_student_enrollment": 1200,
        "latitude": 41.878113,
        "longitude": -87.629799
    },
    {
        "school_id": "c3d4e5f6-a7b8-6c7d-1e2f-9g8h7j6k5l4m",
        "school_name": "MONTESSORI LEARNING CENTER",
        "address": "789 Discovery Lane",
        "city": "Austin",
        "zip": 78701,
        "total_student_enrollment": 180,
        "latitude": 30.267153,
        "longitude": -97.743057
    },
    {
        "school_id": "d4e5f6a7-b8c9-7d8e-2f3g-0h1j2k3l4m5n",
        "school_name": "SUNSHINE ELEMENTARY",
        "address": "101 Bright Path",
        "city": "Miami",
        "zip": 33101,
        "total_student_enrollment": 420,
        "latitude": 25.761681,
        "longitude": -80.191788
    },
    {
        "school_id": "e5f6a7b8-c9d0-8e9f-3g4h-1j2k3l4m5n6p",
        "school_name": "WESTSIDE PREPARATORY SCHOOL",
        "address": "202 Scholar Street",
        "city": "Seattle",
        "zip": 98101,
        "total_student_enrollment": 550,
        "latitude": 47.606209,
        "longitude": -122.332069
    }
]

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

def process_schools(batch_size=5):
    """Process schools from sample data"""
    # Initialize the database connection
    conn = init_processed_schools_db()
    
    # Get schools from sample data
    all_schools = SAMPLE_SCHOOLS
    
    print(f"Found {len(all_schools)} schools in sample data")
    
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
    schools_file = f"schools_to_process_{timestamp}.json"
    
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
    repaired_file = f"repaired_school_updates_{timestamp}.json"
    with open(repaired_file, 'w') as f:
        json.dump(repaired_json, f, indent=2)
    
    print(f"Saved repaired JSON to {repaired_file}")
    print("\nAll schools processed successfully")
    
    return repaired_file

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Process schools directly")
    parser.add_argument("--batch_size", type=int, default=5, help="Number of schools to process")
    parser.add_argument("--view-processed", action="store_true", help="View all processed schools")
    args = parser.parse_args()
    
    if args.view_processed:
        view_processed_schools()
    else:
        process_schools(args.batch_size)
