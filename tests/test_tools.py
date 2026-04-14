import sys
import os
import json

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

# Import the tools
from src.dbenc.tools.scraping_tool import ScrapingTool
from src.dbenc.tools.geocoding_tool import GeocodingTool
from src.dbenc.tools.supabase_tool import SupabaseTool

def test_scraping_tool():
    print("\n=== Testing ScrapingTool ===")
    scraping_tool = ScrapingTool(mock_mode=True)

    # Test with dictionary input
    result1 = scraping_tool._run(action="scrape_private", school_name="Sacred Heart School", city="Morrilton", state="AR")
    print(f"Test 1 (dict input): {json.dumps(result1, indent=2)}")

    # Test with string input
    result2 = scraping_tool._run(action="scrape_private", **{"school_name": "St. Mary's Academy"})
    print(f"Test 2 (string param): {json.dumps(result2, indent=2)}")

    # Test with direct string input
    result3 = scraping_tool._run(action="scrape_public", school_name="Lincoln High School")
    print(f"Test 3 (direct string): {json.dumps(result3, indent=2)}")

def test_geocoding_tool():
    print("\n=== Testing GeocodingTool ===")
    geocoding_tool = GeocodingTool(mock_mode=True)

    # Test with dictionary input
    result1 = geocoding_tool._run(action="geocode", location="123 Main St, Austin, TX 78701")
    print(f"Test 1 (location string): {json.dumps(result1, indent=2)}")

    # Test with address components
    result2 = geocoding_tool._run(action="geocode", address="456 Oak Ave", city="San Francisco", state="CA", zip_code="94102")
    print(f"Test 2 (address components): {json.dumps(result2, indent=2)}")

    # Test with direct string input
    result3 = geocoding_tool._run(action="geocode", location="789 Pine St, Seattle, WA 98101")
    print(f"Test 3 (direct string): {json.dumps(result3, indent=2)}")

def test_supabase_tool():
    print("\n=== Testing SupabaseTool ===")
    # Note: This will try to connect to the actual Supabase instance
    # We're just testing the input parsing, not the actual database operations
    try:
        supabase_tool = SupabaseTool()

        # Test help action
        result1 = supabase_tool._run(action="help")
        print(f"Test 1 (help): Available actions: {result1.get('available_actions')}")

        # Test update_school with dictionary input
        test_data = {
            "school_id": "123e4567-e89b-12d3-a456-426614174000",
            "data": {
                "total_student_enrollment": 500,
                "latitude": 30.123456,
                "longitude": -97.654321
            }
        }
        result2 = supabase_tool._run(action="update_school", **test_data)
        print(f"Test 2 (dict input): {result2}")

        # Test with direct input
        result3 = supabase_tool._run(action="update_school", school_id="123e4567-e89b-12d3-a456-426614174001", data={
            "total_student_enrollment": 750,
            "latitude": 40.123456,
            "longitude": -87.654321
        })
        print(f"Test 3 (direct input): {result3}")

    except Exception as e:
        print(f"Error testing SupabaseTool: {e}")
        print("This is expected if you don't have Supabase credentials set up.")

if __name__ == "__main__":
    test_scraping_tool()
    test_geocoding_tool()
    test_supabase_tool()
