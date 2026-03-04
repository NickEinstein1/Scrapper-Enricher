# School Data Enrichment Project

## Overview

The School Data Enrichment Project is an automated system for gathering, processing, and enriching data about schools from various online sources. It uses CrewAI agents to research, scrape, geocode, and compile comprehensive information about schools.

## Features

- **AI-Powered Data Enrichment**: Uses CrewAI agents to gather and process school data
- **Multi-Source Integration**: Collects data from privateschoolreview.com, publicschoolreview.com, and other sources
- **Geocoding**: Adds precise geographic coordinates to school records
- **Database Integration**: Updates Supabase database with enriched data
- **Tracking System**: Prevents duplicate processing of schools
- **Batch Processing**: Efficiently processes schools in configurable batches
- **Error Handling**: Robust retry mechanisms and error reporting
- **Supabase MCP Integration**: Connect AI tools directly to your Supabase database
- **Context Window Management**: Optimized agent configurations to prevent context window exceeded errors
- **Data Validation**: Comprehensive validation of all fields before database updates

## Documentation

- [Comprehensive Guide](docs/comprehensive_guide.md): Complete guide with code examples for running with live/mock data and batch processing
- [Complete Workflow Documentation](docs/school_data_enrichment_workflow.md): Detailed workflow explanation
- [Quick Start Guide](docs/quick_start_guide.md): Brief guide to get started quickly
- [Supabase MCP Integration](docs/supabase_mcp_integration.md): Guide to integrating with Supabase MCP
- [MCP Example Prompts](docs/supabase_mcp_prompts.md): Example prompts for MCP

## Installation

Ensure you have Python >=3.10 <3.13 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:

(Optional) Lock the dependencies and install them by using the CLI command:
```bash
crewai install
```

### Node.js Dependencies

For Supabase MCP server integration, you'll need Node.js and the following packages:

```bash
npm install @supabase/mcp-server-supabase punycode2
```

### Customizing

**Add your credentials into the `.env` file**

```
OPENAI_API_KEY=your_openai_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
```

- Modify `src/dbenc/config/agents.yaml` to define your agents
- Modify `src/dbenc/config/tasks.yaml` to define your tasks
- Modify `src/dbenc/crew.py` to add your own logic, tools and specific args
- Modify `src/dbenc/main.py` to add custom inputs for your agents and tasks

## Running the Project

### Starting the MCP Server

Before running the project with real data, start the Supabase MCP server:

```bash
npx -y @supabase/mcp-server-supabase@latest --access-token=your_access_token
```

You can test the MCP connection using the provided HTML test file:

```bash
# Open the MCP test HTML file in your browser
open mcp_test.html
```

### Basic Usage

1. Prepare schools for processing:
   ```bash
   python process_supabase_schools.py --batch_size 5
   ```

2. Run the CrewAI system:
   ```bash
   python -m dbenc.main run --batch_size 5 --timeout 300
   ```

3. Update the database:
   ```bash
   # Find the latest repaired JSON file
   latest_file=$(ls -t repaired_school_updates_*.json | head -1)

   # Update the database
   python src/update_db_schools.py $latest_file
   ```

4. View results:
   ```bash
   # View enriched schools
   python src/view_enriched_schools.py

   # View processed schools
   python process_supabase_schools.py --view-processed
   ```

5. Monitor progress:
   ```bash
   # Monitor the progress of the project
   python monitor_progress.py
   ```

### Automated Batch Processing

To automate the entire workflow for multiple batches:

```bash
python src/batch_process.py --batch_size 5 --timeout 300 --batches 3
```

This will process 3 batches of 5 schools each, handling all steps automatically.

### Optimized Batch Processing

For more efficient processing with context window management:

```bash
python run_batch_schools.py --batch_size=2 --max_schools=10 --timeout=600
```

Parameters:
- `--batch_size`: Number of schools to process in each batch (default: 1, recommended: 2-3)
- `--max_schools`: Maximum number of schools to process in total (default: 10)
- `--timeout`: Timeout in seconds for each batch (default: 300)
- `--use_mock`: Use mock data instead of real data (optional flag)

