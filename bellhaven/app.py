"""Local review app.  python -m bellhaven.app  ->  http://127.0.0.1:5000

Every CRM write happens here, and only after a reviewer clicks Approve.
"""
from __future__ import annotations

import json

from urllib.parse import urlparse

from flask import Flask, abort, flash, redirect, render_template_string, request, url_for

from . import store
from .apply import apply_proposal
from .config import CRM_BROWSER
from .pipeline import run as run_pipeline

app = Flask(__name__)
app.secret_key = "local-review-only"

KIND_LABEL = {
    "update_fields": ("Field update", "#2563eb"), "reparent": ("Re-parent", "#7c3aed"),
    "chow": ("CHOW (new account)", "#b45309"), "create": ("New account", "#059669"),
    "duplicate": ("Duplicate", "#64748b"), "stale_chow": ("Off website: CHOW", "#b45309"),
    "stale_moved": ("Off website: moved", "#b45309"), "stale_review": ("Off website: review", "#dc2626"),
    "chow_link": ("CHOW link", "#b45309"), "confirmed": ("Confirmed match", "#059669"),
}
KIND_ORDER = ["chow", "chow_link", "stale_chow", "reparent", "update_fields", "create", "duplicate", "stale_moved",
              "stale_review"]
SOP_KINDS = {"chow", "chow_link", "reparent", "stale_chow", "stale_moved"}  # kinds where the billing SOP decided


def money(v):
    try:
        return "${:,.0f}".format(float(v or 0))
    except (TypeError, ValueError):
        return str(v)


app.jinja_env.filters["money"] = money


@app.before_request
def same_origin_only():
    """Writes only from this app's own pages (blocks cross-site form posts to the local server)."""
    if request.method == "POST":
        src = request.headers.get("Origin") or request.referrer or ""
        if urlparse(src).netloc != request.host:
            abort(403)


def _back():
    ref = request.referrer or ""
    return ref if urlparse(ref).netloc == request.host else url_for("index")


def _load(row):
    d = dict(row)
    d["actions"] = json.loads(row["actions"] or "[]")
    d["evidence"] = json.loads(row["evidence"] or "{}")
    d["result"] = json.loads(row["result"]) if row["result"] else None
    return d


@app.get("/")
def index():
    status = request.args.get("status", "pending")
    db = store.connect()
    rows = [_load(r) for r in store.listing(db, status)]
    rows.sort(key=lambda r: (KIND_ORDER.index(r["kind"]) if r["kind"] in KIND_ORDER else 99, r["title"]))
    runs = db.execute("SELECT * FROM runs ORDER BY id DESC LIMIT 1").fetchall()
    return render_template_string(PAGE, rows=rows, status=status, counts=store.counts(db), runs=runs,
                                  K=KIND_LABEL, crm=CRM_BROWSER, json=json, SOP_KINDS=SOP_KINDS)


@app.post("/p/<int:pid>/approve")
def approve(pid):
    db = store.connect()
    try:
        res = apply_proposal(db, pid, request.form.get("note", ""))
    except ValueError as e:
        flash(f"#{pid}: {e}", "err")
        return redirect(_back())
    if "error" in res:
        flash(f"#{pid} FAILED: {res['error']}", "err")
    else:
        created = ", ".join(res.get("created", []))
        flash(f"#{pid} applied to CRM." + (f" Created account {created}." if created else ""), "ok")
    return redirect(_back())


@app.post("/p/<int:pid>/reject")
def reject(pid):
    db = store.connect()
    row = store.get(db, pid) or abort(404)
    if not store.reject(db, pid, request.form.get("note", "")):
        flash(f"#{pid} is already {store.get(db, pid)['status']}", "err")
    else:
        partial = json.loads(row["result"]) if row["result"] else {}
        msg = f"#{pid} rejected - it will not be proposed again unless the facts change."
        if partial.get("done"):
            msg += (f" NOTE: steps {partial['done']} were already written before it failed"
                    + (f" (created {', '.join(partial.get('created', []))})" if partial.get("created") else "")
                    + " - check them in the CRM.")
        flash(msg, "ok" if not partial.get("done") else "err")
    return redirect(_back())


@app.post("/run")
def run_now():
    try:
        stats = run_pipeline()
        flash(f"Pipeline run complete: {stats}", "ok")
    except Exception as e:  # surface the error to the reviewer instead of a 500
        flash(f"Pipeline failed: {e}", "err")
    return redirect(url_for("index"))


