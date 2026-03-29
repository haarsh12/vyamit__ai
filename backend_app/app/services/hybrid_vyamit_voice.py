"""
Hybrid LLM pipeline for Vyamit AI (hackathon): Qwen (HF) → Gemini (REST) → Gemma (HF).
Uses LangChain ConversationBufferMemory per user. Verbose terminal logging.
Gemini path delegates to AIService.run_gemini_only — same behavior as before.
"""

from __future__ import annotations

import json
import os
import textwrap
import time
from threading import Lock
from typing import Any, Dict, List, Optional

from langchain.memory import ConversationBufferMemory
from langchain_core.messages import AIMessage, HumanMessage
from langchain_huggingface import HuggingFaceEndpoint

from app.db.models import Item
from app.services.ai_service import AIService

# Defaults (override via env). If a repo 404s on Inference API, set HUGGINGFACE_QWEN_MODEL e.g. to Qwen/Qwen2.5-9B-Instruct
HUGGINGFACE_QWEN_MODEL = os.getenv("HUGGINGFACE_QWEN_MODEL", "Qwen/Qwen3.5-9B")
HUGGINGFACE_GEMMA_MODEL = os.getenv("HUGGINGFACE_GEMMA_MODEL", "google/gemma-3-27b-it")


def _hf_token() -> Optional[str]:
    return os.getenv("HUGGINGFACE_API_TOKEN") or os.getenv("HF_TOKEN") or os.getenv(
        "HUGGINGFACEHUB_API_TOKEN"
    )


def _banner(title: str) -> None:
    line = "=" * 72
    print(f"\n{line}\n  {title}\n{line}")


def _parse_bill_json(raw: str) -> Optional[Dict[str, Any]]:
    if not raw or not raw.strip():
        return None
    text = raw.strip()
    for fence in ("```json", "```JSON", "```"):
        text = text.replace(fence, "")
    text = text.strip()
    try:
        data = json.loads(text)
        if isinstance(data, dict) and "type" in data:
            return data
    except json.JSONDecodeError:
        pass
    return None


