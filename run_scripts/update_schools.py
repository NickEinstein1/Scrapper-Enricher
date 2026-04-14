import json
import logging
from dbenc.tools.supabase_tool import SupabaseTool

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_schools_from_json(json_file_path):
    """Update schools in the database using the repaired JSON file"""
    try:
        # Load the JSON file
        with open(json_file_path, 'r') as f:
            updates = json.load(f)
        
        logger.info(f"Loaded {len(updates)} school updates from {json_file_path}")
        
        # Create a Supabase tool
        supabase_tool = SupabaseTool()
        logger.info("Connected to Supabase")
        
        # Process each update
        success_count = 0
        error_count = 0
        
        for update in updates:
            try:
                school_id = update.get('school_id')
                data = update.get('data', {})
                
                if not school_id:
                    logger.error(f"Missing school_id in update: {update}")
                    error_count += 1
                    continue
                
                # Update the school in the database
                result = supabase_tool.update_school(school_id=school_id, data=data)
                
                if result.get('status') == 'success':
                    logger.info(f"Successfully updated school {school_id}")
                    success_count += 1
                else:
                    logger.error(f"Failed to update school {school_id}: {result.get('error')}")
                    error_count += 1
            
            except Exception as e:
                logger.error(f"Error updating school: {e}")
                error_count += 1
        
        # Print summary
        logger.info(f"Update complete: {success_count} successful, {error_count} failed")
        return {
            "success_count": success_count,
            "error_count": error_count,
            "total": len(updates)
        }
    
    except Exception as e:
        logger.error(f"Error in update_schools_from_json: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Update schools in the database using a JSON file')
    parser.add_argument('json_file', help='Path to the JSON file with school updates')
    args = parser.parse_args()
    
    result = update_schools_from_json(args.json_file)
    print(f"Update result: {json.dumps(result, indent=2)}")
