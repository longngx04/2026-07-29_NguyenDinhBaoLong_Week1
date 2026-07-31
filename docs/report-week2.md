# Báo cáo Week-2 — Project Sentinel

## Mục tiêu tuần này

Tuần 1 đã có bằng chứng quét thô (`results/raw/opengrep.json`). Tuần 2 này em tập trung biến kết quả đó thành **dữ liệu đơn giản** để AI Agent (và người review) dùng được: cùng một schema finding, kèm một kho tri thức nhỏ để tra cứu tên lỗ hổng.

Mục tiêu không phải “phân tích hết 23 finding” hay dựng Agent đầy đủ. Em chỉ cần chứng minh được hai việc:

1. Đọc được kết quả scan Week-1 và đưa về cấu trúc chung.
2. Khi tìm “SQL Injection” hoặc “XSS”, hệ thống trả về tài liệu liên quan trong kho tri thức.

## Những gì đã dựng trong Week-2


| Thành phần                         | Vai trò                                                   |
| ---------------------------------- | --------------------------------------------------------- |
| `week2/normalize.py`               | Đọc OpenGrep JSON, xuất finding chuẩn hóa                 |
| `week2/schema.py`                  | Map severity / rule id / title ngắn                       |
| `week2/search.py`                  | Tìm kiếm keyword + synonym trên `knowledge/**/*.md`       |
| `results/normalized/findings.json` | File tổng hợp 23 cảnh báo đã chuẩn hóa                    |
| `knowledge/owasp-top10.md`         | Tóm tắt OWASP Top 10:2021                                 |
| `knowledge/tools/`                 | Ghi chú OpenGrep và schema finding                        |
| `knowledge/examples/`              | 17 ví dụ lỗ hổng web ngắn (SQLi, XSS, CMDi, SSRF, XXE, …) |
| `make normalize` / `make search`   | Lệnh vận hành local                                       |




## Kiến trúc

```
results/raw/opengrep.json
           |
   python -m week2.normalize
           |
results/normalized/findings.json
  (schema chung cho Agent)

knowledge/**/*.md
           |
   python -m week2.search "SQL Injection"
           |
     top-k tài liệu liên quan
```

Cách hệ thống được tách:

- **Normalize**  
Chỉ đọc report OpenGrep Week-1. Không chạy lại scanner, không sửa WebGoat. Mỗi phần tử trong `results[]` thành một finding có field ổn định (`tool`, `severity`, `file_or_url`, `title`, `cwe`, `owasp`, …).
- **Knowledge base**  
Tài liệu Markdown tự viết, gắn `title` / `tags` ở frontmatter để search ưu tiên đúng loại lỗ hổng. Nội dung cố ý ngắn — đủ để Agent lấy ngữ cảnh, chưa phải encyclopedia.
- **Search**  
Keyword ranking (stdlib): token hóa query, mở rộng synonym (`sqli` ↔ SQL injection, `xss` ↔ cross-site scripting), cộng điểm title/tags nặng hơn body. Không embedding, không gọi API, không vector DB.



## Schema finding chung

Ví dụ một bản ghi sau khi normalize:

```json
{
  "id": "opengrep-002",
  "tool": "opengrep",
  "tool_version": "1.26.0",
  "severity": "high",
  "file_or_url": "targets/webgoat/.../LessonConnectionInvocationHandler.java",
  "line": 31,
  "title": "Potential SQL injection",
  "rule_id": "java-sql-statement-execution",
  "cwe": "CWE-89",
  "owasp": "A03:2021-Injection",
  "message": "Potential SQL injection: a Statement execution method receives a query value...",
  "confidence": "MEDIUM",
  "fingerprint": "..."
}
```

Map severity từ OpenGrep:


| OpenGrep  | Schema nội bộ  |
| --------- | -------------- |
| `ERROR`   | `high`         |
| `WARNING` | `medium`       |
| `INFO`    | `low`          |
| khác      | `low` / `info` |


File tổng hợp bọc thêm `source`, `count`, và mảng `findings` để Agent đọc một lần là biết số lượng.

## Cách chạy

Cần có `results/raw/opengrep.json` từ Week-1 (`make scan` nếu chưa có trên máy local). Repo đã commit sẵn bản normalized để mentor xem không cần quét lại.

```bash
make normalize                 # ghi results/normalized/findings.json
make search Q='SQL Injection'  # tra cứu kho tri thức
make search Q='XSS'
```

