---
layout: post
title: "Kubernetes, Helm & GitLab CI/CD: Example App Deployment"
description: >-
  A practical walkthrough of deploying a Spring Boot application to Kubernetes using Helm charts with per-environment values files, orchestrated through a GitLab CI/CD pipeline.
author: ryo
date: 2025-07-21 00:49:50 +0800
categories: [DevOps & Cloud Native]
tags: [kubernetes, helm, gitlab, cicd, devops, cheatsheet]
toc: true
comments: true
pin: false
published: true
---

## 1. What We're Building

A `my-api` Spring Boot application, containerised, deployed to Kubernetes via Helm, with a GitLab CI/CD pipeline that:

1. Builds and tests the app
2. Builds and pushes a Docker image to GitLab Container Registry
3. Deploys to a `dev` environment automatically on every merge to `main`
4. Deploys to `prod` on a manual trigger

**Final Helm chart layout:**

```
helm/
└── my-api/
    ├── Chart.yaml
    ├── values.yaml              # shared defaults
    ├── values-dev.yaml          # dev overrides
    ├── values-prod.yaml         # prod overrides
    └── templates/
        ├── _helpers.tpl
        ├── deployment.yaml
        ├── service.yaml
        ├── configmap.yaml
        ├── secret.yaml
        └── ingress.yaml
```

---

## 2. Docker Image

```dockerfile
# Dockerfile
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
COPY target/my-api.jar app.jar
ENTRYPOINT ["java", "-jar", "app.jar"]
```

Build and run locally:

```bash
docker build -t my-api:local .
docker run -p 8080:8080 my-api:local
```

---

## 3. Helm Chart

### 3.1. `Chart.yaml`

```yaml
apiVersion: v2
name: my-api
description: Helm chart for my-api Spring Boot application
type: application
version: 0.1.0        # chart version
appVersion: "1.0.0"   # app version (informational only)
```

### 3.2. `_helpers.tpl`

Reusable named templates. Use `define` blocks to declare named templates and `include` to call them from other templates.

{% raw %}
```yaml
{{- define "my-api.name" -}}
{{- .Chart.Name }}
{{- end }}

{{- define "my-api.fullname" -}}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "my-api.labels" -}}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
app.kubernetes.io/name: {{ include "my-api.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "my-api.selectorLabels" -}}
app.kubernetes.io/name: {{ include "my-api.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```
{% endraw %}

### 3.3. `values.yaml` (shared defaults)

```yaml
replicaCount: 1

image:
  repository: registry.gitlab.com/my-group/my-api
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 80
  targetPort: 8080

ingress:
  enabled: true
  className: nginx
  host: my-api.example.com
  tls: false

resources:
  requests:
    cpu: 100m
    memory: 256Mi
  limits:
    cpu: 500m
    memory: 512Mi

app:
  logLevel: INFO
  dbUrl: jdbc:postgresql://localhost:5432/mydb

# Secret values - do not commit real values here
# Override via values-<env>.yaml or CI --set flags
secret:
  dbPassword: changeme
  jwtSecret: changeme
```

### 3.4. `values-dev.yaml`

```yaml
replicaCount: 1

image:
  tag: dev-latest   # overridden by CI with the actual commit SHA

ingress:
  host: my-api-dev.example.com

resources:
  requests:
    cpu: 100m
    memory: 256Mi
  limits:
    cpu: 250m
    memory: 384Mi

app:
  logLevel: DEBUG
  dbUrl: jdbc:postgresql://dev-db:5432/mydb_dev
```

### 3.5. `values-prod.yaml`

```yaml
replicaCount: 3

image:
  tag: prod-latest   # overridden by CI

ingress:
  host: my-api.example.com
  tls: true

resources:
  requests:
    cpu: 250m
    memory: 512Mi
  limits:
    cpu: 1000m
    memory: 1Gi

app:
  logLevel: WARN
  dbUrl: jdbc:postgresql://prod-db:5432/mydb_prod
```

### 3.6. `templates/configmap.yaml`

Non-sensitive configuration passed to the app as environment variables.

{% raw %}
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "my-api.fullname" . }}
  labels:
    {{- include "my-api.labels" . | nindent 4 }}
data:
  LOG_LEVEL: {{ .Values.app.logLevel | quote }}
  DB_URL: {{ .Values.app.dbUrl | quote }}
  SERVER_PORT: "8080"
```
{% endraw %}

### 3.7. `templates/secret.yaml`

Sensitive values. In real deployments, inject via CI `--set` flags or an external secrets manager (Vault, AWS Secrets Manager, External Secrets Operator) rather than storing in values files.

{% raw %}
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: {{ include "my-api.fullname" . }}
  labels:
    {{- include "my-api.labels" . | nindent 4 }}
type: Opaque
data:
  DB_PASSWORD: {{ .Values.secret.dbPassword | b64enc | quote }}
  JWT_SECRET: {{ .Values.secret.jwtSecret | b64enc | quote }}
```
{% endraw %}

### 3.8. `templates/deployment.yaml`

