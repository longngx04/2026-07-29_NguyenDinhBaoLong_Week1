---
title: CWE-79 Cross-site Scripting XSS
tags: [cwe-79, cwe, xss, cross-site-scripting]
---

# CWE-79 — Improper Neutralization of Input During Web Page Generation (XSS)

User-controlled data is included in HTML/JS without proper encoding.

## Mitigation

Context-aware output encoding; sanitize rich HTML with a vetted library; CSP.
