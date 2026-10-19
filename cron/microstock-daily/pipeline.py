#!/usr/bin/env python3
"""
Microstock asset pipeline (VPS, daily).

Stages:
  1. research   — pick N safe subjects (curated pool, rotated) + best-effort scrape
  2. generate   — Kenari qwen-image-3.0-pro -> PNG (b64)
  3. curate     — vision model (qwen3-8-omni-flash:free) scores artifacts; regenerate
                  once if below threshold
  4. vectorize  — vtracer PNG -> SVG
  5. metadata   — one LLM call builds title/description/keywords/model-tag for all

Output: /root/microstock/output/YYYY-MM-DD/{png,svg}/ + manifest.csv
"""
import os, sys, json, csv, base64, time, random, re, datetime, urllib.request

BASE = "https://kenari.id/v1"
KEY = os.environ.get("HERMES_CUSTOM_API_KENARI_ID_API_KEY", "")
ROOT = "/root/microstock"
VENV_PY = f"{ROOT}/.venv/bin/python"
GVENV_PY = "/root/.hermes/gvenv/bin/python"
STATE_FILE = f"{ROOT}/state.json"

IMG_MODEL = "qwen-image-3.0-pro"
VISION_MODEL = "qwen3-8-omni-flash:free"
META_MODEL = "deepseek-v4-1-flash:free"

N_ASSETS = int(os.environ.get("N_ASSETS", "10"))
MIN_SCORE = 7.0
MAX_GEN_TRIES = 2


def http(url, obj, timeout=180):
    req = urllib.request.Request(
        url,
        data=json.dumps(obj).encode(),
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def log(msg):
    print(f"[{datetime.datetime.now():%H:%M:%S}] {msg}", flush=True)


# ---------- 1. research ----------
def load_subjects():
    with open(f"{ROOT}/subjects.json") as f:
        d = json.load(f)
    return d["style_suffix"], d["subjects"]


def scrape_hints():
    """Best-effort: pull subject words from AgentsOfAI trending page. Never raises."""
    try:
        req = urllib.request.Request(
            "https://agentsofai.art/trend/images",
            headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"},
        )
        html = urllib.request.urlopen(req, timeout=20).read().decode(errors="ignore")
        alts = re.findall(r'alt="([^"]{3,60})"', html)
        # crude filter: keep only plausible visual nouns, drop junk
        words = set()
        for a in alts:
            for w in re.findall(r"[a-zA-Z]{4,}", a):
                if w.lower() not in {"image", "photo", "asset", "preview"}:
                    words.add(w.lower())
        return list(words)[:20]
    except Exception:
        return []


def pick_subjects(style, pool, n):
    state = {}
    if os.path.exists(STATE_FILE):
        state = json.load(open(STATE_FILE))
    start = state.get("last_index", 0)
    selected = [pool[(start + i) % len(pool)] for i in range(n)]
    state["last_index"] = (start + n) % len(pool)
    json.dump(state, open(STATE_FILE, "w"))
    return selected


# ---------- 2. generate ----------
def generate(prompt, out_path):
    d = http(
        f"{BASE}/images/generations",
        {"model": IMG_MODEL, "prompt": prompt, "n": 1, "response_format": "b64_json"},
    )
    b64 = d["data"][0].get("b64_json") or d["data"][0].get("url", "").split(",", 1)[-1]
    raw = base64.b64decode(b64)
    open(out_path, "wb").write(raw)
    return len(raw)


# ---------- 3. curate ----------
def score_image(png_path):
    b64 = base64.b64encode(open(png_path, "rb").read()).decode()
    d = http(
        f"{BASE}/chat/completions",
        {
            "model": VISION_MODEL,
            "response_format": {"type": "json_object"},
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": (
                        "Kamu reviewer microstock AI. Lihat gambar ini lalu jawab SATU "
                        "keputusan biner: apakah gambar ini punya artefak AI yang TERLIHAT JELAS "
                        "(bentuk meleleh, bayangan salah, garis putus/bergelombang, halusinasi "
                        "objek, teks kacau, distorsi) sampai perlu ditolak?\n"
                        "Balas HANYA JSON, tanpa teks lain:\n"
                        '{"reject": <true ATAU false>, "note": "<1 kalimat pendek>"}'
                    )},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
                ],
            }],
        },
    )
    txt = d["choices"][0]["message"]["content"].strip()
    def payload_safe(x):
        x = x.strip()
        if x.startswith("```"):  # strip fences if any
            x = x.split("\n", 1)[1] if "\n" in x else x
            x = x.rsplit("```", 1)[0]
        return x.strip()
    for candidate in [txt, payload_safe(txt)]:
        try:
            j = json.loads(candidate)
            reject = bool(j.get("reject"))
            note = str(j.get("note", ""))[:120]
            return (reject, note)
        except Exception:
            pass
        m_j = re.search(r'\{[^{}]*"reject"[^{}]*\}', candidate, re.S)
        if m_j:
            try:
                j = json.loads(m_j.group(0))
                return (bool(j.get("reject")), str(j.get("note", ""))[:120])
            except Exception:
                pass
    # fallback: look for the word
    reject = bool(re.search(r"\btrue\b", txt, re.I)) and not re.search(r'\b"reject"\s*:\s*false', txt, re.I)
    return (reject, txt[:120])


