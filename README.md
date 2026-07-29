# Project Sentinel — Week 1–2

Project Sentinel chạy OpenGrep để quét bảo mật tĩnh trên [OWASP WebGoat](https://owasp.org/www-project-webgoat/) — ứng dụng cố ý có lỗ hổng để học và demo.

OpenGrep quét mã nguồn Java với bộ rule trong `rules/opengrep/`, xuất JSON gốc. Week-2 chuẩn hóa findings và cung cấp kho tri thức + tìm kiếm từ khóa.

Target chỉ mở trên loopback (`127.0.0.1`), nên chỉ truy cập được từ máy đang chạy.

## Bắt đầu nhanh (Week-1 scan)

Cần có: Docker Engine kèm Docker Compose v2, `curl`, `jq`, và Python 3. Nếu lấy code bằng Git, khởi tạo submodule WebGoat trước.

```bash
# Chỉ cần khi clone bằng Git:
git submodule update --init --recursive
make target-up
# Mở trình duyệt: http://127.0.0.1:8080/WebGoat/
make scan
make target-down
```

Kết quả quét gốc: `results/raw/opengrep.json`.

## Week-2 — Normalize và knowledge search

```bash
make normalize
# → results/normalized/findings.json
# → results/normalized/findings.jsonl

make search Q='SQL Injection'
make search Q='XSS'
```

Kho tri thức nằm ở `knowledge/` (OWASP, CWE, ví dụ lỗ hổng web, ghi chú OpenGrep).

Workflow CI chạy scan rồi normalize; artifact gồm raw + normalized reports.

Xem thêm:

- [Week-1 handoff](docs/week1.md)
- [Week-2 handoff](docs/week2.md)
