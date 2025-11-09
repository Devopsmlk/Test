# Qashqade DevOps Assessment - Documentation

## Overview

Complete DevOps solution with Flask API, PostgreSQL database, deployed on Azure Kubernetes Service with CI/CD automation.

**Stack:** Python/Flask, Docker, Kubernetes, Terraform, Azure (AKS, ACR, PostgreSQL, Key Vault), Azure DevOps

**What's Delivered:**
- RESTful API with health check and word transformation endpoints
- Automated testing with pytest
- CI/CD pipeline (Test → Build → Deploy)
- Infrastructure as Code with Terraform
- Kubernetes deployment with NGINX ingress

---

## Architecture
```
Azure DevOps Pipeline
  ├─ Test Stage (pytest)
  ├─ Build Stage (Docker → ACR)
  └─ Deploy Stage (K8s)
        ↓
Azure Cloud
  ├─ ACR (Container Registry)
  ├─ AKS (Kubernetes Cluster)
  │   ├─ Ingress (Port 80)
  │   ├─ Service (ClusterIP)
  │   └─ Pods (Flask App:4004)
  ├─ PostgreSQL (Database)
  └─ Key Vault (Secrets)
```

**Request Flow:** User → Ingress:80 → Service → Pod:4004 → PostgreSQL

---

## Quick Start

### Prerequisites
```bash
az --version          # Azure CLI 2.50+
terraform --version   # 1.5+
kubectl version       # Latest
docker --version      # Latest
```

### 1. Local Testing (Docker Compose)
```bash
# Start services
docker-compose up -d

# Test endpoints
curl http://localhost:4004/api/health
curl "http://localhost:4004/api/mirror?word=fOoBar25"
# Expected: {"transformed": "52RAbOoF"}

# Verify database
docker exec -it qashqade-postgres psql -U postgres -d qashqade -c "SELECT * FROM word_transformations;"

# Cleanup
docker-compose down
```

---

## Infrastructure Deployment

### Deploy with Terraform
```bash
cd terraform

# Initialize
terraform init

# Deploy
terraform apply -auto-approve

# Get outputs
terraform output acr_login_server
terraform output aks_cluster_name
terraform output key_vault_name
terraform output postgres_fqdn
```

**Resources Created:**
- Resource Group: `rg-qashqade-test`
- ACR: `acrqashqade.azurecr.io`
- AKS: `aks-qashqade` (2 nodes, Standard_B2s)
- PostgreSQL: `postgres-qashqade` (v15, publicly accessible with Azure Services firewall rule)
- Key Vault: `kv-qashqade-XXXXXX` (random suffix)
- NGINX Ingress Controller (auto-installed)

### Connect to AKS
```bash
az aks get-credentials --resource-group rg-qashqade-test --name aks-qashqade

# Verify
kubectl get nodes
kubectl get pods -n ingress-nginx
```

---

## CI/CD Pipeline Setup

### Azure DevOps Configuration

**1. Create Service Connections:**

**ACR Connection:**
- Project Settings → Service Connections → New
- Type: Docker Registry
- Azure Container Registry: `acrqashqade`
- Name: `acr-connection`

**AKS Connection:**
- Type: Kubernetes
- Authentication: Azure Subscription
- Cluster: `aks-qashqade`
- Name: `aks-connection`

**2. Create Pipeline:**
- Pipelines → New Pipeline
- Azure Repos Git → Select repo
- Existing YAML: `azure-pipelines.yml`
- Run

### Pipeline Stages
```yaml
Test Stage:
  - Install dependencies
  - Run pytest
  - Publish results
  
Build Stage (only if tests pass):
  - Login to ACR
  - Build Docker image
  - Push with BuildId tag + latest
  
Deploy Stage (only if build succeeds):
  - Apply K8s manifests
  - Update deployment image
```

---

## Testing & Validation

### Get Application URL
```bash
# Get ingress IP (wait 2-3 minutes after deployment)
kubectl get ingress qashqade-ingress
INGRESS_IP=$(kubectl get ingress qashqade-ingress -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Test endpoints
curl http://$INGRESS_IP/api/health
curl "http://$INGRESS_IP/api/mirror?word=fOoBar25"
curl "http://$INGRESS_IP/api/mirror?word=Hello"
```

### Verify Database
```bash
# Connect to PostgreSQL
psql "host=postgres-qashqade.postgres.database.azure.com port=5432 dbname=qashqade user=qashqadeadmin password=YourSecureP@ssw0rd! sslmode=require"

# Check transformations
SELECT * FROM word_transformations ORDER BY created_at DESC;
```

---

## Security Implementation

### Key Vault

**Secrets Stored:**
- `db-admin-password` - PostgreSQL password
- `db-admin-username` - PostgreSQL username  
- `db-host` - PostgreSQL FQDN
- `acr-username` - ACR credentials
- `acr-password` - ACR credentials

**Access:**
- AKS managed identity has Get/List permissions

**View Secrets:**
```bash
KV_NAME=$(terraform output -raw key_vault_name)
az keyvault secret list --vault-name $KV_NAME -o table
```

**Current Setup:** K8s manifests use direct environment variables. Key Vault exists and stores all secrets for reference.

**Enhanced Approach:** Use Azure Key Vault Secrets Provider (CSI Driver) for automatic secret sync to pods.

---

## Architecture Improvements

### 1. Hub-and-Spoke Network Topology
**Current:** Single VNet  
**Enhanced:** Hub VNet (Firewall, Bastion, shared services) + Spoke VNets per environment  
**Benefit:** Network isolation, centralized security, cost optimization

