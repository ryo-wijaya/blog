---
layout: post
title: "Sprint 5 @ CACIB - Configuration Upload Tool"
description: >-
  Sprint recap [23/09/2024 - 07/10/2024]. Started working on frontend and backend components for another internal tool.
author: ryo
date: 2024-10-06 12:25:34 +0800
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

1. **Configuration Upload Utility Tool**
  - Rebrand the JSON-Avro tool to be a generic utility web platform for the team, and include a new configuration upload module in it.
  - The idea is that BAs should be able to upload Excel files, have the sheets validated, uploaded into S3, stored in an archive, and have the data updated in the corresponding tables (for each Excel sheet) in the PostgreSQL database. The data in these tables can contain configurations or parameters, and will be automatically pulled by the system during the running of ETL tasks.
  - Every upload/insert to a location should have an audit trail stored in PostgreSQL.

---

### Main Activities

- **Fell Sick**: :+1:
- **Trainings**: SQL, GitLab CI/CD, and Azure DevOps trainings as part of a department-wide new joiner training initiative.
- **Gain Accesses**: Project S3, PostgreSQL, Certificates, etc.
- **Utility Tool Work**: Started working on the frontend and backend components for the tool. While it's initially supposed to be for 1 type of configuration data, extra time was spent making the tool generic and user-friendly, and able to ingest any type of configuration or parameter data. Documented it and wrote a user guide.
- **Demo Was Cancelled**

---

### Key Challenges/Blockers

- **Certificates**: I was getting a `PKIX path build failure: unable to find valid certification path` error thrown by the AWS client when attempting to upload into AWS S3 from my Java application. Turns out I had to import a certificate into my java trust store with `keytool`. Also had to do this in my Dockerfile for the runtime used by the container running in Kubernetes (for the deployed tool).

---

### Learning Outcomes

- **Security Infrastructure: Certificates**: Learned about the practical use of certificates in SSL/TLS communication to secure connections. Server certificates are often checked to see if it's issued by a trusted authority.
- **Security Infrastructure: Trust Stores**: Learned about repositories called trust stores such as `cacerts`, the default java trust store that comes with the JDK and JRE. It's a file containing a collection of trusted certificates from well-known Certificate Authorities (CAs). `keytool` can be used to import root/intermediate certificates of servers into this keystore file.

---
