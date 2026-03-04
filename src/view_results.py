import json
import os
import glob
from datetime import datetime
from pprint import pprint

def find_latest_results_file(mock=False):
    """Find the most recent results file"""
    pattern = "mock_results_*.json" if mock else "results_*.json"
    result_files = glob.glob(pattern)
    if not result_files:
        return None

    # Sort by modification time (newest first)
    result_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return result_files[0]

def load_results(file_path):
    """Load results from a JSON file"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading results file: {e}")
        return None

def format_school_data(results):
    """Format school data for display"""
    formatted_data = []

    if not results or "results" not in results:
        print("No results found or invalid results format")
        return formatted_data

    for batch_result in results["results"]:
        # Check if the result contains task outputs
        if "task_outputs" in batch_result and batch_result["task_outputs"]:
            for task_output in batch_result["task_outputs"]:
                if isinstance(task_output, str):
                    # Try to parse the task output as JSON
                    try:
                        task_data = json.loads(task_output)
                        if isinstance(task_data, dict) and "data" in task_data:
                            formatted_data.append(task_data["data"])
                    except Exception as e:
                        print(f"Error parsing task output: {e}")
                        # If not JSON, just add the string
                        formatted_data.append({"raw_output": task_output})
                elif isinstance(task_output, dict):
                    formatted_data.append(task_output)

        # Check if the result itself contains data
        if "result" in batch_result and batch_result["result"]:
            try:
                result_data = json.loads(batch_result["result"])
                if isinstance(result_data, list):
                    formatted_data.extend(result_data)
                elif isinstance(result_data, dict):
                    formatted_data.append(result_data)
            except:
                # If not JSON, check if it's a list of schools
                if isinstance(batch_result["result"], list):
                    formatted_data.extend(batch_result["result"])
                elif isinstance(batch_result["result"], dict):
                    formatted_data.append(batch_result["result"])
                else:
                    # Just add the string result
                    formatted_data.append({"raw_output": batch_result["result"]})

    return formatted_data

def display_school_data(school_data):
    """Display school data in a readable format"""
    if not school_data:
        print("No school data found")
        return

    print(f"\n{'=' * 80}")
    print(f"PROCESSED SCHOOL DATA ({len(school_data)} schools)")
    print(f"{'=' * 80}\n")

    for i, school in enumerate(school_data, 1):
        print(f"\nSCHOOL #{i}:")
        print(f"{'-' * 40}")

        if isinstance(school, dict):
            for key, value in school.items():
                print(f"{key.upper()}: {value}")
        else:
            print(school)

    print(f"\n{'=' * 80}")

def main():
    # Find the latest results file (use mock results)
    use_mock = True  # Set to True to use mock results, False to use real results
    latest_file = find_latest_results_file(mock=use_mock)
    if not latest_file:
        print(f"No {'mock ' if use_mock else ''}results files found")
        return

    print(f"Loading results from: {latest_file}")

    # Load the results
    results = load_results(latest_file)
    if not results:
        return

    # Format and display the school data
    school_data = format_school_data(results)
    display_school_data(school_data)

    # Also display the raw results for debugging
    print("\nRAW RESULTS:")
    pprint(results)

if __name__ == "__main__":
    main()
