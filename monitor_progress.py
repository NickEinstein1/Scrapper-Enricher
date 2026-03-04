#!/usr/bin/env python3
"""
Monitor the progress of the School Data Enrichment project.
This script analyzes the processed_schools.json file and the batch results files
to provide a summary of the project's progress.
"""

import os
import json
import glob
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('monitor_progress.log')
    ]
)
logger = logging.getLogger(__name__)

# File to track processed schools
PROCESSED_SCHOOLS_FILE = "processed_schools.json"

def load_processed_schools():
    """Load the list of already processed schools"""
    if os.path.exists(PROCESSED_SCHOOLS_FILE):
        try:
            with open(PROCESSED_SCHOOLS_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.warning(f"Error reading {PROCESSED_SCHOOLS_FILE}, starting with empty list")
    return {"processed_school_ids": []}

def get_batch_results():
    """Get all batch results files"""
    batch_files = glob.glob("batch_schools_*.json")
    batch_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return batch_files

def analyze_batch_file(file_path):
    """Analyze a batch results file"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Get file creation time
        file_time = datetime.fromtimestamp(os.path.getctime(file_path))
        
        # Count successful and failed updates
        successful_updates = 0
        failed_updates = 0
        
        for result in data.get('results', []):
            if isinstance(result, dict):
                # Check for explicit error field
                if 'error' in result:
                    failed_updates += 1
                    continue
                
                # Check result text
                if 'result' in result:
                    result_text = str(result.get('result', ''))
                    if 'successfully updated' in result_text.lower() or 'success' in result_text.lower():
                        successful_updates += 1
                    elif 'failed' in result_text.lower() or 'error' in result_text.lower():
                        failed_updates += 1
        
        return {
            'file_path': file_path,
            'file_time': file_time,
            'successful_updates': successful_updates,
            'failed_updates': failed_updates,
            'total_results': len(data.get('results', []))
        }
    except Exception as e:
        logger.error(f"Error analyzing batch file {file_path}: {e}")
        return {
            'file_path': file_path,
            'file_time': datetime.fromtimestamp(os.path.getctime(file_path)),
            'error': str(e)
        }

def get_total_schools():
    """Get the total number of schools in the database"""
    try:
        # Import the Supabase tool
        from src.dbenc.tools.supabase_tool import SupabaseTool
        
        # Connect to Supabase
        supabase_tool = SupabaseTool()
        
        # Get the total number of schools
        schools = supabase_tool._client.table("schools").select("count", count="exact").execute()
        return schools.count
    except Exception as e:
        logger.error(f"Error getting total schools: {e}")
        return "Unknown"

def get_schools_needing_enrichment():
    """Get the number of schools needing enrichment"""
    try:
        # Import the Supabase tool
        from src.dbenc.tools.supabase_tool import SupabaseTool
        
        # Connect to Supabase
        supabase_tool = SupabaseTool()
        
        # Get schools needing enrichment (missing total_student_enrollment, latitude, or longitude)
        schools = supabase_tool._client.table("schools").select("count", count="exact").or_("total_student_enrollment.is.null,latitude.is.null,longitude.is.null").execute()
        return schools.count
    except Exception as e:
        logger.error(f"Error getting schools needing enrichment: {e}")
        return "Unknown"

def main():
    """Main function to monitor progress"""
    logger.info("Starting School Data Enrichment Progress Monitor")
    
    # Get processed schools
    processed_schools = load_processed_schools()
    processed_count = len(processed_schools.get("processed_school_ids", []))
    logger.info(f"Processed schools: {processed_count}")
    
    # Get batch results
    batch_files = get_batch_results()
    logger.info(f"Found {len(batch_files)} batch results files")
    
    # Analyze batch files
    batch_analyses = []
    for file_path in batch_files:
        analysis = analyze_batch_file(file_path)
        batch_analyses.append(analysis)
    
    # Get total schools and schools needing enrichment
    total_schools = get_total_schools()
    schools_needing_enrichment = get_schools_needing_enrichment()
    
    # Generate report
    print("\n" + "="*80)
    print("SCHOOL DATA ENRICHMENT PROGRESS REPORT")
    print("="*80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total schools in database: {total_schools}")
    print(f"Schools processed: {processed_count}")
    print(f"Schools still needing enrichment: {schools_needing_enrichment}")
    print(f"Completion percentage: {(processed_count / total_schools) * 100:.2f}% (if all schools need enrichment)")
    
    print("\nRECENT BATCH RESULTS:")
    print("-"*80)
    for i, analysis in enumerate(batch_analyses[:5]):  # Show only the 5 most recent
        print(f"Batch {i+1}: {analysis['file_path']}")
        print(f"  Time: {analysis['file_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        if 'error' in analysis:
            print(f"  Error: {analysis['error']}")
        else:
            print(f"  Successful updates: {analysis['successful_updates']}")
            print(f"  Failed updates: {analysis['failed_updates']}")
            print(f"  Total results: {analysis['total_results']}")
        print()
    
    print("="*80)
    print("RECOMMENDATIONS:")
    
    # Generate recommendations based on analysis
    if processed_count == 0:
        print("- Start processing schools by running run_batch_schools.py")
    elif schools_needing_enrichment == 0:
        print("- All schools have been enriched! Project is complete.")
    else:
        print(f"- Continue processing the remaining {schools_needing_enrichment} schools")
        
        # Check for failed updates
        failed_batches = [a for a in batch_analyses if a.get('failed_updates', 0) > 0]
        if failed_batches:
            print(f"- Investigate and fix the {sum(a.get('failed_updates', 0) for a in failed_batches)} failed updates")
    
    print("="*80)

if __name__ == "__main__":
    main()
