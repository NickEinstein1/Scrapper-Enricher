# School Data Enrichment Architecture

## Overview

The School Data Enrichment solution uses a sophisticated AI-powered workflow to gather, process, and enrich data about schools from various online sources. The system integrates with Supabase MCP (Model Context Protocol) servers for database operations and uses CrewAI agents to orchestrate the workflow.

## Key Components

### 1. User Interface
- **run_batch_schools.py**: Entry point that initiates the batch processing of schools with configurable parameters (batch size, timeout, etc.)

### 2. Core System
- **main.py**: Orchestrates the workflow, initializes the database, creates the crew, and processes schools in batches
- **crew.py**: Implements the CrewAI setup with agents and tasks, manages the execution flow

### 3. CrewAI Agents
- **Researcher Agent**: Queries the Supabase database for schools needing enrichment
- **Scraper Agent**: Scrapes school data from web sources (privateschoolreview.com and publicschoolreview.com)
- **Geocoder Agent**: Adds geographic coordinates to school records
- **Reporter Agent**: Updates the database with enriched data and generates reports

### 4. Tools
- **Supabase Tool**: Connects to Supabase MCP servers for database operations
- **Scraping Tool**: Scrapes data from web sources
- **Geocoding Tool**: Adds geographic coordinates to school records

### 5. External Services
- **Supabase MCP Server**: Connects AI tools directly to the Supabase database
- **Supabase Database**: Stores school data
- **Web Sources**: External websites with school information
- **Geocoding Services**: Services for converting addresses to coordinates

### 6. Data Storage
- **processed_schools.json**: Tracks processed schools to prevent duplicate processing
- **batch_schools_*.json**: Stores results of batch processing

## Data Flow

1. **User initiates the process** through run_batch_schools.py with batch parameters
2. **main.py initializes the system** and creates the SchoolEnrichmentCrew
3. **Researcher Agent** queries Supabase for schools needing enrichment
4. **Supabase Tool** connects to the MCP server to retrieve school data
5. **Scraper Agent** determines if each school is private or public
6. **Scraping Tool** fetches detailed information from appropriate web sources
7. **Geocoder Agent** processes school addresses
8. **Geocoding Tool** converts addresses to precise geographic coordinates
9. **Reporter Agent** validates and compiles the enriched data
10. **Supabase Tool** updates the database with the enriched data
11. **main.py saves results** to batch_schools_*.json files
12. **main.py tracks processed schools** in processed_schools.json

## MCP Server Integration

The Supabase MCP (Model Context Protocol) server is a critical component that:

1. **Connects AI tools directly to Supabase**: Allows the CrewAI agents to interact with the database using natural language
2. **Handles authentication**: Uses access tokens for secure connections
3. **Provides database operations**: Querying, updating, and managing school records
4. **Enables AI-assisted database management**: Schema design, SQL generation, and data exploration

The MCP server is started using:
```bash
npx -y @supabase/mcp-server-supabase@latest --access-token=your_access_token
```

## Supabase Tool Implementation

The Supabase Tool (`src/dbenc/tools/supabase_tool.py`) is the bridge between the CrewAI agents and the Supabase database. It:

1. **Establishes connections**: Creates a client connection to Supabase
2. **Provides actions**: Implements various actions like get_schools, update_school, query
3. **Validates data**: Ensures data meets requirements before updating the database
4. **Handles errors**: Implements robust error handling and logging

## Optimization Features

1. **Batch Processing**: Efficiently processes schools in configurable batches
2. **Context Window Management**: Optimized agent configurations to prevent context window exceeded errors
3. **Tracking System**: Prevents duplicate processing of schools
4. **Error Handling**: Robust retry mechanisms and error reporting
5. **Data Validation**: Validates fields like total_student_enrollment, latitude, longitude before database updates
