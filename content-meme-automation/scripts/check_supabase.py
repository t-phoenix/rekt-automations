#!/usr/bin/env python3
"""
Simple script to test the connection to Supabase Database and Storage.

Usage:
    python scripts/check_supabase.py
"""
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

load_dotenv(project_root / ".env")

try:
    from src.utils.supabase_client import get_supabase_client
except ImportError:
    print("❌ Error: Could not import supabase_client.")
    print("Make sure 'supabase' is installed: pip install supabase")
    sys.exit(1)

def check_supabase_connection():
    print("=" * 60)
    print("🔍 CHECKING SUPABASE CONNECTION")
    print("=" * 60)
    
    try:
        client = get_supabase_client()
        print("✅ Environment Variables: Loaded successfully")
        
        # Check Database Connection via an arbitrary query (e.g. limit 1 from rekt_meme_automation_runs)
        try:
            db_res = client.table("rekt_meme_automation_runs").select("id").limit(1).execute()
            print("✅ Database Connection:  Connected successfully (rekt_meme_automation_runs table accessible)")
        except Exception as e:
            print(f"❌ Database Connection:  Failed to query 'rekt_meme_automation_runs' table.\n   Error: {e}")
            print("   Did you run the 'scripts/supabase_schema.sql' in your Supabase SQL Editor?")
            
        # Check Storage Connection by listing the bucket
        try:
            storage_res = client.storage.get_bucket("rekt_media")
            print(f"✅ Storage Bucket:     'rekt_media' accessible (Public: {storage_res.public})")
        except Exception as e:
            print(f"❌ Storage Bucket:     Failed to access 'rekt_media' bucket.\n   Error: {e}")
            print("   Did you run the 'scripts/supabase_schema.sql' in your Supabase SQL Editor?")
            
    except ValueError as ve:
        print(f"❌ Missing Configuration: {ve}")
        print("Please check your .env file for SUPABASE_URL and SUPABASE_SERVICE_KEY")
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        
    print("=" * 60)

if __name__ == "__main__":
    check_supabase_connection()
