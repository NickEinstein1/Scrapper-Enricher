# Supabase MCP Integration

The School Data Enrichment project supports integration with Supabase MCP (Model Context Protocol) to enable AI-assisted database operations.

## What is Supabase MCP?

Supabase MCP (Model Context Protocol) is a server that connects AI tools like Cursor, Claude, and VS Code Copilot directly to your Supabase database. It allows these AI tools to perform database operations, manage tables, fetch configuration, and query data on your behalf.

## Benefits for School Data Enrichment

1. **AI-Assisted Database Management**: AI tools can help design, query, and manage your school database schema
2. **Streamlined Development**: Reduce context switching between tools when working with your database
3. **Enhanced Data Exploration**: Use natural language to query your school data
4. **Automated Schema Generation**: Generate TypeScript types based on your database schema
5. **Simplified Debugging**: Access logs and troubleshoot issues directly through AI assistants

## Setup Instructions

### 1. Create a Personal Access Token (PAT)

1. Go to your [Supabase settings](https://supabase.com/dashboard/account/tokens)
2. Create a token named "School Data Enrichment MCP"
3. Copy the token for configuration

### 2. Configure Your AI Tool

#### VS Code

1. Ensure you have the `.vscode/mcp.json` file in your project
2. When prompted, enter your Supabase PAT
3. VS Code will automatically connect to your Supabase database

#### Cursor

1. Ensure you have the `.cursor/mcp.json` file in your project
2. Cursor will automatically connect to your Supabase database
3. You can verify the connection in Cursor's settings under MCP

#### Claude

1. Ensure you have the `.mcp.json` file in your project root
2. Claude will automatically connect to your Supabase database
3. You can verify the connection by asking Claude about your database

#### Windsurf

1. Ensure you have the `.windsurf/mcp.json` file in your project
2. Windsurf will automatically connect to your Supabase database
3. You can verify the connection by asking Windsurf to query your database

### 3. Start Using MCP

Once configured, you can start using natural language to interact with your database. See the [example prompts](supabase_mcp_prompts.md) for ideas on how to use MCP with your project.

## Available Tools

The Supabase MCP server provides the following tools:

### Project Management
- `list_projects`: Lists all Supabase projects
- `get_project`: Gets details for a project
- `create_project`: Creates a new Supabase project
- `pause_project`: Pauses a project
- `restore_project`: Restores a project

### Database Operations
- `list_tables`: Lists all tables within the specified schemas
- `list_extensions`: Lists all extensions in the database
- `list_migrations`: Lists all migrations in the database
- `apply_migration`: Applies a SQL migration to the database
- `execute_sql`: Executes raw SQL in the database
- `get_logs`: Gets logs for a Supabase project

### Project Configuration
- `get_project_url`: Gets the API URL for a project
- `get_anon_key`: Gets the anonymous API key for a project

### Development Tools
- `generate_typescript_types`: Generates TypeScript types based on the database schema

## Security Considerations

1. **Access Control**:
   - Consider using the `--read-only` flag for sensitive operations
   - Limit the PAT permissions to only what's needed

2. **Token Management**:
   - Store tokens securely
   - Rotate tokens regularly
   - Don't commit tokens to version control

3. **Data Privacy**:
   - Be cautious about what data is shared with AI assistants
   - Consider anonymizing sensitive data

## Troubleshooting

### MCP Server Not Starting

If the MCP server fails to start:

1. Verify that Node.js is installed and in your PATH
2. Check that your PAT is valid and has the necessary permissions
3. Try running the MCP server command manually to see any error messages:
   ```
   npx -y @supabase/mcp-server-supabase@latest --access-token=your_token
   ```

### Connection Issues

If your AI tool can't connect to Supabase:

1. Verify that your Supabase project is active
2. Check that your PAT has access to the project
3. Ensure your `.env` file has the correct Supabase URL and keys

### Punycode Deprecation Warning

If you see a warning like `[DEP0040] DeprecationWarning: The 'punycode' module is deprecated`:

1. This is coming from a dependency in the Supabase JS client
2. We've addressed this by installing the `punycode2` package as a userland alternative
3. Our test scripts use this fix by adding the following code at the top:
   ```javascript
   // Use the userland alternative to punycode to fix deprecation warning
   require.cache[require.resolve('punycode')] = {
     exports: require('punycode2')
   };
   ```
4. You can install the fix with: `npm install punycode2`

### Counting Records Error

If you see an error like `failed to parse select parameter (count(*))`:

1. The Supabase JavaScript client doesn't support the SQL-style `count(*)` syntax directly
2. Instead, use the count parameter in the select method:
   ```javascript
   // Correct way to count records
   const { count, error } = await supabase
     .from('schools')
     .select('*', { count: 'exact', head: true });
   ```
3. The `head: true` parameter makes it more efficient by not returning the actual records

## Example Integration with School Data Enrichment

### Querying Unprocessed Schools

You can ask your AI assistant:
"Show me how many schools in the database haven't been processed yet"

The AI will use MCP to execute a query like:
```sql
SELECT COUNT(*)
FROM schools s
LEFT JOIN processed_schools ps ON s.school_id = ps.school_id
WHERE ps.school_id IS NULL;
```

### Analyzing Enrichment Results

You can ask your AI assistant:
"Generate a report on our enrichment success rate by state"

The AI will use MCP to execute queries and generate a report with the results.

### Optimizing Database Schema

You can ask your AI assistant:
"Suggest improvements to our database schema for better performance"

The AI will analyze your schema and suggest optimizations like adding indexes or restructuring tables.
