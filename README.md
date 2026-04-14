# Checkov Terraform Security Audit

Static security analysis of a deliberately misconfigured AWS Terraform configuration using [Checkov](https://www.checkov.io/) v3.2.521 by Prisma Cloud.

---

## What is Checkov?

Checkov is an open-source static analysis tool for Infrastructure-as-Code (IaC). It scans Terraform, CloudFormation, Kubernetes, ARM, and other IaC files for misconfigurations against 1000+ built-in security policies mapped to CIS Benchmarks, AWS best practices, and compliance frameworks (SOC2, PCI-DSS, HIPAA).

It runs **entirely offline** — no AWS credentials needed, no cloud connection required. Pure static analysis.

---

## Setup

### Prerequisites
- Python 3.8+
- pip3
- Git

### Install Checkov

```bash
pip3 install checkov
```

Verify installation:

```bash
checkov --version
# Expected: checkov 3.2.521 (or newer)
```

If you get "command not found" after install:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

---

## Repository Structure

```
checkov-terraform-audit/
├── README.md                  ← This file
├── checkov-output.txt         ← Raw CLI scan output
├── checkov-results.json       ← Machine-readable JSON results
└── terraform-example/
    └── main.tf                ← Intentionally misconfigured Terraform
```

---

## Terraform Code Scanned

`./terraform-example/main.tf` contains deliberately misconfigured AWS resources across four categories — written to trigger real-world security findings.

| Resource Name | Type | Lines | Known Issues |
|---|---|---|---|
| `aws_s3_bucket.example` | S3 Bucket | 15–17 | No encryption, no public access block, no logging, no versioning |
| `aws_security_group.allow_all` | Security Group | 27–44 | Full open ingress + egress on all ports to 0.0.0.0/0 |
| `aws_instance.web` | EC2 Instance | 47–65 | IMDSv1 enabled, EBS unencrypted, no IAM profile, no monitoring |
| `aws_iam_role_policy.admin_policy` | IAM Policy | 68–82 | Wildcard `Action: *` and `Resource: *` |

---

## How to Run the Scan

```bash
# CLI output — save and display simultaneously
checkov -d ./terraform-example --output cli 2>&1 | tee checkov-output.txt

# JSON output — for programmatic use or CI/CD integration
checkov -d ./terraform-example --output json > checkov-results.json 2>&1
```

---

## Scan Results Summary

**Checkov version:** 3.2.521  
**Scan target:** `./terraform-example/main.tf`  
**Framework:** Terraform

| Metric | Count |
|--------|-------|
| ✅ Passed checks | **12** |
| ❌ Failed checks | **27** |
| ⏭ Skipped checks | **0** |
| **Total checks run** | **39** |

### Failures by Resource

| Resource | Failed | Root Cause Summary |
|---|---|---|
| `aws_iam_role_policy.admin_policy` | **9** | Wildcard `Action: *` + `Resource: *` |
| `aws_s3_bucket.example` | **8** | Bare bucket — no controls configured |
| `aws_security_group.allow_all` | **6** | All ports open to internet, both directions |
| `aws_instance.web` | **5** | IMDSv1, unencrypted EBS, no monitoring, no IAM profile |

### Passes by Resource (What Was Correct)

| Check ID | Description | Resource |
|---|---|---|
| CKV_AWS_93 | S3 policy does not lockout root user | `aws_s3_bucket.example` |
| CKV_AWS_19 | S3 data encrypted at rest (AES256 default) | `aws_s3_bucket.example` |
| CKV_AWS_20 | S3 ACL does not allow public READ | `aws_s3_bucket.example` |
| CKV_AWS_57 | S3 ACL does not allow public WRITE | `aws_s3_bucket.example` |
| CKV_AWS_46 | No hard-coded secrets in EC2 user data | `aws_instance.web` |
| CKV_AWS_88 | EC2 instance has no public IP | `aws_instance.web` |
| CKV2_AWS_5 | Security Group is attached to a resource | `aws_security_group.allow_all` |
| CKV_AWS_41 | No hard-coded AWS keys in provider block | `aws.default` |
| CKV_AWS_60 | IAM role restricts assume-role to specific service | `aws_iam_role.demo_role` |
| CKV_AWS_61 | IAM role does not allow cross-service assume-role | `aws_iam_role.demo_role` |
| CKV_AWS_274 | IAM role does not use AdministratorAccess managed policy | `aws_iam_role.demo_role` |
| CKV2_AWS_56 | IAM role does not use IAMFullAccess managed policy | `aws_iam_role.demo_role` |

---

## Detailed Failed Checks

### IAM Policy — `aws_iam_role_policy.admin_policy` — 9 Failures

The policy uses `Action: "*"` and `Resource: "*"` — this is the single most dangerous IAM configuration. One misconfiguration triggered 9 distinct policy violations because the wildcard violates multiple security categories simultaneously.

| Check ID | Description | Severity |
|---|---|---|
| CKV_AWS_62 | Full `*:*` admin privileges granted | 🔴 Critical |
| CKV_AWS_63 | Wildcard `*` used as Action | 🔴 Critical |
| CKV_AWS_355 | Wildcard `*` as Resource for restrictable actions | 🔴 Critical |
| CKV_AWS_286 | Policy allows privilege escalation | 🔴 Critical |
| CKV_AWS_287 | Policy allows credential exposure | 🔴 Critical |
| CKV_AWS_288 | Policy allows data exfiltration | 🔴 Critical |
| CKV_AWS_289 | Permissions management without constraints | 🔴 Critical |
| CKV_AWS_290 | Write access without constraints | 🟠 High |
| CKV2_AWS_40 | Full IAM privileges granted | 🔴 Critical |

**Vulnerable code:**
```hcl
policy = jsonencode({
  Version = "2012-10-17"
  Statement = [{
    Action   = "*"      # Every AWS API call
    Effect   = "Allow"
    Resource = "*"      # Every resource in the account
  }]
})
```

**Fixed code:**
```hcl
policy = jsonencode({
  Version = "2012-10-17"
  Statement = [{
    Effect = "Allow"
    Action = [
      "s3:GetObject",
      "s3:PutObject"
    ]
    Resource = "arn:aws:s3:::my-demo-checkov-bucket/*"
  }]
})
```

**Why this matters:** In a real account, any EC2 instance with this role attached can call `iam:CreateAccessKey`, `sts:AssumeRole`, `ec2:RunInstances`, or literally any other AWS API. One compromised instance = full account takeover. This is why Checkov breaks it into 9 separate checks — credential exposure, data exfiltration, and privilege escalation are distinct attack chains, not the same risk.

---

### S3 Bucket — `aws_s3_bucket.example` — 8 Failures

A 2-line bucket declaration with zero security configuration.

| Check ID | Description | Severity |
|---|---|---|
| CKV2_AWS_6 | No Public Access Block configured | 🔴 Critical |
| CKV_AWS_145 | Not encrypted with KMS | 🟠 High |
| CKV_AWS_18 | Access logging not enabled | 🟡 Medium |
| CKV_AWS_21 | Versioning not enabled | 🟡 Medium |
| CKV2_AWS_62 | Event notifications not enabled | 🟡 Medium |
| CKV2_AWS_61 | No lifecycle configuration | 🟡 Medium |
| CKV_AWS_144 | Cross-region replication not enabled | 🟡 Medium |

**Vulnerable code:**
```hcl
resource "aws_s3_bucket" "example" {
  bucket = "my-demo-checkov-bucket"
}
```

**Fixed code:**
```hcl
resource "aws_s3_bucket_public_access_block" "example" {
  bucket                  = aws_s3_bucket.example.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "example" {
  bucket = aws_s3_bucket.example.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_versioning" "example" {
  bucket = aws_s3_bucket.example.id
  versioning_configuration {
    status = "Enabled"
  }
}
```

**Why this matters:** AWS does not block public access by default. A bare bucket declaration means anyone on the internet can potentially access it if a bucket policy or ACL is misconfigured downstream. The 2019 Capital One breach exposed 100M+ records partly due to misconfigured S3 access controls.

---

### Security Group — `aws_security_group.allow_all` — 6 Failures

`protocol = "-1"` with `0.0.0.0/0` is all-traffic, all-ports, from/to the entire internet — both inbound and outbound. One block, 6 check failures.

| Check ID | Description | Severity |
|---|---|---|
| CKV_AWS_277 | All ports open inbound from 0.0.0.0/0 | 🔴 Critical |
| CKV_AWS_24 | Port 22 (SSH) open from 0.0.0.0/0 | 🔴 Critical |
| CKV_AWS_25 | Port 3389 (RDP) open from 0.0.0.0/0 | 🔴 Critical |
| CKV_AWS_382 | All ports open outbound to 0.0.0.0/0 | 🟠 High |
| CKV_AWS_260 | Port 80 (HTTP) open from 0.0.0.0/0 | 🟠 High |
| CKV_AWS_23 | Ingress/egress rules missing descriptions | 🟢 Low |

**Vulnerable code:**
```hcl
ingress {
  from_port   = 0
  to_port     = 0
  protocol    = "-1"
  cidr_blocks = ["0.0.0.0/0"]
}
```

**Fixed code:**
```hcl
ingress {
  description = "HTTPS from trusted network"
  from_port   = 443
  to_port     = 443
  protocol    = "tcp"
  cidr_blocks = ["10.0.0.0/8"]
}

egress {
  description = "HTTPS outbound only"
  from_port   = 443
  to_port     = 443
  protocol    = "tcp"
  cidr_blocks = ["0.0.0.0/0"]
}
```

**Why this matters:** Open SSH (22) and RDP (3389) to the internet are the most commonly exploited entry points in AWS compromises. Shodan constantly indexes AWS instances with these ports open. Time-to-first-probe after launching an internet-exposed EC2 instance is typically under 60 seconds.

---

### EC2 Instance — `aws_instance.web` — 5 Failures

| Check ID | Description | Severity |
|---|---|---|
| CKV_AWS_79 | IMDSv1 enabled (`http_tokens = "optional"`) | 🟠 High |
| CKV_AWS_8 | Root EBS volume not encrypted (`encrypted = false`) | 🟠 High |
| CKV2_AWS_41 | No IAM instance profile attached | 🟡 Medium |
| CKV_AWS_126 | Detailed monitoring not enabled | 🟡 Medium |
| CKV_AWS_135 | EBS optimization not enabled | 🟢 Low |

**Vulnerable code:**
```hcl
metadata_options {
  http_endpoint = "enabled"
  http_tokens   = "optional"  # IMDSv1 allowed
}

root_block_device {
  encrypted = false
}
```

**Fixed code:**
```hcl
resource "aws_instance" "web" {
  ami                  = "ami-0c55b159cbfafe1f0"
  instance_type        = "t3.micro"   # t3 supports EBS optimization; t2 does not
  iam_instance_profile = aws_iam_instance_profile.web_profile.name
  monitoring           = true
  ebs_optimized        = true

  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"   # Enforces IMDSv2
  }

  root_block_device {
    encrypted = true
  }
}
```

**Why this matters:** IMDSv1 is exploitable via Server-Side Request Forgery (SSRF). An attacker who can make the instance issue an HTTP request to `http://169.254.169.254/latest/meta-data/iam/security-credentials/` retrieves temporary IAM credentials — no login required. The Capital One breach (2019) used exactly this path. `http_tokens = "required"` kills this vector with one line.

> **Note on CKV_AWS_135:** `t2.micro` does not support EBS optimization — this is an AWS instance type limitation, not a code error. Switching to `t3.micro` resolves it.

---

## Key Takeaways

1. **One IAM wildcard = 9 failures = full account compromise potential.** Never use `Action: *` + `Resource: *`. Scope every policy to the minimum required actions and specific resource ARNs.

2. **A bare S3 bucket is never acceptable.** AWS ships with permissive defaults. Every bucket needs an explicit public access block, encryption config, and versioning — minimum.

3. **`protocol = "-1"` with `0.0.0.0/0` is not a shortcut — it's a liability.** Open SSH and RDP to the internet are the top two entry points in AWS breach reports year over year.

4. **IMDSv1 is a documented, exploited attack path.** One line (`http_tokens = "required"`) closes it. There is no reason to leave it optional.

5. **12 checks passed** — worth noting. The IAM role's assume-role policy was correctly scoped, no credentials were hard-coded in provider config, and the EC2 instance had no public IP. These are baselines, not achievements.

6. **Checkov runs in seconds with zero cloud access.** Shift-left means catching this before `terraform apply`, not after an incident.

---

## CI/CD Integration — GitHub Actions

Add this file to your repo to block PRs that introduce security misconfigurations:

```yaml
# .github/workflows/checkov.yml
name: Checkov IaC Security Scan

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  checkov:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Run Checkov
        uses: bridgecrewio/checkov-action@master
        with:
          directory: ./terraform-example
          framework: terraform
          output_format: cli
          soft_fail: false      # Fails the PR — this is the important part
```

`soft_fail: false` is what actually gates merges. Without it, Checkov runs but never blocks anything — security theater.

---

## References

- [Checkov Documentation](https://www.checkov.io/1.Welcome/Quick%20Start.html)
- [CKV_AWS_79 — IMDSv2 Enforcement](https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-general-policies/bc-aws-general-31)
- [CKV_AWS_62 — IAM Wildcard Policy](https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-iam-policies/bc-aws-iam-45)
- [CKV2_AWS_6 — S3 Public Access Block](https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-networking-policies/s3-bucket-should-have-public-access-blocks-defaults-to-false-if-the-public-access-block-is-not-attached)
- [Capital One Breach Analysis — IMDSv1 SSRF](https://krebsonsecurity.com/2019/08/what-we-can-learn-from-the-capital-one-hack/)
- [AWS IAM Least Privilege Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html#grant-least-privilege)
