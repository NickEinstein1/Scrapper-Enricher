import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

def test_supabase_tool():
    try:
        from src.dbenc.tools.supabase_tool import SupabaseTool
        logger.info("Successfully imported SupabaseTool")
        
        # Create an instance of the tool
        tool = SupabaseTool()
        logger.info("Successfully created SupabaseTool instance")
        
        # Test connection
        logger.info("Testing connection...")
        result = tool.test_connection()
        logger.info(f"Connection test result: {result}")
        
        return True
    except Exception as e:
        logger.error(f"Error testing SupabaseTool: {e}")
        return False

def test_scraping_tool():
    try:
        from src.dbenc.tools.scraping_tool import ScrapingTool
        logger.info("Successfully imported ScrapingTool")
        
        # Create an instance of the tool with mock mode enabled
        tool = ScrapingTool(mock_mode=True)
        logger.info("Successfully created ScrapingTool instance in mock mode")
        
        # Test the help function
        logger.info("Testing help function...")
        result = tool._run(action="help")
        logger.info(f"Help function result: {result}")
        
        return True
    except Exception as e:
        logger.error(f"Error testing ScrapingTool: {e}")
        return False

def test_geocoding_tool():
    try:
        from src.dbenc.tools.geocoding_tool import GeocodingTool
        logger.info("Successfully imported GeocodingTool")
        
        # Create an instance of the tool with mock mode enabled
        tool = GeocodingTool(mock_mode=True)
        logger.info("Successfully created GeocodingTool instance in mock mode")
        
        # Test the help function
        logger.info("Testing help function...")
        result = tool._run(action="help")
        logger.info(f"Help function result: {result}")
        
        return True
    except Exception as e:
        logger.error(f"Error testing GeocodingTool: {e}")
        return False

def test_crew_initialization():
    try:
        from src.dbenc.crew import SchoolEnrichmentCrew
        logger.info("Successfully imported SchoolEnrichmentCrew")
        
        # Create an instance of the crew with mock mode enabled
        crew = SchoolEnrichmentCrew(use_mock=True, timeout=30)
        logger.info("Successfully created SchoolEnrichmentCrew instance")
        
        return True
    except Exception as e:
        logger.error(f"Error initializing SchoolEnrichmentCrew: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting component tests")
    
    # Test the components one by one
    supabase_test = test_supabase_tool()
    scraping_test = test_scraping_tool()
    geocoding_test = test_geocoding_tool()
    crew_test = test_crew_initialization()
    
    # Print summary
    logger.info("\nTest Summary:")
    logger.info(f"SupabaseTool: {'PASS' if supabase_test else 'FAIL'}")
    logger.info(f"ScrapingTool: {'PASS' if scraping_test else 'FAIL'}")
    logger.info(f"GeocodingTool: {'PASS' if geocoding_test else 'FAIL'}")
    logger.info(f"SchoolEnrichmentCrew: {'PASS' if crew_test else 'FAIL'}")
    
    if all([supabase_test, scraping_test, geocoding_test, crew_test]):
        logger.info("All components passed the tests!")
    else:
        logger.info("Some components failed the tests. See logs above for details.")
