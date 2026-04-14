import json
import os
from datetime import datetime

def find_latest_results_file():
    """Find the most recent results file in school_output/"""
    search_dir = "school_output" if os.path.isdir("school_output") else "."
    result_files = [
        os.path.join(search_dir, f)
        for f in os.listdir(search_dir)
        if f.startswith('results_') and f.endswith('.json')
    ]
    if not result_files:
        return None

    # Sort by modification time (newest first)
    result_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return result_files[0]

def format_results(input_file, output_file=None):
    """Format the results file into a more readable format"""
    # Load the results
    with open(input_file, 'r') as f:
        results = json.load(f)
    
    # Extract the relevant information
    formatted_results = {
        "summary": {
            "total_batches": results.get("total_batches", 0),
            "total_schools": 0,
            "complete_schools": 0,
            "missing_fields": {}
        },
        "batches": []
    }
    
    # Process each batch
    for i, batch in enumerate(results.get("results", []), 1):
        batch_result = batch.get("result", "")
        
        # Try to extract structured information from the result
        batch_info = {
            "batch_number": i,
            "result": batch_result
        }
        
        # Extract summary information if available
        if "Total Schools:" in batch_result:
            try:
                total_schools_line = [line for line in batch_result.split('\n') if "Total Schools:" in line][0]
                total_schools = int(total_schools_line.split(':')[1].strip())
                formatted_results["summary"]["total_schools"] = max(formatted_results["summary"]["total_schools"], total_schools)
            except:
                pass
        
        if "Complete Schools:" in batch_result:
            try:
                complete_schools_line = [line for line in batch_result.split('\n') if "Complete Schools:" in line][0]
                complete_schools = int(complete_schools_line.split(':')[1].strip())
                formatted_results["summary"]["complete_schools"] = max(formatted_results["summary"]["complete_schools"], complete_schools)
            except:
                pass
        
        if "Missing Fields:" in batch_result:
            try:
                missing_fields_line = [line for line in batch_result.split('\n') if "Missing Fields:" in line][0]
                missing_fields_str = missing_fields_line.split(':')[1].strip()
                missing_fields = json.loads(missing_fields_str)
                
                # Update the missing fields count
                for field, count in missing_fields.items():
                    if field in formatted_results["summary"]["missing_fields"]:
                        formatted_results["summary"]["missing_fields"][field] = max(
                            formatted_results["summary"]["missing_fields"][field], 
                            count
                        )
                    else:
                        formatted_results["summary"]["missing_fields"][field] = count
            except:
                pass
        
        formatted_results["batches"].append(batch_info)
    
    # Save the formatted results
    if output_file is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        os.makedirs("school_output", exist_ok=True)
        output_file = os.path.join("school_output", f"formatted_results_{timestamp}.json")
    
    with open(output_file, 'w') as f:
        json.dump(formatted_results, f, indent=2)
    
    print(f"Formatted results saved to {output_file}")
    return output_file

if __name__ == "__main__":
    # Find the latest results file
    latest_file = find_latest_results_file()
    if not latest_file:
        print("No results files found")
        exit(1)
    
    print(f"Formatting results from {latest_file}")
    output_file = format_results(latest_file)
    
    # Print the formatted results
    with open(output_file, 'r') as f:
        formatted_results = json.load(f)
    
    print("\nSUMMARY:")
    print(f"Total Batches: {formatted_results['summary']['total_batches']}")
    print(f"Total Schools: {formatted_results['summary']['total_schools']}")
    print(f"Complete Schools: {formatted_results['summary']['complete_schools']}")
    print(f"Missing Fields: {json.dumps(formatted_results['summary']['missing_fields'], indent=2)}")
