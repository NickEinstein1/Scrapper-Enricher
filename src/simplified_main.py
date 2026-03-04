import os
from dotenv import load_dotenv
import json
from supabase import create_client, Client
import requests
from bs4 import BeautifulSoup
import time
import random
import logging
from typing import Dict, Any, List
import uuid
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class SupabaseHelper:
    """Helper class for Supabase operations"""
    
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL or SUPABASE_ANON_KEY environment variables are not set")
        
        self.client = create_client(self.supabase_url, self.supabase_key)
    
    def get_schools_needing_enrichment(self, limit=10):
        """Get schools that need enrichment"""
        try:
            result = self.client.table("schools").select("*").limit(limit).execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting schools: {e}")
            return []
    
    def update_school(self, school_id, data):
        """Update a school with enriched data"""
        try:
            result = self.client.table("schools").update(data).eq("school_id", school_id).execute()
            return result.data
        except Exception as e:
            logger.error(f"Error updating school: {e}")
            return None

class ScrapingHelper:
    """Helper class for web scraping"""
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    
    def scrape_school_info(self, school_name, city, state="TX"):
        """Scrape information about a school"""
        try:
            # Format the search query
            query = f"{school_name} {city} {state}"
            search_url = f"https://www.privateschoolreview.com/search-results?q={query.replace(' ', '+')}"
            
            # Get the search results page
            response = requests.get(search_url, headers=self.headers)
            if response.status_code != 200:
                logger.warning(f"Failed to get search results for {query}: {response.status_code}")
                return {}
            
            # Parse the search results
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the first search result
            result = soup.select_one('.school-listing')
            if not result:
                logger.warning(f"No search results found for {query}")
                return {}
            
            # Get the link to the school page
            link = result.select_one('a.school-name')
            if not link:
                logger.warning(f"No link found in search result for {query}")
                return {}
            
            school_url = "https://www.privateschoolreview.com" + link['href']
            
            # Get the school page
            response = requests.get(school_url, headers=self.headers)
            if response.status_code != 200:
                logger.warning(f"Failed to get school page for {query}: {response.status_code}")
                return {}
            
            # Parse the school page
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract information
            info = {}
            
            # Get the school name
            name_elem = soup.select_one('h1.school-name')
            if name_elem:
                info['school_name'] = name_elem.text.strip()
            
            # Get the address
            address_elem = soup.select_one('.address')
            if address_elem:
                info['address'] = address_elem.text.strip()
            
            # Get the phone number
            phone_elem = soup.select_one('.phone')
            if phone_elem:
                info['phone'] = phone_elem.text.strip()
            
            # Get the religious orientation
            religious_elem = soup.select_one('.religious-orientation')
            if religious_elem:
                info['religious_orientation'] = religious_elem.text.strip()
            
            # Get the enrollment
            enrollment_elem = soup.select_one('.enrollment')
            if enrollment_elem:
                enrollment_text = enrollment_elem.text.strip()
                try:
                    # Extract the number from text like "Enrollment: 250 students"
                    enrollment = int(''.join(filter(str.isdigit, enrollment_text)))
                    info['total_student_enrollment'] = enrollment
                except ValueError:
                    pass
            
            # Add the source URL
            info['source_url'] = school_url
            
            return info
            
        except Exception as e:
            logger.error(f"Error scraping school info: {e}")
            return {}

class GeocodingHelper:
    """Helper class for geocoding"""
    
    def __init__(self):
        self.api_key = os.getenv("GEOCODING_API_KEY")
        if not self.api_key:
            logger.warning("GEOCODING_API_KEY environment variable is not set")
    
    def geocode_address(self, address, city, state="TX", zip_code=None):
        """Geocode an address to get latitude and longitude"""
        try:
            if not self.api_key:
                # Return mock data if no API key
                return {"latitude": 30.2672 + random.uniform(-1, 1), "longitude": -97.7431 + random.uniform(-1, 1)}
            
            # Format the address
            full_address = f"{address}, {city}, {state}"
            if zip_code:
                full_address += f" {zip_code}"
            
            # Call the geocoding API (using OpenStreetMap/Nominatim for demonstration)
            url = f"https://nominatim.openstreetmap.org/search?q={full_address.replace(' ', '+')}&format=json&limit=1"
            headers = {
                "User-Agent": "SchoolEnrichmentProject/1.0"
            }
            
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                logger.warning(f"Failed to geocode address {full_address}: {response.status_code}")
                return {}
            
            data = response.json()
            if not data:
                logger.warning(f"No geocoding results found for {full_address}")
                return {}
            
            result = data[0]
            return {
                "latitude": float(result["lat"]),
                "longitude": float(result["lon"])
            }
            
        except Exception as e:
            logger.error(f"Error geocoding address: {e}")
            return {}

def enrich_school_data(school):
    """Enrich a school's data with scraped information and geocoding"""
    try:
        enriched_data = {}
        
        # Scrape additional information
        scraper = ScrapingHelper()
        scraped_data = scraper.scrape_school_info(
            school_name=school.get("school_name", ""),
            city=school.get("city", "")
        )
        
        # Add scraped data to enriched data
        for key, value in scraped_data.items():
            if value and (key not in school or not school[key]):
                enriched_data[key] = value
        
        # Geocode the address if needed
        if not school.get("latitude") or not school.get("longitude"):
            geocoder = GeocodingHelper()
            geocoded_data = geocoder.geocode_address(
                address=school.get("address", ""),
                city=school.get("city", ""),
                zip_code=school.get("zip")
            )
            
            # Add geocoded data to enriched data
            for key, value in geocoded_data.items():
                if value:
                    enriched_data[key] = value
        
        # Add timestamp
        enriched_data["enriched_at"] = str(datetime.now())
        
        return enriched_data
        
    except Exception as e:
        logger.error(f"Error enriching school data: {e}")
        return {}

def main():
    """Main function to run the school enrichment process"""
    try:
        # Initialize Supabase
        supabase = SupabaseHelper()
        
        # Get schools needing enrichment
        schools = supabase.get_schools_needing_enrichment(limit=5)
        logger.info(f"Found {len(schools)} schools to enrich")
        
        # Process each school
        for i, school in enumerate(schools):
            logger.info(f"Processing school {i+1}/{len(schools)}: {school.get('school_name')}")
            
            # Enrich the school data
            enriched_data = enrich_school_data(school)
            
            if enriched_data:
                logger.info(f"Enriched data: {json.dumps(enriched_data, indent=2)}")
                
                # Update the school in the database
                result = supabase.update_school(school["school_id"], enriched_data)
                if result:
                    logger.info(f"Successfully updated school {school.get('school_name')}")
                else:
                    logger.error(f"Failed to update school {school.get('school_name')}")
            else:
                logger.warning(f"No enriched data found for school {school.get('school_name')}")
            
            # Add a delay to avoid rate limiting
            time.sleep(2)
        
        logger.info("School enrichment process completed")
        
    except Exception as e:
        logger.error(f"Error in main function: {e}")

if __name__ == "__main__":
    main()
