import json
import os
from tabulate import tabulate
from dbenc.tools.supabase_tool import SupabaseTool

def get_schools_from_database(limit=10):
    """Get schools from the database"""
    try:
        # Create a Supabase tool
        supabase_tool = SupabaseTool()
        print("Connected to Supabase")
        
        # Get schools from the database
        result = supabase_tool._run(action="get_schools", limit=limit)
        schools = result.get("schools", [])
        
        print(f"Retrieved {len(schools)} schools from the database")
        return schools
    
    except Exception as e:
        print(f"Error getting schools from database: {e}")
        return []

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
        "latitude", 
        "longitude"
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
        print(f"School ID: {school.get('school_id', 'N/A')}")
        print(f"Address: {school.get('address', 'N/A')}, {school.get('city', 'N/A')}, {school.get('zip', 'N/A')}")
        print(f"Enrollment: {school.get('total_student_enrollment', 'N/A')} students")
        
        # Location information
        print("\nLOCATION INFORMATION:")
        print(f"Latitude: {school.get('latitude', 'N/A')}")
        print(f"Longitude: {school.get('longitude', 'N/A')}")

def main():
    # Get schools from the database
    limit = 10  # Number of schools to retrieve
    schools = get_schools_from_database(limit=limit)
    
    if not schools:
        print("No schools found in the database")
        return
    
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
