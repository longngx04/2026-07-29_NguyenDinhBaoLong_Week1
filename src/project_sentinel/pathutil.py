"""Path helpers for finding locations after the folder-structure migration."""

# Pre-refactor scans used targets/webgoat/; submodule now lives under benchmarks/.
_LEGACY_WEBGOAT_PREFIX = "targets/webgoat/"
_CANONICAL_WEBGOAT_PREFIX = "benchmarks/targets/webgoat/"


def canonicalize_source_path(relative_path: str) -> str:
    """Normalize finding paths to the current WebGoat layout.

    Accepts both legacy ``targets/webgoat/...`` and canonical
    ``benchmarks/targets/webgoat/...`` prefixes.
    """
    clean = str(relative_path).strip().replace("\\", "/")
    if clean.startswith(_LEGACY_WEBGOAT_PREFIX):
        return _CANONICAL_WEBGOAT_PREFIX + clean[len(_LEGACY_WEBGOAT_PREFIX) :]
    return clean
