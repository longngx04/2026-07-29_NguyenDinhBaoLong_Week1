"""
OpenRouter LLM Provider implementation using standard-library HTTPS calls.
"""

import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional
from week3.llm.base import AnalysisPacket, LLMProvider, LLMResult


def _sanitize_error(error_msg: str, api_key: str) -> str:
    if not error_msg:
        return "Unknown error"
    if api_key and api_key in error_msg:
        error_msg = error_msg.replace(api_key, "[REDACTED_API_KEY]")
    return error_msg


class OpenRouterClient(LLMProvider):
    """Direct OpenRouter provider implementation using stdlib HTTPS."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://openrouter.ai/api/v1",
        model: str = "deepseek/deepseek-v4-flash-0731",
        timeout_seconds: float = 60.0,
        max_retries: int = 1,
        system_prompt: Optional[str] = None
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self._system_prompt = system_prompt

    def _load_system_prompt(self) -> str:
        if self._system_prompt is not None:
            return self._system_prompt
        prompt_file = Path(__file__).resolve().parent.parent.parent / "prompts" / "security_analysis_system.md"
        if prompt_file.exists():
            return prompt_file.read_text(encoding="utf-8")
        return "You are Project Sentinel's Security Analysis Agent. Return structured JSON only."

    def analyze(self, packet: AnalysisPacket, system_prompt: Optional[str] = None) -> LLMResult:
        """Analyze packet by sending HTTPS request to OpenRouter Chat Completions API."""
        if not self.api_key or not self.api_key.strip():
            raise ValueError("LLM_API_KEY is required when LLM_PROVIDER=openrouter")

        if not self.base_url.startswith("https://"):
            raise ValueError("LLM_BASE_URL must be an HTTPS URL")

        active_system_prompt = system_prompt or self._load_system_prompt()
        endpoint = f"{self.base_url.rstrip('/')}/chat/completions"

        packet_dict = {
            "task": packet.task,
            "output_language": packet.output_language,
            "group_key": packet.group_key,
            "finding_group": packet.finding_group,
            "source_evidence": packet.source_evidence,
            "knowledge_hits": packet.knowledge_hits,
            "output_schema": packet.output_schema,
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": active_system_prompt},
                {"role": "user", "content": json.dumps(packet_dict, ensure_ascii=False)}
            ],
            "temperature": 0,
            "response_format": {"type": "json_object"}
        }

        body_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Project-Sentinel-Week3/1.0"
        }

        attempts = 0
        last_error: Optional[str] = None
        start_time = time.time()

        while attempts <= self.max_retries:
            attempts += 1
            req = urllib.request.Request(endpoint, data=body_bytes, headers=headers, method="POST")
            
            try:
                with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
                    resp_bytes = response.read()
                    resp_json = json.loads(resp_bytes.decode("utf-8"))
                    
                    if "choices" not in resp_json or not resp_json["choices"]:
                        last_error = "OpenRouter response missing 'choices'"
                        if attempts <= self.max_retries:
                            continue
                        break

                    first_choice = resp_json["choices"][0]
                    content_str = first_choice.get("message", {}).get("content", "")
                    
                    if not content_str:
                        last_error = "OpenRouter choice message content is empty"
                        if attempts <= self.max_retries:
                            continue
                        break

                    content_clean = content_str.strip()
                    if content_clean.startswith("```"):
                        lines = content_clean.splitlines()
                        if lines[0].startswith("```"):
                            lines = lines[1:]
                        if lines and lines[-1].startswith("```"):
                            lines = lines[:-1]
                        content_clean = "\n".join(lines).strip()

                    try:
                        parsed = json.loads(content_clean)
                    except json.JSONDecodeError as je:
                        last_error = f"Malformed assistant JSON response: {je}"
                        if attempts <= self.max_retries:
                            continue
                        break

                    usage = resp_json.get("usage", {})
                    latency = (time.time() - start_time) * 1000

                    return LLMResult(
                        raw_response=content_str,
                        parsed_response=parsed,
                        model_name=resp_json.get("model", self.model),
                        request_id=resp_json.get("id"),
                        prompt_tokens=usage.get("prompt_tokens"),
                        completion_tokens=usage.get("completion_tokens"),
                        total_tokens=usage.get("total_tokens"),
                        latency_ms=latency
                    )

            except urllib.error.HTTPError as e:
                status_code = e.code
                err_msg = f"HTTP Error {status_code}: {e.reason}"
                last_error = _sanitize_error(err_msg, self.api_key)
                
                # Retry on 429 (Rate Limit) or 5xx (Server Error)
                if (status_code == 429 or status_code >= 500) and attempts <= self.max_retries:
                    time.sleep(0.5)
                    continue
                else:
                    # Non-retryable HTTP error (e.g., 400 Bad Request, 401 Unauthorized)
                    break

            except Exception as e:
                err_msg = f"Network or transport error: {type(e).__name__}: {e}"
                last_error = _sanitize_error(err_msg, self.api_key)
                if attempts <= self.max_retries:
                    time.sleep(0.5)
                    continue
                break

        latency = (time.time() - start_time) * 1000
        return LLMResult(
            raw_response="",
            parsed_response=None,
            model_name=self.model,
            latency_ms=latency,
            error=last_error or "OpenRouter analysis failed"
        )
