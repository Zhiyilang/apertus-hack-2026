# 🌿 Apertus Garden Oracle

**A sovereign, multilingual garden & nature assistant built on [Apertus](https://huggingface.co/swiss-ai) — Switzerland's fully open LLM.**

Submitted to **Hack Apertus 2026** (Online Hackathon, Oct 1–16).  
Tracks: **Track 2B — Own Project** (primary) · **Track 1B — Swiss Voices** (alignment angle).

---

## Why this project

Apertus is trained across **1,800+ languages**, including **Swiss German (Schwiizertüütsch)** and **Romansh (Rumantsch)** — low-resource languages most assistants silently fail on. The Garden Oracle turns that strength into a concrete, useful tool: localized, climate-aware gardening and nature advice that *stays in the user's dialect*.

It is deliberately **sovereign-deployable**: all inference runs on-prem via `transformers` / `vLLM`. No external API, no telemetry, no data leaves the machine — a core Hack Apertus judging criterion.

## Features

- 🌍 **Multilingual + dialect-aware**: English, Deutsch, Français, Italiano, **Schwiizertüütsch**, **Rumantsch**.
- 🪴 **Practical advice**: planting windows, companion planting, pests, soil, seasonal planning.
- 🔒 **Sovereign**: on-prem Apertus inference; air-gapped capable.
- 🧪 **Red-team ready**: bundled evaluation harness (Track 1A) to document model behaviour.
- 🧩 **Simple, dependency-light**: stdlib CLI + optional Gradio web demo.

## Quick start

```bash
pip install -r requirements.txt
huggingface-cli login          # accept the gated license for swiss-ai/Apertus-v1.5-8B
export HF_TOKEN=hf_xxx

# one-off question in Swiss German
python garden_oracle.py --lang "Schwiizertüütsch" --ask "Wenn pflanz ich Tomate?"
# Romansh
python garden_oracle.py --lang "rumansh" --ask "Co imprim chal dunna els plantas?"
# interactive
python garden_oracle.py --interactive --lang "Schwiizertüütsch"
```

> Model weights are **gated** on Hugging Face. You must log in and accept the
> license for `swiss-ai/Apertus-v1.5-8B` (or `70B`) before local inference works.
> Without a model, the client prints a clear, actionable error instead of failing silently.

## Architecture

```
garden_oracle.py   → CLI / interactive REPL (language + dialect steering)
apertus_client.py  → sovereign Apertus client (local-first, optional HF remote opt-in)
eval_harness.py    → red-team evaluation across 6 concern dimensions (Track 1A)
results/           → eval reports (run eval_harness.py to produce real ones)
SUBMISSION.md      → Devpost submission draft
```

The client is **local-first**: it tries `transformers` on-prem, and only uses the
Hugging Face hosted `InferenceClient` if you explicitly pass `--remote` (which is
*not* sovereign and should be avoided for the air-gapped deployment story).

## Deployment (sovereign / on-prem)

```bash
# with vLLM (served locally, no external calls)
vllm serve swiss-ai/Apertus-v1.5-8B --tensor-parallel-size 1
# point apertus_client at your local endpoint, or keep using transformers directly
```

Everything runs behind your own network. Perfect for public-sector or
security-sensitive horticulture / agri advisory use.

## Evaluation & red-teaming (Track 1A)

```bash
python eval_harness.py --out results/redteam.json
```

The harness probes six Hack Apertus concern dimensions (cultural misrepresentation,
bias, PII disclosure, IP generation, historical accuracy, and Swiss-dialect
fidelity). Each flagged case is one documented issue (submit up to 5 for the
Red-Teaming challenge). See `results/redteam.sample.json` for the report schema.

## Judging alignment

| Criterion | How this project meets it |
|---|---|
| Purposeful use of AI | Apertus is the inference engine, not a wrapper |
| Technical rigor | Real client + eval harness + clear deployment path |
| Value | Localized agri/horticulture advice for underserved dialects |
| Cost & scalability | Runs on a single GPU on-prem; no per-call API cost |
| Sovereign deployability | Air-gapped capable, no external dependencies at runtime |
| Implementation feasibility | Stdlib CLI + optional Gradio; small, maintainable |

## License

Apache-2.0 (aligned with Apertus). See `LICENSE`.
