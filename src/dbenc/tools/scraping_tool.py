from langchain.tools import BaseTool
import requests
from bs4 import BeautifulSoup
import time
import random
import logging
import json
from typing import Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScrapingTool(BaseTool):
    name: str = "scraping_tool"
    description: str = "Scrape school data from review sites"

    model_config = {"arbitrary_types_allowed": True}
    session: requests.Session = None
    mock_mode: bool = False

    def __init__(self, mock_mode: bool = False):
        super().__init__()
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
        })
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

        logger.info(f"Running ScrapingTool with action: {action}, kwargs: {kwargs}")

        try:
            if action == "scrape_private":
                # Handle action_input parameter from CrewAI
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
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to parse action_input as JSON: {e}")
                    elif isinstance(action_input, dict):
                        # If action_input is already a dict, update kwargs
                        for key, value in action_input.items():
                            if key != "action":  # Skip the action key
                                kwargs[key] = value
                        logger.info(f"Used action_input as dict: {action_input}")

                # Extract parameters from kwargs
                logger.info(f"Extracting parameters from kwargs: {kwargs}")
                school_name = kwargs.get("school_name", "")
                city = kwargs.get("city", "")
                state = kwargs.get("state", "TX")
                logger.info(f"Extracted from kwargs: school_name={school_name}, city={city}, state={state}")

                # Validate inputs
                if not school_name:
                    logger.error("school_name is required but not provided")
                    return {"error": "school_name is required"}

                # Normalize inputs
                school_name = school_name.strip().upper()
                city = city.strip() if city else ""
                state = state.strip().upper() if state else "TX"

                # Validate state code
                if len(state) != 2:
                    logger.warning(f"State code '{state}' is not a valid 2-letter code, using it anyway")

                logger.info(f"Scraping private school: {school_name}, {city}, {state}")
                return self.scrape_private_school_review(school_name, city, state)

            elif action == "scrape_public":
                # Handle action_input parameter from CrewAI
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
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to parse action_input as JSON: {e}")
                    elif isinstance(action_input, dict):
                        # If action_input is already a dict, update kwargs
                        for key, value in action_input.items():
                            if key != "action":  # Skip the action key
                                kwargs[key] = value
                        logger.info(f"Used action_input as dict: {action_input}")

                # Extract parameters from kwargs
                logger.info(f"Extracting parameters from kwargs: {kwargs}")
                school_name = kwargs.get("school_name", "")
                city = kwargs.get("city", "")
                state = kwargs.get("state", "TX")
                logger.info(f"Extracted from kwargs: school_name={school_name}, city={city}, state={state}")

                # Validate inputs
                if not school_name:
                    logger.error("school_name is required but not provided")
                    return {"error": "school_name is required"}

                # Normalize inputs
                school_name = school_name.strip().upper()
                city = city.strip() if city else ""
                state = state.strip().upper() if state else "TX"

                # Validate state code
                if len(state) != 2:
                    logger.warning(f"State code '{state}' is not a valid 2-letter code, using it anyway")

                logger.info(f"Scraping public school: {school_name}, {city}, {state}")
                return self.scrape_public_school_review(school_name, city, state)

            elif action == "help":
                return {
                    "available_actions": ["scrape_private", "scrape_public", "help"],
                    "description": "This tool scrapes school data from PrivateSchoolReview and PublicSchoolReview websites.",
                    "parameters": {
                        "scrape_private": {
                            "school_name": "Name of the school (required)",
                            "city": "City where the school is located",
                            "state": "State where the school is located (default: TX)"
                        },
                        "scrape_public": {
                            "school_name": "Name of the school (required)",
                            "city": "City where the school is located",
                            "state": "State where the school is located (default: TX)"
                        }
                    }
                }
            else:
                return {"error": f"Unknown action: {action}"}
        except Exception as e:
            logger.error(f"Error in ScrapingTool: {e}")
            return {"error": f"Error in ScrapingTool: {str(e)}"}

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _fetch_url(self, url: str) -> str:
        # Add a delay between requests to avoid rate limiting
        time.sleep(random.uniform(2, 5))

        # Update user agent for each request to avoid detection
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15"
        ]

        self.session.headers.update({
            "User-Agent": random.choice(user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.google.com/"
        })

        logger.info(f"Fetching URL: {url}")
        response = self.session.get(url, timeout=10)
        response.raise_for_status()
        return response.text

    def scrape_private_school_review(self, school_name: str, city: str = "", state: str = "TX") -> Dict[str, Any]:
        # Use mock data if in mock mode
        if self.mock_mode:
            logger.info(f"Using mock data for private school: {school_name}, {city}, {state}")
            mock_data = {
                "source": "privateschoolreview",
                "source_url": f"https://www.privateschoolreview.com/schools/{school_name.lower().replace(' ', '-')}",
                "school_name": school_name,
                "total_student_enrollment": 250,
                "address": "123 School St",
                "city": city or "Sample City",
                "state": state,
                "zip": "12345",
                "phone": "(555) 123-4567",
                "school_type": "REGULAR ELEMENTARY OR SECONDARY",
                "religious_orientation": "Christian",
                "days_in_school_year": 180
            }
            return {"status": "success", "data": mock_data}

        try:
            # Build search query
            query = school_name
            if city:
                query += f" {city}"
            if state:
                query += f" {state}"

            search_url = f"https://www.privateschoolreview.com/search-results?q={query.replace(' ', '+')}"
            logger.info(f"Searching PrivateSchoolReview: {search_url}")

            content = self._fetch_url(search_url)
            soup = BeautifulSoup(content, 'html.parser')

            # Find the first school result
            school_link = soup.select_one('a.school-name')
            if not school_link:
                return {"error": f"No results found for {query}"}

            school_url = f"https://www.privateschoolreview.com{school_link['href']}"
            logger.info(f"Found school: {school_url}")

            school_content = self._fetch_url(school_url)
            school_soup = BeautifulSoup(school_content, 'html.parser')

            # Extract data
            data = {"source": "privateschoolreview", "source_url": school_url}

            # School name
            name_elem = school_soup.select_one('h1.school-name')
            if name_elem:
                data["school_name"] = name_elem.text.strip()

            # Enrollment
            enrollment_elem = school_soup.select_one(".enrollment, .student-count, .students")
            if enrollment_elem:
                try:
                    data["total_student_enrollment"] = int(''.join(filter(str.isdigit, enrollment_elem.text)))
                except ValueError:
                    pass

            # Address
            address_elem = school_soup.select_one(".school-address, .address")
            if address_elem:
                data["address"] = address_elem.text.strip()

            # Phone
            phone_elem = school_soup.select_one('.phone')
            if phone_elem:
                data["phone"] = phone_elem.text.strip()

            # Religious orientation
            religious_elem = school_soup.select_one('.religious-orientation')
            if religious_elem:
                data["religious_orientation"] = religious_elem.text.strip()

            return {"status": "success", "data": data}
        except Exception as e:
            logger.error(f"Error scraping PrivateSchoolReview: {e}")
            return {"error": str(e)}

    def scrape_public_school_review(self, school_name: str, city: str = "", state: str = "TX") -> Dict[str, Any]:
        # Use mock data if in mock mode
        if self.mock_mode:
            logger.info(f"Using mock data for public school: {school_name}, {city}, {state}")
            mock_data = {
                "source": "publicschoolreview",
                "source_url": f"https://www.publicschoolreview.com/schools/{school_name.lower().replace(' ', '-')}",
                "school_name": school_name,
                "total_student_enrollment": 1200,
                "address": "456 Public School Ave",
                "city": city or "Sample City",
                "state": state,
                "zip": "12345",
                "phone": "(555) 987-6543",
                "school_type": "REGULAR ELEMENTARY OR SECONDARY",
                "days_in_school_year": 180
            }
            return {"status": "success", "data": mock_data}

        try:
            # Build search query
            query = school_name
            if city:
                query += f" {city}"
            if state:
                query += f" {state}"

            search_url = f"https://www.publicschoolreview.com/search-results?q={query.replace(' ', '+')}"
            logger.info(f"Searching PublicSchoolReview: {search_url}")

            content = self._fetch_url(search_url)
            soup = BeautifulSoup(content, 'html.parser')

            # Find the first school result
            school_link = soup.select_one('a.school-name, .school-listing a')
            if not school_link:
                return {"error": f"No results found for {query}"}

            school_url = f"https://www.publicschoolreview.com{school_link['href']}"
            logger.info(f"Found school: {school_url}")

            school_content = self._fetch_url(school_url)
            school_soup = BeautifulSoup(school_content, 'html.parser')

            # Extract data
            data = {"source": "publicschoolreview", "source_url": school_url}

            # School name
            name_elem = school_soup.select_one('h1.school-name')
            if name_elem:
                data["school_name"] = name_elem.text.strip()

            # Enrollment
            enrollment_elem = school_soup.select_one(".enrollment, .student-count, .students")
            if enrollment_elem:
                try:
                    data["total_student_enrollment"] = int(''.join(filter(str.isdigit, enrollment_elem.text)))
                except ValueError:
                    pass

            # Address
            address_elem = school_soup.select_one(".school-address, .address")
            if address_elem:
                data["address"] = address_elem.text.strip()

            # Phone
            phone_elem = school_soup.select_one('.phone')
            if phone_elem:
                data["phone"] = phone_elem.text.strip()

            return {"status": "success", "data": data}
        except Exception as e:
            logger.error(f"Error scraping PublicSchoolReview: {e}")
            return {"error": str(e)}