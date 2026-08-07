# Báo cáo Week-1 — Project Sentinel

## Mục tiêu tuần này

Tuần 1 này em dựng một prototype quét bảo mật tĩnh (static analysis) chạy được lặp lại trên cùng một target. Mục tiêu không phải “tìm hết lỗ hổng”, mà là có một đường chạy ổn định: cùng phiên bản target, cùng rule, cùng lệnh, ra cùng dạng bằng chứng JSON để mentor và nhóm review được.

Hệ thống dùng **OpenGrep `v1.26.0`** để quét mã nguồn Java của **OWASP WebGoat `v2025.3`**. WebGoat là ứng dụng cố ý có lỗ hổng, chỉ dùng để học và demo trên máy local — không phải môi trường production.

## Những gì đã dựng trong Week-1


| Thành phần                                          | Vai trò                                              |
| --------------------------------------------------- | ---------------------------------------------------- |
| `benchmarks/targets/webgoat`                                   | Source WebGoat pin qua Git submodule ở tag `v2025.3` |
| `docker-compose.yml`                                | Chạy container WebGoat runtime + image scanner       |
| `infra/docker/scanner/`                                          | Image chứa OpenGrep, `curl`, `jq`                    |
| `configs/opengrep/java-security.yml`                  | Bộ 3 rule bảo mật Java do project tự giữ             |
| `make target-up` / `make scan` / `make target-down` | Lệnh vận hành local                                  |
| `.github/workflows/security-scan.yml`               | CI chạy cùng lệnh scan và upload artifact            |


## Kiến trúc

```
Developer / GitHub Actions
           |
        make scan
           |
  Docker Compose scanner image
           |
        OpenGrep
     (mã nguồn Java)
           |
  artifacts/raw/opengrep.json

Trình duyệt local --> container WebGoat --> 127.0.0.1:8080 / 127.0.0.1:9090
```

Cách hệ thống được tách:

- **Target runtime (`webgoat`)**  
Ứng dụng cần demo/quét, bật bằng `make target-up`. Port bind chặt vào `127.0.0.1:8080` và `127.0.0.1:9090`, nên chỉ máy local mới vào được.
- **Scanner image (`scanner`)**  
Image Docker riêng, không dùng chung process với WebGoat. Khi scan, image mount:
  - `benchmarks/targets/webgoat` — chỉ đọc
  - `configs/opengrep` — chỉ đọc
  - `artifacts/` — nơi duy nhất trong project được ghi kết quả
- **Lệnh scan**  
`make scan` gọi `scripts/scan-opengrep.sh`: tải/kiểm tra binary OpenGrep (checksum SHA256), build image scanner, chạy OpenGrep, rồi dùng `jq` kiểm tra JSON hợp lệ trước khi báo xong.
- **CI**  
Workflow GitHub Actions checkout submodule, chạy `make scan`, validate `artifacts/raw/opengrep.json`, rồi upload artifact `raw-scan-reports`.

## Cách chạy

```bash
# Nếu clone bằng Git:
git submodule update --init --recursive

make target-up        # đợi WebGoat sẵn sàng (health check)
# Mở trình duyệt: http://127.0.0.1:8080/WebGoat/
make scan             # tạo báo cáo raw OpenGrep
make target-down      # tắt container local
```

Cần có: Docker Engine + Compose v2, `curl`, `jq`.

Vì WebGoat cố ý có lỗ hổng, không nên mở port ra ngoài máy đang làm việc.

## Các endpoint WebGoat chính dùng cho demo


| Mục đích                          | Method và path                                     |
| --------------------------------- | -------------------------------------------------- |
| Vào ứng dụng bằng trình duyệt     | `GET http://127.0.0.1:8080/WebGoat/`               |
| Health check cho `make target-up` | `GET /WebGoat/actuator/health`                     |
| Trang đăng ký                     | `GET /WebGoat/registration`                        |
| Tạo tài khoản                     | `POST /WebGoat/register.mvc`                       |
| Dữ liệu bảng điểm                 | `GET /WebGoat/scoreboard-data`                     |
| Tổng quan bài học                 | `GET /WebGoat/service/lessonoverview.mvc/{lesson}` |


WebGoat còn rất nhiều endpoint theo từng bài học. Bảng trên chỉ liệt kê những endpoint vận hành cần cho demo, không phải toàn bộ API của ứng dụng.

