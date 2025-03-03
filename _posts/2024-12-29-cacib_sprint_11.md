---
layout: post
title: "Sprint 11 @ CACIB - Implementing SSO & Configuration Upload Tool (4)"
description: >-
  Sprint recap [16/12/2024 - 30/12/2024]. Implemented OAuth2 based SSO (OpenID Connect), as well as new validations for the configuration upload tool.
author: ryo
date: 2024-12-29 01:16:53 +0800
categories: [Credit Agricole, Sprints]
tags: [sprint]
image:
  path: assets/img/cacib/cacib-logo-2-modified.png
  alt: CACIB Logo
show_image_in_post: false
toc: true
comments: false
pin: false
published: true
---

### Jira Tickets

1. **Implement Company SSO into UI Project**
  - The flow to implement is the OAuth 2.0 Authorization Code Flow with OpenID Connect (OIDC) for Single Sign-On (SSO) flow.

2. **New Group Upload Validator**
  - Configured separately in a database with a 'group_upload_with' sheet name. Excel sheets configured with this validation can only be uploaded to S3 and database locations if the specified 'group_upload_with' sheet is also included.

---

### Main Activities

- **SSO Implementation**: Made changes to UI, backend, and deployment project. The authorization code flow simplified is as follows: UI --(redirect)--> IDP --(redirect)--> UI --(POST request)--> Backend --(POST request)--> IDP --(response)--> Backend --(response)--> Frontend, with the final response being a JWT token. Unit tests.
- **Configuration Upload Tool Hotfixes**: Refactor Consistency Validator class to be case-insensitive (e.g. for a configured value 'abc,123,xyz', cells with data such as 'AbC' or 'XYZ' will not fail the validation). Other refactoring.
- **JSON-Avro Tool QoL Changes**: Specify exact upload locations (S3 and DB) instead of just success messages. Adjust margins.
- **Deploy JSON-Avro Tool to INT**: A new environment now exists (INT). Promoted image to staging + deployed latest DB changes. 
- **New Validator Class - GroupUpload**: Validation configured separately in a database with a comma-separated 'group_upload_with' sheet name. E.g. Excel sheets configured with the 'group_upload_with' validation 'sheetA,sheetB' can only be uploaded to S3 and database locations if the Excel file includes sheetA and sheetB, and sheetA and sheetB both pass their own validations and are also selected for upload. 
- **Demo**: To team.

---

### Key Challenges/Blockers

- **First Time Implementing OIDC SSO**: Spent some time to research good practices for the required authentication flow, such as implementing measure to prevent token theft and CSRF attacks.  

---

### Learning Outcomes

- **Overall Familiarity with Java Development**: Refactored code to use Lombok annotations, follow standard principles (logging, proper Spring DI), and other good Java coding practices. E.g. I didn't know that [Spring Constructor Injection should always be used over Field Injection](https://medium.com/@anil.java.story/why-spring-constructor-injection-is-the-recommended-approach-75edca1f9b36). This 1. Ensures dependencies are final and immutable and 2. prevents the risk of `null` dependencies (as injection always takes place after the class/bean is initialized). 
- **Familiarity with OAuth2.0 Authorization Code Flow**: Understanding the implementation of each step in the flow.

| *    | From    | To      | Description |
|------|---------|---------|-------------|
| 1    | UI      | IDP     | User is redirected to the IDP for authentication. A few things are included as query parameters, a UUIDv4 `state` (to prevent CSRF), and `nonce` (to prevent replay attacks). |
| 2    | IDP     | UI      | IDP validates the login, associates the `nonce` with the session, and redirects back with a short-lived one-time authorization code and the same `state`. The UI must check that the `state` is the same to ensure request integrity. |
| 3    | UI      | Backend | Frontend sends the auth `code` along with the original `nonce` to the backend for validation and token exchange. |
| 4    | Backend | IDP    | Backend exchanges the authorization `code` for an ID token and access token (JWT). |
| 5    | IDP     | Backend | IDP returns an ID token (with `nonce` claim) and an access token (JWT). The backend must: (1) Recompute the RSA public key using the `modulus` and `exponent` values provided in the IDP’s public JWKs and verify the JWT's signature to ensure authenticity, and (2) Validate that the `nonce` in the ID token matches the originally sent `nonce` to prevent replay attacks. |
| 6    | Backend | UI     | After the token is verified, it is returned to the frontend. |



---