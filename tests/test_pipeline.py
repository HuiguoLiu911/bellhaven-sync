"""Offline tests: matcher decisions on a real snapshot + full approve/re-run cycle on a fake CRM."""
import copy
import json
from pathlib import Path

import pytest

from bellhaven import store
from bellhaven.apply import apply_proposal
from bellhaven.crm import CRMError
from bellhaven.matcher import build_proposals

SNAP = json.loads((Path(__file__).parent / "fixtures" / "snapshot_2026-10-12.json").read_text())
BH = "0015QAPLGS3FVYEEEM"


class FakeCRM:
    """In-memory CRM that enforces the same rules the real API reported (mutable fields, status values)."""
    ACCT_MUTABLE = {"name", "parent_id", "status", "note", "care_type", "phone", "billing_street", "billing_city",
                    "billing_state", "billing_zip", "chow_current_account", "duplicate_of_account"}
    CONTACT_MUTABLE = {"name", "title", "email", "phone", "is_active", "account_id"}
    STATUSES = {"Active", "Inactive", "Needs Review"}

    def __init__(self, accounts, contacts):
        self.a = {x["account_id"]: copy.deepcopy(x) for x in accounts}
        self.c = {x["contact_id"]: copy.deepcopy(x) for x in contacts}
        self.n = 0
        self.posts = 0

    def _validate(self, f, mutable):
        bad = set(f) - mutable
        if not f or bad:
            raise CRMError(f"422 No mutable fields / unknown fields {bad}")
        if "status" in f and f["status"] not in self.STATUSES:
            raise CRMError(f"422 status must be one of {self.STATUSES}")

    def accounts(self, zip=None):
        return [copy.deepcopy(a) for a in self.a.values() if zip is None or a.get("billing_zip") == zip]

    def contacts(self): return list(copy.deepcopy(self.c).values())
    def account(self, i): return copy.deepcopy(self.a[i])
    def contact(self, i): return copy.deepcopy(self.c[i])

    def update_contact(self, i, f):
        self._validate(f, self.CONTACT_MUTABLE)
        self.c[i].update(f)

    def update_account(self, i, f):
        self._validate(f, self.ACCT_MUTABLE)
        self.a[i].update(f)
        if "parent_id" in f:
            self.a[i]["parent_name"] = self.a.get(f["parent_id"], {}).get("name", "")

    def create_account(self, f):
        self._validate(f, self.ACCT_MUTABLE)
        if not f.get("name"):
            raise CRMError("422 name is required")
        self.posts += 1
        self.n += 1
        new = {"account_id": f"NEW{self.n:03d}", "lifetime_revenue": 0, "outstanding_ar": 0,
               "chow_current_account": "", "duplicate_of_account": "", "note": "", "created_by_candidate": True,
               "parent_name": self.a[f["parent_id"]]["name"], **f}
        self.a[new["account_id"]] = new
        return new


@pytest.fixture
def props():
    return {p["key"]: p for p in build_proposals(SNAP["locs"], SNAP["accts"], SNAP["cons"])}


def test_sop_chow_vs_reparent(props):
    # Marietta/Tiffin: revenue AND AR > 0 -> CHOW (old account untouched except pointer)
    for acct in ("001A34WFSUYHCRBLFT", "001U6RW32TY0WSXZZB"):
        p = props[f"chow:{acct}"]
        assert [a["op"] for a in p["actions"]] == ["create", "update"]
        assert p["actions"][1]["fields"] == {"chow_current_account": "$new"}
    # Lima has revenue but AR == 0 -> direct re-parent
    assert props["reparent:001LGFPBJY4N9MB6KL"]["actions"][0]["fields"]["parent_id"] == BH
    # Sandusky dropped off the site, Millstone owns it, revenue+AR -> link, don't touch parent
    assert props["stale_chow:001SXSF4ELF0Z2LGDM->0017JP8Z1UQ763BVK3"]["actions"][0]["fields"] == \
        {"chow_current_account": "0017JP8Z1UQ763BVK3"}


def test_lookalikes_are_not_matched(props):
    assert "create:amberly-manor" in props            # CRM Amberly Manor is in Colorado
    assert "create:bellhaven-at-union-square" in props  # Union Square Senior Living: other address/admin
    assert not any(k.startswith("duplicate:001GNU41AVXZRLLJ9P") for k in props)


