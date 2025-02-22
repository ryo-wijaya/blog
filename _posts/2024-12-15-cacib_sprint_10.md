---
layout: post
title: "Sprint 10 @ CACIB - Configuration Upload Tool 3"
description: >-
  Sprint recap [02/12/2024 - 16/12/2024]. Code quality fixes, unit tests, and the implementation of more validation classes for the tool.
author: ryo
date: 2024-12-16 02:20:31 +0800
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

1. **Migrate Tool's Logic to Backend Repo (con't)**
  - Sonarqube code quality fixes and unit tests.

2. **New Consistency Validator**
  - Configured separately with a comma-separated list of strings. Excel columns configured with this validation can only have row data containing one of these list values, otherwise the sheet validation will fail.

3. **New Regex Validator**
  - Configured separately with a regex pattern. Excel columns configured with this validation can only have row data that matches the configured regex pattern, otherwise the sheet validation will fail.

---

### Main Activities

- **New Validator Class - Consistency**
- **New Validator Class - Regex**
- **New Liquibase Changesets**: For functional database tables related to my tickets.
- **Code Quality Fixes**: As the project must now be scanned by Sonarqube, bugs, vulnerabilities, and code coverage must be brought up to standard.
- **Unit Tests**: From 0% (due to no previous requirement for unit testing internal utility tools).

---

### Key Challenges/Blockers

- **Wrestling with Sonarqube**: Spent some time fixing code smells and vulnerabilities. 
- **Wrestling with Unit Tests**: JUnit testing makes me want to end myself.
- **Wrestling with Liquibase**: First time using Liquibase as a database migration tool, and I ran into checksum validation problems and some other issues.
---

### Learning Outcomes

- **Overall Familiarity with Java Development**: Fixing Sonarqube issues for Java code helped me familiarize myself with things to watch out for, such as using try-with-resources blocks (for AutoClosable resources) instead of manually managing resources, or overly-complex logic flows (not enough abstraction) etc.
- **Learning to use Liquibase**: Learning how Liquibase can be used to manage database migrations, versioning, and rollbacks via code (can be source-controlled), as well as how it can be automated in the CI/CD pipeline.

---

