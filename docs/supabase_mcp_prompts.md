# Supabase MCP Example Prompts

This document contains example prompts for using Supabase MCP with the School Data Enrichment project. These prompts can be used with AI assistants like Cursor, Claude, or VS Code Copilot to interact with your Supabase database.

## Database Schema Exploration

- "Show me the current schema of the schools table"
- "List all tables in the database and their relationships"
- "What columns exist in the schools table?"
- "Generate a diagram of the database schema"

## Database Queries

- "Show me all schools that have been processed but don't have latitude/longitude coordinates"
- "Find schools with enrollment over 500 students in California"
- "List the top 10 schools by enrollment"
- "Find schools that have religious orientation information"
- "Show me schools that were processed in the last week"

## Schema Management

- "Create a new table to track school programs with fields for program name, description, and school ID"
- "Add a new column to the schools table to track the last update date"
- "Generate a migration to add indexes for frequently queried fields"
- "Create a view that shows schools with their enrichment status"
- "Add a foreign key constraint between schools and processed_schools tables"

## Data Analysis

- "Analyze the distribution of school sizes across different states"
- "Find patterns in school enrichment success rates"
- "Generate a report on geocoding accuracy"
- "Compare public vs private school enrichment success rates"
- "Identify states with the most schools in the database"

## TypeScript Generation

- "Generate TypeScript types for the school database schema"
- "Create interfaces for the school data model"
- "Update the TypeScript types to include the new school_programs table"
- "Generate a TypeScript client for interacting with the schools API"

## Data Quality Checks

- "Find schools with missing or invalid data"
- "Identify duplicate school entries"
- "Check for schools with extreme enrollment values that might be errors"
- "Verify that all processed schools have valid coordinates"
- "Find schools with inconsistent naming patterns"

## Optimization Suggestions

- "Suggest indexes to improve query performance"
- "Analyze the most frequent queries and suggest optimizations"
- "Recommend database structure improvements"
- "Suggest batch size optimizations based on database performance"

## Example Workflows

### Enriching a New Batch of Schools

1. "Show me how many unprocessed schools are in the database"
2. "Generate a query to select 10 unprocessed schools"
3. "Create a migration to mark these schools as being processed"
4. "Generate code to update these schools with enriched data"

### Analyzing Enrichment Results

1. "Show me the success rate of school enrichment over time"
2. "Identify common patterns in schools that fail enrichment"
3. "Generate a report on the quality of enriched data"
4. "Create a visualization of enrichment progress by state"

### Improving Database Performance

1. "Analyze the current database schema for performance issues"
2. "Suggest indexes for frequently queried fields"
3. "Generate migrations to implement the suggested indexes"
4. "Measure query performance before and after the changes"
