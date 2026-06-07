---
layout: post
title: "Character Encodings Reference"
description: >-
  A reference of character encodings.
author: ryo
date: 2025-03-17 23:25:59 +0800
categories: [Software Engineering]
tags: [encoding, cheatsheet]
toc: true
comments: true
pin: false
published: true
---

## Overview

Character Encoding Reference.

---

## Key Concepts

- **Character set** - maps characters to numbers. e.g. `A` = 65. Unicode is a character set.
- **Encoding** - rules for storing those numbers as bytes. e.g. 65 → `0x41`. UTF-8 is an encoding.
- **Code point** - a single character entry in a character set. Written as `U+XXXX` in Unicode.
- **Code unit** - the atomic unit of storage for an encoding. UTF-8 = 8-bit units. UTF-16 = 16-bit units.
- **BOM (Byte Order Mark)** - `U+FEFF` placed at the start of a file to signal byte order. Required in UTF-16. Unnecessary and often harmful in UTF-8.
- **Surrogate pair** - two UTF-16 code units used together to encode a code point outside the BMP (`U+10000`+).

---

## ASCII

128 characters, 0–127, 7 bits, stored as 1 byte.

| Range | Contents |
|---|---|
| 0–31 | Control characters (`\n`, `\t`, `\r`, null, etc.) |
| 32–126 | Printable: A–Z, a–z, 0–9, punctuation, space |
| 127 | Delete |

| Char | Dec | Hex | Binary |
|---|---|---|---|
| `A` | 65 | 0x41 | 0100 0001 |
| `a` | 97 | 0x61 | 0110 0001 |
| `0` | 48 | 0x30 | 0011 0000 |
| `space` | 32 | 0x20 | 0010 0000 |

### Extended ASCII

8th bit used to add 128 more characters (slots 128-255). Not standardised - each group defined their own:

| Variant | Coverage |
|---|---|
| **ISO 8859-1 (Latin-1)** | Western European: `é`, `ñ`, `ü` |
| **Windows-1252 (CP1252)** | Same as Latin-1 for 160–255, different at 128–159 |
| **Shift-JIS** | Japanese |
| **GB2312** | Simplified Chinese |

Bytes 0–127 are consistent across all variants. Bytes 128–255 are encoding-specific. This is the root of most legacy encoding corruption.

---

## Unicode

One universal character set for every writing system.

- **~150,000 code points**, range `U+0000`–`U+10FFFF`
- Divided into 17 **planes** of 65,536 code points each
- **Plane 0 = Basic Multilingual Plane (BMP)**: `U+0000`–`U+FFFF`, covers most everyday characters
- Planes 1–16: emoji, historic scripts, rarely used symbols

| Code point | Char | Notes |
|---|---|---|
| `U+0041` | `A` | = ASCII 65 |
| `U+00E9` | `é` | Latin small e with acute |
| `U+4E2D` | `中` | Chinese "middle" |
| `U+1F600` | `😀` | Plane 1, needs 4 bytes in UTF-8 |
| `U+FEFF` | BOM | Byte Order Mark |

Unicode defines the code points. UTF-8, UTF-16, and UTF-32 define how they're stored as bytes.

---

## UTF-32

Fixed-width: every code point = 4 bytes, always.

| Code point | Bytes |
|---|---|
| `U+0041` | `00 00 00 41` |
| `U+1F600` | `00 01 F6 00` |

- nth character always at byte offset `n × 4` - simple to index
- 4× larger than ASCII for English text
- Rarely used outside of internal runtime representations

---

## UTF-16

Variable-width: 2 bytes for BMP, 4 bytes (surrogate pair) for everything else.

| Range | Encoding |
|---|---|
| `U+0000`–`U+FFFF` (BMP) | 2 bytes directly |
| `U+10000`–`U+10FFFF` | Surrogate pair: high (`0xD800`–`0xDBFF`) + low (`0xDC00`–`0xDFFF`) |

**Used internally by:** Java (`char` = 1 UTF-16 code unit), JavaScript/V8, .NET/C#, Windows APIs.

### BOM in UTF-16

| BOM bytes | Meaning |
|---|---|
| `FE FF` | UTF-16 BE (big-endian) |
| `FF FE` | UTF-16 LE (little-endian) |

UTF-8 BOM = `EF BB BF`. Not needed, but some Windows tools write it anyway. Can silently break parsers that don't expect it.

---

## UTF-8

Variable-width: 1–4 bytes. Dominant encoding on the web (>98% of pages).

| Code point range | Bytes | Byte pattern |
|---|---|---|
| `U+0000`–`U+007F` | 1 | `0xxxxxxx` |
| `U+0080`–`U+07FF` | 2 | `110xxxxx 10xxxxxx` |
| `U+0800`–`U+FFFF` | 3 | `1110xxxx 10xxxxxx 10xxxxxx` |
| `U+10000`–`U+10FFFF` | 4 | `11110xxx 10xxxxxx 10xxxxxx 10xxxxxx` |