Tương đương:

```bash
python3 -m week2.normalize --input results/raw/opengrep.json --output results/normalized/findings.json
python3 -m week2.search "SQL Injection"
python3 -m week2.search "XSS"
```

Cần có: Python 3 (stdlib, không thêm dependency pip cho Week-2).

## Kho tri thức

Em chia `knowledge/` thành ba nhóm:


| Nhóm     | Nội dung chính                                                                                                                                                                                                  |
| -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| OWASP    | `owasp-top10.md` — A01…A10, gắn với pattern Week-1 (injection, deserialization)                                                                                                                                 |
| Tool     | OpenGrep là gì, đọc report thế nào, schema finding sau normalize                                                                                                                                                |
| Examples | 17 file ngắn: SQL Injection, XSS (reflected/stored/DOM), command injection, path traversal, SSRF, XXE, CSRF, IDOR, insecure deserialization, JWT, broken auth, misconfig, vulnerable components, HTML tampering |


Mỗi example nêu pattern nguy hiểm, CWE/OWASP liên quan (nếu có), và hướng mitigation ngắn. Đây là tài liệu học/demo — không thay thế advisory chính thức.

## Kết quả Week-2



### Normalize

Nguồn: OpenGrep `1.26.0` trên WebGoat `v2025.3` (cùng baseline Week-1).

- **23 findings** trong `results/normalized/findings.json`
- Phân bố giữ nguyên so với raw:


| CWE / loại                       | Số lượng |
| -------------------------------- | -------- |
| CWE-89 — SQL statement execution | 20       |
| CWE-502 — unsafe deserialization | 2        |
| CWE-78 — command execution       | 1        |


Severity sau map: toàn bộ 23 finding là `high` (vì rule Week-1 đều `ERROR`).

### Search (tiêu chí hoàn thành)

Em chạy thử hai query bắt buộc:


| Query           | Kết quả mong đợi                                    | Thực tế ngắn                                           |
| --------------- | --------------------------------------------------- | ------------------------------------------------------ |
| `SQL Injection` | Tài liệu SQLi / OWASP Injection / rule OpenGrep SQL | Top hit: ví dụ SQLi concat, login bypass, OWASP Top 10 |
| `XSS`           | Tài liệu Cross-Site Scripting                       | Top hit: XSS reflected, stored, DOM                    |


Search trả về điểm số + đường dẫn file + snippet. Week-1 chưa có rule XSS nên finding normalized không có XSS — kho tri thức vẫn trả lời được câu hỏi về XSS khi Agent hỏi theo tên lỗ hổng.

## Những phần Week 2 chưa làm

- Chưa map từng finding với ground truth / lesson WebGoat một cách có bảng đối chiếu
- Chưa quy trình đánh giá false positive / false negative có số liệu
- Chưa multi-tool normalize (chỉ OpenGrep)
- Chưa semantic search / RAG / embedding — cố ý giữ keyword để pipeline nhẹ
- Chưa AI Agent tự đọc finding rồi giải thích (để tuần sau)

So với hướng Week-2 ghi ở cuối báo cáo Week-1: em đã làm xong phần **chuẩn hóa schema**; phần ground truth và đo precision/recall vẫn để các tuần tiếp theo khi Agent đã có dữ liệu sạch để làm việc.

## Hướng phát triển sang Week 3

1. Agent đọc `results/normalized/findings.json`, với mỗi finding gọi search knowledge để lấy ngữ cảnh CWE/OWASP/ví dụ
2. Sinh bản giải thích ngắn (triage) theo từng nhóm finding — SQL / deserialization / command exec
3. Bắt đầu gắn nhãn true/false positive thủ công trên một mẫu nhỏ để có baseline đánh giá
4. Chỉ khi luồng Agent ổn định mới cân nhắc thêm tool thứ hai hoặc semantic retrieval



## Kết luận

Week-2 đã chuyển 23 finding OpenGrep Week-1 sang schema chung trong `results/normalized/findings.json`, kèm kho tri thức Markdown (OWASP Top 10 + notes tool + 17 ví dụ) và CLI tìm kiếm từ khóa. Query `SQL Injection` và `XSS` đều trả về tài liệu liên quan. Đây là lớp dữ liệu trung gian cho Agent — chưa phải kết luận triage hay đánh giá precision/recall.