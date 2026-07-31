# Project Sentinel — Week 1 & Week 2

Project Sentinel chạy OpenGrep để quét bảo mật tĩnh trên [OWASP WebGoat](https://owasp.org/www-project-webgoat/) — ứng dụng cố ý có lỗ hổng để học và demo.

OpenGrep quét mã nguồn Java với bộ rule trong `rules/opengrep/`, xuất JSON gốc. Week-2 chuẩn hóa finding sang schema chung và tìm kiếm kho tri thức Markdown.

Target chỉ mở trên loopback (`127.0.0.1`), nên chỉ truy cập được từ máy đang chạy.

## Bắt đầu nhanh (Week-1 scan)

Cần có: Docker Engine kèm Docker Compose v2, `curl`, `jq`, và Python 3. Nếu lấy code bằng Git, khởi tạo submodule WebGoat trước. Bản ZIP handoff đã có sẵn `targets/webgoat/`, nên bước này không cần sau khi giải nén.

```bash
# Chỉ cần khi clone bằng Git:
git submodule update --init --recursive
make target-up
# Mở trình duyệt: http://127.0.0.1:8080/WebGoat/
make scan
make target-down
```

Kết quả quét nằm ở `results/raw/opengrep.json`.

## Week-2 — normalize & search

```bash
# Cần results/raw/opengrep.json (chạy make scan nếu chưa có)
make normalize
make search Q='SQL Injection'
make search Q='XSS'
```

- Finding chuẩn hóa: `results/normalized/findings.json`
- Kho tri thức: `knowledge/`
- Package: `week2/` (`python3 -m week2.normalize`, `python3 -m week2.search "..."`)

Workflow CI tại `.github/workflows/security-scan.yml` chạy cùng lệnh scan và upload báo cáo gốc thành artifact `week1-raw-scan-reports`.

Xem thêm [Week-1](docs/week1.md) và [Week-2](docs/week2.md).
