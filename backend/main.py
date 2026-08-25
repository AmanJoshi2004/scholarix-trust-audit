"""
main.py

Flask application for the Scholarix Trust Audit prototype.

Run with:
    python -m backend.main
    (or: flask --app backend.main run --port 8000)

Then open http://127.0.0.1:8000 in a browser. The API is served under
/api/* and the static frontend (frontend/) is served at /.
"""

from __future__ import annotations
import os

from flask import Flask, jsonify, send_from_directory, abort

from . import data_loader
from .confidence_audit import audit_records, summarize

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")


@app.after_request
def add_cors_headers(response):
    # Minimal CORS support (no external dependency) -- lets the frontend call
    # the API even if it's ever served from a different origin/port.
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    return response


def _author_summary_row(author: dict) -> dict:
    profile = author.get("profile") or {}
    results = audit_records(author.get("broad_impact") or [])
    stats = summarize(results)
    return {
        "id": author["id"],
        "name": profile.get("name") or author["id"].replace("_", " "),
        "affiliation": profile.get("affiliation"),
        "total_records": stats["total_records"],
        "overstated": stats["overstated"],
        "understated": stats["understated"],
        "consistent": stats["consistent"],
        "overstated_pct": stats["overstated_pct"],
    }


@app.get("/api/health")
def health():
    authors = data_loader.list_authors()
    return jsonify({"status": "ok", "authors_loaded": len(authors)})


@app.get("/api/summary")
def get_summary():
    """Aggregate confidence-audit stats across all authors' broad_impact records."""
    authors = data_loader.list_authors()
    if not authors:
        abort(404, description="No author data found in data/authors.")

    all_results = []
    for author in authors:
        all_results.extend(audit_records(author.get("broad_impact") or []))

    stats = summarize(all_results)
    stats["authors_count"] = len(authors)

    # A handful of the most severe overstatements, for a "worst offenders" panel.
    detailed = []
    for author in authors:
        profile = author.get("profile") or {}
        for r in audit_records(author.get("broad_impact") or []):
            if r.verdict == "Overstated Confidence":
                d = r.to_dict()
                d["author_id"] = author["id"]
                d["author_name"] = profile.get("name") or author["id"].replace("_", " ")
                detailed.append(d)

    detailed.sort(key=lambda d: d["original_score"] - d["adjusted_score"], reverse=True)
    stats["worst_offenders"] = detailed[:8]

    return jsonify(stats)


@app.get("/api/authors")
def get_authors():
    """List all authors with a lightweight per-author audit summary."""
    authors = data_loader.list_authors()
    rows = [_author_summary_row(a) for a in authors]
    rows.sort(key=lambda r: r["overstated"], reverse=True)
    return jsonify({"count": len(rows), "authors": rows})


@app.get("/api/authors/<author_id>")
def get_author_detail(author_id: str):
    """Full profile + full audited broad_impact record list for one author."""
    author = data_loader.get_author(author_id)
    if author is None:
        abort(404, description=f"Author '{author_id}' not found.")

    profile = author.get("profile") or {}
    publications = author.get("publications") or []
    results = audit_records(author.get("broad_impact") or [])
    stats = summarize(results)

    return jsonify({
        "id": author["id"],
        "name": profile.get("name") or author["id"].replace("_", " "),
        "affiliation": profile.get("affiliation"),
        "metrics": profile.get("metrics"),
        "topics": (profile.get("topics") or [])[:6],
        "publications_count": len(publications),
        "summary": stats,
        "records": [r.to_dict() for r in results],
    })


# --- Static frontend -------------------------------------------------------
@app.get("/")
def serve_index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": getattr(e, "description", "Not found")}), 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=True)