PAGE = r"""
<!doctype html><html><head><meta charset="utf-8"><title>Bellhaven CRM Review</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root{--bg:#f6f7f9;--card:#fff;--ink:#1f2937;--mute:#6b7280;--line:#e5e7eb;--ok:#059669;--bad:#dc2626;--warn:#b45309}
*{box-sizing:border-box}body{margin:0;font:14px/1.45 system-ui,Segoe UI,sans-serif;background:var(--bg);color:var(--ink)}
header{background:#1f3b34;color:#fff;padding:14px 22px;display:flex;gap:18px;align-items:center;flex-wrap:wrap}
header h1{font-size:18px;margin:0;font-weight:600}header a{color:#d1fae5}
.tabs a{color:#fff;text-decoration:none;margin-right:6px;padding:5px 10px;border-radius:14px;background:rgba(255,255,255,.08)}
.tabs a.on{background:#fff;color:#1f3b34;font-weight:600}
main{max-width:1180px;margin:0 auto;padding:18px}
.flash{padding:10px 14px;border-radius:6px;margin-bottom:10px}.flash.ok{background:#d1fae5}.flash.err{background:#fee2e2}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;margin-bottom:16px;overflow:hidden}
.card h2{font-size:15px;margin:0;padding:12px 16px;border-bottom:1px solid var(--line);display:flex;gap:10px;align-items:center}
.pill{color:#fff;font-size:11px;padding:2px 8px;border-radius:10px;white-space:nowrap}
.body{padding:12px 16px;display:grid;grid-template-columns:1fr 1fr;gap:16px}
@media(max-width:860px){.body{grid-template-columns:1fr}}
.reason{grid-column:1/-1;background:#f9fafb;border-left:3px solid #1f3b34;padding:8px 12px}
table{border-collapse:collapse;width:100%;font-size:13px}td,th{border-bottom:1px solid var(--line);padding:4px 6px;text-align:left;vertical-align:top}
th{color:var(--mute);font-weight:500;width:34%}
h3{font-size:12px;text-transform:uppercase;letter-spacing:.06em;color:var(--mute);margin:4px 0 6px}
.sig{list-style:none;padding:0;margin:0}.sig li{padding:2px 0}.sig .ok:before{content:"✔ ";color:var(--ok)}
.sig .bad:before{content:"✘ ";color:var(--bad)}.sig .warn:before{content:"▲ ";color:var(--warn)}.sig .info:before{content:"• ";color:var(--mute)}
.chg td.old{color:var(--bad);text-decoration:line-through}.chg td.new{color:var(--ok);font-weight:600}
.sop{grid-column:1/-1;border:1px solid #fcd34d;background:#fffbeb;padding:8px 12px;border-radius:6px}
.sop.keep{border-color:#f59e0b;background:#fef3c7}
.actions{grid-column:1/-1;display:flex;gap:8px;align-items:center;border-top:1px solid var(--line);padding-top:10px}
.actions input{flex:1;padding:6px 8px;border:1px solid var(--line);border-radius:5px}
button{border:0;border-radius:5px;padding:7px 14px;font-weight:600;cursor:pointer;color:#fff}
.ap{background:var(--ok)}.rj{background:var(--bad)}.run{background:#d1fae5;color:#1f3b34}
.muted{color:var(--mute)}.mono{font-family:ui-monospace,Consolas,monospace;font-size:12px}
details{grid-column:1/-1}summary{cursor:pointer;color:var(--mute)}
</style></head><body>
<header>
 <h1>Bellhaven ↔ CRM review</h1>
 <nav class="tabs">
 {% for s in ['pending','applying','applied','rejected','failed','superseded','info','all'] %}
  <a href="?status={{s}}" class="{{'on' if s==status}}">{{ 'matched (no change)' if s=='info' else s }} {{ counts.get(s,0) if s!='all' else '' }}</a>
 {% endfor %}
 </nav>
 <form method="post" action="/run" style="margin-left:auto" onsubmit="if(this.dataset.sent)return false;this.dataset.sent=1"><button class="run">Run pipeline now</button></form>
 <a href="{{crm}}" target="_blank">Open CRM browser ↗</a>
</header>
<main>
{% with msgs = get_flashed_messages(with_categories=true) %}{% for c,m in msgs %}<div class="flash {{c}}">{{m}}</div>{% endfor %}{% endwith %}
{% if runs %}<p class="muted">Last run #{{runs[0].id}} {{runs[0].status}} at {{runs[0].finished_at or runs[0].started_at}} — {{runs[0].stats}}</p>{% endif %}
{% if not rows %}<p>Nothing here.</p>{% endif %}
{% for r in rows %}{% set e = r.evidence %}{% set k = K.get(r.kind, (r.kind,'#333')) %}
<div class="card" id="p{{r.id}}">
 <h2><span class="pill" style="background:{{k[1]}}">{{k[0]}}</span> <span>#{{r.id}} {{r.title}}</span>
  <span class="muted" style="margin-left:auto;font-weight:400">{{r.status}}{% if r.decided_at %} · {{r.decided_at}}{% endif %}</span></h2>
 <div class="body">
  <div class="reason">{{ e.reasoning }}{% if e.website_check %}<br><span class="muted">{{e.website_check}}</span>{% endif %}</div>
  {% if e.sop and r.kind in SOP_KINDS %}<div class="sop {{'keep' if e.sop.preserve_old}}"><b>Billing SOP:</b> lifetime_revenue {{e.sop.lifetime_revenue|money}},
     outstanding_ar {{e.sop.outstanding_ar|money}} → {{e.sop.decision}}</div>{% endif %}
  {% if e.survivor_rule %}<div class="sop"><b>Survivor rule:</b> {{e.survivor_rule}}</div>{% endif %}

  <div><h3>Website</h3>
  {% if e.website %}<table>
   <tr><th>Name</th><td>{{e.website.name}}</td></tr>
   <tr><th>Address</th><td>{{e.website.street}}<br>{{e.website.city}}, {{e.website.state}} {{e.website.zip}}</td></tr>
   <tr><th>Care</th><td>{{e.website.care_offerings|join(', ')}}</td></tr>
   <tr><th>Administrator</th><td>{{e.website.administrator}}</td></tr>
   <tr><th>Phone</th><td>{{e.website.phone}}</td></tr>
   <tr><th>Source</th><td><a href="{{e.website.url}}" target="_blank">{{e.website.url.split('/')[-1]}}</a> <span class="muted">({{e.website.found_in|join(', ')}})</span></td></tr>
  </table>{% else %}<p class="muted">Not listed on the website.</p>{% endif %}
  {% if e.signals %}<h3 style="margin-top:12px">Match signals</h3><ul class="sig">{% for lvl,txt in e.signals %}<li class="{{lvl}}">{{txt}}</li>{% endfor %}</ul>{% endif %}
  </div>

  <div><h3>CRM</h3>
  {% for a in e.crm %}<table style="margin-bottom:10px">
   <tr><th>Account</th><td><a href="{{crm}}/{{a.account_id}}" target="_blank">{{a.name}}</a> <span class="mono muted">{{a.account_id}}</span></td></tr>
   <tr><th>Parent</th><td>{{a.parent_name or '(none)'}}</td></tr>
   <tr><th>Address</th><td>{{a.billing_street}}<br>{{a.billing_city}}, {{a.billing_state}} {{a.billing_zip}}</td></tr>
   <tr><th>Care / status</th><td>{{a.care_type}} · {{a.status}}</td></tr>
   <tr><th>Revenue / AR</th><td>{{a.lifetime_revenue|money}} / {{a.outstanding_ar|money}}</td></tr>
   {% if a.note %}<tr><th>Existing note</th><td>{{a.note}}</td></tr>{% endif %}
   <tr><th>Contacts</th><td>{{a.contacts|join(', ') or '—'}}</td></tr>
   {% if a.chow_current_account or a.duplicate_of_account %}<tr><th>Links</th><td>chow→{{a.chow_current_account}} dup→{{a.duplicate_of_account}}</td></tr>{% endif %}
  </table>{% else %}<p class="muted">No matching CRM account.</p>{% endfor %}
  {% if e.duplicates %}<h3>Other records for this facility</h3>
   <ul>{% for a in e.duplicates %}<li><a href="{{crm}}/{{a.account_id}}" target="_blank">{{a.name}}</a> ({{a.parent_name or 'no parent'}}) — separate duplicate proposal</li>{% endfor %}</ul>{% endif %}
  </div>

  {% if r.actions %}<div style="grid-column:1/-1"><h3>Proposed writes ({{r.actions|length}})</h3>
  <table class="chg">
  {% for a in r.actions %}
   {% for f,v in a.fields.items() %}<tr>
    <th>{{loop.index==1 and (a.op ~ ' ' ~ (a.account_id or a.contact_id or a.label or '')) or ''}} · {{f}}</th>
    {% if a.op=='create' %}<td class="old"></td>{% else %}{% set ov = (a.before or {}).get(f, '') if f!='note' else '' %}<td class="old">{{ ov }}{% if e.names and ov in e.names %} <span class="muted">({{e.names[ov]}})</span>{% endif %}</td>{% endif %}
    <td class="new">{{ '(id of new account)' if v=='$new' else v }}{% if e.names and v in e.names %} <span class="muted">({{e.names[v]}})</span>{% endif %}</td></tr>{% endfor %}
  {% endfor %}</table></div>{% endif %}

  {% if e.near_misses %}<details><summary>Near misses considered and rejected ({{e.near_misses|length}})</summary>
   {% for n in e.near_misses %}<p><b>{{n.account.name}}</b> ({{n.account.parent_name or 'no parent'}}) — {{n.account.billing_street}}, {{n.account.billing_city}}, {{n.account.billing_state}}: <i>{{n.why_rejected}}</i></p>
   <ul class="sig">{% for lvl,txt in n.signals %}<li class="{{lvl}}">{{txt}}</li>{% endfor %}</ul>{% endfor %}
  </details>{% endif %}

  {% if r.result %}<div style="grid-column:1/-1" class="mono">result: {{ json.dumps(r.result) }}</div>{% endif %}
  {% if r.reviewer_note %}<div style="grid-column:1/-1" class="muted">Reviewer note: {{r.reviewer_note}}</div>{% endif %}
  {% if r.status in ('pending','failed') %}
  <form class="actions" method="post" onsubmit="if(this.dataset.sent)return false;this.dataset.sent=1">
   <input name="note" placeholder="Optional reviewer note" onkeydown="if(event.key==='Enter'){event.preventDefault()}">
   <button class="ap" formaction="/p/{{r.id}}/approve">Approve &amp; write to CRM</button>
   <button class="rj" formaction="/p/{{r.id}}/reject">Reject</button>
  </form>{% endif %}
 </div>
</div>
{% endfor %}
</main></body></html>
"""

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