{% raw %}
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "my-api.fullname" . }}
  labels:
    {{- include "my-api.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "my-api.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "my-api.selectorLabels" . | nindent 8 }}
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - containerPort: 8080
          envFrom:
            - configMapRef:
                name: {{ include "my-api.fullname" . }}
            - secretRef:
                name: {{ include "my-api.fullname" . }}
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
          readinessProbe:
            httpGet:
              path: /actuator/health
              port: 8080
            initialDelaySeconds: 15
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /actuator/health
              port: 8080
            initialDelaySeconds: 30
            periodSeconds: 20
```
{% endraw %}

### 3.9. `templates/service.yaml`

{% raw %}
```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ include "my-api.fullname" . }}
  labels:
    {{- include "my-api.labels" . | nindent 4 }}
spec:
  type: {{ .Values.service.type }}
  selector:
    {{- include "my-api.selectorLabels" . | nindent 4 }}
  ports:
    - port: {{ .Values.service.port }}
      targetPort: {{ .Values.service.targetPort }}
      protocol: TCP
```
{% endraw %}

### 3.10. `templates/ingress.yaml`

{% raw %}
```yaml
{{- if .Values.ingress.enabled }}
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{ include "my-api.fullname" . }}
  labels:
    {{- include "my-api.labels" . | nindent 4 }}
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: {{ .Values.ingress.className }}
  {{- if .Values.ingress.tls }}
  tls:
    - hosts:
        - {{ .Values.ingress.host }}
      secretName: {{ include "my-api.fullname" . }}-tls
  {{- end }}
  rules:
    - host: {{ .Values.ingress.host }}
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: {{ include "my-api.fullname" . }}
                port:
                  number: {{ .Values.service.port }}
{{- end }}
```
{% endraw %}

---

## 4. Helm Commands

```bash
# Lint the chart - catches syntax errors
helm lint helm/my-api

# Render templates locally without installing (great for debugging)
helm template my-api helm/my-api -f helm/my-api/values-dev.yaml

# Install (first time)
helm install my-api-dev helm/my-api \
  -f helm/my-api/values-dev.yaml \
  --namespace dev --create-namespace \
  --set image.tag=abc1234 \
  --set secret.dbPassword=realpass \
  --set secret.jwtSecret=realsecret

# Upgrade (subsequent deploys)
helm upgrade my-api-dev helm/my-api \
  -f helm/my-api/values-dev.yaml \
  --namespace dev \
  --set image.tag=abc1234 \
  --set secret.dbPassword=realpass \
  --set secret.jwtSecret=realsecret

# Install or upgrade in one command
helm upgrade --install my-api-dev helm/my-api \
  -f helm/my-api/values-dev.yaml \
  --namespace dev --create-namespace \
  --set image.tag=$CI_COMMIT_SHORT_SHA

# Check release status
helm status my-api-dev -n dev
helm list -n dev

# View computed values for a running release
helm get values my-api-dev -n dev

# Rollback to previous revision
helm rollback my-api-dev 1 -n dev    # revision number from `helm history`
helm history my-api-dev -n dev

# Uninstall
helm uninstall my-api-dev -n dev
```

---

## 5. GitLab CI/CD Pipeline

### 5.1. Required CI/CD Variables

Set these in **GitLab > Project > Settings > CI/CD > Variables**. Mark sensitive ones as **Masked** and **Protected** (only available on protected branches/tags).

| Variable | Description | Masked |
|---|---|---|
| `KUBECONFIG_DEV` | Base64-encoded kubeconfig for dev cluster | yes |
| `KUBECONFIG_PROD` | Base64-encoded kubeconfig for prod cluster | yes |
| `DB_PASSWORD_DEV` | Dev DB password | yes |
| `DB_PASSWORD_PROD` | Prod DB password | yes |
| `JWT_SECRET_DEV` | Dev JWT secret | yes |
| `JWT_SECRET_PROD` | Prod JWT secret | yes |

The registry (`$CI_REGISTRY`, `$CI_REGISTRY_USER`, `$CI_REGISTRY_PASSWORD`, `$CI_REGISTRY_IMAGE`) are all **predefined GitLab CI variables** - no setup needed.

### 5.2. Full `.gitlab-ci.yml`

```yaml
stages:
  - build
  - docker
  - deploy-dev
  - deploy-prod

variables:
  MAVEN_OPTS: "-Dmaven.repo.local=.m2/repository"
  IMAGE_NAME: $CI_REGISTRY_IMAGE
  CHART_PATH: helm/my-api

# Cache Maven dependencies across jobs on the same branch
cache:
  key: "$CI_COMMIT_REF_SLUG"
  paths:
    - .m2/repository

# ── Stage 1: build & test ─────────────────────────────────────────────────────

