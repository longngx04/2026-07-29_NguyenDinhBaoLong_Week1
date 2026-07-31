---
title: SQL Injection in login query
tags: [example, sql-injection, sqli, authentication, cwe-89]
---

# SQL Injection — login bypass

Query kiểu `SELECT * FROM users WHERE user='...' AND pass='...'` ghép chuỗi cho phép bypass đăng nhập bằng `' OR '1'='1' --`.

Dấu hiệu: SQL Injection / CWE-89 trên form login. Fix: parameterized query + hash mật khẩu, không so sánh plaintext trong SQL động.
