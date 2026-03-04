# School Data Enrichment Project Architecture

## Overview

The School Data Enrichment Project is designed to gather, process, and enrich data about schools from various online sources. It uses CrewAI agents to orchestrate the workflow and connects to Supabase MCP (Multi-Cloud Platform) servers for database operations.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│                      School Data Enrichment System                      │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌───────────────┐     ┌───────────────┐     ┌───────────────┐          │
│  │               │     │               │     │               │          │
│  │  run_batch_   │     │  processed_   │     │  batch_       │          │
│  │  schools.py   │────▶│  schools.json │────▶│  schools_*.json│          │
│  │               │     │               │     │               │          │
│  └───────────────┘     └───────────────┘     └───────────────┘          │
│          │                                            ▲                  │
│          │                                            │                  │
│          ▼                                            │                  │
│  ┌───────────────┐                           ┌────────────────┐         │
│  │               │                           │                │         │
│  │  src/dbenc/   │                           │  Results &     │         │
│  │  main.py      │──────────────────────────▶│  Reporting     │         │
│  │               │                           │                │         │
│  └───────────────┘                           └────────────────┘         │
│          │                                                              │
│          │                                                              │
│          ▼                                                              │
│  ┌───────────────┐                                                      │
│  │               │                                                      │
│  │  src/dbenc/   │                                                      │
│  │  crew.py      │                                                      │
│  │               │                                                      │
│  └───────────────┘                                                      │
│          │                                                              │
│          │                                                              │
│          ▼                                                              │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                                                                 │   │
│  │                        CrewAI Agents                            │   │
│  │                                                                 │   │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐       │   │
│  │  │               │  │               │  │               │       │   │
│  │  │  Researcher   │  │  Scraper      │  │  Geocoder     │       │   │
│  │  │  Agent        │  │  Agent        │  │  Agent        │       │   │
│  │  │               │  │               │  │               │       │   │
│  │  └───────────────┘  └───────────────┘  └───────────────┘       │   │
│  │         │                  │                   │                │   │
│  │         │                  │                   │                │   │
│  │         ▼                  ▼                   ▼                │   │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐       │   │
│  │  │               │  │               │  │               │       │   │
│  │  │  Research     │  │  Scraping     │  │  Geocoding    │       │   │
│  │  │  Task         │  │  Task         │  │  Task         │       │   │
│  │  │               │  │               │  │               │       │   │
│  │  └───────────────┘  └───────────────┘  └───────────────┘       │   │
│  │                                                                 │   │
│  │                  ┌───────────────┐  ┌───────────────┐           │   │
│  │                  │               │  │               │           │   │
│  │                  │  Reporter     │  │  Reporting    │           │   │
│  │                  │  Agent        │  │  Task         │           │   │
│  │                  │               │  │               │           │   │
│  │                  └───────────────┘  └───────────────┘           │   │
│  │                                                                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                │                                        │
│                                │                                        │
│                                ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                                                                 │   │
│  │                           Tools                                 │   │
│  │                                                                 │   │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐       │   │
│  │  │               │  │               │  │               │       │   │
│  │  │  Supabase     │  │  Scraping     │  │  Geocoding    │       │   │
│  │  │  Tool         │  │  Tool         │  │  Tool         │       │   │
│  │  │               │  │               │  │               │       │   │
│  │  └───────────────┘  └───────────────┘  └───────────────┘       │   │
│  │         │                  │                   │                │   │
│  └─────────┼──────────────────┼───────────────────┼────────────────┘   │
│            │                  │                   │                     │
│            ▼                  ▼                   ▼                     │
│  ┌─────────────────┐  ┌───────────────┐  ┌───────────────────┐         │
│  │                 │  │               │  │                   │         │
│  │  Supabase MCP   │  │  Web Scraping │  │  Geocoding        │         │
│  │  Database       │  │  Sources      │  │  Services         │         │
│  │                 │  │               │  │                   │         │
│  └─────────────────┘  └───────────────┘  └───────────────────┘         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Entry Points
- **run_batch_schools.py**: Main entry point for batch processing schools
- **processed_schools.json**: Tracks processed school IDs to prevent duplicate processing
- **batch_schools_*.json**: Output files containing enriched school data

### 2. Core Components
- **src/dbenc/main.py**: Main module that orchestrates the workflow
- **src/dbenc/crew.py**: Implements the CrewAI setup with agents and tasks

### 3. CrewAI Agents and Tasks
- **Researcher Agent**: Queries the Supabase database for schools needing enrichment
- **Scraper Agent**: Scrapes school data from web sources
- **Geocoder Agent**: Adds geographic coordinates to school records
- **Reporter Agent**: Updates the database with enriched data

### 4. Tools
- **Supabase Tool**: Connects to Supabase MCP servers for database operations
- **Scraping Tool**: Scrapes data from privateschoolreview.com and publicschoolreview.com
- **Geocoding Tool**: Adds geographic coordinates to school records

### 5. External Services
- **Supabase MCP Database**: Stores school data
- **Web Scraping Sources**: External websites with school information
- **Geocoding Services**: Services for converting addresses to coordinates

## Data Flow

1. **run_batch_schools.py** initiates the process with batch parameters
2. **main.py** orchestrates the workflow
3. **crew.py** sets up the CrewAI agents and tasks
4. **Researcher Agent** queries Supabase for schools needing enrichment
5. **Scraper Agent** scrapes data from web sources
6. **Geocoder Agent** adds geographic coordinates
7. **Reporter Agent** updates the Supabase database with enriched data
8. Results are saved to batch_schools_*.json files

## MCP Server Integration

The School Data Enrichment Project connects to Supabase MCP (Multi-Cloud Platform) servers through the SupabaseTool. This integration allows:

1. **Database Operations**: Querying and updating school records
2. **Real Data Processing**: Using real data from production databases
3. **Secure Authentication**: Using environment variables for secure access
4. **Efficient Data Retrieval**: Getting only schools that need enrichment
5. **Data Validation**: Validating data before updating the database

The SupabaseTool handles all interactions with the MCP servers, providing a clean interface for the agents to work with.
