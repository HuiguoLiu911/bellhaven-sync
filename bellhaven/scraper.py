"""Scrape every Bellhaven community from the public website.

Discovery is deliberately broad: we walk every page of the /communities directory
AND collect any /communities/<slug> link on the homepage, because the site
announces new communities on the homepage before they appear in the directory
(e.g. "Bellhaven Meadows of Findlay": homepage says 35, directory lists 34).
"""
from __future__ import annotations

import re
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from .config import SITE_BASE

SLUG_RE = re.compile(r"^/communities/[a-z0-9-]+/?$")
CITY_STATE_ZIP_RE = re.compile(r"^(?P<city>.+?),\s*(?P<state>[A-Z]{2})\s+(?P<zip>\d{5})(?:-\d{4})?$")


def _get(session: requests.Session, url: str, retries: int = 3) -> str:
    for attempt in range(retries):
        try:
            r = session.get(url, timeout=30)
            r.raise_for_status()
            return r.text
        except requests.RequestException:
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)
    raise RuntimeError("unreachable")


def _links(html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for a in soup.select("a[href]"):
        href = a["href"].split("?")[0].split("#")[0]
        if SLUG_RE.match(href):
            out.append(href.rstrip("/"))
    return out


def discover_slugs(session: requests.Session) -> tuple[list[str], dict]:
    """Return community paths plus discovery metadata (where each was found)."""
    found: dict[str, set[str]] = {}

    home = _get(session, SITE_BASE + "/")
    for p in _links(home):
        found.setdefault(p, set()).add("homepage")
    m = re.search(r"serve\s+(\d+)\s+communities", home)
    advertised = int(m.group(1)) if m else None

    page, listed = 1, None
    seen_pages = set()
    while page not in seen_pages and page < 100:
        seen_pages.add(page)
        html = _get(session, f"{SITE_BASE}/communities?page={page}")
        if listed is None:
            m = re.search(r"(\d+)\s+communities listed", html)
            listed = int(m.group(1)) if m else None
        links = _links(html)
        for p in links:
            found.setdefault(p, set()).add(f"directory p{page}")
        soup = BeautifulSoup(html, "html.parser")
        nxt = next((a for a in soup.select(".pager a") if "Next" in a.get_text()), None)
        if not nxt or not links:
            break
        m = re.search(r"page=(\d+)", nxt["href"])
        page = int(m.group(1)) if m else page + 1

    meta = {"advertised_count": advertised, "directory_count": listed,
            "discovered_count": len(found),
            "found_in": {k: sorted(v) for k, v in found.items()}}
    return sorted(found), meta


def parse_detail(html: str, url: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    name = soup.select_one(".wrap h1").get_text(strip=True)
    fields: dict[str, object] = {}
    for dt in soup.select("dl.detail dt"):
        dd = dt.find_next_sibling("dd")
        label = dt.get_text(strip=True).lower()
        if label == "address":
            lines = [s.strip() for s in dd.stripped_strings]
            fields["street"] = lines[0] if lines else ""
            m = CITY_STATE_ZIP_RE.match(lines[-1]) if len(lines) > 1 else None
            if m:
                fields.update(city=m["city"], state=m["state"], zip=m["zip"])
            else:
                fields.update(city="", state="", zip="", address_raw=" | ".join(lines))
        elif label == "care offerings":
            fields["care_offerings"] = [b.get_text(strip=True) for b in dd.select(".badge")]
        else:
            fields[label] = dd.get_text(" ", strip=True)
    return {
        "slug": url.rstrip("/").rsplit("/", 1)[-1],
        "url": url,
        "name": name,
        "street": fields.get("street", ""),
        "city": fields.get("city", ""),
        "state": fields.get("state", ""),
        "zip": fields.get("zip", ""),
        "care_offerings": fields.get("care_offerings", []),
        "administrator": fields.get("administrator", ""),
        "phone": fields.get("phone", ""),
    }


def scrape() -> tuple[list[dict], dict]:
    s = requests.Session()
    s.headers["User-Agent"] = "bellhaven-crm-sync/1.0"
    paths, meta = discover_slugs(s)
    locations = []
    for p in paths:
        url = urljoin(SITE_BASE, p)
        loc = parse_detail(_get(s, url), url)
        loc["found_in"] = meta["found_in"][p]
        locations.append(loc)
    return locations, meta


if __name__ == "__main__":
    import json
    locs, meta = scrape()
    print(json.dumps({k: v for k, v in meta.items() if k != "found_in"}, indent=1))
    for l in locs:
        print(f"{l['name']:<55} {l['street']:<32} {l['city']}, {l['state']} {l['zip']}  {l['care_offerings']}  {l['found_in']}")
