---
layout: post
title: "Sprint 9 @ CACIB - Configuration Upload Tool (2)"
description: >-
  Sprint recap [18/11/2024 - 02/12/2024]. Migration of the upload tool's logic and implementation of new validations.
author: ryo
date: 2024-12-01 13:33:36 +0800
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

1. **Migrate Tool's Logic to Backend Repo**
  - The current functions of the tools, namely excel column header validation, S3 bucket upload, PostgreSQL table upload, are called by Spring Controllers to populate the Thymeleaf UI model. All of these should be moved to a new service that would be in charge of the project's backend functions, and the Controllers are to be converted to REST Controllers.

2. **Design and Implement new Configurable Functional Validations**
  - Turns out there are new functional requirements introduced for this tool. New validations to be added include 1. Mandatory Validation (control/validate that cells in a specific column must not be empty), 2. Uniqueness Validation (control/validate that cell data in a specific column must be unique), and 2. Composite Uniqueness Validation (control/validate that cell data in a specific column must be unique as a composite combination of data in other columns as well).

---

### Main Activities

- **Code Migration**: Moved and refactored code meant to be used in the MVC pattern (with Thymeleaf) to another backend service repository, converting Spring Controllers to REST Controllers. 
- **Setup Deployment for new Backend Project**: Ensure the RESTful web service for the new backend project is up and available to access on Kubernetes pods.
- **Integrate Old Frontend with new Backend**: Ensure that the old Thymeleaf frontend can call REST APIs from the new backend without issues.
- **Excel Sheet Validation Design**: These validations are designed to be configured via a PostgreSQL DB. The tool should allow for the conditional validation of data from Excel without code development, only database configurations. The data will finally be populated into S3 and selected PostgreSQL tables, which is also already configured via database configurations.
- **New Validator Class - Mandatory**: Validation configured separately in a database with a boolean column. Excel columns configured to be mandatory cannot have empty cells, otherwise the sheet validation will fail.
- **New Validator Class - Uniqueness**: Validation configured separately in a database with a comma-separates list of IDs. As every column in a sheet must be registered in the database, each has an ID. E.g. An Excel column with ID 3 configured with the uniqueness validation '3' (itself), the column must have cell values unique within itself. If the same column were to be configured with the uniqueness validation '3,4,5', the column must have cell values unique within itself and the other configured columns (like a composite key).
- **Fell Sick**
- **Demo**: To team.

---

### Key Challenges/Blockers

- **Lots of Refactoring**: Since the project started as a Spring Web MVC project with Thymeleaf, Excel sheet data was encapsulated in a data transfer class and passed around by setting attributes in the model. Unfortunately, since backend logic is to be moved to a separate service, this design has to be changed. This is because `org.apache.poi.ss.usermodel`, the Java library used for manipulating Excel sheet data, contains classes that are not serializable.

---

### Learning Outcomes

- **Overall Familiarity with Java Development**: This includes the development of web services, getting more familiar with Spring Boot and JUnit testing, and trying to implement good interface design (ISP, SRP, and Spring DI). 

---

