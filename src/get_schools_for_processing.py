import os
import json
import sqlite3
import logging
from datetime import datetime
from dotenv import load_dotenv
from dbenc.tools.supabase_tool import SupabaseTool

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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

def get_unprocessed_schools(batch_size=5):
    """Get schools from Supabase that haven't been processed yet"""
    # Initialize the database connection
    conn = init_processed_schools_db()
    
    # Initialize Supabase tool
    supabase_tool = SupabaseTool()
    
    # Get schools from Supabase
    result = supabase_tool._run(action="get_schools", limit=50)  # Get more than we need to filter
    
    if not result or 'schools' not in result:
        logger.error("Failed to get schools from Supabase")
        return []
    
    # Filter out schools that have already been processed
    unprocessed_schools = []
    for school in result['schools']:
        school_id = school.get('school_id')
        if school_id and not is_school_processed(conn, school_id):
            unprocessed_schools.append(school)
            if len(unprocessed_schools) >= batch_size:
                break
    
    logger.info(f"Found {len(unprocessed_schools)} unprocessed schools out of {len(result['schools'])} total schools")
    
    # Close the database connection
    conn.close()
    
    return unprocessed_schools

def save_schools_to_file(schools, output_file=None):
    """Save schools to a JSON file for processing"""
    if not output_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"schools_to_process_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(schools, f, indent=2)
    
    logger.info(f"Saved {len(schools)} schools to {output_file}")
    return output_file

def main(batch_size=5, output_file=None):
    """Main function to get unprocessed schools and save them to a file"""
    schools = get_unprocessed_schools(batch_size)
    
    if not schools:
        logger.warning("No unprocessed schools found")
        return None
    
    return save_schools_to_file(schools, output_file)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Get unprocessed schools from Supabase")
    parser.add_argument("--batch_size", type=int, default=5, help="Number of schools to get")
    parser.add_argument("--output_file", type=str, help="Output file path")
    args = parser.parse_args()
    
    main(args.batch_size, args.output_file)
