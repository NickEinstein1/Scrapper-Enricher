# School Data Enrichment Project Documentation

## Overview

The School Data Enrichment Project is designed to gather, process, and enrich data about schools from various sources. This document outlines the complete workflow, tools, and processes used in the project.

## Table of Contents

1. [Project Architecture](#project-architecture)
2. [Dependencies](#dependencies)
3. [Data Sources](#data-sources)
4. [Workflow](#workflow)
5. [Tracking Processed Schools](#tracking-processed-schools)
6. [Scripts and Tools](#scripts-and-tools)
7. [Optimization Strategies](#optimization-strategies)
8. [Troubleshooting](#troubleshooting)
9. [AI Integration with Supabase MCP](#ai-integration-with-supabase-mcp)

## Project Architecture

The project uses a CrewAI-based architecture with multiple specialized agents:

- **Researcher Agent**: Gathers initial information about schools
- **Scraper Agent**: Extracts detailed information from websites
- **Geocoder Agent**: Adds geographic coordinates to school data
- **Reporter Agent**: Compiles data and updates the database

These agents work together in a coordinated workflow to enrich school data.

## Dependencies

- **Python Libraries**:
  - `crewai`: Version compatible with tiktoken 0.8.0
  - `tiktoken`: Version 0.8.0
  - `python-dotenv`: For environment variable management
  - `requests`: For API calls
  - `sqlite3`: For local database operations
  - `tabulate`: For formatted output display

- **APIs**:
  - OpenAI API (paid account)
  - Supabase for database operations

## Data Sources

- **Private Schools**: privateschoolreview.com
- **Public Schools**: publicschoolreview.com
- **Geographic Data**: Various geocoding services

## Workflow

### 1. Preparation Phase

1. **Get Unprocessed Schools**:
   ```bash
   python process_supabase_schools.py --batch_size 5
   ```
   - Retrieves schools from Supabase that haven't been processed yet
   - Creates a `schools_to_process_TIMESTAMP.json` file
   - Creates a `repaired_school_updates_TIMESTAMP.json` file
   - Marks these schools as processed in the tracking database
   - Prevents duplicate processing of schools across different runs

2. **View Processed Schools** (optional):
   ```bash
   python process_supabase_schools.py --view-processed
   ```
   - Displays a list of all schools that have been processed
   - Shows when each school was processed
   - Shows which batch file each school came from

### 2. Processing Phase

1. **Run the CrewAI System**:
   ```bash
   python -m dbenc.main run --batch_size 5 --timeout 300
   ```
   - Processes the schools using the CrewAI agents
   - Timeout set to 300 seconds for optimal performance
   - Batch size determines how many schools to process at once
   - Uses the schools prepared in the previous step

2. **Extract School Data**:
   ```bash
   python src/extract_school_data.py
   ```
   - Extracts enriched school data from the results
   - Skips schools that have already been processed
   - Creates a repaired JSON file with the extracted data
   - If no schools are found in the results, gets unprocessed schools directly from Supabase

### 3. Database Update Phase

1. **Update the Database**:
   ```bash
   python src/update_db_schools.py repaired_school_updates_TIMESTAMP.json
   ```
   - Updates the Supabase database with the enriched data
   - Uses robust error handling with retry mechanisms and exponential backoff
   - Processes updates in batches for efficiency
   - Reports success and failure counts for each batch

2. **View Enriched Data**:
   ```bash
   python src/view_enriched_schools.py
   ```
   - Connects directly to Supabase to get enriched schools
   - Displays the enriched school data in a formatted table
   - Shows detailed information for each school
   - Falls back to local results files if Supabase connection fails

### 4. Batch Processing

For processing multiple batches of schools:
```bash
python src/batch_process.py --batch_size 5 --timeout 300 --batches 3
```
- Processes 3 batches of 5 schools each
- Uses a timeout of 300 seconds per batch
- Automatically handles all the steps in the workflow
- Skips schools that have already been processed

## Tracking Processed Schools

The system uses a SQLite database (`processed_schools.db`) to track which schools have been processed:

1. **Database Structure**:
   - `school_id`: Primary key, the unique identifier for the school
   - `school_name`: The name of the school
   - `processed_date`: When the school was processed
   - `batch_file`: Which batch file the school was part of

2. **Tracking Functions**:
   - `init_processed_schools_db()`: Initializes the database
   - `is_school_processed()`: Checks if a school has already been processed
   - `mark_school_as_processed()`: Marks a school as processed
   - `view_processed_schools()`: Displays all processed schools

3. **Benefits**:
   - Prevents duplicate processing of schools
   - Provides a history of processed schools
   - Makes the system more efficient

## Scripts and Tools

### Main Scripts

1. **process_supabase_schools.py**:
   - Gets unprocessed schools from Supabase
   - Tracks processed schools in SQLite database
   - Creates input files for the CrewAI system
   - Prevents duplicate processing of schools

2. **direct_process.py**:
   - Simplified version of process_supabase_schools.py for testing
   - Uses sample data instead of connecting to Supabase
   - Useful for testing the tracking system

3. **dbenc/main.py**:
   - Main entry point for the CrewAI system
   - Coordinates the agents (researcher, scraper, geocoder, reporter)
   - Processes the schools using the prepared data
   - Checks for existing school data files before querying Supabase

4. **extract_school_data.py**:
   - Extracts data from the results
   - Skips already processed schools using the tracking database
   - Creates repaired JSON files for database updates
   - Falls back to getting schools directly from Supabase if needed

5. **update_db_schools.py**:
   - Updates the Supabase database with enriched data
   - Uses robust error handling with retry mechanisms and exponential backoff
   - Processes updates in batches for efficiency
   - Reports detailed success and failure counts

6. **view_enriched_schools.py**:
   - Connects directly to Supabase to view enriched schools
   - Displays data in both table and detailed formats
   - Shows all enriched fields for each school
   - Falls back to local results files if Supabase connection fails

7. **batch_process.py**:
   - Automates the entire workflow from start to finish
   - Processes multiple batches of schools
   - Handles all the steps in sequence
   - Includes command to view processed schools

### Tools and Utilities

1. **SupabaseTool** (dbenc/tools/supabase_tool.py):
   - Connects to the Supabase database
   - Performs database operations (get, update)
   - Gets schools needing enrichment
   - Handles authentication and API calls

2. **ScrapingTool** (dbenc/tools/scraping_tool.py):
   - Scrapes school data from privateschoolreview.com and publicschoolreview.com
   - Handles different school types appropriately
   - Extracts enrollment numbers, address information, and other details

3. **GeocodingTool** (dbenc/tools/geocoding_tool.py):
   - Adds geographic coordinates to school records
   - Supports multiple geocoding strategies
   - Handles address formatting and validation

4. **error_handling.py**:
   - Provides retry mechanisms with exponential backoff
   - Implements safe execution wrappers
   - Handles batch processing with detailed error tracking
   - Improves resilience against API failures

## Optimization Strategies

1. **Batch Processing**:
   - Process schools in batches to optimize API usage
   - Start with smaller batches (5 schools) and increase as needed
   - Monitor performance and adjust batch size accordingly

2. **Timeout Settings**:
   - Default timeout set to 300 seconds
   - Adjust based on complexity of school data
   - Increase for schools with more missing fields

3. **Error Handling**:
   - Retry failed operations with exponential backoff
   - Track success and failure counts
   - Skip problematic schools and continue processing

4. **Agent Instructions**:
   - Fine-tuned instructions for each agent
   - Clear guidance on handling different school types
   - Specific strategies for data enrichment

## Troubleshooting

### Common Issues

1. **Module Import Errors**:
   - Ensure all dependencies are installed
   - Check Python path settings
   - Use virtual environment for isolation

2. **API Rate Limits**:
   - Adjust batch size and timeout settings
   - Implement delays between API calls
   - Use retry mechanisms with backoff

3. **Database Connection Issues**:
   - Verify Supabase credentials
   - Check network connectivity
   - Use error handling for database operations

4. **Missing or Incomplete Data**:
   - Adjust agent instructions
   - Try alternative data sources
   - Implement fallback strategies

### Monitoring and Maintenance

1. **Regular Checks**:
   - Monitor processed schools database
   - Check for failed updates
   - Verify data quality

2. **System Updates**:
   - Keep dependencies up to date
   - Adjust to API changes
   - Refine agent instructions based on results

3. **Performance Optimization**:
   - Analyze processing times
   - Identify bottlenecks
   - Implement improvements

## AI Integration with Supabase MCP

The School Data Enrichment Project now integrates with Supabase MCP (Model Context Protocol) to enable AI-assisted database operations.

### What is Supabase MCP?

Supabase MCP is a server that connects AI tools like Cursor, Claude, and VS Code Copilot directly to your Supabase database. It allows these AI tools to perform database operations, manage tables, fetch configuration, and query data using natural language.

### Benefits for School Data Enrichment

1. **AI-Assisted Database Management**:
   - Design and modify database schema using natural language
   - Generate complex SQL queries for data analysis
   - Explore database structure and relationships

2. **Development Workflow Improvements**:
   - Reduce context switching between tools
   - Generate TypeScript types from database schema
   - Debug database issues more efficiently

3. **Data Exploration and Analysis**:
   - Query school data using natural language
   - Generate reports on enrichment progress
   - Identify patterns and insights in the data

### Integration with Existing Tools

1. **Supabase Tool**:
   - AI assistants can help generate queries for the SupabaseTool
   - Optimize database operations
   - Suggest schema improvements

2. **Data Extraction**:
   - Generate optimized queries for extracting school data
   - Improve data validation
   - Enhance reporting capabilities

3. **Database Updates**:
   - Verify data quality before updates
   - Generate optimized update queries
   - Monitor update performance

### Setup and Configuration

For detailed setup instructions, see [Supabase MCP Integration](supabase_mcp_integration.md).

## Changelog

### 2025-04-09 (Session 6)
- Integrated Supabase MCP for AI-assisted database operations
- Created configuration files for VS Code, Cursor, and Claude
- Added documentation for MCP integration and example prompts
- Created test script for verifying MCP connection

### 2025-04-09 (Session 5)
- Implemented tracking system for processed schools
- Added robust error handling with retry mechanisms
- Optimized timeout settings for better performance
- Created documentation for the complete workflow

### Previous Updates
- Set up CrewAI agents and tools
- Implemented initial data enrichment process
- Created database update mechanisms
- Added batch processing capabilities
