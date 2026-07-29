---
title: Example insecure Java deserialization
tags: [example, deserialization, cwe-502, java]
---

# Example — Insecure Java deserialization

Reading untrusted bytes with `ObjectInputStream.readObject()` can instantiate unexpected classes and trigger gadgets. Prefer JSON with a schema, or a strict allowlist ObjectInputFilter.