def test_full_cycle_is_idempotent(tmp_path, monkeypatch):
    crm = FakeCRM(SNAP["accts"], SNAP["cons"])
    db = store.connect(tmp_path / "t.db")

    def run():
        rid = store.start_run(db)
        s = store.upsert_proposals(db, rid, build_proposals(SNAP["locs"], crm.accounts(), crm.contacts()))
        store.finish_run(db, rid, "ok", s)
        return s

    first = run()
    assert first["new"] == 29
    pending = store.listing(db, "pending")
    reject_id = next(r["id"] for r in pending if r["kind"] == "stale_review")
    store.set_status(db, reject_id, "rejected", "test")
    for r in pending:
        if r["id"] != reject_id:
            res = apply_proposal(db, r["id"], crm=crm)
            assert "error" not in res, res

    second = run()
    assert second["new"] == 0, second            # nothing re-proposed after decisions
    assert second["already_decided"] == 1        # the rejected one stays rejected
    assert second["confirmed"] == 35             # every website location now matches cleanly
    # CHOW'd accounts kept their old parent
    assert crm.a["001A34WFSUYHCRBLFT"]["parent_name"].startswith("Cedar Trail")
    assert crm.a["001SXSF4ELF0Z2LGDM"]["parent_id"] == BH
    third = run()
    assert third["new"] == 0 and third["superseded"] == 0


# ---------------------------------------------------------------- apply-safety tests
def _queue(tmp_path, crm):
    db = store.connect(tmp_path / "t.db")
    rid = store.start_run(db)
    store.upsert_proposals(db, rid, build_proposals(SNAP["locs"], crm.accounts(), crm.contacts()))
    return db, {r["key"]: r["id"] for r in store.listing(db, "pending")}


def test_double_approve_creates_once(tmp_path):
    crm = FakeCRM(SNAP["accts"], SNAP["cons"])
    db, ids = _queue(tmp_path, crm)
    pid = ids["create:bellhaven-of-batavia"]
    apply_proposal(db, pid, crm=crm)
    with pytest.raises(ValueError):          # second click is refused, not re-executed
        apply_proposal(db, pid, crm=crm)
    assert sum(a["name"] == "Bellhaven of Batavia" for a in crm.a.values()) == 1


def test_chow_partial_failure_retry_does_not_duplicate(tmp_path):
    crm = FakeCRM(SNAP["accts"], SNAP["cons"])
    db, ids = _queue(tmp_path, crm)
    pid = ids["chow:001A34WFSUYHCRBLFT"]
    real_update = crm.update_account
    crm.update_account = lambda i, f: (_ for _ in ()).throw(CRMError("boom"))  # fail after the create
    res = apply_proposal(db, pid, crm=crm)
    assert "error" in res and store.get(db, pid)["status"] == "failed"
    crm.update_account = real_update
    res = apply_proposal(db, pid, crm=crm)   # retry resumes at step 2
    assert "error" not in res
    new = [a for a in crm.a.values() if a["name"] == "Bellhaven of Marietta" and a["parent_id"] == BH]
    assert len(new) == 1
    old = crm.a["001A34WFSUYHCRBLFT"]
    assert old["chow_current_account"] == new[0]["account_id"]
    assert old["parent_name"].startswith("Cedar Trail")      # old account otherwise untouched
    assert old["name"] == "Bellhaven of Marietta" and old["status"] == "Active"


def test_crm_changed_after_proposal_blocks_write(tmp_path):
    crm = FakeCRM(SNAP["accts"], SNAP["cons"])
    db, ids = _queue(tmp_path, crm)
    pid = ids["reparent:001LGFPBJY4N9MB6KL"]               # Lima
    crm.a["001LGFPBJY4N9MB6KL"]["parent_id"] = "001YRHHXQ5HJ0TCL2U"   # someone edits CRM meanwhile
    res = apply_proposal(db, pid, crm=crm)
    assert "error" in res and "changed since" in res["error"]
    assert crm.a["001LGFPBJY4N9MB6KL"]["parent_id"] == "001YRHHXQ5HJ0TCL2U"  # nothing written


def test_revenue_without_ar_reparents_directly(props):
    p = props["reparent:001LGFPBJY4N9MB6KL"]               # Lima: $47k revenue, $0 AR
    assert p["evidence"]["sop"]["lifetime_revenue"] > 0 and p["evidence"]["sop"]["outstanding_ar"] == 0
    assert not any(a["op"] == "create" for a in p["actions"])


