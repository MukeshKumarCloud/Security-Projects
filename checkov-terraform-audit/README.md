# Checkov Terraform Security Audit

Static security analysis of a deliberately misconfigured AWS Terraform example using [Checkov](https://www.checkov.io/).

## What is Checkov?

Checkov is an open-source static analysis tool for Infrastructure-as-Code (IaC). It scans Terraform, CloudFormation, Kubernetes, and other IaC files for misconfigurations against 1000+ built-in security policies mapped to CIS Benchmarks, AWS best practices, and compliance frameworks (SOC2, PCI-DSS, HIPAA).

## Setup

### Prerequisites
- Python 3.8+
- pip

### Install Checkov

```bash
pip3 install checkov
checkov --version
```

## Terraform Code Scanned

The code in `./terraform-example/main.tf` includes intentionally misconfigured AWS resources:

| Resource | Type | Known Issues |
|----------|------|--------------|
| `aws_s3_bucket` | S3 Bucket | No encryption, no public access block, versioning disabled |
| `aws_security_group` | Security Group | Allows all inbound/outbound (0.0.0.0/0) |
| `aws_instance` | EC2 Instance | IMDSv2 not enforced, root volume unencrypted |
| `aws_iam_role_policy` | IAM Policy | Wildcard Action `*` and Resource `*` |

## How to Run

```bash
# CLI output
checkov -d ./terraform-example --output cli

# JSON output
checkov -d ./terraform-example --output json > checkov-results.json
```

## Findings Summary

> Replace the numbers below with your actual scan results from `checkov-output.txt`

| Metric | Count |
|--------|-------|
| Total checks run | XX |
| Passed | XX |
| Failed | XX |
| Skipped | 0 |

## Key Failed Checks

### 1. CKV_AWS_18 — S3 Access Logging Disabled
- **Resource:** `aws_s3_bucket.example`
- **Risk:** No audit trail for bucket access. Required for compliance (PCI-DSS, HIPAA).
- **Fix:** Enable access logging to a separate bucket.

### 2. CKV_AWS_21 — S3 Versioning Disabled
- **Resource:** `aws_s3_bucket_versioning.example`
- **Risk:** Data loss from accidental deletion or overwrites with no recovery path.
- **Fix:** Set `status = "Enabled"` in versioning configuration.

### 3. CKV_AWS_24 — Security Group Allows Unrestricted SSH (Port 22)
- **Resource:** `aws_security_group.allow_all`
- **Risk:** Any IP can attempt SSH. Common attack vector.
- **Fix:** Restrict ingress to specific CIDR ranges or use a bastion/VPN.

### 4. CKV_AWS_8 — EC2 Instance IMDSv2 Not Required
- **Resource:** `aws_instance.web`
- **Risk:** IMDSv1 is vulnerable to SSRF attacks that can steal IAM credentials.
- **Fix:** Set `http_tokens = "required"` in `metadata_options`.

### 5. CKV_AWS_8 — EC2 Root Volume Not Encrypted
- **Resource:** `aws_instance.web`
- **Risk:** Data at rest is unprotected. Fails most compliance frameworks.
- **Fix:** Set `encrypted = true` in `root_block_device`.

### 6. CKV_AWS_40 — IAM Policy Uses Wildcard Actions
- **Resource:** `aws_iam_role_policy.admin_policy`
- **Risk:** Violates principle of least privilege. Any compromise = full AWS account access.
- **Fix:** Scope down to specific actions (e.g., `s3:GetObject`) and specific resources.

## Full Scan Output

See [`checkov-output.txt`](./checkov-output.txt) for the complete CLI output.
See [`checkov-results.json`](./checkov-results.json) for machine-readable results.

## Lessons Learned

1. **Wildcard IAM is always wrong.** Never use `Action: *` + `Resource: *` in production.
2. **IMDSv1 is a known SSRF attack vector** — enforce IMDSv2 on every EC2 instance.
3. **Encryption defaults are off.** AWS doesn't encrypt EBS volumes or S3 by default — you have to explicitly enable it.
4. **0.0.0.0/0 ingress is almost never justified.** Even for public-facing servers, restrict to specific ports.
5. **Checkov runs in seconds.** There's no excuse not to run it in every CI/CD pipeline.

## Integrating Checkov in CI/CD (GitHub Actions)

```yaml
# .github/workflows/checkov.yml
name: Checkov Terraform Scan

on: [push, pull_request]

jobs:
  checkov:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Checkov
        uses: bridgecrewio/checkov-action@master
        with:
          directory: ./terraform-example
          framework: terraform
```

## References

- [Checkov Documentation](https://www.checkov.io/1.Welcome/Quick%20Start.html)
- [CIS AWS Foundations Benchmark](https://www.cisecurity.org/benchmark/amazon_web_services)
- [AWS Security Best Practices](https://docs.aws.amazon.com/security/)
