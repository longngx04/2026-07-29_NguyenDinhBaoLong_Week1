---
title: Example command injection with Runtime.exec
tags: [example, command-injection, cwe-78, java]
---

# Example — Command injection with Runtime.exec

```java
Runtime.getRuntime().exec("ping " + host);
```

Input `8.8.8.8; cat /etc/passwd` may run extra commands when a shell is involved. Prefer argument arrays and avoid shell interpretation.
