---
layout: post
title: "Sprint 4 @ CACIB - JSON-Avro Tool (2)"
description: >-
  Sprint recap [09/09/2024 - 23/09/2024]. Working on the JSON-Avro tool's frontend and backend, as well as starting work on the main project.
author: ryo
date: 2024-09-22 17:58:20 +0800
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

1. **MVP 4 the JSON-Avro tool (demo feedback)**
  - Support bulk file conversion, with a table to view conversion status for each file, as well as a 'download all as ZIP folder' functionality.
  - Support a static directory of Avro schemas to be selected during conversion, with the option to override it with a user-uploaded schema.
  - UI improvements.

2. **Unit test coverage for a certain set of Java ETL drivers (in the main project)**
  - More coverage was needed to pass Sonarqube checks.

---

### Main Activities

- **MVP 4 Work**: Worked on MVP 4 for the JSON-Avro tool, documented it, and created a merge request.
- **Project Setup**: Setting up the main Java project modules locally with IntelliJ.
- **Task Preparation**: Received more KTs for the main project, learned some JUnit, and familiarized myself with the overall codebase.
- **Unit Test Coverage Work**: Wrote tests for my assigned ticket and created a merge request for it.
- **Demo Was Cancelled**

---

### Key Challenges/Blockers

- **Unfamiliar Technology**: With Java development, ETL (for batch) pipelines, and complex code architectures.
- **Dependency Installation Problems**: Turns out my VM was wrongly configured with a different subnet and DNS server from the rest of the team.

---

### Learning Outcomes

- **Java Dependency Management**: Learned about Java dependency management with regards to web proxies and using internal company artifact repositories.
- **Familiarity with JUnit Testing**: JUnit and good testing practices.
- **Familiarity with Spark Java**: A lot of the testing involves working with Java Spark Datasets.
- **Familiarity with Java Developer Tools**: IntelliJ plugins, modules management, Maven tools, etc.

---
