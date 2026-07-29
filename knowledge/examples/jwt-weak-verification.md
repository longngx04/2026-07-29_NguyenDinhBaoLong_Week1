---
title: Example weak JWT verification
tags: [example, jwt, authentication]
---

# Example — Weak JWT verification

Accepting `alg=none` or not validating signatures lets attackers forge tokens. Always verify signature and claims (`exp`, `aud`) with a trusted library configuration.
