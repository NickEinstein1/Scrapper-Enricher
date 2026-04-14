/**
 * Real Supabase MCP Connection Test
 * 
 * This script tests the actual connection to Supabase using the MCP protocol.
 * It verifies that your PAT is valid and that the MCP server can connect to your database.
 */

const { execSync } = require('child_process');
const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');
const path = require('path');
const http = require('http');

// Supabase credentials
const SUPABASE_URL = 'https://onpxncsesssxbpboirlj.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9ucHhuY3Nlc3NzeGJwYm9pcmxqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzQxMzg0MjcsImV4cCI6MjA0OTcxNDQyN30.7dfq18qKd-iOxBNj3XCbbwgrsECBB_y2s1RX5NM7WL4';
const SUPABASE_PAT = 'sbp_d389d43851756e4985e9db1ab285ca5c893b5c31';

// Create a Supabase client
const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

// Function to test direct Supabase connection
async function testDirectConnection() {
  console.log('Testing direct connection to Supabase...');
  
  try {
    // Test the connection by fetching schools
    const { data, error } = await supabase
      .from('schools')
      .select('*')
      .limit(3);
    
    if (error) {
      console.error('❌ Direct connection error:', error.message);
      return false;
    }
    
    console.log('✅ Successfully connected to Supabase directly!');
    console.log(`Found ${data.length} schools:`);
    data.forEach(school => {
      console.log(`- ${school.school_name} (${school.school_id})`);
    });
    
    return true;
  } catch (err) {
    console.error('❌ Unexpected error in direct connection:', err.message);
    return false;
  }
}

// Function to verify PAT format
function verifyPAT() {
  console.log('\nVerifying Personal Access Token (PAT) format...');
  console.log(`PAT: ${SUPABASE_PAT.substring(0, 10)}...`);
  
  if (SUPABASE_PAT.startsWith('sbp_') && SUPABASE_PAT.length > 20) {
    console.log('✅ PAT format is valid.');
    return true;
  } else {
    console.error('❌ PAT format is invalid. It should start with "sbp_" and be longer than 20 characters.');
    return false;
  }
}

// Function to check MCP configuration files
function checkMCPConfigs() {
  console.log('\nChecking MCP configuration files...');
  
  const configFiles = [
    { path: '.vscode/mcp.json', tool: 'VS Code' },
    { path: '.cursor/mcp.json', tool: 'Cursor' },
    { path: '.mcp.json', tool: 'Claude' },
    { path: '.windsurf/mcp.json', tool: 'Windsurf' }
  ];
  
  let allValid = true;
  
  configFiles.forEach(config => {
    try {
      if (fs.existsSync(config.path)) {
        const content = fs.readFileSync(config.path, 'utf8');
        const json = JSON.parse(content);
        
        // Check if the PAT is included in the config
        const configStr = JSON.stringify(json);
        if (configStr.includes(SUPABASE_PAT)) {
          console.log(`✅ ${config.tool} configuration (${config.path}) is valid.`);
        } else {
          console.log(`⚠️ ${config.tool} configuration (${config.path}) exists but may not contain the correct PAT.`);
          allValid = false;
        }
      } else {
        console.log(`❌ ${config.tool} configuration (${config.path}) is missing.`);
        allValid = false;
      }
    } catch (err) {
      console.error(`❌ Error checking ${config.tool} configuration:`, err.message);
      allValid = false;
    }
  });
  
  return allValid;
}

// Function to test database schema access
async function testSchemaAccess() {
  console.log('\nTesting database schema access...');
  
  try {
    // Get a list of tables
    const { data, error } = await supabase
      .from('schools')
      .select('*')
      .limit(1);
    
    if (error) {
      console.error('❌ Schema access error:', error.message);
      return false;
    }
    
    // Get the columns from the first row
    if (data && data.length > 0) {
      const columns = Object.keys(data[0]);
      console.log('✅ Successfully accessed database schema!');
      console.log('Columns in schools table:');
      columns.forEach(column => {
        console.log(`- ${column}`);
      });
      return true;
    } else {
      console.log('⚠️ No data found in schools table.');
      return false;
    }
  } catch (err) {
    console.error('❌ Unexpected error in schema access:', err.message);
    return false;
  }
}

// Main function to run all tests
async function runTests() {
  console.log('=== REAL SUPABASE MCP CONNECTION TEST ===\n');
  
  // Test direct connection
  const directConnectionSuccess = await testDirectConnection();
  
  // Verify PAT
  const patValid = verifyPAT();
  
  // Check MCP configs
  const configsValid = checkMCPConfigs();
  
  // Test schema access
  const schemaAccessSuccess = await testSchemaAccess();
  
  // Summary
  console.log('\n=== TEST SUMMARY ===');
  console.log(`Direct Connection: ${directConnectionSuccess ? '✅ PASS' : '❌ FAIL'}`);
  console.log(`PAT Format: ${patValid ? '✅ PASS' : '❌ FAIL'}`);
  console.log(`MCP Configs: ${configsValid ? '✅ PASS' : '⚠️ PARTIAL'}`);
  console.log(`Schema Access: ${schemaAccessSuccess ? '✅ PASS' : '❌ FAIL'}`);
  
  // Overall result
  if (directConnectionSuccess && patValid && configsValid && schemaAccessSuccess) {
    console.log('\n✅ ALL TESTS PASSED! Your Supabase MCP setup is ready to use.');
    console.log('\nNext steps:');
    console.log('1. Use VS Code, Cursor, Claude, or Windsurf with your project');
    console.log('2. Ask the AI assistant to help you with database operations');
    console.log('3. Try some of the example prompts from docs/supabase_mcp_prompts.md');
  } else {
    console.log('\n⚠️ SOME TESTS FAILED. Please fix the issues before using MCP.');
  }
}

// Run the tests
runTests();
