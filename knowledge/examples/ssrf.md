---
title: Example SSRF
tags: [example, ssrf, server-side-request-forgery]
---

# Example — Server-Side Request Forgery (SSRF)

Application fetches a URL from user input and reaches internal services (`http://169.254.169.254/`). Allowlist hosts/schemes; block link-local and private ranges when possible.
