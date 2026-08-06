"""
Packet builder for Week 3 Security Analysis Agent.
Constructs deterministic AnalysisPacket objects combining deduplicated finding groups,
source evidence snippets, and knowledge retrieval hits.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from week3.config import AppConfig
from week3.evidence import extract_source_window
from week3.grouping import FindingGroup
from week3.llm.base import AnalysisPacket
from week3.retrieval import retrieve_knowledge


def build_analysis_packet(
    group: FindingGroup,
    config: AppConfig,
    project_root: Optional[Path] = None,
    target_root: Optional[Path] = None
) -> AnalysisPacket:
    """Build a complete AnalysisPacket for a finding group without invoking LLM."""
    p_root = project_root or config.project_root
    
    # Determine target_root boundary
    if target_root is None:
        default_target = p_root / "targets" / "webgoat"
        t_root = default_target if default_target.exists() else p_root
    else:
        t_root = target_root

    finding_group_dict = group.to_packet_group_dict()

    # Extract source evidence snippets for group locations
    source_evidence_dicts: List[Dict[str, Any]] = []
    limitations: List[str] = []

    for loc in group.locations:
        sev = extract_source_window(
            project_root=p_root,
            target_root=t_root,
            relative_path=loc.file,
            line=loc.line,
            radius=config.source_radius
        )
        if sev.error:
            limitations.append(f"Evidence error for {loc.file}:{loc.line}: {sev.error}")
        else:
            item = sev.to_evidence_item()
            if item:
                source_evidence_dicts.append(item.to_dict())

    # Retrieve knowledge hits
    hits = retrieve_knowledge(
        title=group.title,
        rule_id=group.rule_id,
        cwe=group.cwe,
        owasp=group.owasp,
        knowledge_dir=config.knowledge_dir,
        top_k=config.top_k_knowledge
    )
    knowledge_hits_dicts = [h.to_dict() for h in hits]

    # Load output JSON schema if available
    schema_dict: Dict[str, Any] = {}
    if config.schema_path.exists():
        try:
            schema_dict = json.loads(config.schema_path.read_text(encoding="utf-8"))
        except Exception:
            schema_dict = {}

    return AnalysisPacket(
        group_key=group.group_key,
        task="Analyze this deduplicated scanner-finding group using only the supplied evidence.",
        output_language="vi",
        finding_group=finding_group_dict,
        source_evidence=source_evidence_dicts,
        knowledge_hits=knowledge_hits_dicts,
        output_schema=schema_dict
    )
