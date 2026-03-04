from dbenc.tools.geocoding_tool import GeocodingTool
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    try:
        print("Creating GeocodingTool")
        geocoding_tool = GeocodingTool()
        print("GeocodingTool created successfully")
        
        # Test geocoding
        address = "1600 Pennsylvania Avenue, Washington DC"
        print(f"Geocoding address: {address}")
        result = geocoding_tool.geocode_location(address)
        print(f"Geocoding result: {result}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
