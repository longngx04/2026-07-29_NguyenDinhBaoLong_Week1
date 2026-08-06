# Project Sentinel

Pipeline bảo mật tĩnh trên [OWASP WebGoat](https://owasp.org/www-project-webgoat/) — ứng dụng cố ý có lỗ hổng để học và demo.

| Tuần | Việc đã có |
| --- | --- |
| **Week-1** | OpenGrep quét Java WebGoat, xuất JSON gốc, chạy local + CI |
| **Week-2** | Chuẩn hóa finding sang schema chung + kho tri thức + tìm kiếm từ khóa |

Target chỉ bind loopback (`127.0.0.1`), nên chỉ máy local truy cập được.

## Yêu cầu

- Docker Engine + Compose v2, `curl`, `jq`
- Python 3 (Week-2)
- Nếu clone bằng Git: khởi tạo submodule WebGoat trước

## Cấu trúc chính

```
rules/opengrep/          # Rule SAST Java
targets/webgoat/         # WebGoat v2025.3 (submodule)
results/raw/             # OpenGrep JSON gốc (local, không commit)
results/normalized/      # Finding đã chuẩn hóa (Week-2)
knowledge/               # OWASP Top 10, notes tool, ví dụ lỗ hổng
week2/                   # normalize + search (Python)
docs/report-week1.md     # Báo cáo Week-1
docs/report-week2.md     # Báo cáo Week-2
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

### Thiết lập môi trường:
1. Sao chép file cấu hình mẫu `.env.example` thành `.env`:
   ```bash
   cp .env.example .env
   ```
2. Điền `LLM_API_KEY` của bạn vào `.env` (file `.env` bị `.gitignore` chặn, không bao giờ được commit).

3. Runtime khi gọi `AppConfig.from_env()` sẽ tự động đọc cấu hình từ file `.env` ở project root.

### Các lệnh Makefile cho Week 3:
```bash
make agent-test         # Chạy full test suite offline với FakeLLM
make analyze-mock       # Phân tích dữ liệu mẫu offline với FakeLLM
make validate-analysis  # Kiểm tra tính hợp lệ của file JSONL kết quả với JSON Schema
make analyze            # Phân tích dữ liệu thực tế kết hợp OpenRouter LLM (.env)
```

### Các chế độ chạy CLI:
- **Offline / Mock mode (CI & Tests — không network, không API key):**
  ```bash
  python3 -m week3.cli analyze --input fixtures/week3/valid-findings.json --provider fake
  ```
- **Real OpenRouter Mode:**
  ```bash
  python3 -m week3.cli analyze --input results/normalized/findings.json --provider openrouter
  ```

> **Lưu ý:** Chế độ OpenRouter thật chỉ phục vụ smoke test thủ công ở môi trường local thông qua file `.env` (tuyệt đối không commit file `.env` và không dán API key trực tiếp trên dòng lệnh).

