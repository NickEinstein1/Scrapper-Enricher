import json
import os
from datetime import datetime

def generate_mock_results():
    """Generate mock results for demonstration purposes"""
    # Sample schools from the database
    schools = [
        {
            "school_id": "9c9c989b-9455-44fc-b7f6-718ac9a22379",
            "school_name": "NORTHSIDE BAPTIST ACADEMY",
            "address": "1800 U.S. 190 Business",
            "city": "Nolanville",
            "zip": 76559,
            "total_student_enrollment": 115,
            "latitude": 31.083976,
            "longitude": -97.634028
        },
        {
            "school_id": "4c032cbc-d947-4c79-a425-da48051f0d31",
            "school_name": "MACEDONIAN CHRISTIAN ACADEMY",
            "address": "401 N VAL VERDE RD",
            "city": "Donna",
            "zip": 78537,
            "total_student_enrollment": 115,
            "latitude": 26.179525,
            "longitude": -98.08292
        },
        {
            "school_id": "85db917d-1cca-477a-a26d-882d7e5da979",
            "school_name": "RISEN CHRIST CHRISTIAN ACADEMY",
            "address": "10595 U.S. 17",
            "city": "Myrtle Beach",
            "zip": 29572,
            "total_student_enrollment": 115,
            "latitude": 33.796474,
            "longitude": -78.74743
        },
        {
            "school_id": "fe336077-dd61-41e0-8788-b1cb3340f6d7",
            "school_name": "VENTURE ACADEMY",
            "address": "989 122nd Street",
            "city": "Chippewa Falls",
            "zip": 54729,
            "total_student_enrollment": 115,
            "latitude": 44.857116,
            "longitude": -91.426589
        },
        {
            "school_id": "91e7401c-e442-4dc3-8703-b7b4c6ab460d",
            "school_name": "ST. PETER'S LUTHERAN SCHOOL",
            "address": "67055 Gratiot",
            "city": "Richmond",
            "zip": 48062,
            "total_student_enrollment": 115,
            "latitude": 42.795338,
            "longitude": -82.737297
        }
    ]
    
    # Generate enriched data for each school
    enriched_schools = []
    for school in schools:
        # Mock data from PrivateSchoolReview
        if "BAPTIST" in school["school_name"] or "CHRISTIAN" in school["school_name"] or "LUTHERAN" in school["school_name"]:
            # Private school
            private_data = {
                "source": "privateschoolreview",
                "source_url": f"https://www.privateschoolreview.com/schools/{school['school_name'].lower().replace(' ', '-')}",
                "total_student_enrollment": school["total_student_enrollment"] + 10,  # Slightly different to show enrichment
                "phone": f"({school['zip'] // 1000}) 555-{school['zip'] % 10000}",
                "religious_orientation": "Christian" if "CHRISTIAN" in school["school_name"] else 
                                        "Baptist" if "BAPTIST" in school["school_name"] else
                                        "Lutheran" if "LUTHERAN" in school["school_name"] else "Non-denominational",
                "tuition": f"${8000 + (school['zip'] % 4000)}",
                "student_teacher_ratio": f"{10 + (school['zip'] % 5)}:1",
                "accreditation": "Association of Christian Schools International"
            }
            school.update(private_data)
        else:
            # Public school
            public_data = {
                "source": "publicschoolreview",
                "source_url": f"https://www.publicschoolreview.com/schools/{school['school_name'].lower().replace(' ', '-')}",
                "total_student_enrollment": school["total_student_enrollment"] + 15,  # Slightly different to show enrichment
                "phone": f"({school['zip'] // 1000}) 555-{school['zip'] % 10000}",
                "school_district": f"{school['city']} School District",
                "state_rank": f"#{school['zip'] % 100}",
                "student_teacher_ratio": f"{12 + (school['zip'] % 8)}:1",
                "free_lunch_eligible": f"{20 + (school['zip'] % 30)}%"
            }
            school.update(public_data)
        
        # Add geocoding confirmation
        geocoding_data = {
            "geocoded_address": f"{school['address']}, {school['city']}, {school['zip']}",
            "geocoded_latitude": school["latitude"] + 0.000001,  # Slightly different to show enrichment
            "geocoded_longitude": school["longitude"] - 0.000001,  # Slightly different to show enrichment
            "geocoding_source": "geopy (Nominatim)",
            "geocoding_confidence": "high"
        }
        school.update(geocoding_data)
        
        # Add enrichment metadata
        school["enriched_at"] = datetime.now().isoformat(),
        school["enrichment_status"] = "complete"
        
        enriched_schools.append(school)
    
    # Create task outputs for each batch of schools
    task_outputs = []
    for i in range(0, len(enriched_schools), 2):
        batch = enriched_schools[i:i+2]
        task_output = {
            "result": f"Successfully enriched {len(batch)} schools",
            "raw_output": None,
            "task_outputs": [json.dumps({"status": "success", "data": school}) for school in batch]
        }
        task_outputs.append(task_output)
    
    # Create the final results
    results = {
        "results": task_outputs,
        "total_batches": len(task_outputs)
    }
    
    return results

def save_mock_results():
    """Save mock results to a file"""
    results = generate_mock_results()

    # Create a filename with the current timestamp
    import os
    os.makedirs("school_output", exist_ok=True)
    filename = os.path.join("school_output", f"mock_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Mock results saved to {filename}")
    return filename

if __name__ == "__main__":
    save_mock_results()
