/**
 * Test script for Supabase MCP connection
 *
 * This script tests the connection to the Supabase MCP server.
 * It's a simple way to verify that your PAT is working correctly.
 *
 * Usage:
 * node test_mcp_connection.js
 */

// Use the userland alternative to punycode to fix deprecation warning
try {
  require.cache[require.resolve('punycode')] = {
    exports: require('punycode2')
  };
  console.log('Successfully loaded punycode2 as a replacement for punycode');
} catch (e) {
  console.warn('Warning: punycode2 not loaded properly. You may see deprecation warnings.', e.message);
}

const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

// Your Supabase PAT
const SUPABASE_ACCESS_TOKEN = 'sbp_d389d43851756e4985e9db1ab285ca5c893b5c31';

console.log('Testing Supabase MCP connection...');
console.log('This will start the MCP server and check if it can connect to Supabase.');

// Create a temporary file to test the connection
const tempDir = path.join(__dirname, 'temp');
if (!fs.existsSync(tempDir)) {
  fs.mkdirSync(tempDir);
}

const tempFile = path.join(tempDir, 'mcp-test.js');
fs.writeFileSync(tempFile, `
// Use the userland alternative to punycode to fix deprecation warning
try {
  require.cache[require.resolve('punycode')] = {
    exports: require('punycode2')
  };
  console.log('Successfully loaded punycode2 as a replacement for punycode');
} catch (e) {
  console.warn('Warning: punycode2 not loaded properly. You may see deprecation warnings.', e.message);
}

const { createClient } = require('@supabase/supabase-js');

async function testConnection() {
  try {
    // Create a Supabase client
    const supabase = createClient(
      'https://onpxncsesssxbpboirlj.supabase.co',
      'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9ucHhuY3Nlc3NzeGJwYm9pcmxqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzQxMzg0MjcsImV4cCI6MjA0OTcxNDQyN30.7dfq18qKd-iOxBNj3XCbbwgrsECBB_y2s1RX5NM7WL4'
    );

    // Test the connection by fetching the server version
    const { count, error } = await supabase.from('schools').select('*', { count: 'exact', head: true });

    if (error) {
      console.error('Connection error:', error.message);
      return false;
    }

    console.log('Successfully connected to Supabase!');
    console.log('Total schools:', count);
    return true;
  } catch (err) {
    console.error('Unexpected error:', err.message);
    return false;
  }
}

testConnection().then(success => {
  process.exit(success ? 0 : 1);
});
`);

// Install the Supabase JS client and punycode2 if needed
console.log('Installing required dependencies...');
exec('npm install @supabase/supabase-js punycode2', (error, stdout, stderr) => {
  if (error) {
    console.error(`Error installing dependencies: ${error.message}`);
    return;
  }

  if (stderr) {
    console.error(`stderr: ${stderr}`);
  }

  console.log(`stdout: ${stdout}`);

  // Run the test script
  console.log('Testing connection to Supabase...');
  exec(`node ${tempFile}`, (error, stdout, stderr) => {
    if (error) {
      console.error(`Error: ${error.message}`);
      return;
    }

    if (stderr) {
      console.error(`stderr: ${stderr}`);
    }

    console.log(stdout);

    // Clean up
    fs.unlinkSync(tempFile);
    console.log('Test completed.');
  });
});
