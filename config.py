import os
from dotenv import load_dotenv

load_dotenv()

# Environment variables
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
JOB_API_KEY = os.environ.get("JOB_API_KEY") 
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

SEEN_JOBS_FILE = "seen_jobs.txt"
CACHE_DIR = "cache"
MATCH_THRESHOLD = int(os.environ.get("MATCH_THRESHOLD", 40)) # Configurable match threshold

os.makedirs(CACHE_DIR, exist_ok=True)
