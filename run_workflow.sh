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
