# AI Model Evaluation Tool

A Python tool for comparing GPT-4o-mini, Gemini 2.5 Flash, and Claude Haiku 3 across five domains: mathematics, factual accuracy, logical reasoning, ethical reasoning, and creative generation. Built as a final-year Honours Project at the University of Hull (2025/26).

Live dashboard: **https://samcurry23.github.io/HonoursProject/**

---

## Setup

1. Clone the repo and install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and add your API keys:
```
OPENAI_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```
You only need one key to run — free tier access is fine for all three providers.

3. Run:
```bash
python main.py
```

---

## Usage

The tool runs from a simple menu. Pick your domains, pick a run size, and it handles the rest — querying each model, scoring responses, and saving results.

| Mode | Questions per domain |
|------|----------------------|
| Quick | 5 |
| Standard | 15 |
| Full | All (~200 total) |

Results save automatically to `results/` as JSON, CSV, and four charts.

---

## Website

Open `website/index.html` in any browser. To load your own results, export a CSV from the main menu and upload it on the Upload tab.

---

## Adding questions

Add JSON files to `data/questions/` — one file per domain. Each question needs:

```json
{
  "id": "math_051",
  "domain": "mathematics",
  "difficulty": "medium",
  "type": "exact",
  "question": "What is 7 × 8?",
  "answer": "56",
  "keywords": ["56"]
}
```

Types: `exact` (maths), `keyword` (factual/logical), `rubric` (ethics/creative).

---

## Troubleshooting

**Gemini returning truncated responses** — make sure you're using the `gemini_client.py` from this repo. The old `google-generativeai` SDK is deprecated; this project uses `google-genai` with thinking tokens disabled.

**Anthropic 529 errors** — these are temporary overload errors and the tool will retry automatically. If they persist, wait a few minutes and try again.

**API key not found** — make sure your `.env` file is in the same folder as `main.py`, not the parent folder.
