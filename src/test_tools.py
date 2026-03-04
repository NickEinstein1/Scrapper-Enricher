import logging
import json
from dotenv import load_dotenv
from dbenc.tools.supabase_tool import SupabaseTool
from dbenc.tools.scraping_tool import ScrapingTool
from dbenc.tools.geocoding_tool import GeocodingTool

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_supabase_tool():
    print("\n=== Testing SupabaseTool ===")
    tool = SupabaseTool()
    
    # Test help action
    print("\nTesting help action:")
    result = tool._run(action="help")
    print(json.dumps(result, indent=2))
    
    # Test get_schools action
    print("\nTesting get_schools action:")
    result = tool._run(action="get_schools", limit=2)
    print(f"Found {len(result['schools'])} schools")
    if result['schools']:
        print(f"First school: {json.dumps(result['schools'][0], indent=2)}")
    
    # Test query action
    print("\nTesting query action:")
    result = tool._run(action="query", table="schools", where={"city": "Austin"}, limit=2)
    print(f"Found {len(result['data'])} schools in Austin")
    if result['data']:
        print(f"First school in Austin: {json.dumps(result['data'][0], indent=2)}")

def test_scraping_tool():
    print("\n=== Testing ScrapingTool ===")
    tool = ScrapingTool()
    
    # Test help action
    print("\nTesting help action:")
    result = tool._run(action="help")
    print(json.dumps(result, indent=2))
    
    # Test scrape_private action
    print("\nTesting scrape_private action:")
    result = tool._run(
        action="scrape_private", 
        school_name="NORTHSIDE BAPTIST ACADEMY", 
        city="Nolanville", 
        state="TX"
    )
    print(json.dumps(result, indent=2))

def test_geocoding_tool():
    print("\n=== Testing GeocodingTool ===")
    tool = GeocodingTool()
    
    # Test help action
    print("\nTesting help action:")
    result = tool._run(action="help")
    print(json.dumps(result, indent=2))
    
    # Test geocode action with full location
    print("\nTesting geocode action with full location:")
    result = tool._run(action="geocode", location="1600 Pennsylvania Avenue, Washington DC")
    print(json.dumps(result, indent=2))
    
    # Test geocode action with components
    print("\nTesting geocode action with components:")
    result = tool._run(
        action="geocode", 
        address="1800 U.S. 190 Business", 
        city="Nolanville", 
        state="TX", 
        zip_code="76559"
    )
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    try:
        test_supabase_tool()
        test_scraping_tool()
        test_geocoding_tool()
    except Exception as e:
        logger.error(f"Error running tests: {e}")
