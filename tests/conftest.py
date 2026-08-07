"""Shared test configuration and fixtures."""

from pathlib import Path

import pytest

# Repository root is the parent of the tests/ directory
REPO_ROOT = Path(__file__).resolve().parent.parent

FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures"
KNOWLEDGE_DIR = REPO_ROOT / "data" / "knowledge-base"
SCHEMAS_DIR = REPO_ROOT / "schemas"


@pytest.fixture
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture
def fixtures_dir() -> Path:
    return FIXTURES_DIR


@pytest.fixture
def knowledge_dir() -> Path:
    return KNOWLEDGE_DIR


@pytest.fixture
def schema_path() -> Path:
    return SCHEMAS_DIR / "security-analysis-record.schema.json"
