import os
import time
import json
import requests
import numpy as np
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer

class HANERMA:
    def __init__(self, api_key: Optional[str] = None, model: str = "kwaipilot/kat-coder-pro:free"):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("No API key provided. Set OPENROUTER_API_KEY environment variable or pass api_key parameter.")
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://localhost",
            "X-Title": "HANERMA"
        }
        self.memory_store: List[Dict[str, Any]] = []
        self.logs: List[Dict[str, Any]] = []
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')

    def _log(self, stage: str, input_data: Any = None, output_data: Any = None, duration: float = None):
        entry = {"timestamp": datetime.now().isoformat(), "stage": stage}
        if input_data is not None:
            entry["input"] = str(input_data)[:1000]
        if output_data is not None:
            entry["output"] = str(output_data)[:3000]
        if duration is not None:
            entry["duration_sec"] = round(duration, 3)
        self.logs.append(entry)

    def _call_llm(self, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 4096):
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        start = time.time()
        response = requests.post(self.base_url, headers=self.headers, json=payload)
        duration = time.time() - start
        if response.status_code == 200:
            result = response.json()["choices"][0]["message"]["content"]
            usage = response.json()["usage"]
            self._log("LLM Call", json.dumps(messages), result, duration)
            return result, usage, duration
        else:
            error = response.text
            self._log("LLM Error", json.dumps(messages), error, duration)
            return f"Error: {error}", {"total_tokens": 0}, duration

    def _extract_confidence(self, text: str) -> float:
        patterns = [r"confidence[^\d]*(\d+)%", r"(\d+)%[^\d]*confident", r"certainty[^\d]*(\d+)", r"(\d+)/10"]
        for pat in patterns:
            match = re.search(pat, text, re.IGNORECASE)
            if match:
                val = int(match.group(1))
                return val / 100.0 if val > 10 else val / 10.0
        return 0.5

    def _get_embedding(self, text: str) -> np.ndarray:
        return self.embedder.encode(text, normalize_embeddings=True)

    def _retrieve_memory(self, prompt: str, top_k: int = 4) -> str:
        if not self.memory_store:
            return ""
        prompt_emb = self._get_embedding(prompt)
        scores = []
        for mem in self.memory_store:
            score = np.dot(prompt_emb, mem["embedding"])
            scores.append((score, mem["text"]))
        scores.sort(reverse=True)
        selected = [text for _, text in scores[:top_k]]
        return "\n".join([f"Memory {i+1}: {txt}" for i, txt in enumerate(selected)])

    def _classifier(self, prompt: str) -> Dict[str, bool]:
        classifier_prompt = f'''Analyze the user prompt and output ONLY JSON:
{{
  "needs_memory": true/false,
  "needs_reasoning": true/false
}}
Prompt: {prompt}'''
        messages = [{"role": "system", "content": "You are a precise routing classifier."},
                    {"role": "user", "content": classifier_prompt}]
        result, _, _ = self._call_llm(messages, temperature=0.0, max_tokens=256)
        try:
            decision = json.loads(result)
            return {"needs_memory": decision.get("needs_memory", False),
                    "needs_reasoning": decision.get("needs_reasoning", False)}
        except:
            return {"needs_memory": True, "needs_reasoning": True}

    def _reasoning(self, prompt: str) -> str:
        messages = [
            {"role": "system", "content": "Perform rigorous Atomic Nested Chain of Thought reasoning with verification."},
            {"role": "user", "content": f'''Decompose into atomic parts.
Recursively decompose complex atoms.
Solve bottom-up with verification.
Check consistency.
Synthesize final answer.
Problem: {prompt}'''}
        ]
        reasoning, _, _ = self._call_llm(messages, temperature=0.7, max_tokens=8192)
        return reasoning

    def ask(self, prompt: str, mode: str = "auto") -> str:
        self._log("New Query", prompt)
        start = time.time()
        decision = self._classifier(prompt) if mode == "auto" else {"needs_memory": True, "needs_reasoning": True}
        self._log("Classifier", output_data=decision)

        memory = self._retrieve_memory(prompt) if decision["needs_memory"] else ""
        if decision["needs_memory"]:
            self._log("Memory Retrieval", output_data=memory[:1000])

        reasoning = self._reasoning(prompt) if decision["needs_reasoning"] else ""
        if decision["needs_reasoning"]:
            self._log("Reasoning", output_data=reasoning[:1000])

        final_messages = [
            {"role": "system", "content": "Respond directly, concisely, accurately, and professionally. End with Confidence: X%."},
            {"role": "user", "content": f'''Relevant past memory:
{memory}

Internal verified reasoning:
{reasoning}

User prompt: {prompt}

Answer directly and end with Confidence: X%'''}
        ]
        response, _, _ = self._call_llm(final_messages, temperature=0.7)
        duration = time.time() - start
        self._log("Final Response", output_data=response, duration=duration)

        combined = f"User: {prompt}\nAssistant: {response}"
        embedding = self._get_embedding(combined)
        self.memory_store.append({"text": combined, "embedding": embedding})

        return response