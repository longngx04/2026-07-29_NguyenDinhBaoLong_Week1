---
title: OWASP Top 10 2021 Overview
tags: [owasp, top10, a01, a02, a03, a04, a05, a06, a07, a08, a09, a10, injection, xss, sql-injection]
---

# OWASP Top 10:2021 — Overview

Tóm tắt nhanh danh mục rủi ro web phổ biến nhất. Dùng làm ngữ cảnh khi đọc finding đã chuẩn hóa.

## A01 Broken Access Control

Người dùng truy cập được dữ liệu hoặc hành động ngoài quyền (IDOR, missing function-level checks).

## A02 Cryptographic Failures

Mã hóa yếu, lộ dữ liệu nhạy cảm, hash mật khẩu kém, TLS sai cấu hình.

## A03 Injection

SQL injection, command injection, LDAP/OS injection — dữ liệu không tin cậy đi vào interpreter. Liên quan trực tiếp tới rule OpenGrep SQL và `Runtime.exec` trong Week-1.

## A04 Insecure Design

Thiết kế thiếu threat modeling, thiếu giới hạn nghiệp vụ, không có kiểm soát an toàn từ đầu.

## A05 Security Misconfiguration

Default credential, debug bật, header bảo mật thiếu, cloud/storage mở công khai.

## A06 Vulnerable and Outdated Components

Thư viện/framework có CVE đã biết, không patch.

## A07 Identification and Authentication Failures

Session cố định, brute-force, credential stuffing, MFA yếu — trước đây gắn với XSS trong một số tài liệu cũ; Top 10:2021 tách XSS sang injection/context khác nhưng XSS vẫn là lỗ hổng web quan trọng (CWE-79).

## A08 Software and Data Integrity Failures

Insecure deserialization, CI/CD thiếu chữ ký, cập nhật không xác thực. OpenGrep rule `ObjectInputStream.readObject` map vào đây.

## A09 Security Logging and Monitoring Failures

Không log sự kiện bảo mật, không cảnh báo, khó điều tra sự cố.

## A10 Server-Side Request Forgery (SSRF)

Server bị lừa gọi URL nội bộ/metadata do attacker kiểm soát.

## Gợi ý tìm kiếm

Thử: `SQL Injection`, `XSS`, `command injection`, `deserialization`, `SSRF`.
