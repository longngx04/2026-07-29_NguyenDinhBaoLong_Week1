"""
Fake LLM Provider implementation for offline testing and CI.
"""

import json
import time
from typing import Any, Dict, Optional
from week3.llm.base import AnalysisPacket, LLMProvider, LLMResult


class FakeLLM(LLMProvider):
    """Fake LLM Provider returning fixture-driven structured responses without network calls."""

    def __init__(
        self,
        custom_response: Optional[Dict[str, Any]] = None,
        should_fail_first: bool = False,
        inject_invalid_provenance: bool = False,
        max_retries: int = 0
    ):
        self.custom_response = custom_response
        self.should_fail_first = should_fail_first
        self.inject_invalid_provenance = inject_invalid_provenance
        self.max_retries = max_retries
        self.call_count = 0

    def analyze(self, packet: AnalysisPacket, system_prompt: Optional[str] = None) -> LLMResult:
        self.call_count += 1
        start_time = time.time()

        if self.should_fail_first and self.call_count == 1:
            if self.max_retries >= 1:
                # Internal provider retry succeeds on second attempt
                self.call_count += 1
            else:
                return LLMResult(
                    raw_response="Invalid JSON response string",
                    parsed_response=None,
                    model_name="fake-llm",
                    latency_ms=(time.time() - start_time) * 1000,
                    error="Malformed output JSON"
                )

        if self.custom_response:
            parsed = dict(self.custom_response)
        else:
            # Generate deterministic fixture response matching schema & provenance
            fg = packet.finding_group or {}
            group_key = packet.group_key or fg.get("group_key", "group-default")
            source_ids = fg.get("source_finding_ids", ["opengrep-test"])
            locations = fg.get("locations", [{"file": "test.java", "line": 10}])
            cwe = fg.get("cwe", ["CWE-89"])
            owasp = fg.get("owasp", ["A03:2021-Injection"])

            if self.inject_invalid_provenance:
                # Inject non-existent ID for canary test
                source_ids = source_ids + ["fake-hallucinated-id-999"]
                locations = locations + [{"file": "invented/path/Fake.java", "line": 999}]

            k_refs = []
            for kh in packet.knowledge_hits:
                if isinstance(kh, dict) and "path" in kh:
                    k_refs.append({"path": kh["path"], "score": float(kh.get("score", 10.0))})

            evidence = [
                {
                    "type": "scanner",
                    "finding_id": source_ids[0] if source_ids else "opengrep-test",
                    "content": "Potential vulnerability detected by scanner"
                }
            ]

            import hashlib
            group_hex = hashlib.md5(group_key.encode("utf-8")).hexdigest()[:12]
            analysis_id = f"analysis-{group_hex}"

            parsed = {
                "schema_version": "1.0",
                "analysis_id": analysis_id,
                "group_key": group_key,
                "source_finding_ids": source_ids,
                "title": fg.get("title", "Potential Security Finding"),
                "severity": "medium",
                "scanner_severities": ["high"],
                "confidence": "medium",
                "confidence_rationale": "A security sink was detected, but reachability is unknown based on supplied evidence.",
                "locations": locations,
                "cwe": cwe,
                "owasp": owasp,
                "evidence": evidence,
                "explanation": "Mock analysis: Potential security issue in the supplied code.",
                "preconditions": ["Input is controlled by an external untrusted user."],
                "verification_steps": ["Verify whether parameterized queries or validation is used."],
                "remediation": ["Apply safe parameterization or input sanitization."],
                "knowledge_refs": k_refs,
                "limitations": ["Data flow was not fully traced interprocedurally."]
            }

        raw_str = json.dumps(parsed, ensure_ascii=False)
        latency = (time.time() - start_time) * 1000

        return LLMResult(
            raw_response=raw_str,
            parsed_response=parsed,
            model_name="fake-llm",
            request_id="req-fake-123",
            prompt_tokens=150,
            completion_tokens=100,
            total_tokens=250,
            latency_ms=latency
        )
