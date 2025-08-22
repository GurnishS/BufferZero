from supabase import create_client, Client
from app.config import SUPABASE_URL, SUPABASE_KEY
from app.logger import logger
import traceback

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    logger.info("✅ Supabase client initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize Supabase client: {e}")
    logger.error(traceback.format_exc())
    raise