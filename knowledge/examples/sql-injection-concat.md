---
title: Example SQL Injection string concatenation
tags: [example, sql-injection, cwe-89, java]
---

# Example — SQL Injection via string concatenation

Vulnerable pattern:

```java
String q = "SELECT * FROM users WHERE name = '" + userInput + "'";
statement.executeQuery(q);
```

Attacker input `' OR '1'='1` can change query logic. Fix with `PreparedStatement` placeholders.
