---
layout: post
title: "HTTP & REST Fundamentals"
description: >-
  HTTP Concepts Cheatsheet: methods, status codes, headers, caching, CORS, URL encoding, and REST API design conventions.
author: ryo
date: 2024-11-13 00:00:00 +0800
categories: [Web Development]
tags: [http, web, rest, api]
toc: true
comments: true
pin: false
published: true
---

## Overview

HTTP (HyperText Transfer Protocol) is a stateless request-response protocol. A client sends a request, a server responds. Most of the web runs on this. It is defined by the IETF through RFC documents, e.g. HTTP/2 is [RFC 9113](https://www.rfc-editor.org/rfc/rfc9113).

There are three versions in use today:
- **HTTP/1.1** handles one request at a time per connection. Most older or simpler servers use this.
- **HTTP/2** sends multiple requests over the same connection at once. Most modern web apps and APIs use this.
- **HTTP/3** uses QUIC instead of TCP, making it faster and more resilient on unstable connections like mobile networks.

---

## HTTP Methods

| Method | Purpose | Request Body |
|---|---|---|
| **GET** | Retrieve a resource | No |
| **HEAD** | Same as GET but no response body | No |
| **POST** | Create a resource or trigger an action | Yes |
| **PUT** | Replace an entire resource | Yes |
| **PATCH** | Partially update a resource | Yes |
| **DELETE** | Remove a resource | No |
| **OPTIONS** | Describe allowed options | No |

### PUT vs PATCH

PUT replaces the entire resource. Sending only `{ "price": 999 }` via PUT wipes every other field. PATCH only updates what is sent.

### Notes

- Don't put actions in URLs. `POST /api/products/456/publish` is fine for an action, but `GET /api/deleteProduct/456` is not. Use `DELETE /api/products/456`.
- POST is not a catch-all. If the operation is a retrieval, update, or deletion, use the appropriate method.
- PUT and PATCH are not interchangeable. If the client only has a partial payload, use PATCH.

---

## Status Codes

### 2xx -- Success

| Code | Name | When to Use |
|---|---|---|
| **200** | OK | Standard success. Return with response body. |
| **201** | Created | Resource was successfully created. Include `Location` header pointing to new resource. |
| **202** | Accepted | Request accepted but processing is async. Used for long-running operations. |
| **204** | No Content | Success but nothing to return. Typical for DELETE or PATCH with no response body. |

**200 vs 204**: if there is nothing to return (delete succeeded, update acknowledged), use 204. Returning 200 with an empty body is technically wrong.

### 3xx -- Redirects

| Code | Name | When to Use |
|---|---|---|
| **301** | Moved Permanently | Resource has permanently moved. Browsers cache this aggressively, so avoid it for anything that might change. |
| **302** | Found | Temporary redirect. Browser does not cache. |
| **303** | See Other | Redirect after a POST (POST-Redirect-GET pattern). Forces GET on the new URL. |
| **304** | Not Modified | Resource has not changed. Used with `ETag`/`If-None-Match`, no body sent, client uses its cache. |
| **307** | Temporary Redirect | Like 302 but preserves the original HTTP method. POST stays POST after redirect. |
| **308** | Permanent Redirect | Like 301 but preserves the original HTTP method. |

### 4xx -- Client Errors

| Code | Name | When to Use |
|---|---|---|
| **400** | Bad Request | Malformed request: invalid JSON, missing required fields, bad syntax. |
| **401** | Unauthorized | Missing or invalid authentication credentials. |
| **403** | Forbidden | Authenticated but not authorized to access this resource. |
| **404** | Not Found | Resource does not exist. |
| **405** | Method Not Allowed | HTTP method not supported for this endpoint. |
| **409** | Conflict | Request conflicts with current state: duplicate resource, version mismatch. |
| **422** | Unprocessable Entity | Request is structurally valid but semantically wrong (e.g., business rule violation). |
| **429** | Too Many Requests | Rate limit hit. Include `Retry-After` header. |

**401 vs 403**: 401 means the server does not know who you are (missing or invalid credentials). 403 means it does know who you are, but you do not have permission. A logged-in user hitting an admin-only endpoint gets 403, not 401.

### 5xx -- Server Errors

| Code | Name | When to Use |
|---|---|---|
| **500** | Internal Server Error | Unexpected server-side failure. Log it, do not expose internals to the client. |
| **502** | Bad Gateway | Server acting as a proxy received an invalid response from upstream. Usually an infrastructure issue. |
| **503** | Service Unavailable | Server is down or overloaded. Include `Retry-After` if recovery time is known. |
| **504** | Gateway Timeout | Upstream server did not respond in time. |

---

## HTTP Headers

### Common Request Headers

| Header | Example | Purpose |
|---|---|---|
| **Authorization** | `Bearer eyJhbGc...` | Sends auth token. |
| **Content-Type** | `application/json` | Format of the request body. |
| **Accept** | `application/json` | Formats the client expects in the response. |
| **Host** | `api.example.com` | Target server hostname. Required in HTTP/1.1. |
| **Cookie** | `session_id=abc123` | Sends stored cookies to the server. |
| **If-None-Match** | `"v1abc123"` | Sends stored ETag for conditional requests. |
| **If-Modified-Since** | `Wed, 21 Oct 2024 07:28:00 GMT` | Sends last-known modified date for conditional requests. |
| **Origin** | `https://app.example.com` | Indicates where the request originated (used in CORS). |

### Common Response Headers

| Header | Example | Purpose |
|---|---|---|
| **Content-Type** | `application/json; charset=utf-8` | Format of the response body. |
| **Set-Cookie** | `session_id=xyz; Path=/; Secure; HttpOnly` | Instructs the client to store a cookie. |
| **Location** | `https://api.example.com/products/456` | Redirect target or URL of newly created resource. |
| **Cache-Control** | `max-age=3600, public` | Caching instructions. |
| **ETag** | `"v1abc123"` | Version identifier for the resource. Used for conditional requests. |
| **Last-Modified** | `Wed, 21 Oct 2024 07:28:00 GMT` | When the resource was last changed. |
| **Access-Control-Allow-Origin** | `https://app.example.com` | CORS: which origin can access this. |
| **Retry-After** | `60` | Seconds to wait before retrying (used with 429, 503). |

---

## Caching

### Cache-Control

The primary header for controlling cache behaviour.

**Response directives (server → client):**

| Directive | Meaning |
|---|---|
| `max-age=N` | Cache is valid for N seconds. |
| `public` | Any cache (browser, CDN, proxy) can store this. |
| `private` | Only the browser can cache. Proxies cannot. Use for user-specific data. |
| `no-cache` | Cache can store it, but must revalidate with the server before each use. |
| `no-store` | Don't cache at all. Use for sensitive data. |
| `must-revalidate` | Once stale, must revalidate before serving. |

### Conditional Requests (ETag / Last-Modified)

Avoids sending a full response body when nothing has changed.

1. Server sends `ETag` (resource version hash) and/or `Last-Modified` in the response.
2. Client stores both. On next request, sends `If-None-Match: <etag>` and/or `If-Modified-Since: <date>`.
3. Server checks if the resource has changed:
   - No change → `304 Not Modified` (empty body, client uses its cache).
   - Changed → `200 OK` with updated resource.

```
# Initial response
200 OK
ETag: "v2abc"
Cache-Control: max-age=3600

# Client re-requests after cache expires
GET /api/resource
If-None-Match: "v2abc"

# If unchanged
304 Not Modified
(no body)
```

---

## CORS

CORS (Cross-Origin Resource Sharing) is a browser mechanism that controls which cross-origin requests are allowed. Browsers enforce the **same-origin policy**: a page at `https://app.example.com` cannot make requests to `https://api.example.com` without explicit server permission.

Two URLs share the same origin only if protocol, domain, and port all match.

### Simple Request

Applies to GET/HEAD/POST with standard headers. Browser adds the `Origin` header automatically.

```
GET /api/products
Origin: https://shop.example.com

-> 200 OK
Access-Control-Allow-Origin: https://shop.example.com
```

Browser checks if the response origin matches. If not, it blocks the response from client-side code (the request still hit the server).

### Preflight Request

Applies to PUT, PATCH, DELETE, or requests with custom headers. Browser sends an `OPTIONS` request first.

```
OPTIONS /api/products/456
Origin: https://shop.example.com
Access-Control-Request-Method: PUT
Access-Control-Request-Headers: Content-Type

-> 200 OK
Access-Control-Allow-Origin: https://shop.example.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Content-Type
Access-Control-Max-Age: 86400
```

If the preflight passes, the browser sends the actual request.

### CORS Response Headers

| Header | Purpose |
|---|---|
| `Access-Control-Allow-Origin` | Which origins are allowed. `*` = any, but incompatible with credentials. |
| `Access-Control-Allow-Methods` | Allowed HTTP methods. |
| `Access-Control-Allow-Headers` | Allowed request headers. |
| `Access-Control-Allow-Credentials` | Whether cookies/auth headers can be sent. Requires a specific origin, not `*`. |
| `Access-Control-Max-Age` | Seconds to cache the preflight response, reducing round trips. |

### Notes

- Setting `Access-Control-Allow-Origin: *` alongside `Access-Control-Allow-Credentials: true` does not work. Browsers reject this combination.
- Any custom request header (e.g. `X-Request-ID`) must be listed in `Access-Control-Allow-Headers`, otherwise the preflight will fail.
- Some frameworks do not automatically handle OPTIONS requests. This needs to be configured explicitly on the server.

---

## URL Structure & Encoding

A URL has several distinct parts:

```
https://shop.example.com:443/api/products?category=phones&sort=price#reviews
\_____/ \______________/ \_/ \__________/ \________________________/ \_____/
scheme       host       port    path             query string        fragment
```

| Part | Description |
|---|---|
| **Scheme** | Protocol: `http` or `https`. |
| **Host** | Domain or IP address of the server. |
| **Port** | Optional. Defaults to 80 for HTTP, 443 for HTTPS. |
| **Path** | Identifies the resource on the server. |
| **Query string** | Key-value pairs after `?`, separated by `&`. Used for filters, pagination, etc. |
| **Fragment** | Starts with `#`. Processed entirely by the browser, never sent to the server. Used to jump to a section of a page. |

### URL Encoding

URLs can only contain a limited set of characters. Anything outside that set must be percent-encoded: the character is replaced with `%` followed by its hex value.

| Character | Encoded | Common Scenario |
|---|---|---|
| Space | `%20` or `+` (in query strings) | Search terms, names with spaces |
| `#` | `%23` | When `#` is meant as data, not a fragment |
| `&` | `%26` | When `&` appears inside a query param value |
| `=` | `%3D` | When `=` appears inside a query param value |
| `/` | `%2F` | When `/` is part of a value, not a path separator |
| `+` | `%2B` | When a literal `+` is needed vs space |
| `@` | `%40` | Emails in query params |

```
# Raw
GET /api/products?name=iPhone 16&tag=new&improved

# Encoded
GET /api/products?name=iPhone%2016&tag=new%26improved
```

### Fragment (#)

The fragment is stripped by the browser before the request is sent. The server never sees it. It is purely client-side, used for anchor links within a page or in single-page apps for client-side routing. E.g. 

```
https://ryo-wijaya.me/#experience
# Server receives: GET /
# Browser scrolls to: <section id="experience">
```

---

## REST API Design

REST is an architectural style, not a standard. These are the conventions I see most applications follow.

### Resources, Not Actions

URLs should represent resources (nouns). The HTTP method already expresses the action, so the URL does not need to repeat it.

```
# Product catalog example
GET    /api/products               # list all products
GET    /api/products/iphone-16     # get a specific product
POST   /api/products               # create a product
PUT    /api/products/iphone-16     # replace a product
PATCH  /api/products/iphone-16     # update fields on a product
DELETE /api/products/iphone-16     # delete a product

# Nested resource
GET    /api/products/iphone-16/reviews    # reviews for a product
POST   /api/products/iphone-16/reviews   # add a review
```

Avoid putting verbs in paths like `/api/getProducts` or `/api/deleteProduct/iphone-16`.

### Query Parameters

Use query params for filtering, sorting, and pagination, not path segments.

```
GET /api/products?category=phones&in_stock=true
GET /api/products?sort=price&order=asc
GET /api/products?page=2&limit=20
```

### Versioning

**URL versioning** (most common):
```
GET /api/v1/products
GET /api/v2/products
```

### Consistent Error Format

```json
{
  "status": 400,
  "error": "VALIDATION_ERROR",
  "message": "Price must be a positive number",
  "details": [
    { "field": "price", "reason": "must be > 0" }
  ]
}
```

---

## Common Flows

### Login (Token-Based)

```
POST /api/auth/login
Content-Type: application/json
{ "email": "john@example.com", "password": "secret" }

-> 200 OK
{ "token": "eyJhbGc..." }

# Subsequent request
GET /api/account/me
Authorization: Bearer eyJhbGc...
```

### File Upload

```
POST /api/products/iphone-16/images
Content-Type: multipart/form-data; boundary=----Boundary

------Boundary
Content-Disposition: form-data; name="file"; filename="front.jpg"
Content-Type: image/jpeg
[binary data]
------Boundary--

-> 201 Created
Location: /api/products/iphone-16/images/front.jpg
```

### Rate Limiting

```
-> 200 OK
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 42

# After limit exceeded
-> 429 Too Many Requests
Retry-After: 60
```

---
