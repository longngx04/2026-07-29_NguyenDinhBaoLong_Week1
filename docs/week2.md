# Báo cáo Week-2 — Project Sentinel

## Mục tiêu

Tuần 2 chuẩn hóa kết quả OpenGrep Week-1 sang một schema chung, dựng kho tri thức Markdown nhỏ, và thêm CLI tìm kiếm theo từ khóa — để Agent (Week-3) có dữ liệu đơn giản để đọc.

## Thành phần

| Thành phần | Vai trò |
| --- | --- |
| `sentinel_data/` | Package Python: `normalize` và `search` |
| `results/normalized/findings.json` | Mảng finding đã chuẩn hóa |
| `results/normalized/findings.jsonl` | Cùng dữ liệu, mỗi dòng một finding |
| `knowledge/` | OWASP / CWE / ví dụ / ghi chú tool |

## Schema finding

```json
{
  "id": "opengrep-001",
  "tool": "opengrep",
  "tool_version": "1.26.0",
  "severity": "high",
  "file_or_url": "targets/webgoat/.../Foo.java",
  "line": 69,
  "title": "Potential command injection",
  "rule_id": "java-command-execution",
  "cwe": "CWE-78",
  "owasp": "A03:2021-Injection",
  "message": "...",
  "confidence": "MEDIUM",
  "raw_check_id": "rules.opengrep.java-command-execution"
}
```

Severity map: OpenGrep `ERROR` → `high`, `WARNING` → `medium`, còn lại → `low`.

## Cách chạy

```bash
# Cần results/raw/opengrep.json từ Week-1 (đã có trong repo hoặc chạy make scan)
make normalize
make search Q='SQL Injection'
make search Q='XSS'
```

Tương đương:

```bash
python3 -m sentinel_data normalize
python3 -m sentinel_data search "SQL Injection"
```

## Search

Search là keyword ranking trên `knowledge/**/*.md` (title/tags nặng hơn body). Không dùng embedding hay LLM trong Week-2.

## Giới hạn

- Chỉ normalize OpenGrep; chưa multi-tool.
- Chưa Agent phân tích (Week-3).
- Chưa RAG/vector DB.
- Chưa đo precision/recall với ground truth.
