# Hack Apertus 2026 — Devpost Submission Draft (Track 2B: Own Project)

> Paste this into your Devpost entry. Repo: https://github.com/Zhiyilang/apertus-hack-2026

## 🌿 Apertus Garden Oracle

A **sovereign, multilingual garden & nature assistant** built on **Apertus v1.5**
(Switzerland's fully open LLM). It gives localized, climate-aware gardening and
nature advice that *stays in the user's language — including low-resource Swiss
dialects* (Schwiizertüütsch, Rumantsch) that most assistants cannot handle.

### The problem
Mainstream assistants collapse Swiss German and Romansh into Standard German or
English, losing local context. Apertus is trained across 1,800+ languages
(incl. Swiss dialects), making it the right foundation for truly local advice.

### What we built
- A local-first **Apertus client** (`apertus_client.py`) — on-prem `transformers`/`vLLM` inference, no external calls, air-gapped capable.
- A **multilingual CLI/oracle** (`garden_oracle.py`) with dialect steering for Schwiizertüütsch, Rumantsch, FR, IT, DE, EN.
- A **red-team evaluation harness** (`eval_harness.py`) covering the six Hack Apertus concern dimensions (Track 1A alignment).

### Demo
```bash
pip install -r requirements.txt
huggingface-cli login   # accept gated license for swiss-ai/Apertus-v1.5-8B
python garden_oracle.py --lang "Schwiizertüütsch" --ask "Wenn pflanz ich Tomate?"
```

### Why it matters (judging)
- **Purposeful AI use** — Apertus is the engine, not a wrapper.
- **Sovereign deployability** — runs on-prem / air-gapped; no per-call cost, no data leaving the machine.
- **Value & scalability** — useful for public-sector and hobby horticulture in multilingual Switzerland.
- **Technical rigor** — real client + eval harness + clear vLLM deployment path.

### Track alignment
- **Primary: Track 2B — Own Project** (working Apertus prototype).
- **Secondary: Track 1B — Swiss Voices** (demonstrates dialect fidelity / phonetic-drift evaluation for Swiss contexts).

### Next steps
- Expand dialect coverage and a curated gardening knowledge pack.
- Add a small RAG over local seed/plant databases for factuality (reduces hallucination).
- On-site Zurich hackathon follow-up (Nov 27–28).
