"""Export the review queue as Markdown for offline/second-opinion review (contains no API token).

    python -m bellhaven.export [status|decisions] > decisions.md
    (decisions = applied + rejected + failed + pending, i.e. everything except superseded/info)
"""
from __future__ import annotations

import json
import sys

from . import store

ORDER = ["chow", "chow_link", "stale_chow", "stale_moved", "reparent", "duplicate", "create", "update_fields", "stale_review"]


def _addr(d):
    return f"{d.get('street') or d.get('billing_street') or ''}, {d.get('city') or d.get('billing_city') or ''}, " \
           f"{d.get('state') or d.get('billing_state') or ''} {d.get('zip') or d.get('billing_zip') or ''}"


def render(status: str = "pending") -> str:
    db = store.connect()
    if status == "decisions":
        raw = [r for st in ("applied", "rejected", "failed", "pending") for r in store.listing(db, st)]
    else:
        raw = store.listing(db, status)
    rows = sorted(raw, key=lambda r: (ORDER.index(r["kind"]) if r["kind"] in ORDER else 99, r["title"]))
    out = [f"# Bellhaven CRM sync: {len(rows)} proposals ({status})\n"]
    for r in rows:
        e, acts = json.loads(r["evidence"]), json.loads(r["actions"])
        names = e.get("names", {})
        res = json.loads(r["result"]) if r["result"] else {}
        out.append(f"## #{r['id']} [{r['kind']}] {r['title']}\n")
        out.append(f"**Status:** {r['status']}" + (f" ({r['decided_at']})" if r["decided_at"] else "")
                   + (f" | reviewer note: {r['reviewer_note']}" if r["reviewer_note"] else "")
                   + (f" | created: {', '.join(res['created'])}" if res.get("created") else "") + "\n")
        out.append(f"**Reasoning:** {e.get('reasoning', '')}\n")
        if e.get("website_check"):
            out.append(f"- {e['website_check']}")
        if e.get("sop"):
            s = e["sop"]
            out.append(f"- **SOP:** revenue ${s['lifetime_revenue']:,.0f}, AR ${s['outstanding_ar']:,.0f} -> {s['decision']}")
        w = e.get("website")
        if w:
            out.append(f"- **Website:** {w['name']} | {_addr(w)} | care: {', '.join(w['care_offerings'])} | "
                       f"admin: {w['administrator']} | phone: {w['phone']}")
        for a in e.get("crm", []):
            out.append(f"- **CRM {a['account_id']}:** {a['name']} | parent: {a['parent_name'] or '(none)'} | {_addr(a)} | "
                       f"{a['care_type']} | {a['status']} | rev ${a['lifetime_revenue'] or 0:,.0f} / AR ${a['outstanding_ar'] or 0:,.0f}"
                       f" | contacts: {', '.join(a['contacts']) or '-'}")
        for d in e.get("duplicates", []):
            out.append(f"- Other record for same facility: {d['account_id']} {d['name']} ({d['parent_name'] or 'no parent'})")
        if e.get("signals"):
            out.append("- **Signals:** " + "; ".join(f"[{lvl}] {t}" for lvl, t in e["signals"]))
        for n in e.get("near_misses", []):
            na = n["account"]
            out.append(f"- **Near miss rejected:** {na['name']} ({na['parent_name'] or 'no parent'}) {_addr(na)}: {n['why_rejected']}")
        out.append("\n**Writes on approval:**\n")
        for a in acts:
            target = a.get("account_id") or a.get("contact_id") or "NEW ACCOUNT"
            for f, v in a.get("fields", {}).items():
                before = (a.get("before") or {}).get(f, "")
                label = lambda x: f"{x} ({names[x]})" if isinstance(x, str) and x in names else x
                v = "(id of new account)" if v == "$new" else label(v)
                out.append(f"- `{a['op']}` {target} . `{f}`: " + (f"{label(before)!s} -> " if a["op"] != "create" and f != "note" else "") + f"{v}")
        out.append("")
    return "\n".join(out)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print(render(sys.argv[1] if len(sys.argv) > 1 else "pending"))