build-and-test:
  stage: build
  image: maven:3.9-eclipse-temurin-17
  script:
    - mvn clean package -DskipTests=false
  artifacts:
    paths:
      - target/*.jar
    expire_in: 1 hour   # passed to the docker job
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'

# ── Stage 2: build & push Docker image ───────────────────────────────────────

docker-build:
  stage: docker
  image: docker:24
  services:
    - docker:24-dind    # Docker-in-Docker daemon
  variables:
    DOCKER_TLS_CERTDIR: "/certs"
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker build -t $IMAGE_NAME:$CI_COMMIT_SHORT_SHA .
    - docker push $IMAGE_NAME:$CI_COMMIT_SHORT_SHA
    # Also tag as dev-latest for traceability
    - docker tag $IMAGE_NAME:$CI_COMMIT_SHORT_SHA $IMAGE_NAME:dev-latest
    - docker push $IMAGE_NAME:dev-latest
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'

# ── Stage 3: deploy to dev ───────────────────────────────────────────────────

deploy-dev:
  stage: deploy-dev
  image: alpine/helm:3.14.0
  before_script:
    # Write kubeconfig from the masked CI variable
    - mkdir -p ~/.kube
    - echo "$KUBECONFIG_DEV" | base64 -d > ~/.kube/config
  script:
    - helm upgrade --install my-api-dev $CHART_PATH
        -f $CHART_PATH/values-dev.yaml
        --namespace dev
        --create-namespace
        --set image.tag=$CI_COMMIT_SHORT_SHA
        --set secret.dbPassword=$DB_PASSWORD_DEV
        --set secret.jwtSecret=$JWT_SECRET_DEV
        --wait        # wait for rollout to complete before marking job done
        --timeout 3m
  environment:
    name: dev
    url: https://my-api-dev.example.com
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'

# ── Stage 4: deploy to prod (manual gate) ────────────────────────────────────

deploy-prod:
  stage: deploy-prod
  image: alpine/helm:3.14.0
  before_script:
    - mkdir -p ~/.kube
    - echo "$KUBECONFIG_PROD" | base64 -d > ~/.kube/config
  script:
    - helm upgrade --install my-api-prod $CHART_PATH
        -f $CHART_PATH/values-prod.yaml
        --namespace prod
        --create-namespace
        --set image.tag=$CI_COMMIT_SHORT_SHA
        --set secret.dbPassword=$DB_PASSWORD_PROD
        --set secret.jwtSecret=$JWT_SECRET_PROD
        --wait
        --timeout 5m
  environment:
    name: prod
    url: https://my-api.example.com
  when: manual          # requires a human to click "Run" in GitLab UI
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
```

### 5.3. Key `.gitlab-ci.yml` Concepts

**`rules`** - controls when a job runs (replaces the older `only`/`except`):

```yaml
rules:
  - if: '$CI_COMMIT_BRANCH == "main"'           # run on main branch
  - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'  # run on MRs
  - if: '$CI_COMMIT_TAG'                        # run on tags
  - when: never                                 # explicit skip
```

**`needs`** - run a job as soon as its dependencies finish, without waiting for the whole stage:

```yaml
docker-build:
  needs: [build-and-test]   # starts immediately when build-and-test passes
```

**`artifacts`** - files produced by a job, passed to subsequent jobs:

```yaml
artifacts:
  paths:
    - target/*.jar
  expire_in: 1 hour
  reports:
    junit: target/surefire-reports/*.xml   # shows test results in GitLab MR UI
```

**`cache`** - persist files between pipeline runs (different from artifacts):

```yaml
cache:
  key: "$CI_COMMIT_REF_SLUG"   # separate cache per branch
  paths:
    - .m2/repository
  policy: pull-push             # pull at job start, push at end (default)
```

**`services`** - sidecar containers available during the job (e.g. a DB for integration tests):

```yaml
build-and-test:
  image: maven:3.9-eclipse-temurin-17
  services:
    - postgres:15           # available at hostname "postgres"
  variables:
    POSTGRES_DB: testdb
    POSTGRES_USER: test
    POSTGRES_PASSWORD: test
```

**`extends`** - reuse job configuration:

```yaml
.helm-base:
  image: alpine/helm:3.14.0
  before_script:
    - mkdir -p ~/.kube

deploy-dev:
  extends: .helm-base
  script: ...
```

**`include`** - split pipelines across files:

```yaml
include:
  - local: .gitlab/ci/build.yml
  - project: my-group/shared-ci
    file: /templates/docker.yml
  - template: Security/SAST.gitlab-ci.yml   # GitLab managed templates
```

### 5.4. Viewing Environments

After the pipeline runs, **GitLab > Deployments > Environments** shows each named environment, its URL, the active deployment, and deployment history. The `when: manual` prod job appears as a play button that a human must click.

---

## 6. Encoding KUBECONFIG for GitLab

To set up `KUBECONFIG_DEV`/`KUBECONFIG_PROD`:

```bash
# On your local machine, encode the kubeconfig
cat ~/.kube/config | base64 | tr -d '\n'
# Paste the output as the CI variable value
```

The pipeline decodes it with `echo "$KUBECONFIG_DEV" | base64 -d > ~/.kube/config`.

For production use, scope the kubeconfig to a service account with only the permissions Helm needs (namespace-level deploy rights), not a cluster-admin kubeconfig.
