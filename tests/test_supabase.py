import os
from dotenv import load_dotenv
import json
from supabase import create_client, Client

load_dotenv()

def main():
    print("Starting test script")
    try:
        # Connect to Supabase
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not supabase_url or not supabase_key:
            print("Error: SUPABASE_URL or SUPABASE_ANON_KEY environment variables are not set")
            return
        
        print(f"Connecting to Supabase at {supabase_url}")
        client = create_client(supabase_url, supabase_key)
        
        # Test the connection by querying the schools table
        result = client.table("schools").select("*").limit(1).execute()
        
        if result.data:
            print("Successfully connected to Supabase!")
            print(f"Found {len(result.data)} school(s):")
            print(json.dumps(result.data, indent=2))
        else:
            print("Connected to Supabase, but no schools found.")
            
    except Exception as e:
        print(f"Error connecting to Supabase: {e}")

if __name__ == "__main__":
    main()
