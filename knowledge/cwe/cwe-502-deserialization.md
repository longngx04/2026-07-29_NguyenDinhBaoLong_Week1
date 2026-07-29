---
title: CWE-502 Deserialization of Untrusted Data
tags: [cwe-502, cwe, deserialization, integrity]
---

# CWE-502 — Deserialization of Untrusted Data

The application deserializes untrusted data without sufficiently verifying that the resulting data will be valid.

## Detection hints

`ObjectInputStream.readObject` on network/user-controlled bytes.

## Mitigation

Avoid native Java serialization for untrusted input; use allowlists or safer encodings.
