import os
from dotenv import load_dotenv

load_dotenv()

from supabase import create_client, Client

def get_supabase_client() -> Client:
    """
    Initialize and return the Supabase client using environment variables.
    Requires SUPABASE_URL and SUPABASE_SERVICE_KEY mapping.
    """
    url: str = os.getenv("SUPABASE_URL")
    key: str = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not url or not key:
        raise ValueError("Supabase environment variables (SUPABASE_URL, SUPABASE_SERVICE_KEY) are missing.")
        
    return create_client(url, key)

def upload_to_storage(client: Client, bucket_name: str, file_path: str, storage_path: str, content_type: str = None) -> bool:
    """
    Upload a local file to a Supabase Storage bucket.
    """
    try:
        with open(file_path, 'rb') as f:
            # We use upsert=True to overwrite existing files if the exact same path is used.
            opts = {"upsert": "true"}
            if content_type:
                opts['content-type'] = content_type
                
            response = client.storage.from_(bucket_name).upload(
                file=f,
                path=storage_path,
                file_options=opts
            )
            return True
    except Exception as e:
        print(f"Error uploading {file_path} to Supabase Storage: {e}")
        return False
