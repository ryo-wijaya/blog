---
layout: post
title: "Certified Kubernetes Application Developer (CKAD) Cheatsheet"
description: >-
  Personal notes and cheatsheet made during CKAD exam prep. Covers all five exam domains: application design and build, deployment, observability, environment and security, and services and networking.
author: ryo
date: 2025-05-14 00:00:00 +0800
categories: [DevOps & Cloud Native]
tags: [kubernetes, ckad, k8s, docker, helm, devops]
toc: true
comments: true
pin: false
published: true
---

## Overview

The [Certified Kubernetes Application Developer (CKAD)](https://training.linuxfoundation.org/certification/certified-kubernetes-application-developer-ckad/) exam is a hands-on, performance-based certification offered by the Linux Foundation and CNCF. The exam runs for 2 hours in a live Kubernetes cluster environment. No multiple choice, all CLI tasks, with `kubectl` documentation available in the exam's environment.

**Official syllabus** (as per the [CNCF curriculum v1.32](https://github.com/cncf/curriculum/blob/master/old-versions/CKAD_Curriculum_v1.32.pdf), which was in effect when this exam was taken in May 2025):

| Domain | Weight |
|---|---|
| Application Design and Build | 20% |
| Application Deployment | 20% |
| Application Observability and Maintenance | 15% |
| Application Environment, Configuration and Security | 25% |
| Services and Networking | 20% |

**Domain breakdown:**
- **Application Design and Build** -- container images, workload resources (Deployment, DaemonSet, CronJob), multi-container Pod patterns, persistent and ephemeral volumes
- **Application Deployment** -- rolling updates, blue/green and canary strategies, Helm, Kustomize
- **Application Observability and Maintenance** -- probes, health checks, CLI monitoring tools, logs, debugging, API deprecations
- **Application Environment, Configuration and Security** -- CRDs, Operators, RBAC, authentication/authorization, resource requests/limits, ConfigMaps, Secrets, ServiceAccounts, SecurityContexts
- **Services and Networking** -- Services (ClusterIP/NodePort/LoadBalancer), Ingress, NetworkPolicies

The exam is based on Kubernetes v1.32.

---

## Exam Tips

### Use `kubectl explain` to Look Up Fields

`kubectl explain` is documentation in the terminal.

```bash
# Top-level fields for a resource
kubectl explain pod
kubectl explain deployment

# Nested fields
kubectl explain pod.spec
kubectl explain pod.spec.containers
kubectl explain pod.spec.containers.resources
kubectl explain pod.spec.containers.livenessProbe
kubectl explain networkpolicy.spec.ingress
```

Add `--recursive` to see the full field tree in one shot:

```bash
kubectl explain pod.spec --recursive
```

### Generate YAML with `--dry-run=client -o yaml`

```bash
# Service
kubectl expose deployment my-app --port=80 --target-port=8080 --dry-run=client -o yaml
```

### Use Aliases and Shortcuts

The `kubectl` binary should be aliased as `k` in the exam environment, it was for me.

```bash
alias k=kubectl

k get po          # pods
k get deploy      # deployments
k get svc         # services
k get cm          # configmaps
k get ns          # namespaces
k get sa          # serviceaccounts
k get pv          # persistentvolumes
k get pvc         # persistentvolumeclaims
k get netpol      # networkpolicies
k get ing         # ingresses
```

### Force Delete Stuck Pods

Pods may be stuck in terminating due to a node issues:

```bash
kubectl delete pod <name> --force --grace-period=0
```

### Edit a Running Resource

For quick changes without re-applying a file:

```bash
kubectl edit deployment my-app
```

To change a specific field directly from the CLI:

```bash
kubectl set image deployment/my-app my-container=nginx:1.25
kubectl set resources deployment/my-app --limits=cpu=200m,memory=256Mi
kubectl scale deployment my-app --replicas=5
```

### Patch Resources

For one-field changes without opening an editor:

```bash
kubectl patch deployment my-app -p '{"spec": {"replicas": 3}}'
```

---

## 1. Basics

### kubectl Commands

| Command | Description |
|---|---|
| `kubectl get <type>` | List resources |
| `kubectl get <type> -l <key>=<value>` | Filter by label |
| `kubectl get pods --show-labels` | Show all pod labels |
| `kubectl describe <type> <name>` | Detailed resource info + events |
| `kubectl apply -f <file>` | Create or update from file |
| `kubectl delete <type> <name>` | Delete resource |
| `kubectl edit <type> <name>` | Edit live resource in-place |
| `kubectl set <field> <type>/<name> <key>=<value>` | Modify a live resource field |
| `kubectl expose <resource>` | Expose a pod/deployment as a service |
| `kubectl exec -it <pod> -- <program>` | Interactive session inside pod |
| `kubectl exec <pod> -- <cmd>` | Run a single command in pod |
| `kubectl logs -f <pod> -c <container>` | Stream logs from a container |
| `kubectl logs -p <pod>` | Logs from previous (crashed) container |
| `kubectl top pod` | Show pod CPU/memory usage |
| `kubectl <cmd> --dry-run=client` | Simulate without creating |
| `kubectl <cmd> -o yaml` | Output as YAML |
| `kubectl explain <path>` | Show valid fields for a resource path |

### Kubernetes Context

A context bundles three things stored in `~/.kube/config`: a cluster, user auth info, and a namespace.

| Command | Description |
|---|---|
| `kubectl config get-contexts` | List all contexts |
| `kubectl config current-context` | Show active context |
| `kubectl config use-context <name>` | Switch context |
| `kubectl config set-context --current --namespace=<ns>` | Switch namespace |
| `kubectl config view` | View full kubeconfig |

### Resource Types Reference

| Resource | Description |
|---|---|
| Pod | Basic unit. Runs one or more containers. |
| ReplicaSet | Maintains N identical pod replicas. |
| Deployment | Manages ReplicaSets with rolling updates and rollback. |
| DaemonSet | Runs one pod per node. Used for logging agents, monitoring, etc. |
| StatefulSet | Ordered pods with stable identity and per-pod storage. Used for databases. |
| Job | Runs pods to completion. For one-off batch tasks. |
| CronJob | Schedules Jobs on a cron expression. |
| Service | Stable networking endpoint for pods. Types: ClusterIP, NodePort, LoadBalancer. |
| Ingress | Routes external HTTP/HTTPS to Services by hostname and path. |
| NetworkPolicy | Firewall rules for pod-to-pod traffic. |
| ConfigMap | Non-sensitive key-value config data. |
| Secret | Sensitive data (passwords, tokens), base64-encoded. |
| PersistentVolume (PV) | Cluster-wide storage resource backed by a physical disk or cloud volume. |
| PersistentVolumeClaim (PVC) | Request for storage. Binds to a PV. |
| ServiceAccount | Pod identity for Kubernetes API access. |
| Role / ClusterRole | Defines allowed actions on resources. Namespaced vs cluster-wide. |
| RoleBinding / ClusterRoleBinding | Grants a Role to a subject. |
| CustomResourceDefinition (CRD) | Extends Kubernetes with new resource types. |
| HorizontalPodAutoscaler (HPA) | Scales pods based on CPU/memory usage. |

### YAML Structure

Every Kubernetes manifest shares the same top-level structure:

```yaml
apiVersion: apps/v1        # API group + version
kind: Deployment           # Resource type
metadata:
  name: my-app
  namespace: dev
  labels:
    app: my-app
spec:                      # Resource-specific configuration
  ...
```

Deployment hierarchy:

```
Deployment
└── spec (Deployment-level)
    ├── replicas
    ├── selector
    └── template (Pod blueprint)
        └── spec (Pod-level)
            ├── containers[]
            │   ├── image
            │   ├── ports
            │   ├── resources
            │   ├── env
            │   └── volumeMounts
            └── volumes
```

---

## 2. Pods, Config, and Resource Management

### ConfigMaps

Store non-sensitive config data as key-value pairs or files.

```bash
kubectl create configmap my-config --from-literal=DB_HOST=localhost
kubectl create configmap app-config --from-file=database.txt
```

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: my-config
data:
  DB_HOST: localhost
  database.txt: |
    DB_HOST=localhost
    DB_PORT=3306
```

### Secrets

Sensitive data stored as base64-encoded values. Default type is `Opaque`.

```bash
kubectl create secret generic my-secret --from-literal=DB_PASS=pass123
kubectl create secret generic my-secret --from-file=./db-details.txt
kubectl create secret docker-registry regcred \
  --docker-server=<registry> \
  --docker-username=<user> \
  --docker-password=<pass>
kubectl create secret tls my-tls --cert=tls.crt --key=tls.key
```

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-secret
type: Opaque
data:
  DB_PASS: cGFzczEyMw==    # base64 of "pass123"
```

Common Secret types:

| Type | Use Case |
|---|---|
| `Opaque` | Generic key-value secrets (default) |
| `kubernetes.io/dockerconfigjson` | Private registry credentials for image pulls |
| `kubernetes.io/tls` | TLS certificate + private key (used by Ingress) |
| `kubernetes.io/service-account-token` | Auto-generated SA token (managed by Kubernetes) |

### Pods

The most basic unit of Kubernetes. It can run 1 or many containers.

```bash
kubectl run mypod --image=nginx:alpine
```

Full pod spec with ConfigMap/Secret injection, volumes, and resource limits:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: full-example-pod
  labels:
    app: my-app
spec:
  serviceAccountName: default
  restartPolicy: Always    # Always | OnFailure | Never
  imagePullSecrets:
  - name: regcred           # Reference a kubernetes.io/dockerconfigjson secret

  volumes:
  - name: cache-volume
    emptyDir: {}
  - name: config-volume
    configMap:
      name: my-config
  - name: secret-volume
    secret:
      secretName: my-secret

  containers:
  - name: main-app
    image: nginx:1.27
    imagePullPolicy: IfNotPresent
    ports:
    - containerPort: 80
    resources:
      requests:
        cpu: "100m"
        memory: "128Mi"
      limits:
        cpu: "500m"
        memory: "256Mi"
    env:
    - name: ENVIRONMENT
      value: production
    - name: DB_HOST
      valueFrom:
        configMapKeyRef:
          name: my-config
          key: DB_HOST
    - name: DB_PASS
      valueFrom:
        secretKeyRef:
          name: my-secret
          key: DB_PASS
    envFrom:
    - configMapRef:
        name: my-config
    - secretRef:
        name: my-secret
    volumeMounts:
    - name: cache-volume
      mountPath: /cache
    - name: config-volume
      mountPath: /etc/config
    - name: secret-volume
      mountPath: /etc/secret
```

### Ephemeral Volumes (emptyDir)

Temporary volume that only lives while the pod runs. Useful for caches and inter-container file sharing.

```yaml
volumes:
- name: cache-volume
  emptyDir: {}
```

### Resource Requests and Limits

Requests are the minimum guaranteed resources. Limits are the maximum. If CPU is exceeded, the container throttles. If memory is exceeded, the container may be killed.

### ResourceQuotas

Enforces namespace-wide limits on object counts and total compute resources.

```bash
kubectl create quota sample-quota --hard=pods=10
```

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: team-quota
  namespace: dev-team
spec:
  hard:
    pods: "10"
    configmaps: "20"
    persistentvolumeclaims: "5"
    requests.cpu: "2"
    requests.memory: 1Gi
    limits.cpu: "4"
    limits.memory: 2Gi
```

### LimitRanges

Automatically assigns default requests/limits and enforces min/max per container. Ensures pods always have resource constraints even if the developer forgot to set them.

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: container-limits
  namespace: dev-team
spec:
  limits:
  - type: Container
    defaultRequest:
      cpu: "100m"
      memory: "128Mi"
    default:
      cpu: "500m"
      memory: "256Mi"
    max:
      cpu: "1"
      memory: "512Mi"
    min:
      cpu: "50m"
      memory: "64Mi"
    maxLimitRequestRatio:
      cpu: "2"
      memory: "4"
```

---

## 3. Workloads and Deployments

### Jobs

Runs pods to completion. Retries on failure.

```bash
kubectl create job sample-job --image=busybox
```

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: hello-job
spec:
  completions: 3      # Total pods to run to completion
  parallelism: 1       # How many run at the same time
  backoffLimit: 4      # Retry attempts before marking failed
  activeDeadlineSeconds: 120    # Kill the whole job after this many seconds regardless of backoffLimit
  template:
    spec:
      containers:
      - name: hello
        image: busybox
        command: ["echo", "Hello CKAD!"]
      restartPolicy: Never    # Required for Jobs
```

### CronJobs

Schedules Jobs on a recurring cron expression.

```bash
kubectl create cronjob sample-cronjob --image=busybox --schedule="*/5 * * * *"
```

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: hello-cronjob
spec:
  schedule: "*/5 * * * *"
  concurrencyPolicy: Forbid       # Allow | Forbid | Replace
  startingDeadlineSeconds: 60
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: hello
            image: busybox
            command: ["date"]
          restartPolicy: Never
```

Cron schedule format:

```
* * * * *
| | | | |
| | | | └─ Weekday (0-6, Sun=0)
| | | └─── Month (1-12)
| | └───── Day of month (1-31)
| └─────── Hour (0-23)
└───────── Minute (0-59)
```

| Expression | Meaning |
|---|---|
| `0 * * * *` | Every hour on the hour |
| `30 14 * * *` | Daily at 14:30 |
| `*/10 * * * *` | Every 10 minutes |
| `0 9 * * 1-5` | Weekdays at 09:00 |
| `0 0 * * *` | Midnight every day |
| `0 0 1 1 *` | Once a year, Jan 1st at midnight |

### Deployments

Manages ReplicaSets with rolling updates and rollback support.

```bash
kubectl create deployment sample-deployment --image=nginx
```

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 3
  minReadySeconds: 10
  revisionHistoryLimit: 5
  progressDeadlineSeconds: 600
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.27
        ports:
        - containerPort: 80
```

### Rollout Commands

| Command | Purpose |
|---|---|
| `kubectl set image deployment/<name> nginx=nginx:1.28` | Update image |
| `kubectl rollout status deployment/<name>` | Check rollout progress |
| `kubectl rollout history deployment/<name>` | View revision history |
| `kubectl rollout undo deployment/<name>` | Roll back to previous version |
| `kubectl rollout undo deployment/<name> --to-revision=3` | Roll back to specific revision |
| `kubectl rollout pause deployment/<name>` | Pause mid-rollout |
| `kubectl rollout resume deployment/<name>` | Resume paused rollout |

### Deployment Strategies

**RollingUpdate** (default): Replaces pods gradually with zero downtime. Controlled by `maxUnavailable` and `maxSurge`.

**Recreate**: Kills all old pods first, then starts new ones. Causes downtime but guarantees no two versions run simultaneously.

**Blue-Green**: Run two deployments in parallel (old=blue, new=green). Switch traffic instantly by updating the Service selector. The Service selects by pod label, not deployment name.

```yaml
# Service pointing to green
selector:
  app: my-app
  version: green
```

**Canary**: Gradually shift traffic to the new version by running both deployments with a shared label and adjusting replica counts.

```yaml
# stable: 9 replicas, canary: 1 replica = 10% canary traffic
# Service selects both via shared label:
selector:
  app: my-app
```

### DaemonSets

Ensures one pod runs on every node. Used for log collectors, monitoring agents, and node-level utilities.

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: log-collector
  namespace: kube-system
spec:
  selector:
    matchLabels:
      app: fluentd
  updateStrategy:
    type: RollingUpdate    # Or OnDelete
  template:
    metadata:
      labels:
        app: fluentd
    spec:
      containers:
      - name: fluentd
        image: fluent/fluentd:v1.16
        volumeMounts:
        - name: varlog
          mountPath: /var/log
      volumes:
      - name: varlog
        hostPath:
          path: /var/log
```

### HorizontalPodAutoscaler (HPA)

Automatically scales the number of pod replicas in a Deployment based on observed CPU or memory usage. Requires the Metrics Server to be running in the cluster.

```bash
# Create from CLI (CPU-based)
kubectl autoscale deployment my-app --cpu-percent=50 --min=2 --max=10
```

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: my-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50    # Scale up when average CPU > 50% of requests
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 70
```

```bash
kubectl get hpa
kubectl describe hpa my-app-hpa
```

The Deployment must have CPU `requests` set, otherwise the HPA has nothing to calculate a percentage against.

---

## 4. Observability and Debugging

### Probes

| Probe | Purpose | Action on Failure |
|---|---|---|
| **Liveness** | Is the container alive? | Restart container |
| **Readiness** | Is the container ready for traffic? | Remove from Service endpoints (no restart) |
| **Startup** | Has the app finished starting? | Block liveness/readiness until passed |

Probe check methods:
- `httpGet` -- HTTP GET to a path/port; success if 2xx/3xx
- `tcpSocket` -- checks if TCP port is open
- `exec` -- runs a command; success if exit code is 0

```yaml
containers:
- name: my-app
  image: busybox
  startupProbe:
    exec:
      command: ["cat", "/tmp/ready"]
    initialDelaySeconds: 5
    periodSeconds: 5
    failureThreshold: 10
  livenessProbe:
    tcpSocket:
      port: 8080
    initialDelaySeconds: 10
    periodSeconds: 10
    failureThreshold: 3
  readinessProbe:
    httpGet:
      path: /healthz
      port: 8080
    initialDelaySeconds: 15
    periodSeconds: 5
    failureThreshold: 3
    successThreshold: 1
```

### Debugging Flow

```bash
kubectl get pods                       # Check status
kubectl describe pod <pod-name>        # Events section has the root cause
kubectl logs <pod-name>                # App logs
kubectl logs -p <pod-name>             # Logs from previous (crashed) container
kubectl exec -it <pod-name> -- sh      # Shell into container
```

| Symptom | Likely Cause | Debug Command |
|---|---|---|
| `ImagePullBackOff` | Wrong image name or missing registry credentials | `kubectl describe pod <pod>` -- check Events |
| `CrashLoopBackOff` | App crashes on startup | `kubectl logs <pod>` or `kubectl logs -p <pod>` |
| Pod Pending | Insufficient resources or bad nodeSelector | `kubectl describe pod <pod>` |
| Readiness failing | Wrong probe path or dependency not ready | `kubectl describe pod <pod>` -- check Events |
| Config issues | Wrong env vars or missing mounts | `kubectl exec -it <pod> -- sh` |

### API Deprecations

Each resource is identified by an API group, version, and kind. Kubernetes graduates APIs through alpha, beta, and stable (GA), and eventually removes old versions.

| Stage | Characteristics |
|---|---|
| Alpha (`v1alpha1`) | Experimental, off by default. |
| Beta (`v1beta1`) | Enabled by default, compatibility guarantees. |
| Stable (`v1`) | Production-ready, long-term supported. |

```bash
kubectl api-versions                    # Check available API versions in the cluster
kubectl explain deployment              # Check which apiVersion to use
```

Common migrations:

| Resource | Old API | Current Stable |
|---|---|---|
| Deployment | `extensions/v1beta1` | `apps/v1` |
| DaemonSet | `extensions/v1beta1` | `apps/v1` |
| StatefulSet | `apps/v1beta1` | `apps/v1` |
| NetworkPolicy | `extensions/v1beta1` | `networking.k8s.io/v1` |
| Ingress | `extensions/v1beta1` | `networking.k8s.io/v1` |
| CronJob | `batch/v1beta1` | `batch/v1` |

`apps/v1` Deployments require `.spec.selector`, which was optional in older APIs.

---

## 5. Storage

### PersistentVolumes (PV)

Cluster-wide storage resource provisioned by an admin. Backed by real storage (disk, NFS, cloud volumes).

```
[ Physical Storage ] <--> [ PV ] <--> [ PVC ] <--> [ Pod ]
```

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: aws-ebs-pv
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce         # RWO: one node | ROX: many nodes read-only | RWX: many nodes read-write
  storageClassName: gp2
  persistentVolumeReclaimPolicy: Delete    # Retain | Delete | Recycle (deprecated)
  awsElasticBlockStore:
    volumeID: vol-0abcd1234efgh5678
    fsType: ext4
```

PV lifecycle phases: `Available` -> `Bound` -> `Released` -> `Failed`

### PersistentVolumeClaims (PVC)

A namespaced request for storage. Kubernetes matches and binds it to a compatible PV (matching accessMode, storageClass, and size).

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: gp2
  resources:
    requests:
      storage: 1Gi
```

```yaml
# Pod using a PVC
volumes:
- name: my-storage
  persistentVolumeClaim:
    claimName: my-pvc
```

Binding rules: PVC accessMode must match PV; PVC requested size must be <= PV capacity; Kubernetes picks the smallest matching PV.

### StorageClasses

Enables dynamic PV provisioning. When a PVC references a StorageClass, Kubernetes creates a PV automatically -- no manual PV creation needed.

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: gp2
provisioner: ebs.csi.aws.com    # CSI driver (in-tree kubernetes.io/aws-ebs was removed in v1.27)
parameters:
  type: gp2
  fsType: ext4
reclaimPolicy: Delete
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer    # Immediate | WaitForFirstConsumer
```

### StatefulSets

For stateful apps that need stable pod identity and per-pod storage. Unlike Deployments, pods are named with an ordinal index (`mysql-0`, `mysql-1`) and scale up/down sequentially.

Requires a **headless Service** (`clusterIP: None`) for stable DNS.

```yaml
# Headless Service
apiVersion: v1
kind: Service
metadata:
  name: mysql
spec:
  clusterIP: None
  selector:
    app: mysql
  ports:
  - port: 3306
# DNS: mysql-0.mysql.default.svc.cluster.local
```

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
spec:
  serviceName: mysql
  replicas: 3
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      containers:
      - name: mysql
        image: mysql:8.0
        ports:
        - containerPort: 3306
        env:
        - name: MYSQL_ROOT_PASSWORD
          value: my-secret-pw
        volumeMounts:
        - name: mysql-data
          mountPath: /var/lib/mysql
  volumeClaimTemplates:
  - metadata:
      name: mysql-data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 5Gi
```

---

## 6. Multi-Container Pod Patterns

### Sidecar

A helper container runs alongside the main container in the same pod, sharing network and volumes. Used to add functionality without modifying the main container.

```yaml
# nginx writes logs to a shared volume; fluentd sidecar streams them out
spec:
  containers:
  - name: nginx
    image: nginx:1.27
    volumeMounts:
    - name: log-volume
      mountPath: /var/log/nginx
  - name: fluentd-sidecar
    image: fluent/fluentd:v1.16
    volumeMounts:
    - name: log-volume
      mountPath: /var/log/nginx
  volumes:
  - name: log-volume
    emptyDir: {}
```

### Init Containers

Runs before the main containers start. All init containers must complete successfully (exit 0) in sequence before the pod proceeds. Used for pre-start setup like waiting for a dependency, running migrations, or writing config.

```yaml
spec:
  volumes:
  - name: config-volume
    emptyDir: {}
  initContainers:
  - name: setup-config
    image: busybox
    command: ['sh', '-c', 'echo "config initialized" > /work/config.txt']
    volumeMounts:
    - name: config-volume
      mountPath: /work
  containers:
  - name: app
    image: nginx
    volumeMounts:
    - name: config-volume
      mountPath: /etc/config
```

---

## 7. Configuration, Security, and RBAC

### ServiceAccounts

A ServiceAccount provides a pod with an identity for authenticating to the Kubernetes API. Every namespace gets a `default` SA that is auto-mounted into pods. Credentials are mounted at `/var/run/secrets/kubernetes.io/serviceaccount/token`.

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: custom-sa
  namespace: dev
```

```yaml
# Assign SA to a pod
spec:
  serviceAccountName: custom-sa
  automountServiceAccountToken: false    # Disable token injection if API access not needed
```

By itself a ServiceAccount has no permissions. It needs a Role and RoleBinding.

### RBAC

**Key Idea:** ServiceAccounts (or users) are the *who*. Roles/ClusterRoles define the *what*. Bindings connect them.

| Component | Scope | Purpose |
|---|---|---|
| Role | Namespaced | Permissions within one namespace |
| ClusterRole | Cluster-wide | Permissions across all namespaces, or for non-namespaced resources |
| RoleBinding | Namespaced | Grants a Role to a subject in a namespace |
| ClusterRoleBinding | Cluster-wide | Grants a ClusterRole to a subject globally |

**Role**

```bash
kubectl create role pod-reader --verb=get --verb=list --resource=pods
```

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-reader
rules:
- apiGroups: [""]               # "" = core API group
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
```

**RoleBinding**

```bash
kubectl create rolebinding read-pods-binding --role=pod-reader --serviceaccount=default:custom-sa
```

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods-binding
  namespace: default
subjects:
- kind: ServiceAccount
  name: custom-sa
  namespace: default
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

**ClusterRole** works the same as Role but applies cluster-wide, and can also target non-namespaced resources (`nodes`, `persistentvolumes`) and non-resource URLs (`/healthz`, `/metrics`).

**Testing permissions**

```bash
kubectl auth can-i list pods --as=system:serviceaccount:prod:web-sa -n prod
kubectl auth can-i list pods -A --as=system:serviceaccount:prod:web-sa
```

### SecurityContext

Security settings applied at pod level (defaults for all containers) or container level (overrides pod-level).

| Setting | Pod-level | Container-level |
|---|---|---|
| `runAsUser`, `runAsGroup` | Yes | Yes (overrides) |
| `fsGroup` | Yes | No |
| `privileged` | No | Yes |
| `capabilities` | No | Yes |
| `readOnlyRootFilesystem` | No | Yes |

```yaml
# Pod-level: all containers run as UID 1000
spec:
  securityContext:
    runAsUser: 1000
    runAsGroup: 3000
    fsGroup: 2000
```

```yaml
# Container-level: least privilege with capabilities
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  readOnlyRootFilesystem: true
  capabilities:
    drop: ["ALL"]
    add: ["NET_BIND_SERVICE"]    # Allow binding to ports < 1024
```

Common Linux capabilities:

| Capability | Purpose |
|---|---|
| `NET_BIND_SERVICE` | Bind to privileged ports (<1024) |
| `CHOWN` | Change file ownership |
| `KILL` | Send signals to other processes |
| `SYS_TIME` | Modify system clock |
| `ALL` | Every capability -- always drop this first |

### CRDs and Operators

Kubernetes lets you define custom resource types via CustomResourceDefinitions, extending the API with your own kinds.

```yaml
# 1. Define the CRD
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: postgresdatabases.mycompany.com
spec:
  group: mycompany.com
  names:
    kind: PostgresDatabase
    plural: postgresdatabases
    singular: postgresdatabase
  scope: Namespaced
  versions:
  - name: v1
    served: true
    storage: true
```

```yaml
# 2. Create a custom resource
apiVersion: mycompany.com/v1
kind: PostgresDatabase
metadata:
  name: customer-db
spec:
  size: small
  version: "15.0"
```

An **Operator** is a controller pod (installed from OperatorHub, Helm, or GitHub) that watches custom resources and acts on them -- creating pods, running migrations, handling upgrades, etc.

```bash
kubectl get crd
kubectl describe crd postgresdatabases.mycompany.com
kubectl get postgresdatabases
```

---

## 8. Services and Networking

### Services

Services provide stable networking for pods. Since pod IPs change on restart, a Service gives a fixed ClusterIP and DNS name backed by an Endpoints object.

```bash
kubectl expose pod my-pod --port=80 --target-port=8080 --name=my-svc
kubectl expose deployment my-deploy --type=NodePort --port=80 --target-port=8080
kubectl expose deployment my-deploy --type=LoadBalancer --port=80 --target-port=8080
```

| Type | Access | Use Case |
|---|---|---|
| ClusterIP (default) | Cluster-internal only | Service-to-service communication |
| NodePort | External via node IP + static port (30000-32767) | Dev/testing without a load balancer |
| LoadBalancer | External via cloud load balancer | Production ingress from the internet |

```yaml
# ClusterIP
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  selector:
    app: my-app
  ports:
  - port: 80           # Service port
    targetPort: 8080   # Container port
```

```yaml
# NodePort
spec:
  type: NodePort
  selector:
    app: my-app
  ports:
  - port: 80
    targetPort: 8080
    nodePort: 30080    # Optional, auto-assigned if omitted
```

Testing:

```bash
kubectl exec -it <pod> -- curl http://my-service:80         # ClusterIP
kubectl get nodes -o wide && curl http://<NodeIP>:30080     # NodePort
kubectl get endpoints <service-name>                         # Verify endpoint exists
```

### Ingress

Single external entry point for HTTP/HTTPS routing to multiple Services by hostname and path. Requires an Ingress Controller (NGINX, Traefik, etc.) to be installed.

```
Internet --> [Ingress Controller] --> Ingress Rules --> Services --> Pods
```

```bash
kubectl get ingressclass
kubectl create ingress web-ing --rule="example.com/=web:80" --class=nginx
```

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - example.com
    secretName: example-tls
  rules:
  - host: example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-service
            port:
              number: 80
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 80
```

Testing:

```bash
kubectl port-forward svc/ingress-nginx-controller -n ingress-nginx 8080:80
curl http://localhost:8080
curl http://localhost:8080/api
```

### NetworkPolicies

Controls pod-to-pod and pod-to-external traffic. Requires a CNI plugin that supports it (Calico, Cilium, Weave Net).

When any NetworkPolicy selects a pod, all traffic not explicitly allowed is denied.

**Restrict ingress by pod label:**

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-db
  namespace: default
spec:
  podSelector:
    matchLabels:
      role: db
  policyTypes:
  - Ingress
  ingress:
  - from:
      - podSelector:
          matchLabels:
            role: frontend
    ports:
    - protocol: TCP
      port: 5432
```

**Restrict by IP range (Ingress + Egress):**

```yaml
spec:
  podSelector:
    matchLabels:
      role: api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
      - ipBlock:
          cidr: 10.0.0.0/24
    ports:
    - protocol: TCP
      port: 80
  egress:
  - to:
      - ipBlock:
          cidr: 0.0.0.0/0
    ports:
    - protocol: TCP
      port: 443
```

---

## 9. Tooling

### Docker

| Action | Command |
|---|---|
| Build image | `docker build -t myimage:1.0 .` |
| List images | `docker images` |
| Run container | `docker run -it myimage:1.0` |
| Tag image | `docker tag myimage:1.0 myrepo/myimage:1.0` |
| Push to registry | `docker push myrepo/myimage:1.0` |
| Inspect container | `docker inspect <container-id>` |
| Login to registry | `docker login <registry-url>` |

### Helm

Manages Kubernetes apps as versioned packages (charts). Uses templating to support multiple environments via `values.yaml`.

| Term | Meaning |
|---|---|
| Chart | Package of Kubernetes manifests (templates + values) |
| Release | Deployed instance of a chart |
| values.yaml | Configurable parameters for the chart |

| Action | Command |
|---|---|
| Add repo | `helm repo add bitnami https://charts.bitnami.com/bitnami` |
| Update repos | `helm repo update` |
| Search | `helm search repo nginx` |
| Install | `helm install my-nginx bitnami/nginx` |
| List releases | `helm list` |
| Upgrade | `helm upgrade my-nginx bitnami/nginx --set service.type=NodePort` |
| Uninstall | `helm uninstall my-nginx` |
| Dry-run | `helm install --dry-run --debug my-nginx bitnami/nginx` |

### Kustomize

Built into `kubectl`. Customizes Kubernetes manifests for different environments without forking the base files. Uses a declarative overlay approach.

| Term | Description |
|---|---|
| Base | Original generic manifests |
| Overlay | Environment-specific patches on top of the base |
| kustomization.yaml | Declares which resources and patches to apply |

```yaml
# kustomization.yaml to apply multiple manifests at once
resources:
  - deployment.yaml
  - service.yaml
```

```bash
kubectl kustomize my-app/           # Preview final manifest
kubectl apply -k my-app/            # Apply with kustomize
```

For multiple environments, keep one base and write small patch files per environment:

```
base/
  deployment.yaml
  service.yaml
overlays/
  dev/
    kustomization.yaml
    patch-replicas.yaml
  prod/
    kustomization.yaml
    patch-replicas.yaml
```
