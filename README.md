# ASG — Authenticity Score Generator

A command-line proof-of-concept that uses **Google Gemini Vision** to analyze photos of a luxury product and return a probabilistic authenticity score, broken down by criterion.

The first vertical is **Gucci** (GG Canvas leather goods). The system evaluates up to 7 photo criteria — logo pattern, hardware, interior label, stitching, lining, closure, and an anti-fraud session challenge — and outputs a weighted score from 0 to 100.

> ⚠️ This is a research prototype. The score is a probabilistic indicator, not a certified authentication.

---

## Requirements

- Python 3.9+
- A [Google Gemini API key](https://aistudio.google.com/apikey) (free tier works)
- The following Python packages:

```bash
pip install Pillow requests
```

---

## Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/your-username/ASG.git
cd ASG/gucci_auth_demo
```

### 2. Get a Gemini API key

Go to [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey) and create a free key.

### 3. Prepare your product photos

Create a folder and name your photos like this (`.jpg`, `.jpeg`, `.png`, or `.webp`):

```
my_photos/
  01_gg_canvas.jpg       ← GG Canvas pattern (front of product)
  02_herrajes.jpg        ← Hardware / clasps / rings (close-up)
  03_etiqueta.jpg        ← Interior label with serial number
  04_costuras.jpg        ← Stitching detail (side view)
  05_interior.jpg        ← Interior / lining
  06_cierre.jpg          ← Main closure / flap
  07_challenge.jpg       ← Anti-fraud: product next to a handwritten session code (optional)
```

Not all photos are required — missing ones are excluded and the score is recalculated over the available criteria.

### 4. Run the analysis

```bash
python3 main.py --api-key YOUR_GEMINI_KEY --folder ./my_photos
```

**Options:**

| Flag | Default | Description |
|------|---------|-------------|
| `--api-key` | *(required)* | Your Gemini API key |
| `--folder` | *(required)* | Path to the folder containing product photos |
| `--delay` | `12` | Seconds to pause between API calls (increase if you hit rate limits) |
| `--session-id` | *(auto)* | Custom session ID for the report |

---

## Example Output

```
AuthScore Demo — Analyzing photos in: ./my_photos
Session: F3A9B21C
Criteria to evaluate: 7

  🔍 Analyzing [GG Canvas Pattern] (01_gg_canvas.jpg)... Score: 87/100
  🔍 Analyzing [Hardware] (02_herrajes.jpg)... Score: 79/100
  🔍 Analyzing [Interior Label] (03_etiqueta.jpg)... Score: 91/100
  🔍 Analyzing [Stitching] (04_costuras.jpg)... Score: 83/100
  🔍 Analyzing [Interior / Lining] (05_interior.jpg)... Score: 74/100
  🔍 Analyzing [Closure System] (06_cierre.jpg)... Score: 88/100
  ⚫ [Anti-Fraud Challenge] — photo not found, skipping

══════════════════════════════════════════════════════════════
  AUTHSCORE — GUCCI AUTHENTICITY REPORT
  Session: F3A9B21C
══════════════════════════════════════════════════════════════

  FINAL SCORE: 84/100  ✅ HIGH
  ████████████████████████████████░░░░░░░░

  Interpretation: High probability of authenticity. The product
  passes thresholds on most evaluated criteria.
```

---

## Generating Synthetic Test Images

If you don't have real product photos yet, generate placeholder images to verify the pipeline runs end-to-end:

```bash
python3 generate_test_images.py
python3 main.py --api-key YOUR_KEY --folder ./test_images
```

> Gemini will return low scores for synthetic images — this is expected. Use them only to confirm the code runs without errors.

---

## Where to Find Real Test Images

For a meaningful authenticity test, use detail shots from legitimate resale platforms:

- **FASHIONPHILE** — [fashionphile.com/search?q=gucci](https://www.fashionphile.com/search?q=gucci) — product listings include close-ups of label, hardware, and lining
- **Vestiaire Collective** — [vestiairecollective.com](https://www.vestiairecollective.com/search/?q=gucci)
- **Reddit r/Authenticate** — community posts with authentication close-ups

See `FUENTES_IMAGENES.txt` for per-criterion guidance.

---

## Rate Limits (Free Tier)

The Gemini free tier has per-minute request limits. If you see `429` errors:

1. Wait 60 seconds and retry
2. Use `--delay 20` to add more pause between requests
3. Add billing to your Google AI account (costs fractions of a cent per request)

---

## Project Structure

```
gucci_auth_demo/
├── main.py                  ← CLI entry point
├── criteria.py              ← Gucci authentication criteria & prompts
├── analyzer.py              ← Gemini Vision API calls + retry logic
├── report.py                ← Score formatting & console output
├── generate_test_images.py  ← Synthetic placeholder image generator
├── INSTRUCCIONES.txt        ← Spanish setup guide
└── FUENTES_IMAGENES.txt     ← Where to find real test images
```

---

## Roadmap

- [ ] Add more Gucci product categories (shoes, wallets, belts)
- [ ] Expand to other brands (Prada, Louis Vuitton, Hermès)
- [ ] REST API wrapper for B2B integration
- [ ] Fine-tuned vision model replacing prompt-based scoring
- [ ] Anti-fraud session challenge enforcement

---

## Disclaimer

This tool produces probabilistic scores based on AI visual analysis. It does not constitute a certified authentication or legal guarantee of product authenticity. The authors assume no liability for decisions made based solely on this output.
