---
layout: post
title: "Sprint 2 @ CACIB - Onboarding"
description: >-
  Sprint recap [12/08/2024 - 26/08/2024]. My first sprint in the team. Onboarding, orientations, and self-learning.
author: ryo
date: 2024-08-29 14:52:23 +0800
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

1. **Confluence New Joiner Onboarding Checklist**
  - Building the team's documentation for future new joiners.

2. **MVP 1 of the JSON-Avro tool (JSON to Avro conversion)**
  - **Date** - Date strings need to be converted to days after unix epoch. Avro expects 'Integer' types as it's more efficient for storage and querying.
  - **Decimal** - Decimal needs to be converted to encoded strings e.g. (\u00FF). Avro expects 'Byte' types as it's more efficient for storage and querying.
  - **Namespace Specification** - JSON nodes with matching Avro schema type 'Union' must be nested with the full Namespace specification. This is to avoid ambiguity for which field-schema the Avro serialization engine should use for encoding, as 'Union' types can include multiple complex types.
  - **Type Specification** - JSON nodes with matching Avro schema type 'Union' must be provided the fully qualified Type name. This is to avoid ambiguity for which Type the Avro serialization engine should expect within the 'Union', as 'Union' fields can allow multiple Avro Types.

---

### Main Activities

- **Meetings:**

  - Setting objectives/expectations with the manager.
  - Functional knowledge transfer (KT) on upstream financing applications for the project.
  - Staff orientation meetings (Business Continuity Planning (BCP), anti-phishing, policies, and compliance, etc.).
  - Task & requirements gathering meetings from the BA for an internal project: a JSON <-> Avro conversion tool to be used by BAs in Singapore and Paris.

- **Tasks:**
  - Setting up of local development environment.
  - Documenting team conventions, software installation guide, and new joiner checklist on Confluence.
  - Self-study on Avro, Java Spring Boot, and functional financing documentation.
  - MVP 1 for the JSON-Avro tool (JSON to Avro conversion) with documentation.

---

### Key Challenges/Blockers

- Working with unfamiliar technology (Java Spring Boot, Avro).
- Trying to grasp some functional financing know-how.

---

### Learning Outcomes

- Gained familiarity with core Java programming, as well as jackson by FasterXML.
- Gained familiarity with Spring Boot, Maven, and Java dependency management.
- Gained familiarity with the Apache Avro serialization format.
- Gained insight into how a bank's core business operates, especially in the area of corporate financing, e.g.:
  - What the front, middle, and back office do and how they interact.
  - How corporate loans, loan syndication, distribution, lender & borrower pools, and loan agents work.
  - The difference between secured and unsecured loans, or revolving credit and term loans.
  - How deals, contracts, loan tranches, and loan utilizations work and how their data is typically structured.