def test_orphan_at_same_address_is_not_ownership_evidence():
    accts = copy.deepcopy(SNAP["accts"])
    for a in accts:
        if a["account_id"] == "0017JP8Z1UQ763BVK3":          # make the Millstone Sandusky record parentless
            a["parent_id"], a["parent_name"] = "", ""
    keys = {p["key"] for p in build_proposals(SNAP["locs"], accts, SNAP["cons"])}
    assert "stale_review:001SXSF4ELF0Z2LGDM" in keys
    assert not any(k.startswith("stale_chow:001SXSF4ELF0Z2LGDM") for k in keys)


# ---------------------------------------------------------------- regression tests from the review
def test_concurrent_approve_is_claimed_once(tmp_path):
    crm = FakeCRM(SNAP["accts"], SNAP["cons"])
    db, ids = _queue(tmp_path, crm)
    pid = ids["create:bellhaven-of-batavia"]
    assert store.claim(db, pid)              # another tab/thread got there first
    with pytest.raises(ValueError):
        apply_proposal(db, pid, crm=crm)
    assert crm.posts == 0


def test_post_is_never_retried_but_get_is(monkeypatch):
    from bellhaven import crm as crm_mod

    class R:
        status_code, text = 502, "bad gateway"
        def json(self): return {}
    calls = []
    c = crm_mod.CRM(token="t", base="http://x")
    monkeypatch.setattr(c.s, "request", lambda m, u, **kw: calls.append(m) or R())
    monkeypatch.setattr(crm_mod.time, "sleep", lambda s: None)
    with pytest.raises(CRMError):
        c.create_account({"name": "x"})
    assert calls == ["POST"]
    calls.clear()
    with pytest.raises(CRMError):
        c.account("a")
    assert calls == ["GET"] * 3


def test_network_error_marks_failed_not_stuck(tmp_path):
    import requests
    crm = FakeCRM(SNAP["accts"], SNAP["cons"])
    db, ids = _queue(tmp_path, crm)
    pid = ids["create:bellhaven-of-batavia"]
    crm.create_account = lambda f: (_ for _ in ()).throw(requests.ConnectionError("reset"))
    res = apply_proposal(db, pid, crm=crm)
    assert "ConnectionError" in res["error"] and store.get(db, pid)["status"] == "failed"


def test_create_refused_when_account_already_exists(tmp_path):
    crm = FakeCRM(SNAP["accts"], SNAP["cons"])
    db, ids = _queue(tmp_path, crm)
    crm.create_account({"name": "Batavia (added by hand)", "parent_id": BH, "billing_street": "2000 Hospital Drive",
                        "billing_city": "Batavia", "billing_state": "OH", "billing_zip": "45103", "status": "Active"})
    res = apply_proposal(db, ids["create:bellhaven-of-batavia"], crm=crm)
    assert "already exists" in res["error"] and crm.posts == 1


def test_note_is_appended_to_live_note(tmp_path):
    crm = FakeCRM(SNAP["accts"], SNAP["cons"])
    db, ids = _queue(tmp_path, crm)
    crm.a["001NXP9X46CWEPSLSV"]["note"] = "Rep: billing goes to the PO Box, keep it on invoices"
    res = apply_proposal(db, ids["update:001NXP9X46CWEPSLSV"], crm=crm)   # Ashtabula
    assert "error" not in res
    note = crm.a["001NXP9X46CWEPSLSV"]["note"]
    assert note.startswith("Rep: billing goes to the PO Box") and "bellhaven-sync" in note


def test_sop_inputs_changing_blocks_reparent(tmp_path):
    crm = FakeCRM(SNAP["accts"], SNAP["cons"])
    db, ids = _queue(tmp_path, crm)
    crm.a["001LGFPBJY4N9MB6KL"]["outstanding_ar"] = 2500   # Lima now has AR -> CHOW, not re-parent
    res = apply_proposal(db, ids["reparent:001LGFPBJY4N9MB6KL"], crm=crm)
    assert "changed since" in res["error"]
    assert crm.a["001LGFPBJY4N9MB6KL"]["parent_id"] != BH


