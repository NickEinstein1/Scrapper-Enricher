#!/usr/bin/env python3
"""
Test script for the geocoding tool.
This script tests the geocoding tool with various input formats to ensure it works correctly.
"""

import sys
import os
import json
import logging

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join('logs', 'geocoding_test.log'))
    ]
)
logger = logging.getLogger(__name__)

# Import the geocoding tool
from src.dbenc.tools.geocoding_tool import GeocodingTool

def test_geocoding_with_full_address():
    """Test geocoding with a full address string"""
    logger.info("Testing geocoding with full address")
    
    geocoding_tool = GeocodingTool(mock_mode=False)
    
    # Test with a full address string
    address = "1600 Pennsylvania Avenue, Washington DC 20500"
    logger.info(f"Geocoding address: {address}")
    
    # Test using the _run method with action_input as a string
    result1 = geocoding_tool._run(
        action="geocode", 
        action_input=json.dumps({"location": address})
    )
    logger.info(f"Result with action_input as string: {json.dumps(result1, indent=2)}")
    
    # Test using the _run method with action_input as a dict
    result2 = geocoding_tool._run(
        action="geocode", 
        action_input={"location": address}
    )
    logger.info(f"Result with action_input as dict: {json.dumps(result2, indent=2)}")
    
    # Test using the geocode_location method directly
    result3 = geocoding_tool.geocode_location(address)
    logger.info(f"Result with direct method call: {json.dumps(result3, indent=2)}")
    
    return result1, result2, result3

def test_geocoding_with_components():
    """Test geocoding with address components"""
    logger.info("Testing geocoding with address components")
    
    geocoding_tool = GeocodingTool(mock_mode=False)
    
    # Test with address components
    address = "1600 Pennsylvania Avenue"
    city = "Washington"
    state = "DC"
    zip_code = "20500"
    
    logger.info(f"Geocoding components: address={address}, city={city}, state={state}, zip_code={zip_code}")
    
    # Test using the _run method with action_input as a string
    result1 = geocoding_tool._run(
        action="geocode", 
        action_input=json.dumps({
            "address": address,
            "city": city,
            "state": state,
            "zip_code": zip_code
        })
    )
    logger.info(f"Result with action_input as string: {json.dumps(result1, indent=2)}")
    
    # Test using the _run method with action_input as a dict
    result2 = geocoding_tool._run(
        action="geocode", 
        action_input={
            "address": address,
            "city": city,
            "state": state,
            "zip_code": zip_code
        }
    )
    logger.info(f"Result with action_input as dict: {json.dumps(result2, indent=2)}")
    
    return result1, result2

def test_geocoding_with_school_data():
    """Test geocoding with real school data"""
    logger.info("Testing geocoding with real school data")
    
    geocoding_tool = GeocodingTool(mock_mode=False)
    
    # Test with a real school
    school = {
        "school_id": "test-school-id",
        "school_name": "Test School",
        "address": "123 Main Street",
        "city": "Anytown",
        "state": "TX",
        "zip": 12345
    }
    
    logger.info(f"Geocoding school: {school['school_name']}")
    
    # Build the location string
    location = f"{school['address']}, {school['city']}, {school['state']} {school['zip']}"
    
    # Test using the _run method with action_input as a string
    result1 = geocoding_tool._run(
        action="geocode", 
        action_input=json.dumps({"location": location})
    )
    logger.info(f"Result with full location: {json.dumps(result1, indent=2)}")
    
    # Test using the _run method with components
    result2 = geocoding_tool._run(
        action="geocode", 
        action_input={
            "address": school['address'],
            "city": school['city'],
            "state": school['state'],
            "zip_code": str(school['zip'])
        }
    )
    logger.info(f"Result with components: {json.dumps(result2, indent=2)}")
    
    return result1, result2

def main():
    """Main function to run all tests"""
    logger.info("Starting geocoding tool tests")
    
    try:
        # Test with full address
        full_address_results = test_geocoding_with_full_address()
        logger.info("Full address test completed")
        
        # Test with components
        components_results = test_geocoding_with_components()
        logger.info("Components test completed")
        
        # Test with school data
        school_results = test_geocoding_with_school_data()
        logger.info("School data test completed")
        
        # Check if all tests were successful
        all_results = full_address_results + components_results + school_results
        success_count = sum(1 for result in all_results if result.get('status') == 'success')
        
        logger.info(f"Tests completed: {len(all_results)} tests, {success_count} successful")
        
        if success_count == len(all_results):
            logger.info("All tests passed!")
        else:
            logger.warning(f"{len(all_results) - success_count} tests failed")
            
    except Exception as e:
        logger.error(f"Error running tests: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()
