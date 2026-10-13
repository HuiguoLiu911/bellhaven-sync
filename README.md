# Bellhaven → CRM ownership sync

Keeps the CRM's facility → parent-company links for **Bellhaven Senior Living** in line with
Bellhaven's public website. It scrapes the website, matches each community to a CRM account,
queues proposed fixes with evidence, and writes to the CRM **only** when a reviewer approves the
fix in a local review app.

```
scraper.py ──► matcher.py ──► store.py (SQLite queue) ──► app.py (review UI) ──► apply.py ──► CRM API
  website        pure logic      idempotent upsert          approve / reject       only writer
```

## Run it

```bash
python -m venv .venv && .venv/Scripts/activate      # (source .venv/bin/activate on mac/linux)
pip install -r requirements.txt
echo CRM_TOKEN=<your token> > .env  # UTF-8, UTF-8-BOM and PowerShell's UTF-16 are all accepted
python -m bellhaven.pipeline     # scrape + match + queue (no CRM writes)
python -m bellhaven.app          # http://127.0.0.1:5000 to review, approve, reject
python -m bellhaven.export decisions > decisions.md   # human-readable record of every proposal and decision
python -m pytest -q tests        # 20 offline tests (fake CRM that enforces the real API's validation)
```

**Schedule.** `deploy/crontab` is the supported setup: the pipeline runs daily at 6am Central on the same
host as the review app, so both share `data/sync.db`, the decision memory that makes re-runs safe.
`.github/workflows/daily-sync.yml` is the hosted variant (DST-aware `timezone: America/Chicago`, queue kept
in the Actions cache). In production both would point `SYNC_DB` at shared storage or a real database.

## 1. Scraper (`bellhaven/scraper.py`)
* It walks every page of `/communities`, following the "Next" link until there isn't one, and opens
  each community's detail page to get the street, city/state/ZIP, care offerings, administrator and phone.
* **It also collects community links from the homepage.** The homepage says "35 communities" and
  announces *Bellhaven Meadows of Findlay*, but the directory only lists 34. Scraping only the
  directory would wrongly treat Findlay as "not on the website".
* It records the advertised count, the directory count and the discovered count. The pipeline **aborts the
  run** (no proposals at all) if the scrape looks partial: fewer locations than the directory says it lists
  (works on the very first run), fewer than 80% of the best of the last 7 runs (so the baseline can't ratchet
  down), or any detail page that didn't parse into a full address (markup changed). A site outage or redesign
  therefore can't produce "these facilities left Bellhaven" proposals.

## 2. Matching (`bellhaven/matcher.py`)
Each website location is compared with every non-parent CRM account on independent signals:

| Signal | Notes |
|---|---|
| Street (normalized) | `Boulevard→blvd`, `Northwest→nw`, `Pk→pike`, `Road→rd`… A PO Box counts as *unknown*, not a conflict |
| City / state / ZIP | ZIP mismatches with an exact street match still count as the same facility (and get a ZIP fix) |
| Administrator | The website lists the administrator; an active CRM contact with that name is strong evidence |
| Phone | Exact digits match (rare in this data, but decisive when present) |
| Name similarity | Uses core tokens only ("Bellhaven", "of", "Care Center"… are stripped). **Used only as supporting evidence**, because names are what change in an acquisition |

**Same facility** means the same state and one of these holds: an exact street match plus the same city or ZIP;
an unknown street (blank / PO Box) plus the same city plus a name, phone or administrator match; the same city plus a
phone or administrator match when the street doesn't conflict; or, when the street *does* conflict, the same city plus
**both** phone and administrator. If several accounts describe one facility, a survivor is chosen. The ranking is:
active, administrator match, phone match, **already under Bellhaven**, revenue history, most contacts, exact address,
then account id as the final tie-break. An existing Bellhaven record therefore always beats an old owner's record, so
the system never creates a third copy. Every other copy becomes a `duplicate` proposal, except an old owner's copy that
carries revenue **and** AR: the SOP says to preserve it, so it gets a `chow_link` instead (see below).

Lookalikes are shown to the reviewer as **near misses** with the reason they were rejected:
* *Amberly Manor* (website, Hudson OH) vs CRM *Amberly Manor* (Juniper Point, **Colorado Springs, CO**). Same name, different facility, so a new account is created.
* *Bellhaven at Union Square* (118 Union Square Dr) vs *Union Square Senior Living* (Juniper Point, 240 Market St). Same city and similar name, but the street, administrator and phone all differ, so a new account is created and Juniper's account is left alone.

## 3. Outcomes and how each is written

| Kind | When | Writes on approval |
|---|---|---|
| `update_fields` | Matched, already under Bellhaven, stale name/address/ZIP/care/status | PATCH changed fields + audit note |
| `reparent` | Matched under another/no parent, SOP allows a move | PATCH `parent_id` (+ renames) + note |
| `chow` | Matched under another parent **and** revenue > 0 **and** AR > 0 | POST new account under Bellhaven, then PATCH old `chow_current_account = new id`; old account otherwise untouched |
| `create` | On the website, no CRM account | POST new account under Bellhaven |
| `duplicate` | Extra record of the same facility | PATCH `duplicate_of_account = survivor`, `status = Inactive`, note; move its active contacts to the survivor |
| `chow_link` | Extra record under a *different* owner that has revenue + AR, while the survivor already represents the facility | PATCH only `chow_current_account = survivor`; nothing else touched (SOP preservation) |
| `stale_chow` | Under Bellhaven, gone from the website, another owner's account at the same address, revenue + AR | PATCH `chow_current_account = that existing account` |
| `stale_moved` | Same as above but SOP doesn't require preservation | Mark as duplicate of the new owner's record |
| `stale_review` | Under Bellhaven, gone from the website, no evidence of the new owner | `status = Needs Review` + note. Parent kept as-is, because we don't know where it went and guessing would be worse. Accounts a human already set Inactive are left alone |

