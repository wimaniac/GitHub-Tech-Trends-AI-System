"""
Cấu hình cho GitHub Tech Trends AI System.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# === Đường dẫn ===
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "github_trends.db"
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

# === GitHub API ===
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_API_BASE = "https://api.github.com"
GITHUB_TRENDING_URL = "https://github.com/trending"

# Rate limiting
MAX_REQUESTS_PER_HOUR = 5000 if GITHUB_TOKEN else 60
REQUEST_DELAY = 1.0  # giây giữa các request

# === Thu thập dữ liệu ===
TRENDING_SINCE = ["daily", "weekly", "monthly"]

# === AI Model ===
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
MIN_CLUSTER_SIZE = 5
CLUSTERING_MIN_SAMPLES = 3

# === Gemini AI ===
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.0-flash"

# === Scheduler ===
COLLECT_INTERVAL_HOURS = 6      # Thu thập trending mỗi 6 giờ
ANALYSIS_INTERVAL_HOURS = 12    # Phân tích mỗi 12 giờ

# === API Server ===
API_HOST = "0.0.0.0"
API_PORT = 8001
