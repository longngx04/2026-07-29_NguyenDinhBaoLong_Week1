---
title: DOM-based XSS
tags: [example, xss, dom, cross-site-scripting, cwe-79]
---

# XSS — DOM-based

JavaScript phía client lấy dữ liệu từ `location.hash` / `innerHTML` mà không kiểm soát. Không cần phản hồi server chứa script.

Mitigation: tránh `innerHTML` với dữ liệu không tin cậy; dùng `textContent`; validate URL fragment.