class HybridVyamitVoiceService:
    """
    Order: Qwen (Hugging Face) → Gemini (existing AIService) → Gemma (Hugging Face).
    Same master prompt as AIService for all steps (built via AIService._build_vyamit_prompt).
    """

    def __init__(self) -> None:
        self._ai = AIService()
        self._memories: Dict[int, ConversationBufferMemory] = {}
        self._lock = Lock()
        self._qwen_llm: Optional[HuggingFaceEndpoint] = None
        self._gemma_llm: Optional[HuggingFaceEndpoint] = None

    def _memory_for(self, user_id: int) -> ConversationBufferMemory:
        with self._lock:
            if user_id not in self._memories:
                self._memories[user_id] = ConversationBufferMemory(
                    return_messages=True,
                    memory_key="chat_history",
                    input_key="input",
                    output_key="output",
                )
            return self._memories[user_id]

    def _format_history(self, memory: ConversationBufferMemory, max_turns: int = 6) -> str:
        msgs = memory.chat_memory.messages[-(max_turns * 2) :]
        if not msgs:
            return ""
        lines: List[str] = []
        for m in msgs:
            if isinstance(m, HumanMessage):
                lines.append(f"User: {m.content}")
            elif isinstance(m, AIMessage):
                lines.append(f"Assistant: {m.content}")
        return "\n".join(lines)

    def _compose_full_prompt(
        self, base_prompt: str, memory: ConversationBufferMemory
    ) -> str:
        hist = self._format_history(memory)
        if not hist:
            return base_prompt
        return (
            "CONVERSATION SO FAR (follow context; output still must be ONE JSON object):\n"
            f"{hist}\n\n---\n\n{base_prompt}"
        )

    def _ensure_hf_llm(self, repo_id: str, label: str) -> Optional[HuggingFaceEndpoint]:
        token = _hf_token()
        if not token:
            print("⚠️ Hybrid: No HUGGINGFACE_API_TOKEN / HF_TOKEN — skipping HF models.")
            return None
        try:
            return HuggingFaceEndpoint(
                repo_id=repo_id,
                huggingfacehub_api_token=token,
                task="text-generation",
                max_new_tokens=768,
                temperature=0.2,
                top_p=0.9,
                do_sample=True,
            )
        except Exception as e:
            print(f"⚠️ Hybrid: Failed to build HuggingFaceEndpoint for {label} ({repo_id}): {e}")
            return None

    def _invoke_hf(
        self, llm: HuggingFaceEndpoint, label: str, repo_id: str, prompt: str
    ) -> Optional[str]:
        t0 = time.perf_counter()
        print(f"\n  ▶ [{label}] repo={repo_id}")
        print(f"  ▶ Prompt length: {len(prompt)} chars")
        try:
            out = llm.invoke(prompt)
            dt = time.perf_counter() - t0
            text = out if isinstance(out, str) else str(out)
            print(f"  ✓ [{label}] OK in {dt:.2f}s")
            print(textwrap.indent(text[:4000], "  │ "))
            if len(text) > 4000:
                print(f"  │ ... ({len(text)} chars total, truncated in log)")
            return text
        except Exception as e:
            dt = time.perf_counter() - t0
            print(f"  ✗ [{label}] FAILED after {dt:.2f}s: {e}")
            return None

    def process_voice_command(
        self, user_text: str, inventory: List[Item], user_id: int
    ) -> Dict[str, Any]:
        memory = self._memory_for(user_id)
        base_prompt = self._ai._build_vyamit_prompt(user_text, inventory)
        full_prompt = self._compose_full_prompt(base_prompt, memory)

        _banner("VYAMIT HYBRID LLM — PIPELINE START")
        print(f"  user_id: {user_id}")
        print(f"  raw_user_text: {user_text!r}")
        print(f"  inventory_rows: {len(inventory)}")
        print(f"  memory_turns: {len(memory.chat_memory.messages) // 2}")
        print(f"  order: QWEN ({HUGGINGFACE_QWEN_MODEL}) → GEMINI → GEMMA ({HUGGINGFACE_GEMMA_MODEL})")

        token = _hf_token()
        last_error = ""
        if not token:
            print("\n⚠️ HYBRID: No HUGGINGFACE_API_TOKEN / HF_TOKEN — skipping Qwen & Gemma; using Gemini only.")

        # 1) Qwen
        if token:
            if self._qwen_llm is None:
                self._qwen_llm = self._ensure_hf_llm(HUGGINGFACE_QWEN_MODEL, "QWEN")
            if self._qwen_llm is not None:
                raw = self._invoke_hf(
                    self._qwen_llm, "QWEN", HUGGINGFACE_QWEN_MODEL, full_prompt
                )
                parsed = _parse_bill_json(raw) if raw else None
                if parsed is not None:
                    print("\n✅ HYBRID: Qwen produced valid Vyamit JSON.")
                    memory.save_context(
                        {"input": user_text},
                        {"output": json.dumps(parsed, ensure_ascii=False)[:2000]},
                    )
                    _banner("VYAMIT HYBRID LLM — PIPELINE END (winner: QWEN)")
                    return parsed
                last_error = "Qwen: no valid JSON with 'type' field"
                print(f"\n⚠️ HYBRID: {last_error}; falling through to Gemini.")

        # 2) Gemini (unchanged google-generativeai stack via AIService.run_gemini_only)
        print("\n─── GEMINI (official google-generativeai) ───")
        t0 = time.perf_counter()
        gemini_out = self._ai.run_gemini_only(full_prompt)
        dt = time.perf_counter() - t0
        # Only the hard failure after all Gemini model names fail uses the Hindi system message
        gemini_system_outage = gemini_out.get("type") == "ERROR" and "सिस्टम त्रुटि" in gemini_out.get(
            "msg", ""
        )
        if not gemini_system_outage:
            print(f"\n✅ HYBRID: Gemini completed in {dt:.2f}s → type={gemini_out.get('type')}")
            memory.save_context(
                {"input": user_text},
                {"output": json.dumps(gemini_out, ensure_ascii=False)[:2000]},
            )
            _banner("VYAMIT HYBRID LLM — PIPELINE END (winner: GEMINI)")
            return gemini_out
        last_error = f"Gemini all candidate models failed: {gemini_out.get('msg', '')}"
        print(f"\n⚠️ HYBRID: {last_error}; trying Gemma.")

        # 3) Gemma
        if token:
            if self._gemma_llm is None:
                self._gemma_llm = self._ensure_hf_llm(HUGGINGFACE_GEMMA_MODEL, "GEMMA")
            if self._gemma_llm is not None:
                raw_g = self._invoke_hf(
                    self._gemma_llm, "GEMMA", HUGGINGFACE_GEMMA_MODEL, full_prompt
                )
                parsed_g = _parse_bill_json(raw_g) if raw_g else None
                if parsed_g is not None:
                    print("\n✅ HYBRID: Gemma produced valid Vyamit JSON.")
                    memory.save_context(
                        {"input": user_text},
                        {"output": json.dumps(parsed_g, ensure_ascii=False)[:2000]},
                    )
                    _banner("VYAMIT HYBRID LLM — PIPELINE END (winner: GEMMA)")
                    return parsed_g

        print(f"\n❌ HYBRID: All stages failed. Last note: {last_error}")
        _banner("VYAMIT HYBRID LLM — PIPELINE END (FAILED)")
        return {
            "type": "ERROR",
            "items": [],
            "msg": "सिस्टम त्रुटि: कृपया बाद में पुनः प्रयास करें।",
            "should_stop": False,
        }
