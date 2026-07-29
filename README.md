# Project Sentinel — Week 1

Project Sentinel chạy OpenGrep để quét bảo mật tĩnh trên [OWASP WebGoat](https://owasp.org/www-project-webgoat/) — ứng dụng cố ý có lỗ hổng để học và demo.

OpenGrep quét mã nguồn Java với bộ rule trong `rules/opengrep/`, xuất JSON gốc.

Target chỉ mở trên loopback (`127.0.0.1`), nên chỉ truy cập được từ máy đang chạy.

## Bắt đầu nhanh

Cần có: Docker Engine kèm Docker Compose v2, `curl`, và `jq`. Nếu lấy code bằng Git, khởi tạo submodule WebGoat trước. Bản ZIP handoff đã có sẵn `targets/webgoat/`, nên bước này không cần sau khi giải nén.

```bash
# Chỉ cần khi clone bằng Git:
git submodule update --init --recursive
make target-up
# Mở trình duyệt: http://127.0.0.1:8080/WebGoat/
make scan
make target-down
```

Kết quả quét nằm ở `results/raw/opengrep.json`.

Workflow CI tại `.github/workflows/security-scan.yml` chạy cùng lệnh và upload báo cáo gốc thành artifact `week1-raw-scan-reports`.

Xem thêm [ghi chú handoff Week-1](docs/week1.md) để biết kiến trúc, endpoint dùng cho demo, kết quả quét, và các giới hạn hiện tại.
