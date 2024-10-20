---
layout: post
title: "Sprint 6 @ Crédit Agricole CIB"
description: >-
  Sprint recap [07/10/2024 - 21/10/2024]. Working on UI analysis of other Angular projects in the bank, in preparation for UI development.
author: ryo
date: 2024-10-20 20:00:20 +0800
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

1. **UI Analysis for Angular Project A (UI Components)**
  - The bank uses it's own in-house UI component library, which implements the bank's design language. Project A has been successful in implementing and extending this component library.
  - My task is to identify and document components in project A that wrap these in-house UI components, including models used and inputs/outputs, and analyze what will be reusable for the upcoming UI development for my team's ETL-monitoring task.

2. **UI Analysis for Angular Project B (Functionality)**
  - While Angular project B is older and doesn't implement the bank's in-house UI component library, its functionalities are more in-line with the upcoming UI development task for my team (ETL-monitoring).
  My task is to identify services and components that will be reusable with regards to ETL-monitoring, along with API requests/responses, and models used.

---

### Main Activities

- **Organizational Meetings**: Company Town Hall, updates on upcoming technologies to be introduced within CACIB in the near future, product presentations to department heads by department architects, etc.
- **Trainings**: Angular trainings as part of a department-wide new joiner training initiative.
- **Frontend JavaScript Environment Setup**: Setup of Node & NPM, including company proxy servers and Angular CLI.
- **Gain Accesses**: Getting dev environment and source code access to both project A and B took a little time.
- **Worked on UI Analysis and Documentation**: For both project A and B on confluence.
- **Demos**: Demo-ed the Configuration Upload Utility Tool from last sprint (sprint 5) twice, one to BAs, and one to the entire team as part of the sprint demo.

---

### Key Challenges/Blockers

- **Unfamiliarity with Angular**: Most of my frontend experience at the time was either with React or React-based frameworks, and server-side rendering Java solutions (JSP, JSF, Thymeleaf). I've touched Angular before in school, but not in depth.
- **Oof**: UI Documentation can get mind-numbing :skull:.

---

### Learning Outcomes

- **Familiarity with Angular**: It turns out that spending 2 whole weeks reading, trying to understand, and documenting Angular code actually helps in learning how Angular works, including how large Angular application implement certain good Angular practices. 
- **Gain Understanding on Team's Core ETL Project**: It turns out that many (or most) development operations in my department work with managing complex ETL chains, where each step in the chain can work with large amounts of data. Seeing and using the UI implementations of Project A and B firsthand helped me better understand my own team's core product.

---
