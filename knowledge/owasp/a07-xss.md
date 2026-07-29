---
title: OWASP A07 XSS Cross Site Scripting
tags: [owasp, a07, xss, cross-site-scripting]
---

# OWASP — Cross-Site Scripting (XSS)

XSS lets an attacker inject scripts into pages viewed by other users. Types include reflected, stored, and DOM-based XSS.

## Why it matters

Scripts can steal sessions, rewrite the UI, or call APIs as the victim.

## Safe patterns

- Encode output for the HTML/JS/URL context.
- Prefer frameworks that auto-escape templates.
- Use Content-Security-Policy as defense in depth.

## Search note

This knowledge entry exists so queries like `XSS` return a relevant document even when the current OpenGrep rule pack does not emit XSS findings.
