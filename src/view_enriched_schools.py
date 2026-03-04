import json
import os
import glob
import sys
from tabulate import tabulate
from dotenv import load_dotenv

# Add the current directory to the Python path
sys.path.append('.')

# Load environment variables
load_dotenv()

def find_latest_results_file(mock=True):
    """Find the most recent results file"""
    pattern = "mock_results_*.json" if mock else "results_*.json"
    result_files = glob.glob(pattern)
    if not result_files:
        return None

    # Sort by modification time (newest first)
    result_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return result_files[0]

def load_results(file_path):
    """Load results from a JSON file"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading results file: {e}")
        return None

def extract_schools(results):
    """Extract school data from results"""
    schools = []

    if not results or "results" not in results:
        print("No results found or invalid results format")
        return schools

    for batch_result in results["results"]:
        if "task_outputs" in batch_result and batch_result["task_outputs"]:
            for task_output in batch_result["task_outputs"]:
                if isinstance(task_output, str):
                    try:
                        task_data = json.loads(task_output)
                        if isinstance(task_data, dict) and "data" in task_data:
                            schools.append(task_data["data"])
                    except:
                        pass

    return schools

def display_schools_table(schools):
    """Display schools in a table format"""
    if not schools:
        print("No schools found")
        return

    # Define the fields to display
    fields = [
        "school_name",
        "address",
        "city",
        "zip",
        "total_student_enrollment",
        "phone",
        "religious_orientation",
        "source"
    ]

    # Prepare the table data
    table_data = []
    for school in schools:
        row = []
        for field in fields:
            row.append(school.get(field, "N/A"))
        table_data.append(row)

    # Display the table
    print(tabulate(table_data, headers=fields, tablefmt="grid"))

def display_school_details(schools):
    """Display detailed information for each school"""
    if not schools:
        print("No schools found")
        return

    for i, school in enumerate(schools, 1):
        print(f"\n{'=' * 80}")
        print(f"SCHOOL #{i}: {school.get('school_name', 'Unknown')}")
        print(f"{'=' * 80}")

        # Basic information
        print("\nBASIC INFORMATION:")
        print(f"Address: {school.get('address', 'N/A')}, {school.get('city', 'N/A')}, {school.get('zip', 'N/A')}")
        print(f"Phone: {school.get('phone', 'N/A')}")
        print(f"Enrollment: {school.get('total_student_enrollment', 'N/A')} students")

        # School type information
        print("\nSCHOOL TYPE INFORMATION:")
        print(f"Source: {school.get('source', 'N/A')}")
        if "religious_orientation" in school:
            print(f"Religious Orientation: {school.get('religious_orientation', 'N/A')}")
        if "school_district" in school:
            print(f"School District: {school.get('school_district', 'N/A')}")
        if "school_type" in school:
            print(f"School Type: {school.get('school_type', 'N/A')}")

        # Additional information
        print("\nADDITIONAL INFORMATION:")
        if "student_teacher_ratio" in school:
            print(f"Student-Teacher Ratio: {school.get('student_teacher_ratio', 'N/A')}")
        if "tuition" in school:
            print(f"Tuition: {school.get('tuition', 'N/A')}")
        if "state_rank" in school:
            print(f"State Rank: {school.get('state_rank', 'N/A')}")
        if "free_lunch_eligible" in school:
            print(f"Free Lunch Eligible: {school.get('free_lunch_eligible', 'N/A')}")

        # Location information
        print("\nLOCATION INFORMATION:")
        print(f"Latitude: {school.get('latitude', 'N/A')}")
        print(f"Longitude: {school.get('longitude', 'N/A')}")
        if "geocoded_address" in school:
            print(f"Geocoded Address: {school.get('geocoded_address', 'N/A')}")

        # Enrichment information
        print("\nENRICHMENT INFORMATION:")
        print(f"Enrichment Status: {school.get('enrichment_status', 'N/A')}")
        print(f"Enriched At: {school.get('enriched_at', 'N/A')}")
        if "source_url" in school:
            print(f"Source URL: {school.get('source_url', 'N/A')}")

def get_enriched_schools_from_supabase(limit=10):
    """Get enriched schools directly from Supabase"""
    try:
        import requests
        import os

        # Get Supabase credentials from environment variables
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY")

        if not SUPABASE_URL or not SUPABASE_KEY:
            print("Supabase credentials not found in environment variables")
            return []

        # Set up the request headers
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json"
        }

        # Query for schools that have been enriched (have latitude and longitude)
        url = f"{SUPABASE_URL}/rest/v1/schools?select=*&limit={limit}"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            schools = response.json()
            return schools
        else:
            print(f"Error fetching schools from Supabase: {response.text}")
            return []
    except Exception as e:
        print(f"Error in get_enriched_schools_from_supabase: {e}")
        return []

def main():
    # Try to get schools from Supabase first
    print("Fetching enriched schools from Supabase...")
    schools_from_supabase = get_enriched_schools_from_supabase(limit=20)

    if schools_from_supabase:
        print(f"\nFound {len(schools_from_supabase)} enriched schools in Supabase")

        # Display schools in a table format
        print("\nSCHOOLS SUMMARY:")
        display_schools_table(schools_from_supabase)

        # Display detailed information for each school
        print("\nDETAILED SCHOOL INFORMATION:")
        display_school_details(schools_from_supabase)
        return

    # If no schools from Supabase, try to find the latest results file
    use_mock = False  # Set to True to use mock results, False to use real results
    latest_file = find_latest_results_file(mock=use_mock)
    if not latest_file:
        print(f"No {'mock ' if use_mock else ''}results files found")
        return

    print(f"Loading results from: {latest_file}")

    # Load the results
    results = load_results(latest_file)
    if not results:
        return

    # Extract and display the schools
    schools = extract_schools(results)
    print(f"\nFound {len(schools)} schools")

    # Display schools in a table format
    print("\nSCHOOLS SUMMARY:")
    display_schools_table(schools)

    # Display detailed information for each school
    print("\nDETAILED SCHOOL INFORMATION:")
    display_school_details(schools)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        # Install tabulate if not available
        print("If you're missing the tabulate package, install it with: pip install tabulate")
