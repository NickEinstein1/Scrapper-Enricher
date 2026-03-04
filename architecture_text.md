# School Data Enrichment Architecture

## System Components and Data Flow

```
+------------------+     +-------------------+     +-------------------+
|  User Interface  |     |    Core System    |     | External Services |
|                  |     |                   |     |                   |
| [run_batch_      |---->| [main.py]         |<--->| [Supabase MCP     |
|  schools.py]     |     |                   |     |  Server]          |
+------------------+     | [crew.py]         |     |                   |
                         |                   |     | [Supabase         |
                         | +---------------+ |     |  Database]        |
                         | | CrewAI Agents | |     |                   |
                         | |               | |     | [Web Sources]     |
                         | | - Researcher  | |     |                   |
                         | | - Scraper     | |     | [Geocoding        |
                         | | - Geocoder    | |     |  Services]        |
                         | | - Reporter    | |     +-------------------+
                         | +---------------+ |
                         |                   |
                         | +---------------+ |     +-------------------+
                         | |    Tools      | |     |   Data Storage    |
                         | |               | |     |                   |
                         | | - SupabaseTool|<----->| [processed_       |
                         | | - ScrapingTool| |     |  schools.json]    |
                         | | - GeocodingTool |     |                   |
                         | +---------------+ |     | [batch_schools_   |
                         +-------------------+     |  *.json]          |
                                                   +-------------------+
```

## Data Flow Steps

1. User initiates the process through run_batch_schools.py
2. main.py initializes the system and creates the SchoolEnrichmentCrew
3. Researcher Agent queries Supabase for schools needing enrichment
4. Supabase Tool connects to the MCP server to retrieve school data
5. Scraper Agent determines if each school is private or public
6. Scraping Tool fetches detailed information from web sources
7. Geocoder Agent processes school addresses
8. Geocoding Tool converts addresses to precise coordinates
9. Reporter Agent validates and compiles the enriched data
10. Supabase Tool updates the database with the enriched data
11. main.py saves results to batch_schools_*.json files
12. main.py tracks processed schools in processed_schools.json

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
