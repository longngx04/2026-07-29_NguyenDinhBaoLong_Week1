---
title: SQL Injection via string concatenation
tags: [example, sql-injection, sqli, cwe-89, injection, java]
---

# SQL Injection — string concatenation

Vulnerable pattern:

```java
String q = "SELECT * FROM users WHERE name = '" + userInput + "'";
statement.executeQuery(q);
```

Attacker input `' OR '1'='1` thay đổi logic query. Mitigation: dùng `PreparedStatement` với placeholder `?`.