This optimized script prevents context window exceeded errors by limiting batch sizes and managing memory efficiently.

## Project Structure

```
school-data-enrichment/
├── src/
│   ├── dbenc/
│   │   ├── config/
│   │   │   ├── agents.yaml    # Agent configurations
│   │   │   └── tasks.yaml     # Task configurations
│   │   ├── tools/
│   │   │   ├── supabase_tool.py  # Supabase integration
│   │   │   ├── scraping_tool.py  # Web scraping
│   │   │   └── geocoding_tool.py # Geocoding
│   │   ├── crew.py           # CrewAI setup
│   │   └── main.py           # Main entry point
│   ├── extract_school_data.py  # Data extraction
│   ├── update_db_schools.py    # Database updates
│   ├── view_enriched_schools.py  # Results viewing
│   ├── batch_process.py        # Batch processing
│   └── error_handling.py       # Error handling utilities
├── process_supabase_schools.py  # School processing script
├── run_real_school.py          # Single school processing
├── run_batch_schools.py        # Optimized batch processing
├── docs/
│   ├── school_data_enrichment_workflow.md  # Complete documentation
│   └── quick_start_guide.md    # Quick reference
├── .env                        # Environment variables
├── requirements.txt            # Dependencies
├── CHANGELOG.md                # Change history
└── README.md                   # This file
```

## Understanding the CrewAI System

The School Data Enrichment Project uses CrewAI to coordinate multiple AI agents:

1. **Researcher Agent**: Gathers initial information about schools
2. **Scraper Agent**: Extracts detailed information from websites
3. **Geocoder Agent**: Adds geographic coordinates to school data
4. **Reporter Agent**: Compiles data and updates the database

These agents collaborate on a series of tasks, leveraging their collective skills to enrich school data. The `src/dbenc/config/agents.yaml` file outlines the capabilities and configurations of each agent.

## Troubleshooting

If you encounter issues:

1. **Check logs** for error messages
2. **Verify API keys** are correct in the `.env` file
3. **Ensure dependencies** are installed
4. **Adjust timeout settings** if operations are timing out
5. **Check database connection** if updates fail
6. **Context Window Exceeded**: Reduce batch size to 1 or 2 schools and use the optimized `run_batch_schools.py` script
7. **API Rate Limits**: Increase wait time between batches
8. **Geocoding Failures**: Try with just city and state if full address fails
9. **Scraping Failures**: Try variations of the school name

### MCP Server Issues

If you encounter issues with the MCP server:

1. **Check MCP server status**: Make sure the MCP server is running
2. **Verify access token**: Ensure your access token is valid
3. **Test connection**: Use the `mcp_test.html` file to test the connection
4. **Check Node.js**: Ensure Node.js is installed and up to date
5. **Install dependencies**: Make sure you've installed the required Node.js packages
6. **Restart MCP server**: If all else fails, restart the MCP server

### Reporter Agent Issues

If the Reporter agent fails to update the database:

1. **Check school_id format**: Ensure the school_id is a valid UUID
2. **Validate data**: Make sure the data meets the validation requirements
3. **Check JSON format**: Ensure the JSON payload is properly formatted
4. **Review logs**: Check the logs for specific error messages
5. **Test with a single school**: Try updating a single school to isolate the issue

For detailed troubleshooting, refer to the [Comprehensive Guide](docs/comprehensive_guide.md) and [Complete Workflow Documentation](docs/school_data_enrichment_workflow.md).

## Support

For support, questions, or feedback regarding the School Data Enrichment Project:

- Visit the [CrewAI documentation](https://docs.crewai.com) for framework details
- Reach out through the [CrewAI GitHub repository](https://github.com/joaomdmoura/crewai) for framework issues
- [Join the CrewAI Discord](https://discord.com/invite/X4JWnZnxPb) for community support

Let's create wonders together with the power of AI-driven data enrichment!
