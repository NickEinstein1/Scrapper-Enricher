# School Data Enrichment Project: Comprehensive Guide

This guide provides detailed instructions for running the School Data Enrichment Project from start to finish, including both mock and live data options, as well as batch processing.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Setup and Installation](#setup-and-installation)
3. [Running with Live Data](#running-with-live-data)
4. [Running with Mock Data](#running-with-mock-data)
5. [Batch Processing](#batch-processing)
6. [Monitoring and Reporting](#monitoring-and-reporting)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Configuration](#advanced-configuration)

## Project Overview

The School Data Enrichment Project uses AI agents to gather, process, and enrich data about schools from various online sources. The system connects to Supabase MCP servers for database operations and uses the OpenAI API for AI processing.

### Key Features

- **AI-Powered Data Enrichment**: Uses CrewAI agents to gather and process school data
- **Multi-Source Integration**: Collects data from privateschoolreview.com, publicschoolreview.com, and other sources
- **Geocoding**: Adds precise geographic coordinates to school records
- **Database Integration**: Updates Supabase database with enriched data
- **Batch Processing**: Efficiently processes schools in configurable batches
- **Context Window Management**: Optimized agent configurations to prevent context window exceeded errors
- **Data Validation**: Comprehensive validation of all fields before database updates

## Setup and Installation

### Prerequisites

1. **Python Environment**:
   - Python 3.9+ installed
   - Virtual environment recommended

2. **API Keys**:
   - OpenAI API key (paid account)
   - Supabase credentials

### Installation Steps

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/school-data-enrichment.git
   cd school-data-enrichment
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Create a `.env` file in the project root with the following:
   ```
   MODEL=gpt-3.5-turbo
   OPENAI_API_KEY=your_openai_api_key
   SUPABASE_URL=your_supabase_url
   SUPABASE_ANON_KEY=your_supabase_anon_key
   SUPABASE_KEY=your_supabase_key
   ```

## Running with Live Data

### Single School Processing

To process a single school with live data:

```bash
python run_real_school.py
```

This script will:
1. Find the next unprocessed school in the database
2. Process it using the CrewAI agents
3. Update the database with the enriched data
4. Mark the school as processed

### Code Explanation

The `run_real_school.py` script uses the following key parameters:

```python
# Set parameters for the run
use_mock = False  # Use real mode for actual data enrichment
timeout = 600     # Set a longer timeout (10 minutes) for real operations
```

The script connects to the Supabase database, retrieves an unprocessed school, and runs the CrewAI system to enrich the data.

## Running with Mock Data

To run the system with mock data (for testing purposes):

```bash
python run_real_school.py --use_mock
```

To modify the script to use mock data, change the `use_mock` parameter to `True`:

```python
# Set parameters for the run
use_mock = True  # Use mock mode for testing
timeout = 300    # Set a shorter timeout for testing
```

### Mock Data vs. Live Data

- **Mock Data**: Uses predefined sample data instead of making real API calls to external websites. Useful for testing the system without consuming API credits or hitting rate limits.
- **Live Data**: Makes actual API calls to school review websites and geocoding services to gather real-time data.

## Batch Processing

For more efficient processing of multiple schools:

### Basic Batch Processing

```bash
python run_batch_schools.py --batch_size=2 --max_schools=10 --timeout=600
```

Parameters:
- `--batch_size`: Number of schools to process in each batch (default: 1, recommended: 2-3)
- `--max_schools`: Maximum number of schools to process in total (default: 10)
- `--timeout`: Timeout in seconds for each batch (default: 300)
- `--use_mock`: Use mock data instead of real data (optional flag)

### Using Mock Data with Batch Processing

```bash
python run_batch_schools.py --batch_size=3 --max_schools=10 --timeout=300 --use_mock
```

This will process up to 10 schools in batches of 3, using mock data instead of making real API calls.

### Code Explanation

The `run_batch_schools.py` script handles batch processing with these key components:

```python
# Get unprocessed schools
unprocessed_schools = get_unprocessed_schools(limit=args.max_schools)

# Process schools in batches
batch_size = min(args.batch_size, 3)  # Limit batch size to prevent context window issues

# Split schools into smaller batches
batches = []
for i in range(0, len(unprocessed_schools), batch_size):
    batches.append(unprocessed_schools[i:i + batch_size])

# Process each batch
for i, batch in enumerate(batches):
    logger.info(f"Processing batch {i+1} of {len(batches)}")
    batch_results = process_batch(batch, batch_size, use_mock=args.use_mock, timeout=args.timeout)
    
    # Wait between batches to avoid rate limiting
    if i < len(batches) - 1:
        wait_time = 5
        logger.info(f"Waiting {wait_time} seconds before processing next batch...")
        time.sleep(wait_time)
```

### Optimizing Batch Size

- For **live data**: Start with a batch size of 1-2 schools to prevent context window exceeded errors
- For **mock data**: You can use larger batch sizes (3-5) since the data is simpler

## Monitoring and Reporting

### Checking Processed Schools

To view which schools have been processed:

```bash
python -c "import json; f=open('processed_schools.json'); data=json.load(f); print(f'Processed {len(data[\"processed_school_ids\"])} schools')"
```

### Viewing Results Files

Results are saved to timestamped JSON files:
- Single school: `real_school_YYYYMMDD_HHMMSS.json`
- Batch processing: `batch_schools_YYYYMMDD_HHMMSS.json`

To view the latest results:

```bash
# For single school processing
latest_file=$(ls -t real_school_*.json | head -1)
cat $latest_file

# For batch processing
latest_file=$(ls -t batch_schools_*.json | head -1)
cat $latest_file
```

### Checking Logs

Logs are saved to:
- Single school: `real_school_run.log`
- Batch processing: `batch_schools_run.log`

To view the latest logs:

```bash
# For single school processing
tail -100 real_school_run.log

# For batch processing
tail -100 batch_schools_run.log
```

## Troubleshooting

### Common Issues and Solutions

1. **Context Window Exceeded Error**:
   - Reduce batch size to 1 or 2 schools
   - Use the optimized `run_batch_schools.py` script
   - Increase timeout value

   ```bash
   python run_batch_schools.py --batch_size=1 --timeout=900
   ```

2. **API Rate Limits**:
   - Increase wait time between batches
   - Reduce batch size
   - Add more delay between API calls

3. **Geocoding Failures**:
   - Try with just city and state if full address fails
   - Check address formatting
   - Verify geocoding API credentials

4. **Database Connection Issues**:
   - Verify Supabase credentials in `.env` file
   - Check network connectivity
   - Test connection with a simple query

   ```bash
   python -c "from src.dbenc.tools.supabase_tool import SupabaseTool; tool = SupabaseTool(); print(tool.get_schools_needing_enrichment(limit=1))"
   ```

## Advanced Configuration

### Modifying Agent Configurations

Agent configurations are stored in `src/dbenc/config/agents.yaml`. You can modify these to change agent behavior:

```yaml
researcher:
  role: "School Data Researcher"
  goal: "Find schools that need data enrichment"
  backstory: "You are an expert at finding schools that need additional data..."

scraper:
  role: "Web Scraper"
  goal: "Extract detailed information about schools from websites"
  backstory: "You are an expert at extracting information from school websites..."
```

### Customizing Timeout Settings

For schools with complex data needs, you may need to increase the timeout:

```bash
python run_real_school.py --timeout=900  # 15 minutes
```

Or for batch processing:

```bash
python run_batch_schools.py --batch_size=2 --timeout=900
```

### Running the Complete Workflow

For a complete end-to-end workflow:

1. **Process a single school with live data**:
   ```bash
   python run_real_school.py
   ```

2. **Process multiple schools in batches**:
   ```bash
   python run_batch_schools.py --batch_size=2 --max_schools=10 --timeout=600
   ```

3. **Process a large number of schools overnight**:
   ```bash
   python run_batch_schools.py --batch_size=2 --max_schools=100 --timeout=600
   ```

4. **Test the system with mock data**:
   ```bash
   python run_batch_schools.py --batch_size=3 --max_schools=10 --use_mock
   ```

### Example Complete Workflow Script

Here's a complete script that demonstrates the entire workflow:

```bash
#!/bin/bash

# Set parameters
BATCH_SIZE=2
MAX_SCHOOLS=20
TIMEOUT=600
USE_MOCK=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --mock)
      USE_MOCK=true
      shift
      ;;
    --batch-size=*)
      BATCH_SIZE="${1#*=}"
      shift
      ;;
    --max-schools=*)
      MAX_SCHOOLS="${1#*=}"
      shift
      ;;
    --timeout=*)
      TIMEOUT="${1#*=}"
      shift
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

echo "Starting School Data Enrichment Workflow"
echo "Parameters:"
echo "  Batch Size: $BATCH_SIZE"
echo "  Max Schools: $MAX_SCHOOLS"
echo "  Timeout: $TIMEOUT"
echo "  Use Mock Data: $USE_MOCK"

# Run the batch processing
if [ "$USE_MOCK" = true ]; then
  python run_batch_schools.py --batch_size=$BATCH_SIZE --max_schools=$MAX_SCHOOLS --timeout=$TIMEOUT --use_mock
else
  python run_batch_schools.py --batch_size=$BATCH_SIZE --max_schools=$MAX_SCHOOLS --timeout=$TIMEOUT
fi

# Check the results
LATEST_FILE=$(ls -t batch_schools_*.json | head -1)
echo "Results saved to $LATEST_FILE"

# Count processed schools
PROCESSED_COUNT=$(python -c "import json; f=open('processed_schools.json'); data=json.load(f); print(len(data['processed_school_ids']))")
echo "Total processed schools: $PROCESSED_COUNT"

echo "Workflow completed"
```

Save this as `run_workflow.sh` and make it executable:

```bash
chmod +x run_workflow.sh
```

Then run it:

```bash
./run_workflow.sh --batch-size=2 --max-schools=20
```

Or with mock data:

```bash
./run_workflow.sh --mock --batch-size=3 --max-schools=10
```
