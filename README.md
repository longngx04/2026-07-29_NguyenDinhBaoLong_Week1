# Project Sentinel

Pipeline bảo mật tĩnh trên [OWASP WebGoat](https://owasp.org/www-project-webgoat/) — ứng dụng cố ý có lỗ hổng để học và demo.

| Tuần | Việc đã có |
| --- | --- |
| **Week-1** | OpenGrep quét Java WebGoat, xuất JSON gốc, chạy local + CI |
| **Week-2** | Chuẩn hóa finding sang schema chung + kho tri thức + tìm kiếm từ khóa |
| **Week-3** | Security Analysis Agent (LLM Deduplication, Evidence, Provenance Check, JSONL & Summary) |

Target chỉ bind loopback (`127.0.0.1`), nên chỉ máy local truy cập được.

## Yêu cầu

- Docker Engine + Compose v2, `curl`, `jq`
- Python 3.12 (Week-2 & Week-3)
- Nếu clone bằng Git: khởi tạo submodule WebGoat trước

## Cấu trúc chính

```
rules/opengrep/          # Rule SAST Java
targets/webgoat/         # WebGoat v2025.3 (submodule)
results/raw/             # OpenGrep JSON gốc (local, không commit)
results/normalized/      # Finding đã chuẩn hóa (Week-2)
results/analysis/        # Output JSONL & run-summary (Week-3, gitignored)
knowledge/               # OWASP Top 10, notes tool, ví dụ lỗ hổng
week2/                   # normalize + search (Python)
week3/                   # Security Analysis Agent (Config, Grouping, Evidence, Provenance Validation, Pipeline, CLI)
docs/report-week1.md     # Báo cáo Week-1
docs/report-week2.md     # Báo cáo Week-2
docs/report-week3.md     # Báo cáo Week-3
```

## Week-1 — quét OpenGrep

```bash
git submodule update --init --recursive   # chỉ khi clone Git
make target-up
# Mở trình duyệt: http://127.0.0.1:8080/WebGoat/
make scan
make target-down
```

- Báo cáo gốc: `results/raw/opengrep.json`
- CI (`.github/workflows/security-scan.yml`) chạy cùng lệnh scan và upload artifact `week1-raw-scan-reports`

Chi tiết: [docs/report-week1.md](docs/report-week1.md)

## Week-2 — normalize & search

Cần có `results/raw/opengrep.json` (chạy `make scan` nếu chưa có). Repo đã kèm `results/normalized/findings.json` (23 findings).

```bash
make normalize
make search Q='SQL Injection'
make search Q='XSS'
```

Hoặc:

```bash
python3 -m week2.normalize
python3 -m week2.search "SQL Injection"
python3 -m week2.search "XSS"
```

| Output | Path |
| --- | --- |
| Finding chuẩn hóa | `results/normalized/findings.json` |
| Kho tri thức | `knowledge/` |
| Package | `week2/` |

Schema finding (rút gọn): `tool`, `severity`, `file_or_url`, `title`, `cwe`, `owasp`, …

Chi tiết: [docs/report-week2.md](docs/report-week2.md)

## Week-3 — Security Analysis Agent (LLM)

Security Analysis Agent phân tích lỗ hổng bảo mật sử dụng LLM qua OpenRouter Chat Completions API (model `deepseek/deepseek-v4-flash-0731`) hoặc offline test boundary (`FakeLLM`).

### Quy trình chạy đầy đủ (Full Run Sequence):

```bash
git submodule update --init --recursive
make normalize
make agent-test
cp .env.example .env  # local only, bổ sung LLM_API_KEY
make analyze          # requires API key
make validate-analysis
```

### 1. Mock demo (no API key / CI & Offline)
```bash
make agent-test                                               # Full 63 tests offline
make analyze-mock                                             # Demo nhanh: fixture 2 findings + FakeLLM
make analyze-offline-full                                     # Full offline: 23 findings → 21 groups + FakeLLM
make validate-analysis                                        # Validate JSONL với JSON Schema
```

### 2. Real OpenRouter run (requires API key)
```bash
cp .env.example .env                                          # Đã được .gitignore chặn
# Thêm LLM_API_KEY=sk-or-v1-... vào file .env
make analyze                                                  # Phân tích 23 findings thật trên WebGoat
python3 -m week3.cli analyze --input results/normalized/findings.json --provider openrouter
make validate-analysis                                        # Validation kết quả sau khi phân tích
```

Chi tiết: [docs/report-week3.md](docs/report-week3.md)

> **Lưu ý:** Chế độ OpenRouter thật chỉ phục vụ smoke test thủ công ở môi trường local thông qua file `.env` (tuyệt đối không commit file `.env` và không dán API key trực tiếp trên dòng lệnh).

