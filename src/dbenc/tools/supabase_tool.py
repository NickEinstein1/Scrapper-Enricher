from langchain.tools import BaseTool
from supabase import create_client, Client
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import os
import logging
import uuid
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class School(BaseModel):
    school_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    school_name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    zip: Optional[int] = None
    school_type: str = Field(default="Unknown")
    total_student_enrollment: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    source: Optional[str] = None

class SupabaseTool(BaseTool):
    name: str = "supabase_tool"
    description: str = "Interact with Supabase school database"

    model_config = {"arbitrary_types_allowed": True}
    client: Client = None

    def __init__(self):
        super().__init__()
        if not self.client:
            self.client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_ANON_KEY"))
            logger.info("Connected to Supabase")

    def _run(self, *args, **kwargs) -> Dict[str, Any]:
        """Run the tool with the specified action

        This method handles both positional and keyword arguments to be compatible
        with different versions of CrewAI.
        """
        # Handle both positional and keyword arguments
        action = "test"

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

        logger.info(f"Running SupabaseTool with action: {action}, kwargs: {kwargs}")

        try:
            # Handle different input formats
            if not isinstance(kwargs, dict):
                try:
                    # Try to parse as JSON
                    kwargs = json.loads(kwargs)
                except:
                    # If parsing fails, log the error and continue with empty dict
                    logger.error(f"Failed to parse kwargs as JSON: {kwargs}")
                    kwargs = {}

            if action == "test":
                return self.test_connection()
            elif action == "initialize":
                return self.initialize_database()
            elif action == "get_schools":
                limit = kwargs.get("limit", 5)
                return {"schools": self.get_schools_needing_enrichment(limit=limit)}
            elif action == "update_school":
                # Log the raw input for debugging
                logger.info(f"Raw update_school input: {kwargs}")

                # Log the raw kwargs for debugging
                logger.info(f"Raw kwargs for update_school: {kwargs}")

                # Extract school_id and data directly from kwargs
                school_id = kwargs.get("school_id")
                data = kwargs.get("data", {})

                logger.info(f"Extracted school_id: {school_id}")
                logger.info(f"Extracted data: {data}")

                # Handle case where data might be a string
                if isinstance(data, str):
                    try:
                        data = json.loads(data)
                        logger.info(f"Parsed data from string: {data}")
                    except Exception as e:
                        logger.error(f"Failed to parse data as JSON: {data}, Error: {str(e)}")
                        return {"error": f"Invalid data format: {data}"}

                if not school_id:
                    logger.error("school_id is required but was not provided")
                    logger.error(f"Received kwargs: {kwargs}")
                    return {"error": "school_id is required. Please provide a valid UUID in the 'school_id' field."}

                # Log the update attempt
                logger.info(f"Attempting to update school with ID: {school_id}")
                logger.info(f"Update data: {data}")

                return self.update_school(school_id, data)
            elif action == "get_all_schools":
                limit = kwargs.get("limit", 10)
                return {"schools": self.get_all_schools(limit=limit)}
            elif action == "query":
                table = kwargs.get("table", "schools")
                where = kwargs.get("where", {})
                limit = kwargs.get("limit", 10)
                return {"data": self.query_table(table, where, limit)}
            elif action == "help":
                return {
                    "available_actions": [
                        "test", "initialize", "get_schools", "update_school",
                        "get_all_schools", "query", "help"
                    ],
                    "description": "This tool interacts with the Supabase database to get and update school data.",
                    "parameters": {
                        "update_school": {
                            "school_id": "UUID of the school to update (required)",
                            "data": "Dictionary of fields to update (required)"
                        }
                    },
                    "example": "supabase_tool._run(action='update_school', school_id='uuid', data={'total_student_enrollment': 500})"
                }
            else:
                return {"error": f"Unknown action: {action}"}
        except Exception as e:
            logger.error(f"Error in SupabaseTool: {e}")
            return {"error": f"Error processing request: {str(e)}"}

    def initialize_database(self) -> Dict[str, Any]:
        result = self.client.table("schools").select("*").execute().data
        if result:
            return {"status": "Database already initialized", "school_count": len(result)}

        sample_schools = [
            {
                "school_id": str(uuid.uuid4()),
                "school_name": "Sample School",
                "address": "123 Main St",
                "city": "Sample City",
                "zip": 12345,
                "school_type": "Public"
            }
        ]
        self.client.table("schools").insert(sample_schools).execute()
        return {"status": "Database initialized", "school_count": 1}

    def get_schools_needing_enrichment(self, limit: int = 5) -> List[Dict[str, Any]]:
        # Get schools from the database
        schools = self.client.table("schools").select("*").limit(limit).execute().data
        logger.info(f"Retrieved {len(schools)} schools from the database")

        # For testing purposes, create a list of schools with missing fields
        required_fields = ["school_name", "address", "city", "zip", "total_student_enrollment", "latitude", "longitude"]
        result = []

        for school in schools:
            # Create a copy of the school with only the required fields
            school_data = {
                "school_id": school["school_id"],
                "school_name": school["school_name"],
                "address": school.get("address"),
                "city": school.get("city"),
                "zip": school.get("zip"),
                "total_student_enrollment": school.get("total_student_enrollment"),
                "latitude": school.get("latitude"),
                "longitude": school.get("longitude")
            }

            # Add missing fields
            missing_fields = [f for f in required_fields if school.get(f) is None]
            if not missing_fields:  # If no missing fields, create some for testing
                missing_fields = ["total_student_enrollment", "latitude", "longitude"]

            school_data["missing_fields"] = missing_fields
            result.append(school_data)

        logger.info(f"Returning {len(result)} schools with missing fields")
        return result

    def update_school(self, school_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a school in the database with robust data validation"""
        try:
            # Validate school_id format (basic UUID validation)
            if not school_id or not isinstance(school_id, str) or len(school_id) != 36:
                logger.error(f"Invalid school_id format: {school_id}")
                return {"error": f"Invalid school_id format: {school_id}"}

            # Validate data is not empty
            if not data or not isinstance(data, dict):
                logger.error(f"Invalid data format: {data}")
                return {"error": f"Invalid data format: {data}"}

            # Validate and clean data fields
            validated_data = {}
            validation_errors = []

            # Validate total_student_enrollment
            if "total_student_enrollment" in data:
                enrollment = data["total_student_enrollment"]
                try:
                    enrollment = int(enrollment)  # Convert to int if it's a string
                    if 10 <= enrollment <= 5000:
                        validated_data["total_student_enrollment"] = enrollment
                    else:
                        msg = f"Invalid total_student_enrollment: {enrollment} (must be between 10 and 5000)"
                        logger.warning(msg)
                        validation_errors.append(msg)
                except (ValueError, TypeError):
                    msg = f"Invalid total_student_enrollment: {enrollment} (must be an integer)"
                    logger.warning(msg)
                    validation_errors.append(msg)

            # Validate latitude
            if "latitude" in data:
                latitude = data["latitude"]
                try:
                    latitude = float(latitude)  # Convert to float if it's a string
                    if 24 <= latitude <= 50:  # Continental US
                        validated_data["latitude"] = latitude
                    else:
                        msg = f"Invalid latitude: {latitude} (must be between 24 and 50 for continental US)"
                        logger.warning(msg)
                        validation_errors.append(msg)
                except (ValueError, TypeError):
                    msg = f"Invalid latitude: {latitude} (must be a number)"
                    logger.warning(msg)
                    validation_errors.append(msg)

            # Validate longitude
            if "longitude" in data:
                longitude = data["longitude"]
                try:
                    longitude = float(longitude)  # Convert to float if it's a string
                    if -125 <= longitude <= -65:  # Continental US
                        validated_data["longitude"] = longitude
                    else:
                        msg = f"Invalid longitude: {longitude} (must be between -125 and -65 for continental US)"
                        logger.warning(msg)
                        validation_errors.append(msg)
                except (ValueError, TypeError):
                    msg = f"Invalid longitude: {longitude} (must be a number)"
                    logger.warning(msg)
                    validation_errors.append(msg)

            # Validate phone number format if present
            if "phone" in data:
                phone = data["phone"]
                import re
                # Check if it matches (XXX) XXX-XXXX format
                if isinstance(phone, str) and re.match(r'\(\d{3}\) \d{3}-\d{4}', phone):
                    validated_data["phone"] = phone
                else:
                    msg = f"Invalid phone format: {phone} (must be in format (XXX) XXX-XXXX)"
                    logger.warning(msg)
                    validation_errors.append(msg)

            # Copy other fields that don't need special validation
            for key, value in data.items():
                if key not in ["total_student_enrollment", "latitude", "longitude", "phone"] and key not in validated_data:
                    validated_data[key] = value

            # Check if we have any valid data to update
            if not validated_data:
                logger.error(f"No valid data to update for school {school_id}")
                return {"error": "No valid data to update", "validation_errors": validation_errors}

            # Log the update attempt with validated data
            logger.info(f"Updating school {school_id} with validated data: {validated_data}")

            # Update the school with validated data
            result = self.client.table("schools").update(validated_data).eq("school_id", school_id).execute()

            # Log the result
            logger.info(f"Update result: {result.data}")

            response = {
                "status": "success",
                "data": result.data,
                "message": f"School {school_id} updated successfully"
            }

            # Include validation warnings if any
            if validation_errors:
                response["validation_warnings"] = validation_errors
                response["message"] += f" with {len(validation_errors)} validation warnings"

            return response
        except Exception as e:
            logger.error(f"Error updating school {school_id}: {str(e)}")
            return {"error": str(e), "school_id": school_id}

    def get_all_schools(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self.client.table("schools").select("*").limit(limit).execute().data

    def query_table(self, table: str, where: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]:
        """Query a table with filters"""
        try:
            query = self.client.table(table).select("*")

            # Apply filters
            for key, value in where.items():
                if value == "None" or value is None:
                    # Filter for NULL values
                    query = query.is_(key, None)
                else:
                    # Filter for specific values
                    query = query.eq(key, value)

            # Apply limit
            query = query.limit(limit)

            # Execute query
            result = query.execute()
            return result.data
        except Exception as e:
            logger.error(f"Error querying table {table}: {e}")
            return []

    def test_connection(self) -> Dict[str, Any]:
        result = self.client.table("schools").select("*").limit(1).execute().data
        return {"status": "success", "data": result[0] if result else None}