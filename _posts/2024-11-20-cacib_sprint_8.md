---
layout: post
title: "Sprint 8 @ CACIB - GitLab CI/CD"
description: >-
  Sprint recap [04/11/2024 - 18/11/2024]. Mostly working on helping to refine the team's GitLab CI/CD pipelines.
author: ryo
date: 2024-11-20 18:23:35 +0800
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

1. **Establish A Common Base GitLab CI Project**
  - The team currently manages 4-5 projects, one Angular and the rest Java, where each project has its own unique GitLab CI file. The idea is to create a new project containing base GitLab CI files for Java/Angular, that each project can "inherit" from. The parent CI files should contain all possible stages. A project should be able to run a subset of stages by skipping any stage from the parent file.

2. **CI/CD Gap Analysis**
  - One of the company's architects had previously drawn up a design document containing a CI/CD flowchart and individual stage details. There are discrepancies between each project's CI/CD flow and the designed flow. The end goal is a document that identifies these discrepancies to be able to create technical tasks aimed at fixing them.   

---

### Main Activities

- **Create Common GitLab CI Files**: Create CI files abstracting out the stages build, test, version, sonar scan, publish jar, build docker, deploy to dev, and other stages to a common parent location for both Java and Angular. The current GitLab CI/CD file hierarchy is: Base CI file (common tags, tools, images) >> Tech Stack specific CI file >> Project CI file.
- **Test and Validate each Project's Pipeline**: Version tag the common GitLab files and refactor each project's CI file to extend from the parent CI files, skipping any stage that is not necessary for that project. Each project's CI file can also pass in project specific variables to the parent file.
- **CI/CD Gap Analysis**: Go through the design document for the expected CI/CD flow and note the differences for each project's CI/CD pipeline between the expected flow and the actual flow. For example, some stages should not trigger for some branches, some stages should be manual but it is not, some stages are missing, some stages happen in the wrong order, etc.
- **Validate OpenIDC Credentials for the Company's IDP**: In the previous sprint I started the onboarding process for SSO in the new UI project. The onboarding for our dev environment was completed this sprint, hence I tested the credentials through the SSO flow, simulated from browser to postman to a python script decoding the JWT. I got back to the IDP team so they can validate the logs and documented the testing process.
- **Spark Training**: Attended the first session of company-wide Apache Spark training.
- **Demo Was Cancelled**

---

### Key Challenges/Blockers

- **Unfamiliarity with current project's CI**: I wasn't familiar with some of the tools and steps in the current pipeline for a couple of the projects, so I had to spend some time studying them first.
- **Unfamiliarity with GitLab CI**: I wasn't familiar with GitLab CI in general, and had to spend some time studying the template syntax as well as some of the keywords.
---

### Learning Outcomes

- **Familiarity with GitLab CI/CD**: E.g. Turns out you can use the `include` and the `local` keyword to reference a parent CI file in the same repository (for inheritance from the base CI file to the Tech Stack specific CI file). For cross-repository inheritance, instead of using `remote` to reference a URL, you can reference CI files in the same top-level group or subgroup via the `project`, `ref`, and `file` keywords. There are also certain limitations to this approach, such as YAML anchors and aliases from parent CI files not being usable by child CI files (cross-file referencing), instead the `extends` keyword should be used, leading to some refactoring across the projects. Also, all child CI files inheriting from parent CI files must implement/specify all the stages from the parent. If a stage is to be skipped, the `when` keyword specifying `never` should be used. To be able to achieve this, all original stage definitions from the parent CI file must use `when` instead of `only` to define conditional usage, as both keywords conflict with each other.
- **Some Familiarity with Bash Scripting**: Some of the project's original pipelines contained a number of bash scripts to run reports (e.g. SonarQube, Checkmarx), or setup build tools or image versioning etc. Having never done it before it was nice to see and learn how it's done.

---