def test_half_applied_chow_does_not_propose_successor_as_duplicate(tmp_path):
    crm = FakeCRM(SNAP["accts"], SNAP["cons"])
    db, ids = _queue(tmp_path, crm)
    real = crm.update_account
    crm.update_account = lambda i, f: (_ for _ in ()).throw(CRMError("boom"))
    apply_proposal(db, ids["chow:001A34WFSUYHCRBLFT"], crm=crm)          # create ok, link failed
    crm.update_account = real
    keys = {p["key"] for p in build_proposals(SNAP["locs"], crm.accounts(), crm.contacts())}
    assert not any(k.startswith("duplicate:") and "001A34WFSUYHCRBLFT" in k for k in keys)
    assert not any(k.startswith(("chow:001A34", "create:bellhaven-of-marietta")) for k in keys)
    # ...and the failed row (with progress) survives a re-run instead of being superseded
    rid = store.start_run(db)
    store.upsert_proposals(db, rid, build_proposals(SNAP["locs"], crm.accounts(), crm.contacts()))
    assert store.get(db, ids["chow:001A34WFSUYHCRBLFT"])["status"] == "failed"
    assert "error" not in apply_proposal(db, ids["chow:001A34WFSUYHCRBLFT"], crm=crm)
    assert crm.posts == 1


def test_reject_keeps_partial_progress_record(tmp_path):
    crm = FakeCRM(SNAP["accts"], SNAP["cons"])
    db, ids = _queue(tmp_path, crm)
    pid = ids["chow:001A34WFSUYHCRBLFT"]
    crm.update_account = lambda i, f: (_ for _ in ()).throw(CRMError("boom"))
    apply_proposal(db, pid, crm=crm)
    assert store.reject(db, pid, "changed my mind")
    assert json.loads(store.get(db, pid)["result"])["created"] == ["NEW001"]
    assert not store.reject(db, pid)                      # can't re-reject / flip a decided row


def test_inactive_bellhaven_account_is_not_flipped_to_needs_review():
    accts = copy.deepcopy(SNAP["accts"])
    next(a for a in accts if a["account_id"] == "00116ETS45BL7DTQP7")["status"] = "Inactive"   # Alliance
    keys = {p["key"] for p in build_proposals(SNAP["locs"], accts, SNAP["cons"])}
    assert "stale_review:00116ETS45BL7DTQP7" not in keys


def test_existing_bellhaven_record_beats_old_owner_record_with_ar():
    accts = copy.deepcopy(SNAP["accts"])
    ct = next(a for a in accts if a["account_id"] == "0011AB44D05WLA9HTX")   # Cedar Trail of Monroe
    ct["lifetime_revenue"], ct["outstanding_ar"] = 40000, 900
    props_ = {p["key"]: p for p in build_proposals(SNAP["locs"], accts, SNAP["cons"])}
    assert "chow_link:0011AB44D05WLA9HTX->001U1750VLVJAGG1S5" in props_      # linked, not retired
    assert not any(k.startswith("chow:") and "0011AB44" in k for k in props_)  # no third account
    assert "duplicate:0011AB44D05WLA9HTX->001U1750VLVJAGG1S5" not in props_


def test_conflicting_street_needs_phone_and_admin():
    from bellhaven.matcher import compare
    loc = next(l for l in SNAP["locs"] if l["slug"] == "bellhaven-of-maplewood")
    other = copy.deepcopy(next(a for a in SNAP["accts"] if a["account_id"] == "0019M1Z45PGV2DJ971"))  # 431 Main St
    other["phone"] = loc["phone"]                                        # phone alone, different street
    assert not compare(loc, other, [])["same"]


def test_scrape_guard():
    from bellhaven.pipeline import ScrapeRejected, check_scrape
    locs = SNAP["locs"]
    meta = {"directory_count": 34, "advertised_count": 35}
    assert check_scrape(locs, meta, [35, 35]) == []
    with pytest.raises(ScrapeRejected):                  # a directory page went missing (works on first run)
        check_scrape(locs[:20], meta, [])
    with pytest.raises(ScrapeRejected):                  # baseline can't ratchet down run by run
        check_scrape(locs[:27], {}, [35, 30, 28])
    broken = copy.deepcopy(locs); broken[0]["street"] = ""
    with pytest.raises(ScrapeRejected):                  # markup drift -> blank address
        check_scrape(broken, meta, [])
