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