- **ASCII-compatible** - code points 0–127 are identical to ASCII bytes. Any ASCII file is valid UTF-8.
- **Self-synchronising** - byte prefix tells you the role: `0` = 1-byte char, `110` = 2-byte start, `1110` = 3-byte start, `11110` = 4-byte start, `10` = continuation byte.
- **No BOM needed** - no endianness issue.

### Encoding Example: `é` (`U+00E9`)

`U+00E9` = binary `000 1110 1001`. Falls in `U+0080`–`U+07FF` → 2-byte pattern `110xxxxx 10xxxxxx`.

Fill in bits: `1100 0011` `1010 1001` → `0xC3 0xA9`

### Why Latin-1 → UTF-8 Produces `HÃ©llo`

`é` in Latin-1 = single byte `0xE9`. Read as UTF-8, `0xE9` = `1110 1001` - start of a 3-byte sequence. The bytes that follow don't match the `10xxxxxx` continuation pattern, so the decoder outputs replacement characters. `0xC3 0xA9` (the correct UTF-8 for `é`) decoded as Latin-1 gives `Ã` + `©`, producing `HÃ©llo`.

---

## Common Encoding Bugs

### MySQL `utf8` vs `utf8mb4`

MySQL's `utf8` only handles up to 3-byte sequences. Emoji need 4 bytes. Use `utf8mb4` always.

```sql
-- Set on connection
SET NAMES utf8mb4;
```

```
# JDBC connection string
jdbc:mysql://host/db?useUnicode=true&characterEncoding=utf8mb4
```

### Python file/CSV reads

Python 3 defaults to UTF-8. Excel exports are often `latin1` or `cp1252`.

```python
open('file.csv', encoding='utf-8')        # explicit UTF-8
open('file.csv', encoding='utf-8-sig')    # UTF-8, strips BOM if present
open('file.csv', encoding='latin1')       # Windows/Excel exports
```

### Java `String.length()` with emoji

Returns UTF-16 code units, not characters. `"😀".length()` = `2`.

```java
String s = "😀";
s.length();                        // 2  (UTF-16 code units)
s.codePointCount(0, s.length());   // 1  (actual characters)
```

### URL / percent encoding

Non-ASCII characters must be percent-encoded as their UTF-8 bytes. `é` (`0xC3 0xA9`) → `%C3%A9`. Double-encoding gives `%25C3%25A9`. Decoding with the wrong charset gives corrupted query params.

### HTTP Content-Type

```
Content-Type: text/html; charset=utf-8
```

Without `charset`, browsers guess. Declare it explicitly.

---

## Encoding Comparison

| Encoding | Bytes/char | ASCII compatible | Used by |
|---|---|---|---|
| ASCII | 1 (7-bit) | Is ASCII | Legacy systems |
| Latin-1 / ISO 8859-1 | 1 | 0–127 only | Western European legacy |
| Windows-1252 | 1 | 0–127 only | Windows, Excel |
| UTF-32 | 4 (fixed) | No | Some internal runtimes |
| UTF-16 | 2 or 4 | No | Java, .NET, JS internals, Windows |
| UTF-8 | 1–4 | Yes | Web, Linux, modern default |

---

## Number Base Conversion

Relevant when reading byte values and code points.

| Decimal | Hex | Binary |
|---|---|---|
| 0 | 0x00 | 0000 0000 |
| 10 | 0x0A | 0000 1010 |
| 15 | 0x0F | 0000 1111 |
| 16 | 0x10 | 0001 0000 |
| 65 | 0x41 | 0100 0001 |
| 97 | 0x61 | 0110 0001 |
| 127 | 0x7F | 0111 1111 |
| 128 | 0x80 | 1000 0000 |
| 195 | 0xC3 | 1100 0011 |
| 169 | 0xA9 | 1010 1001 |
| 233 | 0xE9 | 1110 1001 |
| 255 | 0xFF | 1111 1111 |

### Conversion rules

**Decimal → Hex:** divide by 16 repeatedly, remainders (in reverse) are the hex digits. Digits above 9: A=10, B=11, C=12, D=13, E=14, F=15.

**Hex → Binary:** each hex digit maps directly to 4 bits.

| Hex | Binary |
|---|---|
| 0 | 0000 |
| 1 | 0001 |
| 2 | 0010 |
| 3 | 0011 |
| 4 | 0100 |
| 5 | 0101 |
| 6 | 0110 |
| 7 | 0111 |
| 8 | 1000 |
| 9 | 1001 |
| A | 1010 |
| B | 1011 |
| C | 1100 |
| D | 1101 |
| E | 1110 |
| F | 1111 |

**Example:** `0xC3` → `C` = `1100`, `3` = `0011` → `1100 0011` = 195 in decimal.

**Binary → Decimal:** sum of `bit × 2^position` (right to left, starting at 0). `1100 0011` = 128 + 64 + 2 + 1 = 195.

