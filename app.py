import os
import string
import random
import time
from urllib.parse import urlparse

from flask import Flask, request, redirect, jsonify

app = Flask(__name__)

# In-memory storage (resets when container restarts)
URLS = {}   # code -> {"url": str, "created": float, "clicks": int}
ALPHABET = string.ascii_letters + string.digits

BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")
CODE_LEN = int(os.getenv("CODE_LEN", "6"))

def is_valid_url(u: str) -> bool:
    try:
        p = urlparse(u)
        return p.scheme in ("http", "https") and bool(p.netloc)
    except Exception:
        return False

def new_code() -> str:
    # Try a few times to avoid collisions
    for _ in range(20):
        code = "".join(random.choice(ALPHABET) for _ in range(CODE_LEN))
        if code not in URLS:
            return code
    raise RuntimeError("Could not generate unique code")

@app.get("/")
def home():
    return f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>Mini URL Shortener</title>
  <style>
    body {{ font-family: system-ui, Arial; max-width: 720px; margin: 40px auto; padding: 0 16px; }}
    input {{ width: 100%; padding: 12px; font-size: 16px; }}
    button {{ padding: 12px 16px; font-size: 16px; margin-top: 10px; cursor: pointer; }}
    .card {{ border: 1px solid #ddd; border-radius: 10px; padding: 16px; margin-top: 18px; }}
    code {{ background: #f5f5f5; padding: 2px 6px; border-radius: 6px; }}
  </style>
</head>
<body>
  <h1>Mini URL Shortener</h1>
  <p>Paste a long URL → get a short link. (In-memory; resets on restart.)</p>

  <div class="card">
    <input id="url" placeholder="https://example.com/very/long/link" />
    <button onclick="shorten()">Shorten</button>
    <p id="out"></p>
  </div>

  <div class="card">
    <p>API:</p>
    <ul>
      <li><code>POST /api/shorten</code> JSON: {{"url":"https://..."}}</li>
      <li><code>GET /api/stats</code></li>
      <li><code>GET /health</code></li>
    </ul>
  </div>

<script>
async function shorten() {{
  const url = document.getElementById("url").value.trim();
  const out = document.getElementById("out");
  out.textContent = "Working...";
  const res = await fetch("/api/shorten", {{
    method: "POST",
    headers: {{ "Content-Type": "application/json" }},
    body: JSON.stringify({{ url }})
  }});
  const data = await res.json();
  if (!res.ok) {{
    out.textContent = "Error: " + (data.error || "unknown");
    return;
  }}
  out.innerHTML = `Short link: <a href="${{data.short_url}}" target="_blank">${{data.short_url}}</a>`;
}}
</script>
</body>
</html>
"""

@app.post("/api/shorten")
def shorten():
    payload = request.get_json(silent=True) or {}
    url = (payload.get("url") or "").strip()

    if not is_valid_url(url):
        return jsonify(error="Please provide a valid http/https URL"), 400

    code = new_code()
    URLS[code] = {"url": url, "created": time.time(), "clicks": 0}
    return jsonify(
        code=code,
        long_url=url,
        short_url=f"{BASE_URL.rstrip('/')}/{code}",
    )

@app.get("/api/stats")
def stats():
    total = len(URLS)
    clicks = sum(v["clicks"] for v in URLS.values())
    return jsonify(total_links=total, total_clicks=clicks, links=URLS)

@app.get("/health")
def health():
    return jsonify(status="ok")

@app.get("/<code>")
def go(code: str):
    item = URLS.get(code)
    if not item:
        return "<h2>Not found</h2><p>Unknown code.</p>", 404
    item["clicks"] += 1
    return redirect(item["url"], code=302)

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
