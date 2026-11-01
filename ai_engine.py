from __future__ import annotations

import json
import os
from typing import Iterable, Sequence

import requests


class AIEngine:
    """Integrates with the OpenRouter API to support note summarization, tagging, and Q&A."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str = "https://openrouter.ai/api/v1/chat/completions",
    ) -> None:
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is required. Set it in your environment or .env file.")

        self.model = model or os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": os.getenv("APP_URL", "https://github.com/solodevelopersai/local-ai-note-assistant"),
            "X-Title": os.getenv("APP_NAME", "Local AI Note Assistant"),
        }

    def _chat(self, messages: Sequence[dict], temperature: float = 0.2) -> str:
        payload = {
            "model": self.model,
            "messages": list(messages),
            "temperature": temperature,
        }

        response = requests.post(
            self.base_url,
            headers=self.headers,
            json=payload,
            timeout=90,
        )

        if response.status_code != 200:
            try:
                detail = response.json()
            except ValueError:
                detail = response.text
            raise RuntimeError(f"OpenRouter API request failed: {response.status_code} - {detail}")

        data = response.json()

        try:
            return data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"Unexpected OpenRouter response format: {data}") from exc

    def summarize_note(self, text: str, max_length: int = 400) -> str:
        if not text or not text.strip():
            return "No content available to summarize."

        prompt = (
            "You are an expert research assistant. Summarize the following note in a clear, concise, "
            "well-structured format. Keep the summary practical and useful for future retrieval. "
            f"Limit the response to around {max_length} characters.\n\nNote content:\n{text[:15000]}"
        )

        return self._chat(
            [
                {"role": "system", "content": "You are a helpful assistant for personal knowledge management."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )

    def generate_tags(self, text: str, max_tags: int = 8) -> list[str]:
        if not text or not text.strip():
            return []

        prompt = (
            "Extract the most relevant topic tags for this note. Return only valid JSON as a list of strings. "
            "Use concise keywords or short phrases, prioritize the most important themes, and avoid generic tags. "
            f"Maximum {max_tags} tags.\n\nNote content:\n{text[:15000]}"
        )

        raw = self._chat(
            [
                {"role": "system", "content": "You are a knowledgeable tagging assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
        )

        try:
            values = json.loads(raw)
            if isinstance(values, list):
                tags = [str(tag).strip() for tag in values if str(tag).strip()]
                return tags[:max_tags]
        except json.JSONDecodeError:
            pass

        # Fallback parsing for API responses that include markdown code fences
        cleaned = raw.replace("```json", "").replace("```", "").strip()
        try:
            values = json.loads(cleaned)
            if isinstance(values, list):
                tags = [str(tag).strip() for tag in values if str(tag).strip()]
                return tags[:max_tags]
        except json.JSONDecodeError:
            pass

        fallback_tags = []
        for line in raw.splitlines():
            cleaned_line = line.strip().strip("-\"'[]:, ")
            if cleaned_line:
                fallback_tags.append(cleaned_line)
        return fallback_tags[:max_tags]

    def answer_query(self, query: str, documents: Iterable[object]) -> str:
        query = query.strip()
        if not query:
            return "Please provide a question to answer."

        note_context = []
        for doc in documents:
            text = getattr(doc, "text", "")
            filename = getattr(doc, "filename", "Unknown")
            if text and text.strip():
                note_context.append(f"Document: {filename}\n{text[:4000]}")

        if not note_context:
            return "No local notes were found to answer this question."

        context = "\n\n---\n\n".join(note_context)

        prompt = (
            "Answer the user's question using only the local content provided below. "
            "If the information is not present, say clearly that it is not available in the local notes. "
            "Cite the relevant document names when useful.\n\n"
            f"Question: {query}\n\n"
            f"Local note content:\n{context[:25000]}"
        )

        return self._chat(
            [
                {"role": "system", "content": "You are a knowledgeable personal knowledge assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
