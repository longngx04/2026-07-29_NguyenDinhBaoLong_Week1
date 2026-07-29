---
title: Example reflected XSS
tags: [example, xss, reflected-xss, cwe-79]
---

# Example — Reflected Cross-Site Scripting (XSS)

A search endpoint echoes `q` into HTML without encoding:

`/search?q=<script>alert(1)</script>`

Another user clicking a crafted link runs the script in their browser session.