### 2. Private AKS Cluster
**Current:** Public API endpoint  
**Enhanced:** Private cluster with no internet exposure  
**Benefit:** Eliminates attack surface, zero-trust compliance

### 3. Private Endpoints for PaaS Services
**Current:** Public endpoints for ACR, PostgreSQL (with Azure Services firewall rule), and Key Vault  
**Enhanced:** Private Link for all services  
**Benefit:** Data stays on Azure backbone, prevents exfiltration, network-level access control

### 4. Azure Bastion for Management
**Current:** Direct kubectl/SSH access  
**Enhanced:** Browser-based Bastion host in dedicated subnet  
**Benefit:** No public IPs, full session audit, JIT access integration

### 5. Self-Hosted DevOps Agents
**Current:** Microsoft-hosted agents
**Enhanced:** Self-hosted agents deployed on jumphost/VM in private subnet with access to private AKS cluster and PaaS services  
**Benefit:** Required for private cluster deployments, can access private endpoints without VNet injection, custom tool installation, faster builds with persistent cache

---

## Cleanup
### Full Teardown (After Evaluation)
```bash
cd terraform
terraform destroy -auto-approve
```

### Full Teardown (After Evaluation)
```bash
cd terraform
terraform destroy -auto-approve
```
---

# Multi-Tenant Architecture Strategy (Bonus)

**Challenge:** Serving 10+ customers where each needs their own isolated infrastructure (compute, storage, database).

---

### 1. Isolation Approach

**Full Isolation (Dedicated Resources)**  
Each customer gets their own complete infrastructure stack - separate clusters, databases, storage. Higher operational cost but provides strong security boundaries and independent scaling. Best for production environments and enterprise customers with compliance requirements.

**Shared Infrastructure (Logical Separation)**  
Customers share underlying infrastructure with separation at application/namespace level. Cost-efficient but requires careful resource management to prevent one customer impacting others. Suitable for non-production environments.

**Hybrid Model**  
Core platform shared, data plane isolated. Balances cost optimization with security needs.

**Recommendation:** Shared infrastructure for dev/staging environments, full isolation for production. This balances cost efficiency in lower environments while maintaining security and performance guarantees where it matters.

---

### 2. Infrastructure Templating

**Best Practice:** Infrastructure as reusable templates with customer-specific parameters:
- Customer identifier
- Resource sizing (tier: basic/premium)
- Geographic region
- Environment type

**Key Principle:** One template serves all customers. New customer deployment becomes parameter substitution, not template modification. Ensures consistency and reduces configuration drift across tenants.

**Implementation:** Dynamic resource naming using variables - `{service}-{customer}-{environment}`. This enables programmatic deployment and clear resource ownership.

---

### 3. Deployment Automation

**Manual Approach Doesn't Scale:** Beyond 5-10 customers, manual deployment becomes bottleneck and error-prone.

**Automation Requirements:**
- Single deployment pipeline accepting customer parameters
- Idempotent operations (safe to re-run)
- Validation steps before provisioning
- Rollback capability for failed deployments

**Onboarding Target:** Fully automated customer provisioning completing in under 30 minutes. From signup to live environment without manual intervention.

---

### 4. Database Strategy

**Approach:** Database-per-customer with complete isolation.

**Why This Matters:** If Customer B accidentally sees Customer A's data even once, your business is dead. No clever application-level filtering, no shared schemas with tenant IDs, no shortcuts.

**Bottom Line:** Separate databases = sleep at night. The cost difference is negligible compared to the risk of data leakage. Security and compliance become straightforward when databases are physically isolated.

---

### 5. Cost Attribution

**Business Requirement:** Understanding per-customer profitability.

**Implementation:** Comprehensive resource tagging strategy - every deployed resource tagged with customer identifier. Enables automated cost reporting, budget tracking, and unit economics analysis. Critical for identifying unprofitable customers and optimization opportunities.

---

### 6. Monitoring & Operations

**Per-Customer Visibility:** Separate monitoring dashboards per tenant showing health metrics, performance, and SLA compliance. Enables quick issue isolation and customer-specific troubleshooting.

**Platform-Level View:** Aggregate monitoring across all customers for capacity planning, pattern detection, and platform health assessment.

**Operational Goal:** Mean time to detection and resolution shouldn't degrade as customer count increases.

---

### 7. Customer Lifecycle Management

**Onboarding:** Automated provisioning workflow triggered by customer signup. Infrastructure deployment, application configuration, monitoring setup, and credential delivery - all scripted.

**Ongoing Operations:** Parameter-based scaling and upgrades. Customer tier changes or resource adjustments handled through configuration updates, not manual intervention.

**Offboarding:** Controlled teardown process with data export, grace period, and scheduled resource deletion. Maintains audit trail per compliance requirements.

---

## Core Principles

**Parameterization Over Duplication:** One template with variables beats ten copies of similar configurations.

**Automation Over Manual Processes:** If a human does it twice, it should be automated.

**Isolation by Default:** Security and compliance easier to relax than tighten after incidents.

**Observability Per Tenant:** You can't manage what you can't measure, especially at scale.

**Cost Transparency:** Every resource attributable to specific customer enables business decision-making.

---

## Summary

Multi-tenancy success depends on transforming infrastructure from one-off deployment into repeatable, parameterized process. The goal isn't handling 10 customers - it's building a system where customer 100 requires same effort as customer 10. This demands upfront investment in templating, automation, and observability patterns that may seem excessive for initial scale but become critical as customer count grows.
