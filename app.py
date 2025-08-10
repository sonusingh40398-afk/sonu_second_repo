# app.py
from flask import Flask, jsonify, request
import os
import requests
import time

app = Flask(__name__)

# Get source URL from env var or use example public API
SOURCE_URL = os.getenv("SOURCE_URL", "https://jsonplaceholder.typicode.com/posts")

# Simple cache to avoid fetching every request (keeps for CACHE_TTL seconds)
CACHE_TTL = int(os.getenv("CACHE_TTL", "30"))  # seconds
_cache = {"ts": 0, "data": None}

def fetch_source(url):
    """Fetch JSON from source URL and return python object."""
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

@app.route("/")
def index():
    return jsonify({
        "message": "Fetcher service. GET /fetch to retrieve data from SOURCE_URL",
        "source_url": SOURCE_URL,
    })

@app.route("/fetch")
def fetch():
    """Return raw fetched JSON (or cached) and a small summary."""
    now = time.time()
    if _cache["data"] is None or (now - _cache["ts"]) > CACHE_TTL:
        data = fetch_source(SOURCE_URL)
        _cache["ts"] = now
        _cache["data"] = data
    else:
        data = _cache["data"]

    # Build a tiny summary if data is a list or dict
    summary = {}
    if isinstance(data, list):
        summary["type"] = "list"
        summary["count"] = len(data)
        # show first item keys/snapshot
        summary["first_item_preview"] = data[0] if len(data) else None
    elif isinstance(data, dict):
        summary["type"] = "dict"
        summary["keys"] = list(data.keys())
    else:
        summary["type"] = type(data).__name__

    return jsonify({"summary": summary, "data": data})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

