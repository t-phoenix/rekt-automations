import os
import traceback
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_KEY")
sb = create_client(url, key)

try:
    print("Testing nonexistent table:")
    res = sb.table("this_table_does_not_exist").select("*").limit(1).execute()
    print("Select nonexistent worked?", res)
except Exception as e:
    print("Error doing select on nonexistent:", type(e), repr(e))

try:
    print("Testing rekt_meme_twitter_engagement select:")
    res = sb.table("rekt_meme_twitter_engagement").select("*").limit(1).execute()
    print("Select engagement worked!", res)
except Exception as e:
    print("Error doing select on engagement:", type(e), repr(e))
    
try:
    print("Testing rekt_meme_trend_research select:")
    res = sb.table("rekt_meme_trend_research").select("*").limit(1).execute()
    print("Select trend worked!", res)
except Exception as e:
    print("Error doing select on trend:", type(e), repr(e))

