---
layout: post
title: "Sprint 3 @ CACIB - JSON-Avro Tool (1)"
description: >-
  Sprint recap [26/08/2024 - 9/09/2024]. Working on the JSON-Avro tool's frontend and backend.
author: ryo
date: 2024-09-10 17:58:20 +0800
categories: [Crédit Agricole, Sprints]
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

1. **MVP 1 of the JSON-Avro tool (JSON to Avro conversion)**
  - Spillover from last sprint.

2. **MVP 2 of the JSON-Avro tool (Avro to JSON conversion)**
  - Involves reversing the data conversions performed in the first MVP. 

3. **MVP 3 of the JSON-Avro tool (Thymeleaf UI)**
  - Spring MVC controllers for the tool and a Thymeleaf UI (server-side rendering).

---

### Main Activities

- **SonarQube Integration**: Integrated SonarQube into the project and addressed code smells.
- **MVP 2 Work**: Started working on the Avro-to-JSON conversion.
- **MVP 3 Work**: Developed the Thymeleaf UI for the JSON-Avro tool. The tool was dockerized and hosted on Kubernetes by a company architect.
- **Merge Request (MVP 1, 2 and 3)**: Documented and created merge requests for the JSON-Avro conversion tool.
  - Fixed MR comments regarding code quality.
- **Support**: Provided user support for the JSON-Avro conversion tool.
- **Demo**: Demo-ed the JSON-Avro conversion tool to internal stakeholders in Singapore and Paris as part of the sprint demo.

---

### Key Challenges/Blockers

- **Unfamiliar Technology**: Worked with Thymeleaf & Spring Web MVC for the first time, which took some ramp-up.
- **JSON Un-nesting Complexity**: Dealing with un-nesting JSON nodes during the Avro-to-JSON conversion was more challenging than expected.
  - Recursively un-nesting nested types like arrays and records increased complexity.
  - In contrast, converting JSON to Avro mainly involves aligning the JSON structure with the Avro schema.
- **Encoding Differences**: Encountered character encoding issues between web and CLI environments.
  - The tool has 2 clients, web and CLI. The web UI defaulted to ISO_8859-1 encoding, while the CLI used UTF-8, which caused a decimal decoding issue.

---

### Learning Outcomes

- **Thymeleaf & Spring MVC**: Gained experience with Thymeleaf and Spring Web MVC.
- **Character Encodings**: Learned about character encodings and differences between environments.
- **Stepping into the Client's Shoes**: While a developer would be happy to get a full stack-trace whenever an error occurs, a less technically-inclined client would want something more easily understood. It's possible to make both groups happy though. The solution is setting up a server logging strategy combined with returning friendly error messages to the client.

---
