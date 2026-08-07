"""
Main analysis pipeline for Week 3 Security Analysis Agent.
Coordinates loading, deduplication, evidence extraction, knowledge retrieval, LLM analysis,
post-LLM validation, atomic JSONL writing, and run summary output.
"""

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from project_sentinel.analysis.analyzer import analyze_finding_group
from project_sentinel.config import AppConfig
from project_sentinel.analysis.grouping import group_findings
from project_sentinel.ingestion.input_loader import load_findings
from project_sentinel.llm.factory import build_llm
from project_sentinel.analysis.validators import validate_provenance, validate_record_schema, write_jsonl_atomic


def run_pipeline(config: AppConfig) -> Dict[str, Any]:
    """Execute the complete security analysis pipeline end-to-end.
    
    Returns:
        Run summary dictionary.
    """
    start_time = time.time()

    # 1. Load input findings
    finding_file = load_findings(config.input_findings_path)
    findings = finding_file.findings
    input_finding_count = len(findings)

    # 2. Group findings deterministically
    groups = group_findings(findings, near_dup_line_threshold=config.near_dup_line_threshold)
    group_count = len(groups)

    # 3. Instantiate provider
    provider = build_llm(config)

    records: List[Dict[str, Any]] = []
    llm_call_count = 0
    retry_count = 0
    invalid_output_count = 0
    total_prompt_tokens: Optional[int] = None
    total_completion_tokens: Optional[int] = None
    total_llm_tokens: Optional[int] = None
    last_prompt_sha256: str = ""

    for group in groups:
        # Initial analysis attempt
        analysis_res = analyze_finding_group(group, config, provider=provider)
        llm_call_count += 1
        last_prompt_sha256 = analysis_res.prompt_payload.prompt_sha256

        # Accumulate tokens if present
        lr = analysis_res.llm_result
        if lr.prompt_tokens is not None:
            total_prompt_tokens = (total_prompt_tokens or 0) + lr.prompt_tokens
        if lr.completion_tokens is not None:
            total_completion_tokens = (total_completion_tokens or 0) + lr.completion_tokens
        if lr.total_tokens is not None:
            total_llm_tokens = (total_llm_tokens or 0) + lr.total_tokens

        # Check for initial LLM execution error
        if lr.error or not lr.parsed_response:
            invalid_output_count += 1
            continue

        record_dict = lr.parsed_response

        # Post-LLM Schema Validation
        is_schema_valid, schema_err = validate_record_schema(record_dict, config.schema_path)
        
        # Post-LLM Provenance Validation
        is_prov_valid, prov_errs = validate_provenance(
            record_dict=record_dict,
            input_group_finding_ids=group.source_finding_ids,
            input_locations=[{"file": l.file, "line": l.line} for l in group.locations],
            input_knowledge_paths=[h["path"] for h in analysis_res.packet.knowledge_hits],
            input_cwes=group.cwe,
            input_owasps=group.owasp,
            input_source_evidence=analysis_res.packet.source_evidence
        )

        if is_schema_valid and is_prov_valid:
            records.append(record_dict)
        else:
            invalid_output_count += 1
            # Retry once with validation feedback if validation retries permitted
            if config.validation_max_retries >= 1:
                retry_count += 1
                feedback_err = schema_err or "; ".join(prov_errs)
                feedback_prompt = f"{analysis_res.prompt_payload.system_prompt}\n\n[System Note: Your previous output failed validation: {feedback_err}. Correct all schema/provenance errors and return valid JSON only.]"
                
                retry_res = analyze_finding_group(group, config, provider=provider, system_prompt_override=feedback_prompt)
                llm_call_count += 1

                rlr = retry_res.llm_result
                if rlr.parsed_response:
                    r_schema_valid, _ = validate_record_schema(rlr.parsed_response, config.schema_path)
                    r_prov_valid, _ = validate_provenance(
                        record_dict=rlr.parsed_response,
                        input_group_finding_ids=group.source_finding_ids,
                        input_locations=[{"file": l.file, "line": l.line} for l in group.locations],
                        input_knowledge_paths=[h["path"] for h in retry_res.packet.knowledge_hits],
                        input_cwes=group.cwe,
                        input_owasps=group.owasp,
                        input_source_evidence=retry_res.packet.source_evidence
                    )
                    if r_schema_valid and r_prov_valid:
                        records.append(rlr.parsed_response)
                        invalid_output_count -= 1

    output_record_count = len(records)
    
    # 4. Write atomic JSONL output
    write_jsonl_atomic(records, config.output_jsonl_path)

    # 5. Build and write run summary
    runtime_ms = round((time.time() - start_time) * 1000, 2)
    model_name = config.model_name if config.provider_type == "openrouter" else "fake-llm"

    summary_dict = {
        "schema_version": "1.0",
        "input_finding_count": input_finding_count,
        "group_count": group_count,
        "output_record_count": output_record_count,
        "llm_call_count": llm_call_count,
        "retry_count": retry_count,
        "invalid_output_count": max(0, invalid_output_count),
        "runtime_ms": runtime_ms,
        "token_usage": {
            "prompt": total_prompt_tokens,
            "completion": total_completion_tokens,
            "total": total_llm_tokens
        },
        "model": model_name,
        "prompt_sha256": last_prompt_sha256
    }

    config.summary_path.parent.mkdir(parents=True, exist_ok=True)
    config.summary_path.write_text(json.dumps(summary_dict, indent=2, ensure_ascii=False), encoding="utf-8")

    return summary_dict
