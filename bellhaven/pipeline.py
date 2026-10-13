"""Daily entry point: scrape -> fetch CRM -> match -> queue proposals. Never writes to the CRM.

    python -m bellhaven.pipeline
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone

from . import store
from .crm import CRM
from .matcher import build_proposals
from .scraper import scrape

# If the website suddenly lists far fewer communities (outage, redesign, broken parser) we
# would otherwise flag real accounts as "no longer on the website". Refuse instead.
MIN_FRACTION_OF_RECENT_MAX = 0.8
RECENT_RUNS = 7
STALE_LOCK_MINUTES = 30


class ScrapeRejected(RuntimeError):
    pass


def check_scrape(locations: list[dict], meta: dict, recent_counts: list[int]) -> list[str]:
    """Raise ScrapeRejected if the scrape looks partial/broken; return non-fatal warnings."""
    problems = []
    if not locations:
        problems.append("scrape returned 0 locations")
    directory = meta.get("directory_count")
    if directory and len(locations) < directory:
        # every community the directory says it lists must have been scraped (works on the first run too)
        problems.append(f"directory says {directory} communities but only {len(locations)} were scraped")
    if recent_counts and len(locations) < max(recent_counts) * MIN_FRACTION_OF_RECENT_MAX:
        # compare against the best recent run, so a slow decline can't ratchet the baseline down
        problems.append(f"{len(locations)} locations vs {max(recent_counts)} in recent runs")
    bad = [l["url"] for l in locations if not all(l.get(k) for k in ("name", "street", "city", "state", "zip"))]
    if bad:
        problems.append(f"{len(bad)} detail page(s) could not be parsed into a full address (markup changed?): {bad[:3]}")
    if problems:
        raise ScrapeRejected("; ".join(problems) + ". Aborting to avoid false proposals.")
    warnings = []
    if meta.get("advertised_count") and len(locations) < meta["advertised_count"]:
        warnings.append(f"site advertises {meta['advertised_count']} communities, scraped {len(locations)}")
    return warnings


def _recent_counts(db) -> list[int]:
    rows = db.execute("SELECT stats FROM runs WHERE status='ok' ORDER BY id DESC LIMIT ?", (RECENT_RUNS,)).fetchall()
    out = []
    for r in rows:
        try:
            out.append(int(json.loads(r["stats"] or "{}").get("locations") or 0))
        except (ValueError, TypeError):
            continue
    return [n for n in out if n]


def _another_run_in_progress(db, run_id: int) -> bool:
    cutoff = (datetime.now(timezone.utc) - timedelta(minutes=STALE_LOCK_MINUTES)).strftime("%Y-%m-%d %H:%M:%SZ")
    return db.execute("SELECT 1 FROM runs WHERE status='running' AND id<>? AND started_at>?",
                      (run_id, cutoff)).fetchone() is not None


def run() -> dict:
    db = store.connect()
    run_id = store.start_run(db)
    try:
        if _another_run_in_progress(db, run_id):  # cron and the app's "Run now" button share one queue
            raise RuntimeError("another pipeline run is in progress")
        locations, site_meta = scrape()
        warnings = check_scrape(locations, site_meta, _recent_counts(db))
        for w in warnings:
            print(f"WARNING: {w}", file=sys.stderr)
        crm = CRM()
        accounts, contacts = crm.accounts(), crm.contacts()
        proposals = build_proposals(locations, accounts, contacts)
        stats = store.upsert_proposals(db, run_id, proposals)
        stats.update(locations=len(locations), accounts=len(accounts), warnings=warnings,
                     site_advertised=site_meta.get("advertised_count"), site_directory=site_meta.get("directory_count"))
        store.finish_run(db, run_id, "ok", stats)
        return stats
    except Exception as e:
        store.finish_run(db, run_id, "error", {"error": str(e)})
        raise


if __name__ == "__main__":
    print(json.dumps(run(), indent=1))
