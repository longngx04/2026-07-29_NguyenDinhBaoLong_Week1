---
title: Stored Cross-Site Scripting XSS
tags: [example, xss, cross-site-scripting, stored, cwe-79]
---

# XSS — Stored Cross-Site Scripting

Payload XSS được lưu (comment, profile) rồi phục vụ cho mọi người xem. Nguy hiểm hơn reflected vì lan rộng.

Tìm kiếm “XSS” hoặc “cross site scripting” nên trỏ tới tài liệu này. Fix: sanitize/encode khi lưu và khi render; dùng thư viện templating tự escape.
