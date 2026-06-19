# Enterprise CI/CD Security Pipeline: Automated Secret Scanning with Gitleaks

Welcome to the **Enterprise CI/CD Security Pipeline** portfolio piece. This project demonstrates how to implement an industry-standard automated security "tollbooth" that intercepts code uploads, scans for hardcoded credentials using **Gitleaks**, and blocks production deployments if vulnerabilities are found.

This architecture showcases true **Shift-Left Security**, ensuring that human error does not result in compromised cloud infrastructure or leaked API keys.

---

## 📋 Table of Contents
- [Architecture Overview](#-architecture-overview)
- [1. The Scanning Engine (Gitleaks)](#1-the-scanning-engine-gitleaks)
- [2. The GitHub Actions Pipeline](#2-the-github-actions-pipeline)
- [3. The Tollbooth (Branch Protection Rules)](#3-the-tollbooth-branch-protection-rules)
- [4. Secrets Management Best Practices](#4-secrets-management-best-practices)

---

##  Architecture Overview

In a scalable enterprise environment, DevSecOps relies on open-source, community-backed tools to detect vulnerabilities accurately and at speed. This project utilizes:
1. **GitHub Actions:** To automatically provision temporary Linux runners upon code pushes.
2. **Gitleaks:** The industry standard for Static Application Security Testing (SAST) focused entirely on detecting hardcoded secrets (AWS keys, Slack tokens, database passwords).
3. **Pipeline Guardrails:** Utilizing GitHub's native status checks to enforce strict deployment blocking upon failed scans.

---

##  1. The Scanning Engine (Gitleaks)

Instead of relying on custom, hard-to-maintain scripts, this architecture integrates **Gitleaks**. Gitleaks natively supports hundreds of detection rules out of the box, catching secrets across over 150 different service providers. It scans not just the current code, but the entire Git commit history to ensure no secrets were briefly added and "deleted" in previous commits.

---

##  2. The GitHub Actions Pipeline

To automate the execution of Gitleaks, we define a continuous integration pipeline using YAML. This file resides in `.github/workflows/` so the repository automatically recognizes it as a system rule.

```yaml
# File: .github/workflows/gitleaks.yml
name: DevSecOps Secret Scanner (Gitleaks)

on: 
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  scan-secrets:
    runs-on: ubuntu-latest

    steps:
      - name: Download Repository Code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0 # Required so Gitleaks can scan the full commit history

      - name: Execute Gitleaks Scanner
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

##  3. The Tollbooth (Branch Protection Rules)

Running a scanner is only effective if developers cannot bypass the results. To enforce this globally, **Branch Protection Rules** are applied at the repository level:
* **Rule:** `Require status checks to pass before merging.`
* **Target Check:** `scan-secrets`

**Result:** If a developer accidentally hardcodes a credential, the Gitleaks action triggers a pipeline failure (`exit 1`). The GitHub tollbooth reads this failure, grays out the Merge button, and completely blocks the code from hitting the live production environment until the secret is revoked and removed.

---

##  4. Secrets Management Best Practices

By blocking hardcoded passwords at the pipeline level, developers are forced to adopt modern **Secrets Management** practices:

### Tier 1: Platform Native (GitHub Secrets)
Variables are stored securely within the repository settings and injected invisibly during pipeline execution:
```hcl
provider "aws" {
  access_key = var.aws_access_key # Fetched dynamically from vault
}
```

### Tier 2: Dynamic Secrets (HashiCorp Vault)
For FinTech and high-compliance environments, long-lived credentials are removed entirely. The pipeline authenticates with HashiCorp Vault via OIDC, dynamically generating temporary AWS credentials with a strict Time-To-Live (TTL). The keys destroy themselves instantly after the deployment completes.
