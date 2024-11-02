---
layout: post
title: "Sprint 7 @ CACIB - Angular UI Setup"
description: >-
  Sprint recap [21/10/2024 - 04/11/2024]. Working on setting up the Angular UI for the team's ETL monitoring product. A sprint cut short by a public holiday and a day off.
author: ryo
date: 2024-11-02 16:33:45 +0800
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

1. **Bootstrap UI Project + start onboarding to company's private IDP**
  - Kick-starting the UI for the team's ETL monitoring product. Bootstrapping an Angular project with the latest Angular version, setting up UI developer tooling, and creating the landing page (Login). Also setup the deployment to create a DEV environment.
  - Start the onboarding process to the company's private IDP, which will use OpenID Connect (based on OAuth2).

---

### Main Activities

- **Bootstrap Angular Project**: Bootstrap the Angular project with Angular 18, setting up a basic layout, routing, and auth-guard.
- **Setting up UI Developer Tools**: Setup ESLint, Prettier, lint-staged, Husky, and some Git hooks. Implemented linting, formatting, commit-message checking as Husky hooks, on files staged for commit only.
- **Creating UI Landing Page**: Created a basic Login page for the UI, with SSO sign-in as the only authentication method. Mocked the IDP calls.
- **Setting up UI Deployment**: Setup the Kubernetes manifest file, Dockerfile, GitLab CI file, and Nginx configuration file for the automated deployment onto company Kubernetes clusters.
- **Research on Company's Private IDP Provider**: Deep-dive into and the documentation of the company's IDP, including the mechanism, endpoints, security checks needed, and implementation for Angular.
- **Start the Onboarding for the IDP**: Fill up the onboarding questionnaire (functional fields, basic configurations, environment specifications and environment redirect URLs for the auth) with the help of the team and email it to the company's IAMs team. 
- **Demo Was Cancelled**

---

### Key Challenges/Blockers

- **Unfamiliarity with Angular 18**: The later versions of angular bring about some new ways of doing things such as standalone components and signals. I also wasn't very familiar with Angular in the first place so it took a little more time than expected to get everything up and running. 
- **ESLint**: Had some problems with getting ESLint to actually work with its newer flat config format vs the older typical eslintrc formats. Turns out I just had a stupid typo somewhere :rage:.
- **Unfamiliarity with CI/CD**: Spent some extra time on reading into configuring the deployment files for an Angular project. Also spent some extra time debugging errors in my GitLab pipeline stemming from mistakes such as a wrong service account used, wrongly configured Nginx configuration file, as well as a wrongly written Dockerfile. The inability to install Docker locally (due to reasons) did not help, since testing would have to be done on deployed instances.

---

### Learning Outcomes

- **Familiarity with Angular 18**: Gained a little more understanding about the newer Angular changes.
- **Familiarity with CI/CD**: Gained a little more understanding about how deployment works in general (from CI/CD to Docker image repository to Kubernetes cluster), as well as the concept of image-tagging. Its definitely something I still have to research more on and document properly (for personal notes).
- **Familiarity with Authentication**: Gained some idea of how OpenID Connect is supposed to work and how I can implement it. This also needs more research.

---

