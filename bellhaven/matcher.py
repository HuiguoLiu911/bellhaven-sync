"""Match scraped Bellhaven locations to CRM accounts and turn the result into proposals.

Pure functions only: input is (locations, accounts, contacts); output is a list of
proposal dicts. Nothing here talks to the network, so it is easy to test and re-run.

Proposal kinds
--------------
confirmed      location <-> account match, already correct; no write (shown for audit)
update_fields  matched account under Bellhaven, but name/address/care type/status is stale
reparent       matched account under another/no parent; SOP allows moving it directly
chow           matched account under another parent, has revenue AND outstanding AR:
               create a new account under Bellhaven, point old.chow_current_account at it
create         location on the website with no CRM account
duplicate      extra CRM account for the same facility -> duplicate_of_account + Inactive
stale_chow     Bellhaven account no longer on website, a different owner's account exists
               at the same address, and SOP requires preserving the old account
stale_moved    same as above but SOP does not require preservation -> mark duplicate of
               the new owner's record
stale_review   Bellhaven account no longer on website, no evidence of who owns it now
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import date

from .config import BELLHAVEN_PARENT_ID, BELLHAVEN_PARENT_NAME

TAG = "bellhaven-sync"
CHOW_NOTE_RE = re.compile(r"CHOW successor of (\w+)")


def today() -> str:  # evaluated per call: the review app is long-running
    return date.today().isoformat()

CARE_MAP = {
    "assisted living": "Assisted Living",
    "memory support": "Memory Care",
    "memory care": "Memory Care",
    "short-term rehabilitation & nursing": "Skilled Nursing",
    "skilled nursing": "Skilled Nursing",
    "independent living": "Independent Living",
}

STREET_ABBR = {
    "street": "st", "avenue": "ave", "av": "ave", "road": "rd", "drive": "dr", "lane": "ln",
    "boulevard": "blvd", "court": "ct", "place": "pl", "parkway": "pkwy", "pk": "pike",
    "pke": "pike", "highway": "hwy", "circle": "cir", "terrace": "ter", "square": "sq",
    "north": "n", "south": "s", "east": "e", "west": "w",
    "northwest": "nw", "northeast": "ne", "southwest": "sw", "southeast": "se",
    "saint": "st", "suite": "ste",
}
NAME_STOP = {"the", "of", "at", "a", "and", "bellhaven"}
NAME_GENERIC = {"senior", "living", "care", "center", "centre", "healthcare", "health",
                "nursing", "rehabilitation", "rehab", "retirement", "home", "community",
                "communities", "campus", "assisted"}


# ---------------------------------------------------------------- normalizers
def _tokens(s: str) -> list[str]:
    s = (s or "").lower().replace("&", " and ")
    return re.findall(r"[a-z0-9]+", s)


def norm_street(s: str) -> str:
    return " ".join(STREET_ABBR.get(t, t) for t in _tokens(s))


def is_po_box(s: str) -> bool:
    return bool(re.match(r"^\s*p\.?\s*o\.?\s*box\b", s or "", re.I))


def name_core(s: str) -> set[str]:
    return {t for t in _tokens(s) if t not in NAME_STOP and t not in NAME_GENERIC}


def name_sim(a: str, b: str) -> float:
    x, y = name_core(a), name_core(b)
    if not x or not y:
        return 0.0
    return len(x & y) / len(x | y)


def digits(s: str) -> str:
    return re.sub(r"\D", "", s or "")


def care_types(offerings: list[str]) -> list[str]:
    out = []
    for o in offerings:
        m = CARE_MAP.get(o.strip().lower())
        if m and m not in out:
            out.append(m)
    return out


def is_parent_account(a: dict) -> bool:
    return a["name"].endswith("(Parent Account)") or not (a.get("billing_street") or a.get("billing_city"))


def fingerprint(obj) -> str:
    return hashlib.sha1(json.dumps(obj, sort_keys=True).encode()).hexdigest()[:12]


def note_line_append(existing: str, line: str) -> str:
    return f"{existing.rstrip()}\n{line}" if existing and existing.strip() else line


def stamp(existing: str, msg: str) -> str:
    return note_line_append(existing, f"[{today()} {TAG}] {msg}")


# ---------------------------------------------------------------- evidence
def compare(loc: dict, acct: dict, contacts: list[dict]) -> dict:
    """Score how strongly a website location and a CRM account describe the same facility."""
    a_street = acct.get("billing_street") or ""
    if is_po_box(a_street) or not a_street:
        addr = "unknown"
    elif norm_street(a_street) == norm_street(loc["street"]):
        addr = "exact"
    else:
        addr = "conflict"
    same_state = (acct.get("billing_state") or "").upper() == loc["state"].upper()
    same_city = (acct.get("billing_city") or "").strip().lower() == loc["city"].strip().lower()
    same_zip = (acct.get("billing_zip") or "") == loc["zip"]
    phone = bool(digits(loc.get("phone"))) and digits(loc.get("phone")) == digits(acct.get("phone"))
    admin_contacts = [c for c in contacts if c["account_id"] == acct["account_id"] and c.get("is_active")
                      and loc.get("administrator") and c["name"].strip().lower() == loc["administrator"].strip().lower()]
    admin = bool(admin_contacts)
    ns = name_sim(loc["name"], acct["name"])

    same = same_state and (
        (addr == "exact" and (same_zip or same_city))
        or (addr == "unknown" and same_city and (ns >= 0.5 or phone or admin))
        # a conflicting street needs BOTH phone and administrator to agree; one alone is not enough
        or (same_city and addr != "conflict" and (phone or admin))
        or (same_city and phone and admin)
    )
    signals = []
    signals.append(("ok" if addr == "exact" else "warn" if addr == "unknown" else "bad",
                    {"exact": f"Street matches after normalization ('{a_street}' ~ '{loc['street']}')",
                     "unknown": f"CRM street '{a_street or '(blank)'}' is not a physical address",
                     "conflict": f"Street differs: CRM '{a_street}' vs website '{loc['street']}'"}[addr]))
    signals.append(("ok" if same_city and same_state else "bad",
                    f"City/state: CRM {acct.get('billing_city')}, {acct.get('billing_state')} vs website {loc['city']}, {loc['state']}"))
    signals.append(("ok" if same_zip else "warn", f"ZIP: CRM {acct.get('billing_zip') or '(blank)'} vs website {loc['zip']}"))
    signals.append(("ok" if phone else "info", f"Phone: CRM {acct.get('phone') or '(blank)'} vs website {loc.get('phone')}"))
    if loc.get("administrator"):
        signals.append(("ok" if admin else "info",
                        f"Website administrator '{loc['administrator']}' "
                        + ("is an active contact on this account" if admin else "is not a contact on this account")))
    signals.append(("ok" if ns >= 0.5 else "info", f"Name similarity {ns:.2f}: '{acct['name']}' vs '{loc['name']}'"))
    return {"same": same, "addr": addr, "phone": phone, "admin": admin, "name_sim": ns,
            "same_city": same_city, "same_state": same_state, "signals": signals}


def snapshot(acct: dict, contacts: list[dict]) -> dict:
    keys = ["account_id", "name", "parent_id", "parent_name", "billing_street", "billing_city", "billing_state",
            "billing_zip", "care_type", "status", "phone", "lifetime_revenue", "outstanding_ar",
            "chow_current_account", "duplicate_of_account", "note"]
    snap = {k: acct.get(k) for k in keys}
    snap["contacts"] = [f"{c['name']} ({c.get('title') or '-'})" for c in contacts
                        if c["account_id"] == acct["account_id"] and c.get("is_active")]
    return snap


def sop_check(acct: dict) -> dict:
    rev, ar = float(acct.get("lifetime_revenue") or 0), float(acct.get("outstanding_ar") or 0)
    preserve = rev > 0 and ar > 0
    return {"lifetime_revenue": rev, "outstanding_ar": ar, "preserve_old": preserve,
            "decision": ("Revenue history AND outstanding AR > 0 -> billing needs the old account preserved: "
                         "do NOT re-parent; create a new account under the correct parent and set "
                         "chow_current_account on the old one.") if preserve else
                        ("No revenue history" if rev <= 0 else "No outstanding AR")
                        + " -> SOP allows re-parenting the existing account directly."}


# ---------------------------------------------------------------- main entry
def build_proposals(locations: list[dict], accounts: list[dict], contacts: list[dict]) -> list[dict]:
    by_id = {a["account_id"]: a for a in accounts}
    parent = by_id.get(BELLHAVEN_PARENT_ID) or next((a for a in accounts if a["name"] == BELLHAVEN_PARENT_NAME), None)
    if parent is None:
        raise RuntimeError(f"Parent account {BELLHAVEN_PARENT_ID} / '{BELLHAVEN_PARENT_NAME}' not found in CRM")
    bh_id = parent["account_id"]

    # Old accounts whose CHOW successor already exists (created by an approved CHOW whose link step
    # has not landed yet). Treat them as retired so the successor isn't proposed as their duplicate.
    chow_pending = {m.group(1) for a in accounts for m in [CHOW_NOTE_RE.search(a.get("note") or "")] if m}

    def retired(a):  # already resolved by an earlier decision; never a match candidate
        return bool(a.get("duplicate_of_account") or a.get("chow_current_account")) or a["account_id"] in chow_pending

    facilities = [a for a in accounts if not is_parent_account(a)]
    live = [a for a in facilities if not retired(a)]
    proposals: list[dict] = []
    claimed: set[str] = set()

    def pname(pid):
        return by_id[pid]["name"] if pid in by_id else "(no parent)"

    for loc in locations:
        site = {k: loc.get(k) for k in ["name", "street", "city", "state", "zip", "care_offerings",
                                        "administrator", "phone", "url", "found_in"]}
        comps = {a["account_id"]: compare(loc, a, contacts) for a in live}
        matches = [a for a in live if comps[a["account_id"]]["same"]]
        near = [a for a in facilities if a not in matches and (
            (comps.get(a["account_id"], {}).get("same_city") and name_sim(loc["name"], a["name"]) >= 0.5)
            or name_sim(loc["name"], a["name"]) >= 0.99)]
        near_ev = []
        for a in near:
            c = comps.get(a["account_id"]) or compare(loc, a, contacts)
            near_ev.append({"account": snapshot(a, contacts), "signals": c["signals"],
                            "why_rejected": "retired (duplicate/CHOW) record" if retired(a) else
                            "Similar name but address/location evidence says it is a different facility"})

        if not matches:
            care = care_types(loc["care_offerings"])
            fields = {"name": loc["name"], "parent_id": bh_id, "billing_street": loc["street"],
                      "billing_city": loc["city"], "billing_state": loc["state"], "billing_zip": loc["zip"],
                      "care_type": care[0] if care else "", "phone": loc.get("phone", ""), "status": "Active",
                      "note": stamp("", f"Created from Bellhaven website listing {loc['url']}.")}
            proposals.append(_p("create", f"create:{loc['slug']}", f"Create account for {loc['name']}",
                                loc["slug"], None,
                                [{"op": "create", "ref": "new", "fields": fields}],
                                {"website": site, "crm": [], "near_misses": near_ev,
                                 "reasoning": "No CRM account matches this location's address, or its city plus phone/administrator."
                                              + (" Similar-named accounts were checked and rejected (see near misses)." if near_ev else "")}))
            continue

        # choose the surviving record among all accounts that describe this facility
        def rank(a):
            c = comps[a["account_id"]]
            # an existing Bellhaven record wins over an old owner's record, so we never create a third copy
            return (a.get("status") != "Inactive", c["admin"], c["phone"], a.get("parent_id") == bh_id,
                    float(a.get("lifetime_revenue") or 0) > 0,
                    len([x for x in contacts if x["account_id"] == a["account_id"]]),
                    c["addr"] == "exact", a["account_id"])
        matches.sort(key=rank, reverse=True)
        surv, losers = matches[0], matches[1:]
        claimed.update(a["account_id"] for a in matches)
        sc = comps[surv["account_id"]]
        evidence = {"website": site, "crm": [snapshot(surv, contacts)], "signals": sc["signals"],
                    "near_misses": near_ev,
                    "duplicates": [snapshot(a, contacts) for a in losers]}

        diffs = _field_diffs(loc, surv)
        on_bh = surv.get("parent_id") == bh_id
        if on_bh and not diffs:
            proposals.append(_p("confirmed", f"confirmed:{loc['slug']}:{surv['account_id']}",
                                f"{loc['name']} matches {surv['name']}", loc["slug"], surv["account_id"], [],
                                {**evidence, "reasoning": "Matched; parent, name and address already correct."}))
        elif on_bh:
            fields = {k: v[1] for k, v in diffs.items()}
            fields["note"] = stamp(surv.get("note", ""), "Updated " + ", ".join(diffs) + f" to match {loc['url']}.")
            proposals.append(_p("update_fields", f"update:{surv['account_id']}",
                                f"Update {', '.join(diffs)} on {surv['name']}", loc["slug"], surv["account_id"],
                                [{"op": "update", "account_id": surv["account_id"], "fields": fields,
                                  "before": _before(surv, fields)}],
                                {**evidence, "diffs": diffs,
                                 "reasoning": "Correct parent already; website shows newer values for: " + ", ".join(diffs) + "."}))
        else:
            sop = sop_check(surv)
            old_parent = pname(surv.get("parent_id"))
            if sop["preserve_old"]:
                care = care_types(loc["care_offerings"])
                new_fields = {"name": loc["name"], "parent_id": bh_id, "billing_street": loc["street"],
                              "billing_city": loc["city"], "billing_state": loc["state"], "billing_zip": loc["zip"],
                              "care_type": care[0] if care else surv.get("care_type", ""),
                              "phone": loc.get("phone") or surv.get("phone", ""), "status": "Active",
                              "note": stamp("", f"CHOW successor of {surv['account_id']} ({surv['name']}, previously under "
                                                f"{old_parent}). Old account preserved for billing per SOP.")}
                proposals.append(_p("chow", f"chow:{surv['account_id']}",
                                    f"CHOW: {surv['name']} ({old_parent} -> Bellhaven)", loc["slug"], surv["account_id"],
                                    [{"op": "create", "ref": "new", "fields": new_fields},
                                     {"op": "update", "account_id": surv["account_id"],
                                      "fields": {"chow_current_account": "$new"},
                                      "before": _before_sop(surv, {"chow_current_account": ""})}],
                                    {**evidence, "sop": sop, "diffs": diffs,
                                     "reasoning": f"Facility is listed on the Bellhaven website but the CRM account sits under "
                                                  f"{old_parent}. {sop['decision']}"}))
            else:
                fields = {"parent_id": bh_id, **{k: v[1] for k, v in diffs.items()}}
                fields["note"] = stamp(surv.get("note", ""),
                                       f"Re-parented from {old_parent} to Bellhaven ({loc['url']})"
                                       + (f"; updated {', '.join(diffs)}" if diffs else "") + ".")
                proposals.append(_p("reparent", f"reparent:{surv['account_id']}",
                                    f"Re-parent {surv['name']}: {old_parent} -> Bellhaven", loc["slug"], surv["account_id"],
                                    [{"op": "update", "account_id": surv["account_id"], "fields": fields,
                                      "before": _before_sop(surv, fields)}],
                                    {**evidence, "sop": sop, "diffs": diffs,
                                     "reasoning": f"Listed on the Bellhaven website but parented to {old_parent}. {sop['decision']}"}))

        for los in losers:
            lc = comps[los["account_id"]]
            lsop = sop_check(los)
            if lsop["preserve_old"] and los.get("parent_id") != surv.get("parent_id"):
                lp = pname(los.get("parent_id"))
                proposals.append(_p("chow_link", f"chow_link:{los['account_id']}->{surv['account_id']}",
                                    f"CHOW link: {los['name']} [{lp}] -> {surv['name']}", loc["slug"], los["account_id"],
                                    [{"op": "update", "account_id": los["account_id"],
                                      "fields": {"chow_current_account": surv["account_id"]},
                                      "before": _before_sop(los, {"chow_current_account": ""})}],
                                    {"website": site, "crm": [snapshot(los, contacts), snapshot(surv, contacts)],
                                     "signals": lc["signals"], "sop": lsop,
                                     "reasoning": f"Same facility as {surv['account_id']}, which is the current record. This copy is "
                                                  f"under {lp} with revenue history and outstanding AR, so per SOP it is preserved "
                                                  f"exactly as is and only linked to the current account via chow_current_account."}))
                continue
            note = stamp(los.get("note", ""), f"Duplicate of {surv['account_id']} ({surv['name']}); same facility "
                                              f"({loc['street']}, {loc['city']}).")
            actions = [{"op": "update", "account_id": los["account_id"],
                        "fields": {"duplicate_of_account": surv["account_id"], "status": "Inactive", "note": note},
                        "before": _before_sop(los, {"duplicate_of_account": "", "status": "", "note": ""})}]
            for c in sorted(contacts, key=lambda c: c["contact_id"]):
                if c["account_id"] == los["account_id"] and c.get("is_active"):
                    actions.append({"op": "move_contact", "contact_id": c["contact_id"], "label": c["name"],
                                    "fields": {"account_id": surv["account_id"]},
                                    "before": {"account_id": los["account_id"]}})
            proposals.append(_p("duplicate", f"duplicate:{los['account_id']}->{surv['account_id']}",
                                f"Duplicate: {los['name']} [{pname(los.get('parent_id'))}] -> {surv['name']}",
                                loc["slug"], los["account_id"], actions,
                                {"website": site, "crm": [snapshot(los, contacts), snapshot(surv, contacts)],
                                 "signals": lc["signals"],
                                 "survivor_rule": "active > administrator match > phone match > already under Bellhaven > "
                                                  "revenue history > number of contacts > exact street > account id (tie-break)",
                                 "reasoning": f"Same facility as surviving record {surv['account_id']} (ranked: active, administrator/phone "
                                              f"match, already under Bellhaven, revenue history, contacts, exact address, then account id). "
                                              f"No merge in the API, so the losing copy is marked Inactive with duplicate_of_account"
                                              + (", and its active contacts are moved to the survivor." if len(actions) > 1 else ".")}))

    # Bellhaven accounts that are no longer on the website
    for a in live:
        if a.get("parent_id") != bh_id or a["account_id"] in claimed or a.get("status") == "Inactive":
            continue  # Inactive = a human already closed it out; don't flip it to Needs Review
        # "Now owned by someone else" needs a record at the same physical address that sits under a
        # *real* other parent; an orphan record at that address is not evidence of a new owner.
        others = [o for o in live if o["account_id"] != a["account_id"]
                  and o.get("parent_id") and o.get("parent_id") != bh_id and o.get("status") != "Inactive"
                  and o.get("billing_state") == a.get("billing_state") and a.get("billing_street")
                  and not is_po_box(a["billing_street"])
                  and norm_street(o.get("billing_street")) == norm_street(a["billing_street"])
                  and (o.get("billing_zip") == a.get("billing_zip") or o.get("billing_city") == a.get("billing_city"))]
        snap = snapshot(a, contacts)
        base_ev = {"website": None, "crm": [snap], "sop": sop_check(a),
                   "website_check": f"Not found among {len(locations)} communities scraped from the Bellhaven website "
                                    f"(directory pages + homepage) on {today()}."}
        if others:
            o = sorted(others, key=lambda x: (x.get("status") != "Active", x["account_id"]))[0]
            owner = pname(o.get("parent_id"))
            ev = {**base_ev, "crm": [snap, snapshot(o, contacts)]}
            if base_ev["sop"]["preserve_old"]:
                proposals.append(_p("stale_chow", f"stale_chow:{a['account_id']}->{o['account_id']}",
                                    f"CHOW: {a['name']} now owned by {owner}", None, a["account_id"],
                                    [{"op": "update", "account_id": a["account_id"],
                                      "fields": {"chow_current_account": o["account_id"]},
                                      "before": _before_sop(a, {"chow_current_account": ""})}],
                                    {**ev, "reasoning": f"No longer on the Bellhaven website, and {owner} already has an account "
                                                        f"({o['name']}) at the same address, so the facility changed ownership. "
                                                        f"{base_ev['sop']['decision']} The current-owner account already exists, "
                                                        f"so we link to it instead of creating a second copy."}))
            else:
                note = stamp(a.get("note", ""), f"Facility now owned by {owner}; current record is {o['account_id']} ({o['name']}).")
                proposals.append(_p("stale_moved", f"stale_moved:{a['account_id']}->{o['account_id']}",
                                    f"{a['name']} now owned by {owner} - retire Bellhaven copy", None, a["account_id"],
                                    [{"op": "update", "account_id": a["account_id"],
                                      "fields": {"duplicate_of_account": o["account_id"], "status": "Inactive", "note": note},
                                      "before": _before_sop(a, {"duplicate_of_account": "", "status": "", "note": ""})}],
                                    {**ev, "reasoning": f"No longer on the Bellhaven website; {owner} has a record at the same "
                                                        f"address. {base_ev['sop']['decision']} The {owner} record already "
                                                        f"represents the facility, so this copy is retired as its duplicate."}))
        else:
            if a.get("status") == "Needs Review":
                continue
            note = stamp(a.get("note", ""), "No longer listed on the Bellhaven website; current owner unknown. "
                                            "Parent left as-is pending research.")
            proposals.append(_p("stale_review", f"stale_review:{a['account_id']}",
                                f"{a['name']} no longer on Bellhaven website", None, a["account_id"],
                                [{"op": "update", "account_id": a["account_id"],
                                  "fields": {"status": "Needs Review", "note": note},
                                  "before": _before(a, {"status": "", "note": ""})}],
                                {**base_ev, "reasoning": "Under the Bellhaven parent but not on the website, and no other "
                                                         "CRM account at that address points to a new owner. We can't tell "
                                                         "whether it was sold, closed or renamed, so flag it for a human "
                                                         "instead of guessing a parent."}))
    # id -> name lookup so the review UI can show account names next to raw ids
    names = {a["account_id"]: a["name"] for a in accounts}
    for p in proposals:
        ids = {v for act in p["actions"] for v in act.get("fields", {}).values()} | \
              {v for act in p["actions"] for v in (act.get("before") or {}).values()}
        p["evidence"]["names"] = {i: names[i] for i in ids if isinstance(i, str) and i in names}
    return proposals


def _field_diffs(loc: dict, acct: dict) -> dict:
    d = {}
    if loc["name"].strip() != (acct.get("name") or "").strip():
        d["name"] = (acct.get("name"), loc["name"])
    a_street = acct.get("billing_street") or ""
    if is_po_box(a_street) or norm_street(a_street) != norm_street(loc["street"]):
        d["billing_street"] = (a_street, loc["street"])
    if (acct.get("billing_city") or "").strip().lower() != loc["city"].strip().lower():
        d["billing_city"] = (acct.get("billing_city"), loc["city"])
    if (acct.get("billing_state") or "").upper() != loc["state"].upper():
        d["billing_state"] = (acct.get("billing_state"), loc["state"])
    if (acct.get("billing_zip") or "") != loc["zip"]:
        d["billing_zip"] = (acct.get("billing_zip"), loc["zip"])
    care = care_types(loc["care_offerings"])
    if care and acct.get("care_type") not in care:
        d["care_type"] = (acct.get("care_type"), care[0])
    if acct.get("status") != "Active":
        d["status"] = (acct.get("status"), "Active")
    return d


def _before(acct: dict, fields: dict) -> dict:
    return {k: acct.get(k) for k in fields if k != "note"}


def _before_sop(acct: dict, fields: dict) -> dict:
    """Also pin the SOP inputs: if revenue/AR change before approval, the decision must be re-made."""
    return {**_before(acct, fields), "lifetime_revenue": acct.get("lifetime_revenue"),
            "outstanding_ar": acct.get("outstanding_ar")}


def _p(kind, key, title, slug, account_id, actions, evidence) -> dict:
    # Fingerprint the substance of the change (notes carry a date stamp, so exclude them):
    # a decided proposal is suppressed on re-runs unless the proposed change itself differs.
    for a in actions:  # the dated note line is appended to the live note at apply time
        if "note" in a.get("fields", {}):
            a["note_line"] = a["fields"]["note"].splitlines()[-1]
    substance = [{**{k: v for k, v in a.items() if k not in ("label", "note_line")},
                  "fields": {k: v for k, v in a.get("fields", {}).items() if k != "note"}} for a in actions]
    return {"kind": kind, "key": key, "title": title, "slug": slug, "account_id": account_id,
            "actions": actions, "evidence": evidence, "fingerprint": fingerprint(substance)}
