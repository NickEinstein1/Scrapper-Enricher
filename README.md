# 🏫 School Data Enrichment System

> An AI-powered, multi-agent pipeline that automatically discovers, scrapes, geocodes, validates, and persists comprehensive school data into a Supabase database — orchestrated entirely by **CrewAI agents** connected to your database via a **live MCP server**.

---

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [CrewAI Agent Pipeline](#crewai-agent-pipeline)
  - [Researcher Agent](#1-researcher-agent)
  - [Scraper Agent](#2-scraper-agent)
  - [Geocoder Agent](#3-geocoder-agent)
  - [Reporter Agent](#4-reporter-agent)
- [Custom Tools](#custom-tools)
  - [SupabaseTool](#supabasetool)
  - [ScrapingTool](#scrapingtool)
  - [GeocodingTool](#geocodingtool)
- [Supabase MCP Server Integration](#supabase-mcp-server-integration)
- [Data Fields Enriched](#data-fields-enriched)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Project](#running-the-project)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)

---

## Overview

The **School Data Enrichment System** solves a critical data completeness problem: school databases often have missing fields such as addresses, enrollment numbers, phone numbers, and GPS coordinates. This system automates filling those gaps by:

1. **Querying** a Supabase database for schools with incomplete records
2. **Scraping** public school review websites for the missing details
3. **Geocoding** school addresses into precise latitude/longitude coordinates
4. **Validating** all data against strict schema rules
5. **Writing** the enriched, validated records back to Supabase

The entire pipeline is orchestrated by four specialised **CrewAI agents** that pass context between themselves in a sequential workflow. The system supports both **live mode** (real web scraping + real database writes) and **mock mode** (deterministic test data) for safe development and testing.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ENTRY POINTS                                 │
│  run_batch_schools.py  │  continuous_processing.py  │  main.py      │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │     CrewAI Orchestrator  │
                    │        (crew.py)         │
                    └────────────┬────────────┘
                                 │  Sequential Process
          ┌──────────────────────┼───────────────────────┐
          │                      │                       │
   ┌──────▼──────┐      ┌────────▼────────┐    ┌────────▼────────┐    ┌────────────────┐
   │  Researcher  │─────▶│    Scraper      │───▶│   Geocoder      │───▶│    Reporter    │
   │    Agent     │      │    Agent        │    │    Agent        │    │    Agent       │
   └──────┬───────┘      └────────┬────────┘    └────────┬────────┘    └───────┬────────┘
          │                       │                      │                     │
   ┌──────▼───────┐      ┌────────▼────────┐    ┌────────▼────────┐    ┌───────▼────────┐
   │ SupabaseTool  │      │  ScrapingTool   │    │ GeocodingTool   │    │ SupabaseTool   │
   │ get_schools   │      │ scrape_private  │    │    geocode      │    │ update_school  │
   └──────┬───────┘      │ scrape_public   │    └────────┬────────┘    └───────┬────────┘
          │              └────────┬────────┘             │                     │
          │                       │                      │                     │
   ┌──────▼───────────────────────▼──────────────────────▼─────────────────────▼────────┐
   │                         SUPABASE DATABASE                                          │
   │                    (via MCP Server + Direct SDK)                                   │
   └─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## CrewAI Agent Pipeline

The pipeline runs **sequentially** — each agent receives the full output of all previous agents as context before acting. This allows the Reporter to compile and validate data from all three prior stages without any extra retrieval calls.

### 1. Researcher Agent

| Property | Detail |
|----------|--------|
| **Role** | School Data Senior Data Researcher |
| **Goal** | Identify schools with incomplete records in Supabase |
| **Tool** | `SupabaseTool` → `action: get_schools` |

**What it does:**
- Calls the Supabase database to retrieve a configurable batch of schools
- Inspects each record for missing fields: `address`, `city`, `zip`, `total_student_enrollment`, `latitude`, `longitude`
- Validates that every `school_id` is a proper UUID before including it
- Produces a structured JSON list of schools with their missing fields for downstream agents
- Automatically retries with a smaller limit if the database call fails

**Output format:**
```json
[
  {
    "school_id": "ee8981ae-7f29-47bf-968c-4829381e0559",
    "school_name": "SACRED HEART CATHOLIC HIGH SCHOOL",
    "missing_fields": ["total_student_enrollment", "latitude", "longitude"]
  }
]
```

---

### 2. Scraper Agent

| Property | Detail |
|----------|--------|
| **Role** | School Data Scraper |
| **Goal** | Enrich school data from PrivateSchoolReview and PublicSchoolReview |
| **Tool** | `ScrapingTool` → `action: scrape_private` or `scrape_public` |

**What it does:**
- Classifies each school as **private** or **public** by scanning the school name for religious terms (`Catholic`, `Christian`, `Lutheran`, `Baptist`, `Episcopal`, `Sacred Heart`, etc.)
- Routes to the correct scraping action:
  - Private schools → `privateschoolreview.com`
  - Public schools → `publicschoolreview.com`
- Fetches and parses school pages using **BeautifulSoup** with rotating User-Agent headers and randomised delays (2–5 seconds) to avoid rate limiting
- Retries up to **3 times** with exponential backoff (`tenacity`) — on each retry it progressively simplifies the school name (removes special characters, tries abbreviations)
- Extracts the following fields: `total_student_enrollment`, `address`, `city`, `zip`, `phone`, `school_type`, `religious_orientation`, `days_in_school_year`

**Output format:**
```json
[
  {
    "school_id": "ee8981ae-7f29-47bf-968c-4829381e0559",
    "enriched_fields": {
      "total_student_enrollment": 500,
      "address": "123 Main St",
      "city": "Austin",
      "zip": 78701,
      "phone": "(512) 555-1234",
      "school_type": "REGULAR ELEMENTARY OR SECONDARY",
      "religious_orientation": "Christian"
    },
    "status": "success"
  }
]
```

---

### 3. Geocoder Agent

| Property | Detail |
|----------|--------|
| **Role** | School Geocoding Specialist |
| **Goal** | Add precise GPS coordinates to each school record |
| **Tool** | `GeocodingTool` → `action: geocode` |

**What it does:**
- Accepts address components (`address`, `city`, `state`, `zip`) or a full location string
- Calls **Nominatim** (OpenStreetMap) via `geopy` with a built-in `RateLimiter` (min 1 second between requests)
- Falls back gracefully: if geocoding a full address fails, retries with city + state only; for PO Box addresses, falls back to city + state immediately
- Validates results: checks that returned coordinates fall within the continental US bounding box (lat: 24–50, lng: -125 to -65)
- Supports **mock mode** for testing — generates deterministic coordinates from an MD5 hash of the location string

**Output format:**
```json
[
  {
    "school_id": "ee8981ae-7f29-47bf-968c-4829381e0559",
    "enriched_fields": {
      "latitude": 30.267153,
      "longitude": -97.743057
    },
    "status": "success"
  }
]
```

---

### 4. Reporter Agent

| Property | Detail |
|----------|--------|
| **Role** | School Data Quality Specialist |
| **Goal** | Validate, compile, and persist all enriched data to Supabase |
| **Tool** | `SupabaseTool` → `action: update_school` |

**What it does:**
- Reads the full context from all three prior agents without any additional tool calls
- Runs a strict **data validation** pass before writing anything:
  - `total_student_enrollment`: must be an integer between 10 and 5,000
  - `latitude`: must be a float between 24.0 and 50.0
  - `longitude`: must be a float between -125.0 and -66.0
  - `phone`: must match format `(XXX) XXX-XXXX`
  - `zip`: must be a valid 5-digit (or ZIP+4) US postal code
- Updates each school **one at a time** (with a 1-second pause between writes) for safe error isolation
- Retries a failed write once after a 2-second wait before logging the failure and continuing
- Produces a structured Markdown summary report with counts of successes and failures

---

## Custom Tools

### SupabaseTool

**File:** `src/dbenc/tools/supabase_tool.py`

A LangChain `BaseTool` that wraps the Supabase Python SDK and exposes a unified action-based interface to the CrewAI agents.

| Action | Description |
|--------|-------------|
| `get_schools` | Fetches schools needing enrichment; flags fields that are `null` or missing |
| `update_school` | Updates a single school by UUID with validated field data |
| `get_all_schools` | Retrieves all schools (used for monitoring/reporting) |
| `query` | Flexible filtered query against any Supabase table |
| `test` | Pings the database to verify connectivity |
| `initialize` | Seeds the database with a sample school record if empty |

Connects using `SUPABASE_URL` + `SUPABASE_ANON_KEY` from the environment. Compatible with both positional (CrewAI 0.28.0) and keyword argument calling conventions.

---

### ScrapingTool

**File:** `src/dbenc/tools/scraping_tool.py`

A LangChain `BaseTool` that scrapes school data from two public review websites using `requests` + `BeautifulSoup`.

| Action | Target Site | School Type |
|--------|------------|-------------|
| `scrape_private` | privateschoolreview.com | Religious / independent schools |
| `scrape_public` | publicschoolreview.com | Public / state schools |

Key implementation details:
- **Rotating User-Agents** — cycles through 3 different browser signatures per request
- **Random delays** — 2–5 second sleep between each HTTP request
- **Exponential backoff** — via `tenacity` (`stop_after_attempt(3)`, `wait_exponential(min=2, max=10)`)
- **Mock mode** — returns realistic deterministic data without making any HTTP calls; activated by `--use_mock` flag

---

### GeocodingTool

**File:** `src/dbenc/tools/geocoding_tool.py`

A LangChain `BaseTool` that converts school addresses into GPS coordinates using **Nominatim** (OpenStreetMap) via `geopy`.

Key implementation details:
- **Rate-limited** — `geopy.extra.rate_limiter.RateLimiter` enforces ≥1 second between requests
- **Smart fallback** — automatically strips address components on retry (full address → city + state)
- **3-attempt retry loop** with progressive address simplification
- **Mock mode** — generates deterministic lat/lng from an MD5 hash of the input string, always within continental US bounds

---

## Supabase MCP Server Integration

This project integrates with Supabase via the **Model Context Protocol (MCP)** — a standard that lets AI agents interact with external services through a structured server interface.

The MCP server exposes Supabase operations (read, write, query) directly to AI tooling without requiring custom API wrappers. It runs as a local Node.js process.

### How it works

```
CrewAI Agent
     │
     │  JSON action call
     ▼
SupabaseTool (_run method)
     │
     │  Supabase Python SDK
     ▼
Supabase REST API ◄──── MCP Server (npx @supabase/mcp-server-supabase)
     │
     ▼
Supabase PostgreSQL Database
```

The MCP server is authenticated with your **Supabase Personal Access Token** (not the anon key), giving it elevated privileges for admin-level operations. This token must never be committed — it belongs only in your `.env` file.

### Starting the MCP server

```bash
npx -y @supabase/mcp-server-supabase@latest --access-token=YOUR_SUPABASE_PAT
```

You can verify the connection using the included test file:

```bash
# Open in browser to test MCP connectivity
start mcp_test.html
```

---

## Data Fields Enriched

| Field | Type | Source | Validation |
|-------|------|--------|-----------|
| `address` | string | ScrapingTool | — |
| `city` | string | ScrapingTool | — |
| `zip` | int/string | ScrapingTool | US ZIP format |
| `phone` | string | ScrapingTool | `(XXX) XXX-XXXX` |
| `total_student_enrollment` | int | ScrapingTool | 10 – 5,000 |
| `school_type` | string | ScrapingTool | — |
| `religious_orientation` | string | ScrapingTool | Private schools only |
| `days_in_school_year` | int | ScrapingTool | — |
| `latitude` | float | GeocodingTool | 24.0 – 50.0 (continental US) |
| `longitude` | float | GeocodingTool | -125.0 – -66.0 (continental US) |

---

## Installation

### Prerequisites

- Python `>=3.10, <3.13`
- Node.js `>=18`
- A Supabase project with a `schools` table

### Python dependencies

This project uses [UV](https://docs.astral.sh/uv/) for dependency management:

```bash
pip install uv
crewai install
```

### Node.js dependencies (MCP server)

```bash
npm install @supabase/mcp-server-supabase punycode2
```

---

## Configuration

Copy your credentials into a `.env` file (never commit this file):

```env
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_ACCESS_TOKEN=sbp_...   # Personal Access Token for MCP server
```

To customise agent behaviour, edit these YAML files:

| File | Purpose |
|------|---------|
| `src/dbenc/config/agents.yaml` | Agent roles, goals, backstories, and tool instructions |
| `src/dbenc/config/tasks.yaml` | Task descriptions, expected output formats, and agent assignments |

---

## Running the Project

### Step 1 — Start the MCP server

The MCP server must be running before you start processing schools with live data:

```bash
npx -y @supabase/mcp-server-supabase@latest --access-token=YOUR_SUPABASE_PAT
```

### Step 2 — Prepare a batch of schools

Fetch unprocessed schools from Supabase and write them to a local JSON batch file:

```bash
python process_supabase_schools.py --batch_size 5
```

### Step 3 — Run the CrewAI pipeline

```bash
# Single run, real data
python -m dbenc.main run --batch_size 5 --timeout 300

# Or use the optimised batch runner (recommended — manages context window)
python run_batch_schools.py --batch_size=2 --max_schools=10 --timeout=600
```

| Parameter | Default | Recommended | Description |
|-----------|---------|-------------|-------------|
| `--batch_size` | 1 | 2–3 | Schools per CrewAI run |
| `--max_schools` | 10 | 10–50 | Total schools to process |
| `--timeout` | 300 | 600 | Seconds per batch before timeout |
| `--use_mock` | off | — | Skip real scraping/geocoding (testing) |

### Step 4 — Automated continuous processing

To process schools in a fully automated loop across many batches:

```bash
python continuous_processing.py
```

Or run a fixed number of batches at once:

```bash
python src/batch_process.py --batch_size 5 --timeout 300 --batches 3
```

### Step 5 — View results and monitor progress

```bash
# View all enriched schools in the database
python src/view_enriched_schools.py

# Monitor overall processing progress
python monitor_progress.py

# View which schools have already been processed
python process_supabase_schools.py --view-processed
```

---

## Project Structure

```
dbenc/
├── src/
│   └── dbenc/
│       ├── config/
│       │   ├── agents.yaml          # Agent roles, goals, backstories & tool instructions
│       │   └── tasks.yaml           # Task descriptions, expected outputs & agent assignments
│       ├── tools/
│       │   ├── supabase_tool.py     # Supabase CRUD operations (get_schools, update_school, …)
│       │   ├── scraping_tool.py     # Web scraper (privateschoolreview / publicschoolreview)
│       │   └── geocoding_tool.py    # Nominatim geocoder with rate limiting & fallback
│       ├── crew.py                  # CrewAI Crew, Agent, Task wiring and execution
│       └── main.py                  # CLI entry point and batch orchestration
├── src/
│   ├── batch_process.py             # Multi-batch automation helper
│   ├── update_db_schools.py         # Manually push a repaired JSON file to Supabase
│   ├── view_enriched_schools.py     # Display enriched school records
│   ├── extract_school_data.py       # Extract + repair agent output JSON
│   ├── error_handling.py            # Shared retry and error utilities
│   └── get_schools_for_processing.py
├── docs/
│   ├── comprehensive_guide.md       # Full guide with code examples
│   ├── quick_start_guide.md         # Quick reference
│   ├── school_data_enrichment_workflow.md
│   ├── supabase_mcp_integration.md  # MCP server setup deep-dive
│   └── supabase_mcp_prompts.md      # Example MCP prompts
├── process_supabase_schools.py      # Fetch & prepare school batches from Supabase
├── run_batch_schools.py             # Optimised batch runner with context window management
├── continuous_processing.py         # Infinite processing loop for large datasets
├── monitor_progress.py              # Progress monitoring dashboard
├── mcp_test.html                    # Browser-based MCP connectivity tester
├── pyproject.toml                   # Python project metadata (UV)
├── package.json                     # Node.js dependencies (MCP server)
├── .env                             # ⚠️ Secret credentials — never commit
└── README.md
```

---

## Troubleshooting

### Agent & Pipeline Issues

| Symptom | Fix |
|---------|-----|
| Context window exceeded | Reduce `--batch_size` to 1 or 2 |
| API rate limits hit | Increase wait time between batches in `continuous_processing.py` |
| Geocoding returns wrong location | Check that the state code is a valid 2-letter US abbreviation |
| Scraping returns no results | Try removing special characters from the school name; check if the school type (public/private) is correctly detected |
| Reporter skips a school | Check validation: enrollment outside 10–5000, coordinates outside continental US, or invalid phone format |

### MCP Server Issues

| Symptom | Fix |
|---------|-----|
| Connection refused | Confirm the MCP server process is still running |
| 401 Unauthorized | Regenerate your Supabase Personal Access Token and update `.env` |
| Node.js errors | Run `npm install` and ensure Node.js `>=18` is installed |
| Supabase updates not appearing | Verify `SUPABASE_URL` and `SUPABASE_ANON_KEY` are correct |

### Reporter Agent DB Update Failures

1. Confirm `school_id` is a valid 36-character UUID string
2. Check that at least one field passes validation (invalid-only payloads are silently skipped)
3. Verify the Supabase table schema matches the field names exactly
4. Review logs — each validation failure is logged with the specific reason

---

## Documentation

- [Comprehensive Guide](docs/comprehensive_guide.md) — Code examples for live data, mock data, and batch processing
- [Workflow Documentation](docs/school_data_enrichment_workflow.md) — End-to-end flow explanation
- [Quick Start Guide](docs/quick_start_guide.md) — Get running in minutes
- [Supabase MCP Integration](docs/supabase_mcp_integration.md) — MCP server setup and usage
- [MCP Example Prompts](docs/supabase_mcp_prompts.md) — Ready-to-use prompts for MCP interactions

---

## External Resources

- [CrewAI Documentation](https://docs.crewai.com)
- [Supabase Documentation](https://supabase.com/docs)
- [Supabase MCP Server](https://github.com/supabase/mcp-server-supabase)
- [geopy / Nominatim](https://geopy.readthedocs.io/)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

