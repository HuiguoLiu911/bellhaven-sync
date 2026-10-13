import os
from pathlib import Path

SITE_BASE = os.environ.get("BELLHAVEN_SITE", "https://analyst-assessment-production.up.railway.app")
API_BASE = os.environ.get("CRM_API_BASE", SITE_BASE + "/api/v1")
# Token is read from the environment (or a local .env file) so it never lands in git.
ROOT = Path(__file__).resolve().parent.parent


def _load_dotenv():
    env = ROOT / ".env"
    if env.exists():
        # Windows PowerShell `echo ... > .env` writes UTF-16; other editors may add a UTF-8 BOM or quotes.
        raw = env.read_bytes()
        text = raw.decode("utf-16") if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else raw.decode("utf-8-sig", errors="replace")
        for line in text.splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip("\"' "))


_load_dotenv()
CRM_TOKEN = os.environ.get("CRM_TOKEN", "")
DB_PATH = Path(os.environ.get("SYNC_DB", ROOT / "data" / "sync.db"))
CRM_BROWSER = f"{SITE_BASE}/crm/{CRM_TOKEN}/accounts"

BELLHAVEN_PARENT_NAME = "Bellhaven Senior Living (Parent Account)"
# Look the parent up by id first (names can be edited in the CRM); name is the fallback.
BELLHAVEN_PARENT_ID = os.environ.get("BELLHAVEN_PARENT_ID", "0015QAPLGS3FVYEEEM")
