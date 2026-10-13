"""Execute an approved proposal against the CRM. Only ever called from the review app.

Safety rules:
  * a proposal is claimed atomically (pending/failed -> applying), so a double-click or a
    second browser tab can never execute the same writes twice;
  * every target record is re-read first; if anything the proposal relied on changed
    (including lifetime_revenue / outstanding_ar, the SOP inputs) the write is refused;
  * a create is refused if a live account for that address already exists under the
    target parent;
  * notes are appended to the CRM's *current* note at write time, never overwritten;
  * progress is persisted after every step, so a retry resumes instead of re-creating;
  * any exception (API error, network error, bad JSON) marks the proposal 'failed'.
"""
from __future__ import annotations

import json

from . import store
from .crm import CRM
from .matcher import is_parent_account, norm_street, note_line_append


class StaleProposal(RuntimeError):
    pass


def _norm(v):
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return float(v)
    return "" if v is None else str(v).strip()


def _live(crm: CRM, action: dict) -> dict | None:
    if action["op"] == "update":
        return crm.account(action["account_id"])
    if action["op"] == "move_contact":
        return crm.contact(action["contact_id"])
    return None


def _check_before(action: dict, live: dict | None):
    """Refuse to write if the CRM no longer looks like it did when the proposal was made."""
    if live is None:
        return
    before = action.get("before") or {}
    drift = {k: (v, live.get(k)) for k, v in before.items() if _norm(live.get(k)) != _norm(v)}
    if drift:
        raise StaleProposal(f"CRM changed since this was proposed: {drift}. Re-run the pipeline.")


def _check_create(crm: CRM, fields: dict):
    """Refuse to create an account that already exists (same street + zip, same parent, not retired)."""
    zip_, street = fields.get("billing_zip", ""), fields.get("billing_street", "")
    if not (zip_ and street):
        return
    for a in crm.accounts(zip=zip_):
        if (not is_parent_account(a) and a.get("parent_id") == fields.get("parent_id")
                and norm_street(a.get("billing_street")) == norm_street(street)
                and a.get("status") != "Inactive"
                and not a.get("duplicate_of_account") and not a.get("chow_current_account")):
            raise StaleProposal(f"An account already exists at this address under the same parent: "
                                f"{a['account_id']} ({a['name']}). Re-run the pipeline.")


def apply_proposal(db, pid: int, reviewer_note: str = "", crm: CRM | None = None) -> dict:
    row = store.get(db, pid)
    if row is None:
        raise ValueError("no such proposal")
    if not store.claim(db, pid):  # atomic: only one caller can move it to 'applying'
        raise ValueError(f"proposal is {store.get(db, pid)['status']}, not pending")
    actions = json.loads(row["actions"])
    # resume support: a previous failed attempt may already have completed some steps
    result = json.loads(row["result"]) if row["result"] else {}
    done = result.setdefault("done", [])
    refs = result.setdefault("refs", {})

    try:
        crm = crm or CRM()
        live = {}
        for i, a in enumerate(actions):
            if i not in done:
                live[i] = _live(crm, a)
                _check_before(a, live[i])
        for i, a in enumerate(actions):
            if i in done:
                continue
            fields = {k: (refs[v[1:]] if isinstance(v, str) and v.startswith("$") else v)
                      for k, v in a.get("fields", {}).items()}
            if a.get("note_line"):
                current = (live.get(i) or {}).get("note", "") if a["op"] != "create" else ""
                fields["note"] = note_line_append(current, a["note_line"])
            if a["op"] == "create":
                _check_create(crm, fields)
                created = crm.create_account(fields)
                refs[a.get("ref", "new")] = created["account_id"]
                result.setdefault("created", []).append(created["account_id"])
            elif a["op"] == "update":
                crm.update_account(a["account_id"], fields)
            elif a["op"] == "move_contact":
                crm.update_contact(a["contact_id"], fields)
            done.append(i)
            store.save_result(db, pid, result)  # persist after every step (crash-safe, no double creates)
    except Exception as e:  # noqa: BLE001 - any failure must leave the row 'failed', never stuck
        result["error"] = f"{type(e).__name__}: {e}"
        store.set_status(db, pid, "failed", reviewer_note, result)
        return result
    result.pop("error", None)
    store.set_status(db, pid, "applied", reviewer_note, result)
    return result
