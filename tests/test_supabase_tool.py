from dbenc.tools.supabase_tool import SupabaseTool
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    try:
        print("Creating SupabaseTool")
        supabase_tool = SupabaseTool()
        print("SupabaseTool created successfully")
        
        # Test getting schools
        print("Getting schools")
        schools = supabase_tool.get_schools_needing_enrichment()
        print(f"Found {len(schools)} schools")
        
        # Print the schools
        for i, school in enumerate(schools):
            print(f"School {i+1}: {json.dumps(school, indent=2)}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