# ---------- 4. vectorize ----------
def vectorize(png_path, svg_path):
    r = os.system(f"{VENV_PY} {ROOT}/vectorize.py '{png_path}' '{svg_path}'")
    return r == 0 and os.path.exists(svg_path)


# ---------- 5. metadata ----------
def build_metadata(items):
    """items: list of dicts(id, category, prompt). One LLM call -> JSON array."""
    brief = [{"id": i["id"], "category": i["category"]} for i in items]
    d = http(
        f"{BASE}/chat/completions",
        {
            "model": META_MODEL,
            "messages": [{
                "role": "user",
                "content": (
                    "Kamu kurator metadata microstock. Untuk tiap item berikut, buat metadata "
                    "dalam Bahasa Inggris yang netral dan jual-siap. JANGAN sebut nama tool/AI "
                    "atau nama artis di judul/deskripsi.\n"
                    "Item (id, kategori):\n" + json.dumps(brief, ensure_ascii=False) + "\n\n"
                    "Balas HANYA JSON array (tanpa markdown) dengan field:\n"
                    '{"id": "...", "title": "...(<=60 char)", "description": "...(1-2 kalimat)", '
                    '"keywords": "k1, k2, ...(12-18 kata kunci dipisah koma)"}\n'
                    "Satu objek per item, pertahankan id yang sama."
                ),
            }],
        },
    )
    txt = d["choices"][0]["message"]["content"]
    txt = re.sub(r"^```(?:json)?|```$", "", txt.strip()).strip()
    return json.loads(txt)


# ---------- main ----------
def main():
    if not KEY:
        log("ERROR: no API key"); sys.exit(1)
    style, pool = load_subjects()

    # 1. research
    picked = pick_subjects(style, pool, N_ASSETS)
    hints = scrape_hints()
    log(f"research: {len(picked)} subjects, scrape hints={len(hints)}")

    day = datetime.date.today().isoformat()
    out_dir = f"{ROOT}/output/{day}"
    png_dir = f"{out_dir}/png"; svg_dir = f"{out_dir}/svg"
    os.makedirs(png_dir, exist_ok=True)
    os.makedirs(svg_dir, exist_ok=True)

    rows = []
    for subj in picked:
        slug = subj["id"]
        prompt = f"{subj['prompt']}, {style}"
        png_path = f"{png_dir}/{slug}.png"
        svg_path = f"{svg_dir}/{slug}.svg"

        # generate with retry
        ok = False
        for attempt in range(1, MAX_GEN_TRIES + 1):
            try:
                size = generate(prompt, png_path)
                reject, note = score_image(png_path)
                log(f"{slug}: reject={reject} ({note[:60]}) attempt={attempt}")
                if not reject:
                    ok = True
                    break
                prompt += ", cleaner sharper edges, fewer artifacts"  # nudge retry
            except Exception as e:
                log(f"{slug} attempt {attempt} ERROR: {e}")
                time.sleep(2)
        if not ok:
            log(f"{slug}: FAILED after {MAX_GEN_TRIES} tries, skipping")
            continue

        # vectorize
        v_ok = vectorize(png_path, svg_path)
        log(f"{slug}: svg={'ok' if v_ok else 'FAILED'} ({os.path.getsize(svg_path) if v_ok else 0}b)")

        rows.append({
            "id": slug, "category": subj["category"], "prompt_png": prompt,
            "reject": reject, "curation_note": note,
            "png": f"png/{slug}.png",
            "svg": f"svg/{slug}.svg" if v_ok else "",
        })
        time.sleep(1)

    if not rows:
        log("ERROR: nothing generated"); sys.exit(1)

    # metadata
    try:
        metas = build_metadata(rows)
        meta_by_id = {m["id"]: m for m in metas}
    except Exception as e:
        log(f"metadata ERROR ({e}); using fallback")
        meta_by_id = {}

    with open(f"{out_dir}/manifest.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "category", "title", "description", "keywords",
                    "reject", "curation_note", "png", "svg"])
        for r in rows:
            m = meta_by_id.get(r["id"], {})
            w.writerow([r["id"], r["category"], m.get("title", ""), m.get("description", ""),
                        m.get("keywords", ""), r["reject"], r["curation_note"],
                        r["png"], r["svg"]])

    log(f"DONE: {len(rows)}/{N_ASSETS} assets -> {out_dir}")
    # upload to Drive (best-effort handled by wrapper; do it here so local cleanup
    # only happens after a successful upload)
    upload_rc = os.system(f"{GVENV_PY} {ROOT}/upload_drive.py '{out_dir}'")
    if upload_rc != 0:
        log("WARN: Drive upload failed (rc=%d); set flag for wrapper" % upload_rc)
        sys.exit(2)
    log("Uploaded to Drive OK")


if __name__ == "__main__":
    main()