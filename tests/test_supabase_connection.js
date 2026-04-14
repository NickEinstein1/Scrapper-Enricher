/**
 * Simple script to test Supabase connection
 */

// Import required modules
const { createClient } = require('@supabase/supabase-js');

// Supabase credentials from .env file
const SUPABASE_URL = 'https://onpxncsesssxbpboirlj.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9ucHhuY3Nlc3NzeGJwYm9pcmxqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzQxMzg0MjcsImV4cCI6MjA0OTcxNDQyN30.7dfq18qKd-iOxBNj3XCbbwgrsECBB_y2s1RX5NM7WL4';

// Create a Supabase client
const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

async function testConnection() {
  try {
    console.log('Testing connection to Supabase...');

    // Test the connection by fetching schools
    const { data, error } = await supabase
      .from('schools')
      .select('*')
      .limit(1);

    if (error) {
      console.error('Connection error:', error.message);
      return;
    }

    console.log('Successfully connected to Supabase!');
    console.log('Data:', data);

    // Test the PAT
    console.log('\nTesting Personal Access Token (PAT)...');
    console.log('PAT: sbp_d389d43851756e4985e9db1ab285ca5c893b5c31');

    // In a real scenario, we would use the PAT to authenticate
    // For now, we'll just check if it's a valid format
    const pat = 'sbp_d389d43851756e4985e9db1ab285ca5c893b5c31';
    if (pat.startsWith('sbp_') && pat.length > 20) {
      console.log('PAT format is valid.');
      console.log('Note: Full PAT validation requires the Supabase Management API.');
    } else {
      console.error('PAT format is invalid.');
    }

  } catch (err) {
    console.error('Unexpected error:', err.message);
  }
}

// Run the test
testConnection();
