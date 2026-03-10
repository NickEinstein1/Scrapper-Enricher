# School Data Enrichment Architecture

## System Overview

The School Data Enrichment solution uses AI-powered agents to gather, process, and enrich data about schools from various online sources. The system integrates with Supabase MCP (Model Context Protocol) servers for database operations.

## Architecture Diagram

```
+----------------------+        +------------------------+        +------------------------+
|   User Interface     |        |     Core System        |        |   External Services    |
|                      |        |                        |        |                        |
|  +--------------+    |        |  +----------------+    |        |  +----------------+    |
|  | User         |    |        |  | main.py        |    |        |  | Supabase MCP   |    |
|  +--------------+    |        |  +----------------+    |        |  | Server         |    |
|         |            |        |         |              |        |  +----------------+    |
|         v            |        |         v              |        |         ^              |
|  +--------------+    |        |  +----------------+    |        |         |              |
|  | run_batch_   |----+------->|  | crew.py        |<---+--------+-------->|              |
|  | schools.py   |    |        |  +----------------+    |        |         v              |
|  +--------------+    |        |         |              |        |  +----------------+    |
+----------------------+        |         |              |        |  | Supabase       |    |
                                |         v              |        |  | Database       |    |
                                |  +----------------+    |        |  +----------------+    |
                                |  | CrewAI Agents  |    |        |         ^              |
                                |  |                |    |        |         |              |
                                |  | - Researcher   |<---+--------+-------->|              |
                                |  | - Scraper      |<---+--------+-------->+----------------+
                                |  | - Geocoder     |<---+--------+-------->|  Web Sources  |
                                |  | - Reporter     |    |        |         +----------------+
                                |  +----------------+    |        |                          
                                |         |              |        |         +----------------+
                                |         v              |        |         | Geocoding      |
                                |  +----------------+    |        |         | Services       |
                                |  | Tools          |<---+--------+-------->|                |
                                |  |                |    |        |         +----------------+
                                |  | - SupabaseTool |    |        |                          
                                |  | - ScrapingTool |    |        +------------------------+
                                |  | - GeocodingTool|    |                                  
                                |  +----------------+    |        +------------------------+
                                |         |              |        |     Data Storage       |
                                |         v              |        |                        |
                                |  +----------------+    |        |  +----------------+    |
                                |  | Results        |----+------->|  | processed_     |    |
                                |  |                |    |        |  | schools.json   |    |
                                |  +----------------+    |        |  +----------------+    |
                                +------------------------+        |                        |
                                                                 |  +----------------+    |
                                                                 |  | batch_schools_ |    |
                                                                 |  | *.json         |    |
                                                                 |  +----------------+    |
                                                                 +------------------------+
```

## Data Flow

1. **User initiates process** through run_batch_schools.py
2. **main.py initializes system** and creates SchoolEnrichmentCrew
3. **Researcher Agent** queries Supabase for schools needing enrichment
4. **Supabase Tool** connects to MCP server to retrieve school data
5. **Scraper Agent** determines if each school is private or public
6. **Scraping Tool** fetches detailed information from web sources
7. **Geocoder Agent** processes school addresses
8. **Geocoding Tool** converts addresses to precise coordinates
9. **Reporter Agent** validates and compiles the enriched data
10. **Supabase Tool** updates the database with the enriched data
11. **main.py saves results** to batch_schools_*.json files
12. **main.py tracks processed schools** in processed_schools.json

## Key Components

### CrewAI Agents
- **Researcher Agent**: Identifies schools needing enrichment
- **Scraper Agent**: Scrapes data from web sources
- **Geocoder Agent**: Adds geographic coordinates
- **Reporter Agent**: Updates database with enriched data

### Tools
- **Supabase Tool**: Connects to Supabase MCP servers
- **Scraping Tool**: Scrapes data from web sources
- **Geocoding Tool**: Adds geographic coordinates

### External Services
- **Supabase MCP Server**: Connects AI tools to database
- **Supabase Database**: Stores school data
- **Web Sources**: External websites with school information
- **Geocoding Services**: Services for converting addresses to coordinates

### Data Storage
- **processed_schools.json**: Tracks processed schools
- **batch_schools_*.json**: Stores batch processing results

## MCP Server Integration

The Supabase MCP (Model Context Protocol) server is a critical component that:

1. **Connects AI tools directly to Supabase**: Allows the CrewAI agents to interact with the database using natural language
2. **Handles authentication**: Uses access tokens for secure connections
3. **Provides database operations**: Querying, updating, and managing school records
4. **Enables AI-assisted database management**: Schema design, SQL generation, and data exploration
