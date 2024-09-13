---
layout: post
title: "My SWE Internship Experience @ Reluvate"
description: >-
  A brief overview of my software engineering internship at Reluvate Technologies that I undertook during the summer at the end of my second year of university (May 2022). Unfortunately, I'm writing this a little over 2 years too late so my memory might not be all there.
author: ryo
date: 2024-09-08 11:18:47 +0800
categories: [Internship]
image:
  path: assets/img/internship/reluvate-logo.jpg
  alt: Reluvate Technologies Logo
show_image_in_post: false
toc: true
comments: true
pin: false
published: true
---

## Introduction

Reluvate Technologies was a company that I applied to for a 3-month internship, right after my 2nd year at university ended. I actually spent half of my first year as a NUS Business student, leaving me a bunch of stuff to catch up on when I finally transferred courses. This led to me unfortunately not having any prior development experiences besides what I had learned in school, essentially meaning that I was going in blind. I applied for the Backend Software Engineering Intern role.

## About Reluvate Technologies

![Reluvate Logo](assets/img/internship/reluvate-logo-mini.png){: width="260" height="260" .right}

<a href="https://www.reluvate.com/" target="_blank">Reluvate Technologies</a> is a Singapore-based startup specializing in IT consulting, with a focus on AI and automation solutions. Their aim is to empower businesses into becoming autonomous organizations (AOs), providing customized tools and software to improve operational efficiency and free up manpower and time for strategic decision-making.

Working with Reluvate was quite the trip, but in a good way. Reluvate fosters a flexible work environment that minimizes micromanagement, empowering employees with the freedom to manage their own schedules (you'll see many people working strange hours, like after midnight, including me). Team members are given the opportunity to contribute to every stage of the product lifecycle, from idea conception to final delivery. As a small company, you'll also have plenty of opportunities to interact with the startup founders, who are honestly a different breed of people when it comes to embodying ownership and commitment.

## Projects and Responsibilities

Out of the few teams in Reluvate, I ended up joining a team dubbed as <a href="https://www.growthmentor.com/glossary/what-is-an-indie-hacker/" target="_blank">Indie Hackers</a>. The idea is to iterate fast, operate with autonomy, and to be product-focused. This small team consisted of me (the backend engineer), a full-time frontend engineer, and a web designer. I was told that the general timeline would involve working on **one project per month**, at the same time allocating resources to occasionally maintaining past projects.

As this was a 3 month summer internship, I ended up working on 3 core projects, along with other side tasks:

### 1. Automated Hiring Portal

As my first proper software engineering project, I was clueless on how to do even the simple stuff, such as managing secrets or dealing with dependency and environment issues. Big thanks to the CEO, who hopped on many calls with me (often at super late hours) to mentor me through the basics of engineering as well as how to approach problems in a systematical way :blush:. Their live hiring portal can be found [here](https://umeume-ffd05.web.app/).

- **Description**: This is an end-to-end automated hiring web platform to manage recruitment, interviews, technical assessments, and document exchange.
- **My Role**: 90% backend development, 10% frontend development.
- **Tech Stack**: JavaScript, Node, React, GCP (Cloud Functions, Firestore, and Cloud Storage).
- **Key Contributions**:
  - CRON jobs that scrapes emails from candidates using JSSoup, directing them to the hiring platform.
  - CRON jobs that trigger email reminders, some with .ics invites, for advancements in the hiring stages, such as interviews, assessments, offers, and document signing.
  - REST APIs for triggering notifications to either the candidate, hiring manager(s) or both groups, after advancements in the hiring stages.

---

### 2. Accounting Web Platform

This project uses the exactly same tech stack as the first, but Python was chosen in place of JavaScript due to differences in PDF generation libraries. This project was the most technically challenging one for me, mostly due to the implementation of recurring payment invoices.

- **Description**: This product automates the management of a company's clients, projects, quotations and invoice generation, recurring payments, and document exchange.
- **My Role**: 100% backend development.
- **Tech Stack**: Python, GCP (Cloud Functions, Firestore, and Cloud Storage).
- **Key Contributions**:
  - REST APIs and services to manage email document exchange and generate financial accounting statistics such as total remaining payment balance per project, total paid amount, and payment history.
  - REST APIs and services to generate quotation and invoice PDFs from HTML templates, populating them with line items.
  - Daily CRON job to generate new billing invoices based on recurring settings specified for the project, akin to the functionality of Google/Outlook calendars for appointment generation.
  - Daily CRON job to traverse outstanding invoices for each project and send reminder emails based on configured reminder settings to the project's principal POC with the invoice PDF, minus any balances that has been paid.

---

### 3. Intranet Web Platform

This was the biggest project I did at Reluvate. This involved the migration and subsequent management of master data from an MSSQL database to a PostgreSQL Cloud instance. Unfortunately, I did not manage to see this project to its end, as 3 months had already elapsed by then.

- **Description**: This product manages a client's cost-centers, accounts, projects, and deliver data-based report generation and analytical charts.
- **My Role**: 100% backend development.
- **Tech Stack**: Python and SQLAlchemy, PostgreSQL, GCP (Cloud Functions, Cloud SQL).
- **Key Contributions**:
  - User authentication and access right management
  - REST APIs for the CRUD of core data components, including email notifications
  - REST APIs for data to be fed to frontend analytical charts
  - DDL and DML SQL scripts for data migration

---

### 4. Other Activities

Besides the 3 core projects, I also helped out when needed with other project teams, as well as participated in proof of concept (POC) development for new project ideas. These involved:

- Integration of Cypress UI testing for regression and E2E testing.
- Implemented a speech-to-text WebSocket server with Python socketIO and Google Speech, also working on the frontend client and components for dynamic real-time display of transcribed text.
- Implemented backend REST APIs in existing Django projects to be used for frontend analytical charts.

## Challenges Faced

Most of the challenges I faced during this internship stemmed from my unfamiliarity with the tech stack (I had only done Java projects in school prior to this), or rather my unfamiliarity with real-world development in general. I needed some ramp up time to learn and develop good software engineering practices as well as master the art of Googling, as my seniors were also pretty busy themselves and didn't have much time for mentorship. I also had some problems managing expectations, and I ended up pushing myself too hard to deliver on features quickly.

## What I've Learned

- **Technical:**

  - How to set up a proper production environment, such as managing secrets and environment variables.
  - Dependency management can be a nightmare across different environments.
  - Gained understanding of software engineering practices like clean code, SOLID principles, and testing.
  - Hands-on experience with Cloud Service Providers (CSPs) like Google Cloud Platform for hosting and deployment.
  - Development basics, including Git workflows, build tools, effective error handling, and debugging techniques.

- **Non-technical:**
  - The importance of clear communication, especially when managing expectations across different stakeholders, and gathering requirements.
  - Learning to work autonomously and being resourceful when troubleshooting or researching solutions.
  - Everything is 'figure-outable', and its common for us developers to want to solve problems ourselves. However, being blocked for too long has impacts on the project and the team. It's smarter and less selfish sometimes to reach out to a more experienced engineer for help (ensure you properly present the solutions you've attempted though). It could be something they've seen before and can guide you to fix it in seconds!

## Key Takeaways

- **The importance of balancing self-reliance and team support**. Knowing when to involve more experienced team members is key to efficiency.
- **The importance of dealing with uncertainty**. Agile projects never start off with all the requirements set in stone. Learning to deal with ambiguity and handle changing requirements will help you stay sane.
- **Master the basics in developer tooling**. Being proficient in tools like Git, package managers, and others is essential for developers, and is a skill that will be carried on to basically every future project you do.
