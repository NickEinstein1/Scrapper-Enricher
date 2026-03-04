# School Data Enrichment Project: Quick Start Guide

## Overview

This guide provides a quick reference for running the School Data Enrichment Project. For detailed documentation, see `school_data_enrichment_workflow.md`.

## Prerequisites

1. **Environment Setup**:
   - Python 3.8+ installed
   - Virtual environment activated
   - All dependencies installed:
     ```bash
     pip install -r requirements.txt
     ```

2. **API Keys**:
   - OpenAI API key in `.env` file
   - Supabase credentials in `.env` file

## Quick Start Workflow

### Step 1: Prepare Schools for Processing

```bash
python process_supabase_schools.py --batch_size 5
```

This will:
- Get 5 unprocessed schools from Supabase
- Create input files for the CrewAI system
- Mark these schools as processed to avoid duplicates
- Track processed schools in the SQLite database

### Step 2: Run the CrewAI System

```bash
python -m dbenc.main run --batch_size 5 --timeout 300
```

This will:
- Process the schools using the CrewAI agents (researcher, scraper, geocoder, reporter)
- Enrich the school data with additional information
- Generate results files with the enriched data
- Use the schools prepared in the previous step

### Step 3: Extract School Data

```bash
python src/extract_school_data.py
```

This will:
- Extract enriched school data from the results
- Skip schools that have already been processed
- Create a repaired JSON file with the extracted data
- If no schools are found in the results, get unprocessed schools directly from Supabase

### Step 4: Update the Database

```bash
# Find the latest repaired JSON file
latest_file=$(ls -t repaired_school_updates_*.json | head -1)

# Update the database
python src/update_db_schools.py $latest_file
```

This will:
- Update the Supabase database with the enriched data
- Use robust error handling with retry mechanisms
- Process updates in batches for efficiency
- Report detailed success and failure counts

### Step 5: View Results

```bash
# View enriched schools directly from Supabase
python src/view_enriched_schools.py

# View processed schools from the tracking database
python process_supabase_schools.py --view-processed
```

## Automated Batch Processing

To automate the entire workflow for multiple batches:

```bash
python src/batch_process.py --batch_size 5 --timeout 300 --batches 3
```

This will:
- Process 3 batches of 5 schools each
- Handle all steps automatically (preparation, processing, extraction, database update)
- Skip schools that have already been processed
- Report progress and results for each batch

You can also use the direct processing script for testing:

```bash
python direct_process.py --batch_size 5
```

This will:
- Use sample data instead of connecting to Supabase
- Track processed schools in the SQLite database
- Create properly formatted JSON files
- Useful for testing the tracking system without using API calls

## Supabase MCP Integration

The School Data Enrichment project now supports integration with Supabase MCP (Model Context Protocol) for AI-assisted database operations.

### Setup MCP

1. **Create a Personal Access Token**:
   - Go to your [Supabase settings](https://supabase.com/dashboard/account/tokens)
   - Create a token named "School Data Enrichment MCP"

2. **Configure Your AI Tool**:
   - For VS Code: Use the configuration in `.vscode/mcp.json`
   - For Cursor: Use the configuration in `.cursor/mcp.json`
   - For Claude: Use the configuration in `.mcp.json`
   - For Windsurf: Use the configuration in `.windsurf/mcp.json`

3. **Test the Connection**:
   ```bash
   node test_mcp_connection.js
   ```

### Using MCP

Once configured, you can use natural language to interact with your database through your AI assistant. For example:

- "Show me all schools that have been processed but don't have coordinates"
- "Generate a report on our enrichment success rate by state"
- "Suggest improvements to our database schema for better performance"

For more examples, see [MCP Example Prompts](supabase_mcp_prompts.md).

## Monitoring and Reporting

### Check Processed Schools
```bash
python process_supabase_schools.py --view-processed
```

This will show:
- All schools that have been processed
- When they were processed
- Which batch file they came from

### View Enriched Schools
```bash
python src/view_enriched_schools.py
```

This will show:
- Schools that have been successfully enriched
- Detailed information for each school
- Geographic coordinates and other enriched fields

### Check Database Update Results
```bash
# Find the latest results file
latest_file=$(ls -t results_*.json | head -1)

# View the results
cat $latest_file
```

## Troubleshooting

If you encounter issues:

1. **Check logs** for error messages
2. **Verify API keys** are correct in the `.env` file:
   ```
   OPENAI_API_KEY=your_openai_api_key
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   SUPABASE_ANON_KEY=your_supabase_anon_key
   ```

3. **Ensure dependencies** are installed:
   ```bash
   pip install -r requirements.txt
   ```

4. **Adjust timeout settings** if operations are timing out:
   ```bash
   python -m dbenc.main run --batch_size 5 --timeout 600  # Increase timeout to 10 minutes
   ```

5. **Check database connection** if updates fail:
   ```bash
   # Test Supabase connection
   python -c "import os; from dotenv import load_dotenv; import requests; load_dotenv(); print(f'SUPABASE_URL: {os.getenv(\'SUPABASE_URL\')}'); print(f'SUPABASE_KEY: {os.getenv(\'SUPABASE_KEY\')[0:5]}...')"
   ```

6. **Reset processed schools tracking** if needed:
   ```bash
   # Remove the processed_schools.db file
   rm processed_schools.db
   ```

For detailed troubleshooting, refer to the main documentation.
