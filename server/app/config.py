from dotenv import load_dotenv
import os
from pathlib import Path


env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    
# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Razorpay configuration
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_SECRET")

# Razorpay webhook secret
RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET")

# Validate environment variables
if not SUPABASE_URL:
    raise ValueError(
        "SUPABASE_URL environment variable is not set.\n"
        "Please create a .env file (copy from .env.example) and add your Supabase credentials."
    )

if not SUPABASE_KEY:
    raise ValueError(
        "SUPABASE_KEY environment variable is not set.\n"
        "Please create a .env file (copy from .env.example) and add your Supabase credentials."
    )
    
# Paths
BASE_DIR = Path(__file__).parent.parent
DOWNLOADS_DIR = BASE_DIR / "downloads"
COOKIES_DIR = BASE_DIR / "app" / "cookies"
COOKIE_PATH = COOKIES_DIR / "cookies.txt"

# Download settings
DEFAULT_DOWNLOAD_TIMEOUT = 600  # 10 minutes
DEFAULT_FFMPEG_TIMEOUT = 300  # 5 minutes

# Cache configuration
MAX_CACHE_SIZE = 5 * 1024 * 1024 * 1024  # 5GB default
CLEANUP_THRESHOLD = 0.8  # Cleanup when 80% full
CLEANUP_TARGET = 0.7  # Clean down to 70% of max size