"""Project paths — .env always resolved from repo root, not from cwd."""

from pathlib import Path

# beauty-booking/
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"
