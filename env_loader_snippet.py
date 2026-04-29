# ----------------------------------------------------------------
# Optional: load .env config without external deps.
# Drop this near the top of fingerprint_runner.py if you want to avoid
# passing --base-url etc. on the command line.
# ----------------------------------------------------------------
import os
from pathlib import Path

def load_env(path=".env"):
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

load_env()
# Then in argparse, replace required=True with default=os.environ.get("BASE_URL"):
#   ap.add_argument("--base-url", default=os.environ.get("BASE_URL"), required=not os.environ.get("BASE_URL"))
#   ap.add_argument("--api-key", default=os.environ.get("API_KEY"))
#   ap.add_argument("--model",   default=os.environ.get("MODEL"))
