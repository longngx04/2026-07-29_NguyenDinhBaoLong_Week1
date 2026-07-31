# Báo cáo Week-2 — Project Sentinel

## Mục tiêu

Tuần 2 chuyển kết quả OpenGrep Week-1 sang schema chung, dựng kho tri thức Markdown nhỏ, và thêm CLI tìm kiếm theo từ khóa — để AI Agent các tuần sau đọc được dữ liệu đơn giản.

## Thành phần

| Thành phần | Vai trò |
| --- | --- |
| `week2/` | Package Python: `normalize` và `search` |
| `results/normalized/findings.json` | Finding đã chuẩn hóa (từ raw OpenGrep) |
| `knowledge/` | OWASP Top 10, ghi chú tool, ~15 ví dụ lỗ hổng web |

## Schema finding

```json
{
  "tool": "opengrep",
  "severity": "high",
  "file_or_url": "targets/webgoat/.../Foo.java",
  "title": "Potential SQL injection",
  "message": "...",
  "rule_id": "java-sql-statement-execution",
  "cwe": "CWE-89",
  "owasp": "A03:2021-Injection",
  "line": 49,
  "fingerprint": "..."
}
```

Severity map: OpenGrep `ERROR` → `high`, `WARNING` → `medium`, còn lại → `low` / `info`.

## Cách chạy

Cần `results/raw/opengrep.json` từ Week-1 (`make scan` nếu chưa có).

```bash
make normalize
make search Q='SQL Injection'
make search Q='XSS'
```

Tương đương:

```bash
python3 -m week2.normalize
python3 -m week2.search "SQL Injection"
python3 -m week2.search "XSS"
```

## Search

Keyword ranking trên `knowledge/**/*.md` (title/tags nặng hơn body), có mở rộng synonym (`sqli`, `xss`, …). Không dùng embedding hay LLM trong Week-2.

## Kết quả normalize gần nhất

- Nguồn: OpenGrep `1.26.0` trên WebGoat `v2025.3`
- **23 findings** trong `results/normalized/findings.json`

## Giới hạn

- Chỉ normalize OpenGrep; chưa multi-tool
- Chưa Agent phân tích (Week-3)
- Chưa RAG/vector DB
- Chưa đo precision/recall với ground truth