"Evidence of a new owner" means an Active record at the same normalized street (and state, plus ZIP or city) that sits
under a **real** other parent. A parentless record at that address is not treated as ownership evidence.

### The billing SOP
Before any parent move, the matcher checks `lifetime_revenue` and `outstanding_ar`. If **both are > 0**, it never
proposes a re-parent. It proposes a CHOW instead (create a new account, point the old account at it, and leave the old
account otherwise exactly as is). The review card shows the two figures and the rule it applied.
* **Bellhaven of Marietta** ($51,250 / $3,800 AR) and **Bellhaven of Tiffin** ($84,000 / $12,400 AR), both under Cedar Trail, get **CHOW**.
* **Bellhaven Crossings of Lima** (Harborview, $47,000 revenue but $0 AR) gets a **direct re-parent**.
* **Bellhaven Meadows of Findlay** (no parent, $22,000 / $0 AR) gets a **direct re-parent**.
* **Bellhaven of Sandusky** ($130,000 / $5,200 AR) has dropped off the Bellhaven site, and *Millstone Care of Sandusky*
  already exists at the same address under Millstone. That means the facility changed hands and the
  "account under the correct parent" already exists. Creating a third record would add a duplicate, so the old account's
  `chow_current_account` is pointed at the existing Millstone account. Its parent and everything else stay untouched.
* Accounts that are already under Bellhaven and carry AR (Akron, Defiance, Meadville) don't need a parent change, so the SOP
  doesn't apply to them.

## 4. Review app (`bellhaven/app.py`)
Each card shows the reasoning, the website record (with a link to the page it was scraped from), the CRM record(s)
(linked to the CRM browser), the match signals (✔/✘/▲), a billing SOP box, the exact before → after writes,
and any near misses that were considered. **Approve** writes to the CRM immediately. **Reject** records the decision.
Tabs show pending, applied, rejected, failed, superseded and matched (no change) items.

Apply safety (`apply.py`, `crm.py`):
* **One execution per proposal.** Approve atomically claims the row (`pending/failed → applying`), so a double-click,
  a second tab or a second reviewer can't run the same writes twice. Pressing Enter in the note box does not submit.
* **No writes on stale facts.** Before writing, every target record is re-read and the write is refused (status
  `failed`) if any field the proposal relied on changed, **including `lifetime_revenue` and `outstanding_ar`**, so an
  account that picked up AR after the proposal can't be re-parented in breach of the SOP.
* **No duplicate creates.** A create is refused if a live account already exists at that street + ZIP under the target
  parent. POSTs are never retried by the HTTP client (only idempotent GET/PATCH are), so a 5xx on a create that
  actually committed can't produce a second account.
* **Resumable.** Multi-step proposals (CHOW = create then link) persist progress after each step; a retry resumes at
  the failed step. A failed row with partial progress is never auto-superseded, and rejecting it keeps the record of
  what was already written (e.g. the created account id). Any exception, network errors included, marks the row `failed`.
* **Notes are appended, never overwritten**: the dated `[date bellhaven-sync]` line is appended to the account's *current*
  note at write time, so a note a rep added after the pipeline ran is kept.

## 5. Daily runs and idempotency (`store.py`)
* Every proposal has a `key` (what it's about, e.g. `reparent:<account_id>`) and a `fingerprint` (a hash of the
  exact change, excluding the dated note).
* If the same key and fingerprint has already been **approved or rejected**, it is skipped on later runs. A rejected
  item stays rejected unless the facts change, in which case the fingerprint changes and it is re-proposed.
* Pending items are refreshed in place (no duplicates in the queue). Pending items that a run no longer produces
  (for example, someone fixed the CRM by hand) are marked **superseded**.
* Once applied, an item drops out naturally on the next run: the CRM now matches the website. Accounts already carrying
  `duplicate_of_account` or `chow_current_account` are treated as retired and are never matched again, so a
  CHOW'd facility doesn't come back as a "duplicate" of its own successor. The same holds mid-CHOW: if the new account
  was created but the link step failed, the old account is recognised from the successor's `CHOW successor of <id>` note.
* Only one run at a time: the pipeline refuses to start while another run (cron or the app's "Run now") is active.
* **The decision memory is `data/sync.db`.** Keep it (back it up, or point `SYNC_DB` at shared storage); a fresh
  clone without it would re-propose things that were rejected. `python -m bellhaven.export decisions` writes a readable copy.
* `tests/test_pipeline.py` proves this on a fake CRM: run → approve everything (reject one) → run again gives 0 new,
  1 already decided, and all 35 locations as clean matches; plus regression tests for double approve, partial CHOW
  failure, network errors, POST retries, SOP inputs changing, notes edited by a rep, and partial/broken scrapes.

## Judgment calls / limitations
* **Phone numbers**: the website and CRM phones disagree for most accounts. A CRM phone could be a direct line, so phone
  mismatches are shown as evidence but never auto-proposed as changes.
* **Care type**: the CRM holds one value. It is updated only if the CRM value isn't among the website's offerings
  (`Short-Term Rehabilitation & Nursing → Skilled Nursing`, `Memory Support → Memory Care`).
* **Kettering** has three records (Harborview, Cedar Trail, and one with no parent), none with revenue or contacts. The survivor is
  picked deterministically. The reviewer can reject that choice if they prefer a different one.
* **Alliance and Coldwater** are under Bellhaven but not on the website, and there's no evidence of a new owner, so they're set to
  Needs Review rather than having their parent guessed or cleared.
