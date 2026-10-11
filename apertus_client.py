"""Apertus Garden Oracle — sovereign Apertus client.

Loads swiss-ai/Apertus-v1.5-8B (or 70B) for fully on-prem inference.
No external API calls are made unless you explicitly opt into the Hugging Face
hosted InferenceClient. This keeps the assistant deployable air-gapped, which is
a core judging criterion of Hack Apertus ("sovereign deployability").

Model weights are gated on Hugging Face. To run locally you must:
  1. log in to HF and accept the license for swiss-ai/Apertus-v1.5-8B
  2. set HF_TOKEN (or use `huggingface-cli login`)
The client degrades gracefully and tells you exactly what is missing.
"""
from __future__ import annotations

import os
import json
from typing import Optional

APERTUS_MODELS = {
    "8b": "swiss-ai/Apertus-v1.5-8B",
    "70b": "swiss-ai/Apertus-v1.5-70B",
}


class ApertusClient:
    """Thin wrapper around Apertus with a local-first, sovereign design."""

    def __init__(
        self,
        size: str = "8b",
        hf_token: Optional[str] = None,
        max_new_tokens: int = 512,
        use_remote_fallback: bool = False,
    ):
        if size not in APERTUS_MODELS:
            raise ValueError(f"size must be one of {list(APERTUS_MODELS)}")
        self.model_id = APERTUS_MODELS[size]
        self.hf_token = hf_token or os.environ.get("HF_TOKEN")
        self.max_new_tokens = max_new_tokens
        self.use_remote_fallback = use_remote_fallback
        self._pipe = None
        self._client = None

    # ----- local (sovereign) path -----
    def _load_local(self):
        if self._pipe is not None:
            return self._pipe
        try:
            from transformers import pipeline  # type: ignore
        except ImportError:
            return None
        self._pipe = pipeline(
            "text-generation",
            model=self.model_id,
            device_map="auto",
            token=self.hf_token,
        )
        return self._pipe

    # ----- optional remote path (opt-in only) -----
    def _load_remote(self):
        if not self.use_remote_fallback:
            return None
        if self._client is not None:
            return self._client
        try:
            from huggingface_hub import InferenceClient  # type: ignore
        except ImportError:
            return None
        if not self.hf_token:
            return None
        self._client = InferenceClient(self.model_id, token=self.hf_token)
        return self._client

    def generate(self, prompt: str, system: Optional[str] = None) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        pipe = self._load_local()
        if pipe is not None:
            out = pipe(messages, max_new_tokens=self.max_new_tokens)
            return out[0]["generated_text"][-1]["content"]

        client = self._load_remote()
        if client is not None:
            resp = client.chat_completion(
                messages=messages, max_tokens=self.max_new_tokens
            )
            return resp.choices[0].message.content

        raise RuntimeError(
            "Apertus model not available.\n"
            "Local: install `transformers`, set HF_TOKEN, and accept the gated\n"
            f"license for {self.model_id} on Hugging Face.\n"
            "Or set use_remote_fallback=True with a valid HF_TOKEN."
        )

    # convenience for batch eval (red-teaming harness)
    def generate_many(self, prompts, system=None):
        for p in prompts:
            yield {"prompt": p, "output": self.generate(p, system=system)}


if __name__ == "__main__":
    # smoke test without a model: prints the expected model id
    c = ApertusClient()
    print("Configured model:", c.model_id)
    print("Set HF_TOKEN and accept the license to enable generation.")
