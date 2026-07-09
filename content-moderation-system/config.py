"""
config.py
---------
Central place for all configuration values.

Why this file exists:
Instead of scattering settings (like database paths, thresholds, secret keys)
all over the code, we keep them in ONE place. This makes the project easy to
tweak later -- e.g. if you want to make the moderation stricter, you only
need to change one number here.
"""

import os
from dotenv import load_dotenv

# Load variables from a .env file if one exists (useful for secrets/API keys)
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
os.makedirs(INSTANCE_DIR, exist_ok=True)

# Get the host and port from environment variables (for public access)
# Default: 0.0.0.0 listens on all network interfaces, port 5000
APP_HOST = os.environ.get("APP_HOST", "0.0.0.0")
APP_PORT = int(os.environ.get("APP_PORT", 5000))


class Config:
    # Flask secret key (used for sessions, flash messages, etc.)
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-this")

    # SQLite database file location.
    # SQLite is a simple, file-based database - perfect for local development.
    # (In the original Azure design, Azure Cosmos DB played this role.)
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(
    INSTANCE_DIR,
    "moderation.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ---- Moderation thresholds ----
    # Text is flagged as "toxic" if its toxicity score (0.0 - 1.0) is >= this value
    TEXT_TOXICITY_THRESHOLD = 0.5

    # Images above this file size (in MB) are auto-flagged for manual review
    # (simple placeholder rule until a real image-analysis model is plugged in)
    IMAGE_SIZE_FLAG_MB = 8

    # ---- Optional: Azure integration placeholders ----
    # If you later get Azure credentials, fill these in and switch the
    # moderator classes (see moderation/text_moderator.py and
    # moderation/image_moderator.py) to call the real Azure AI Vision /
    # Azure AI Language APIs instead of the local logic.
    AZURE_VISION_KEY = os.environ.get("AZURE_VISION_KEY", "")
    AZURE_VISION_ENDPOINT = os.environ.get("AZURE_VISION_ENDPOINT", "")
    AZURE_LANGUAGE_KEY = os.environ.get("AZURE_LANGUAGE_KEY", "")
    AZURE_LANGUAGE_ENDPOINT = os.environ.get("AZURE_LANGUAGE_ENDPOINT", "")
