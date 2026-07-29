---
title: Example SQL Injection in login forms
tags: [example, sql-injection, authentication]
---

# Example — SQL Injection in login forms

Classic teaching case: username/password fields concatenated into an authentication query. Bypass authentication without knowing a real password.

Always bind parameters; never trust form fields inside SQL text.
