---
title: Reflected Cross-Site Scripting XSS
tags: [example, xss, cross-site-scripting, reflected, cwe-79]
---

# XSS — Reflected Cross-Site Scripting

Ứng dụng phản chiếu input (search, error message) vào HTML mà không encode. Payload ví dụ: `<script>alert(1)</script>`.

Cross Site Scripting (XSS) cho phép đánh cắp session cookie hoặc giả mạo hành động. Mitigation: encode output theo context (HTML/attr/JS), Content-Security-Policy.
