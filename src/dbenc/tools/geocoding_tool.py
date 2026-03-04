from langchain.tools import BaseTool
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import logging
import json
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeocodingTool(BaseTool):
    name: str = "geocoding_tool"
    description: str = "Geocode school locations using geopy"

    model_config = {"arbitrary_types_allowed": True}
    geolocator: Nominatim = None
    geocode: RateLimiter = None

    mock_mode: bool = False

    def __init__(self, mock_mode: bool = False):
        super().__init__()
        self.geolocator = Nominatim(user_agent="school_enricher")
        self.geocode = RateLimiter(self.geolocator.geocode, min_delay_seconds=1)
        self.mock_mode = mock_mode

    def _run(self, *args, **kwargs) -> Dict[str, Any]:
        """Run the tool with the specified action

        This method handles both positional and keyword arguments to be compatible
        with different versions of CrewAI.
        """
        # Handle both positional and keyword arguments
        action = "help"

        # Case 1: Called with positional arguments (CrewAI 0.28.0)
        if args and isinstance(args[0], str):
            action_input = args[0]
            try:
                # Try to parse as JSON
                parsed_input = json.loads(action_input)
                if isinstance(parsed_input, dict) and "action" in parsed_input:
                    action = parsed_input.pop("action")
                    # Add the rest to kwargs
                    kwargs.update(parsed_input)
                else:
                    # If not a dict with action, use as action
                    action = action_input
            except (json.JSONDecodeError, TypeError):
                # If not valid JSON, use as action
                action = action_input

        # Case 2: Called with action keyword (original implementation)
        elif "action" in kwargs:
            action = kwargs.pop("action")

        logger.info(f"Running GeocodingTool with action: {action}, kwargs: {kwargs}")

        if action == "geocode":
            # Handle different input formats
            try:
                # Check if action_input is provided and parse it
                action_input = kwargs.get("action_input", None)
                if action_input:
                    logger.info(f"Found action_input: {action_input}")
                    if isinstance(action_input, str):
                        try:
                            # Try to parse action_input as JSON
                            parsed_input = json.loads(action_input)
                            if isinstance(parsed_input, dict):
                                # Update kwargs with parsed input
                                for key, value in parsed_input.items():
                                    if key != "action":  # Skip the action key
                                        kwargs[key] = value
                                logger.info(f"Successfully parsed action_input as JSON: {parsed_input}")
                        except json.JSONDecodeError:
                            # If parsing fails, assume it's a location string
                            logger.info(f"Using action_input as location string: {action_input}")
                            return self.geocode_location(action_input)
                    elif isinstance(action_input, dict):
                        # If action_input is already a dict, update kwargs
                        for key, value in action_input.items():
                            if key != "action":  # Skip the action key
                                kwargs[key] = value
                        logger.info(f"Used action_input as dict: {action_input}")

                # If kwargs is a string, try to parse it as JSON
                if not isinstance(kwargs, dict):
                    try:
                        kwargs = json.loads(kwargs)
                    except:
                        # If parsing fails, assume it's a location string
                        return self.geocode_location(str(kwargs))

                # Extract parameters directly from kwargs
                # Log the raw kwargs for debugging
                logger.info(f"Raw kwargs for geocoding: {kwargs}")

                location = kwargs.get("location", "")
                address = kwargs.get("address", "")
                city = kwargs.get("city", "")
                state = kwargs.get("state", "")
                zip_code = kwargs.get("zip_code", "")

                # Log the extracted parameters
                logger.info(f"Geocoding parameters: location='{location}', address='{address}', city='{city}', state='{state}', zip_code='{zip_code}'")

                # If a full location string is provided, use that
                if location:
                    logger.info(f"Using full location string: {location}")
                    return self.geocode_location(location)

                # Otherwise, build a location string from components
                elif address or city:
                    # Build the most complete location string possible with available components
                    components = []
                    if address:
                        components.append(address)
                    if city:
                        components.append(city)
                    if state:
                        components.append(state)
                    if zip_code:
                        components.append(str(zip_code))

                    full_location = ", ".join(components)
                    logger.info(f"Built location string from components: {full_location}")
                    return self.geocode_location(full_location)

                # Try to use any available information
                elif kwargs.get("school_name", ""):
                    school_name = kwargs.get("school_name", "")
                    logger.info(f"Using school name as fallback: {school_name}")
                    return self.geocode_location(school_name)
                else:
                    logger.error("Insufficient location information provided")
                    return {"error": "Either location, address, city, or school_name is required"}
            except Exception as e:
                logger.error(f"Error processing geocoding input: {e}")
                return {"error": f"Invalid input format: {str(e)}"}

        elif action == "help":
            return {
                "available_actions": ["geocode", "help"],
                "description": "This tool geocodes locations using geopy (not Google API).",
                "parameters": {
                    "geocode": {
                        "location": "Full location string to geocode",
                        "address": "Street address (alternative to location)",
                        "city": "City (required if using address)",
                        "state": "State (default: TX)",
                        "zip_code": "ZIP code"
                    }
                }
            }
        else:
            return {"error": f"Unknown action: {action}"}

    def geocode_location(self, location: str) -> Dict[str, Any]:
        # Validate input
        if not location or not isinstance(location, str) or len(location.strip()) == 0:
            logger.error(f"Invalid location string: {location}")
            return {"status": "error", "error": "Invalid or empty location string"}

        # Clean up the location string
        location = location.strip()
        logger.info(f"Geocoding location: {location}")

        # Use mock data if in mock mode
        if self.mock_mode:
            logger.info(f"Using mock data for geocoding: {location}")
            # Generate deterministic but realistic coordinates based on the location string
            import hashlib
            hash_obj = hashlib.md5(location.encode())
            hash_hex = hash_obj.hexdigest()
            # Use the hash to generate latitude between 25 and 49 (continental US)
            lat_base = int(hash_hex[:8], 16) % 2400 / 100 + 25
            # Use the hash to generate longitude between -65 and -125 (continental US)
            lng_base = int(hash_hex[8:16], 16) % 6000 / 100 - 125

            return {
                "status": "success",
                "data": {
                    "latitude": round(lat_base, 6),
                    "longitude": round(lng_base, 6)
                }
            }

        # Implement retry logic
        max_retries = 3
        retry_count = 0
        last_error = None

        while retry_count < max_retries:
            try:
                logger.info(f"Geocoding attempt {retry_count + 1} for: {location}")
                location_data = self.geocode(location)

                if location_data:
                    logger.info(f"Successfully geocoded: {location} -> ({location_data.latitude}, {location_data.longitude})")
                    return {
                        "status": "success",
                        "data": {
                            "latitude": location_data.latitude,
                            "longitude": location_data.longitude
                        }
                    }

                # If we get here, location was not found
                retry_count += 1
                last_error = "Location not found"
                logger.warning(f"Location not found: {location} (attempt {retry_count}/{max_retries})")

                # Try with a simplified location string on subsequent attempts
                if retry_count < max_retries:
                    # Remove any zip codes or specific address details
                    parts = location.split(",")
                    if len(parts) > 2:
                        # Keep only city and state
                        location = ", ".join(parts[-2:]).strip()
                        logger.info(f"Simplified location for retry: {location}")

            except Exception as e:
                retry_count += 1
                last_error = str(e)
                logger.error(f"Error geocoding {location}: {e} (attempt {retry_count}/{max_retries})")

                if retry_count < max_retries:
                    # Wait before retrying
                    import time
                    time.sleep(1)

        # If we get here, all retries failed
        logger.error(f"All geocoding attempts failed for: {location}")
        return {"status": "error", "error": last_error or "Unknown geocoding error"}