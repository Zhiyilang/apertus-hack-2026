"""Apertus Garden Oracle — a sovereign, multilingual garden & nature assistant.

Built on swiss-ai/Apertus-v1.5 (Switzerland's fully open LLM, trained across
1,800+ languages including Swiss German and Romansh). The Oracle gives localized
gardening, planting, pest and seasonal advice in the user's language — including
low-resource Swiss dialects that most assistants cannot handle.

Usage:
    python garden_oracle.py --lang "Schwiizertüütsch" --ask "Wenn pflanz ich Tomate?"
    python garden_oracle.py --lang "rumansh" --ask "Co imprim chal dunna els plantas?"
    python garden_oracle.py --interactive

Everything runs on-prem via ApertusClient (see apertus_client.py). No data leaves
your machine unless you opt into the optional HF remote endpoint.
"""
from __future__ import annotations

import argparse
import json
import sys

from apertus_client import ApertusClient

SYSTEM_PROMPT = (
    "You are the Apertus Garden Oracle, a careful, practical assistant for "
    "gardening, plants, pests, soil and seasonal planning. You respect the "
    "local language and dialect of the user, including Swiss German "
    "(Schwiizertüütsch) and Romansh. Answer concisely, give concrete, safe, "
    "climate-aware advice, and explicitly note any uncertainty. Never invent "
    "toxic treatments; prefer cultural and biological controls first."
)

# Lightweight language-aware steering so the model stays in dialect.
LANG_HINTS = {
    "schwiizertüütsch": "Respond in Swiss German (Schwiizertüütsch).",
    "swiss german": "Respond in Swiss German (Schwiizertüütsch).",
    "rumansh": "Respond in Romansh (Rumantsch).",
    "romansh": "Respond in Romansh (Rumantsch).",
    "français": "Respond in French.",
    "italiano": "Respond in Italian.",
    "deutsch": "Respond in Standard German.",
    "english": "Respond in English.",
}


def build_prompt(question: str, lang: str) -> str:
    hint = LANG_HINTS.get(lang.strip().lower(), f"Respond in {lang}.")
    return f"{hint}\n\nQuestion: {question}"


def answer(client: ApertusClient, question: str, lang: str) -> str:
    prompt = build_prompt(question, lang)
    return client.generate(prompt, system=SYSTEM_PROMPT)


def main():
    ap = argparse.ArgumentParser(description="Apertus Garden Oracle CLI")
    ap.add_argument("--lang", default="english", help="language / dialect")
    ap.add_argument("--ask", help="one-off question")
    ap.add_argument("--size", default="8b", choices=["8b", "70b"])
    ap.add_argument("--interactive", action="store_true")
    ap.add_argument("--remote", action="store_true",
                    help="allow optional HF hosted inference (not sovereign)")
    args = ap.parse_args()

    client = ApertusClient(size=args.size, use_remote_fallback=args.remote)

    if args.interactive:
        print(f"Apertus Garden Oracle ({args.lang}). Type 'exit' to quit.")
        while True:
            q = input("you> ").strip()
            if q.lower() in {"exit", "quit"}:
                break
            try:
                print("oracle>", answer(client, q, args.lang))
            except RuntimeError as e:
                print("error>", e)
                break
        return

    if args.ask:
        try:
            print(answer(client, args.ask, args.lang))
        except RuntimeError as e:
            print("error>", e)
            sys.exit(2)
        return

    ap.print_help()


if __name__ == "__main__":
    main()
