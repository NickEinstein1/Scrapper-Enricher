import logging
import json
from dbenc.tools.scraping_tool import ScrapingTool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_private_school_scraping(use_mock: bool = True):
    print("\n=== Testing Private School Scraping ===")
    tool = ScrapingTool(mock_mode=use_mock)

    # Test with a known private school
    school_name = "NORTHSIDE BAPTIST ACADEMY"
    city = "Nolanville"
    state = "TX"

    print(f"\nScraping private school: {school_name}, {city}, {state}")
    print(f"Using mock mode: {use_mock}")
    result = tool._run(
        action="scrape_private",
        school_name=school_name,
        city=city,
        state=state
    )
    print(json.dumps(result, indent=2))

def test_public_school_scraping(use_mock: bool = True):
    print("\n=== Testing Public School Scraping ===")
    tool = ScrapingTool(mock_mode=use_mock)

    # Test with a known public school
    school_name = "Austin High School"
    city = "Austin"
    state = "TX"

    print(f"\nScraping public school: {school_name}, {city}, {state}")
    print(f"Using mock mode: {use_mock}")
    result = tool._run(
        action="scrape_public",
        school_name=school_name,
        city=city,
        state=state
    )
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    try:
        # Use mock mode by default to avoid hitting the actual websites
        use_mock = True
        print(f"Starting tests with mock_mode={use_mock}")

        # To use real scraping, set use_mock to False
        # WARNING: This may be blocked by the websites
        # use_mock = False

        test_private_school_scraping(use_mock=use_mock)
        test_public_school_scraping(use_mock=use_mock)
        print("All tests completed successfully!")
    except Exception as e:
        logger.error(f"Error running tests: {e}")
        import traceback
        traceback.print_exc()