## Bộ rule OpenGrep

Rule nằm ở `configs/opengrep/java-security.yml`, cố ý hẹp để Week-1 dễ giải thích và tái chạy:


| Rule id                        | CWE     | Pattern chính                                      | Severity |
| ------------------------------ | ------- | -------------------------------------------------- | -------- |
| `java-sql-statement-execution` | CWE-89  | `Statement.execute / executeQuery / executeUpdate` | ERROR    |
| `java-unsafe-deserialization`  | CWE-502 | `ObjectInputStream.readObject()`                   | ERROR    |
| `java-command-execution`       | CWE-78  | `Runtime.getRuntime().exec(...)`                   | ERROR    |


Mỗi rule gắn metadata CWE/OWASP và confidence `MEDIUM`. Đây là pattern matching trên source — phát hiện chỗ “có dấu hiệu nguy hiểm”, chưa tự kết luận đã exploit được.

## Kết quả quét

Bằng chứng JSON gốc: `artifacts/raw/opengrep.json`  
Lần chạy gần nhất bằng `make scan` trên WebGoat `v2025.3`:

- OpenGrep `1.26.0`
- Quét khoảng 296 file Java với 3 rule
- **23 findings**, **0 errors** trong report


| Rule / CWE                              | Số lượng | Ý nghĩa ngắn                                                                                                         |
| --------------------------------------- | -------- | -------------------------------------------------------------------------------------------------------------------- |
| `java-sql-statement-execution` / CWE-89 | 20       | Có chỗ thực thi SQL qua `Statement`; cần xem query có nhận input người dùng không; nên dùng parameterized statement. |
| `java-unsafe-deserialization` / CWE-502 | 2        | Có dùng `readObject`; cần kiểm tra dữ liệu đến từ đâu và ranh giới tin cậy.                                          |
| `java-command-execution` / CWE-78       | 1        | Có gọi `Runtime.exec`; cần validate input, tránh đưa giá trị không tin cậy vào lệnh hệ thống.                        |


### Finding nằm ở đâu (theo nhóm)

**SQL (20)** — chủ yếu trong các lesson SQL Injection và vài chỗ container/JWT:

- `lessons/sqlinjection/introduction/` — nhiều lesson (Lesson2, 3, 4, 5, 5a, 8, 9, 10)
- `lessons/sqlinjection/advanced/` — Lesson6a, 6b, SqlInjectionChallenge
- Ngoài lesson SQLi: `LessonConnectionInvocationHandler.java`, `UserService.java`, `JWTHeaderKIDEndpoint.java`

**Unsafe deserialization (2)**

- `lessons/deserialization/InsecureDeserializationTask.java`
- `lessons/deserialization/SerializationHelper.java`

**Command execution (1)**

- `org/dummy/insecure/framework/VulnerableTaskHolder.java`

## Những phần Week 1 chưa làm

- Chưa DAST / chưa gửi request tấn công hay exploit target
- Chưa thêm scanner thứ hai (ví dụ FindSecBugs) — giữ pipeline gọn, chỉ OpenGrep
- Chưa chuẩn hóa schema finding, chưa severity scoring nội bộ
- Chưa đo precision/recall hay so sánh với ground truth (để Week-2)
- Output scan không commit vào Git; CI giữ dưới dạng artifact để tải về

## Hướng phát triển sang Week 2

1. Chuẩn hóa `opengrep.json` sang format nội bộ để review/so sánh dễ hơn
2. Map finding với ground truth / lesson WebGoat (nếu dùng được nguồn tham chiếu đã ghi trong `docs/ground-truth.md`)
3. Bắt đầu đánh giá false positive / false negative một cách có quy trình
4. Sau khi có raw evidence ổn định, mới cân nhắc mở rộng rule hoặc thêm tool khác

## Tóm tắt ngắn gửi mentor

Week-1 đã có một pipeline SAST tái chạy được: pin WebGoat `v2025.3` + OpenGrep `v1.26.0` + 3 rule Java, chạy local bằng Make và trên CI. Lần quét gần nhất ra 23 finding (20 SQL, 2 deserialization, 1 command exec), report JSON hợp lệ. Đây là baseline bằng chứng thô để các tuần sau chuẩn hóa và đánh giá — chưa phải kết luận bảo mật cuối cùng.