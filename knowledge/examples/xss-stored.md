---
title: Example stored XSS
tags: [example, xss, stored-xss, cwe-79]
---

# Example — Stored Cross-Site Scripting (XSS)

Attacker saves a comment containing `<script>…</script>`. Every visitor who loads the comment page executes it. Encode on output; sanitize rich text carefully.
