# CloudTrail Error Analyzer

A Python security script that parses AWS CloudTrail JSON log exports,
filters for error events (`errorCode` field), and prints a SOC-style
summary — sorted by error type and user.

**Skills demonstrated:** Python, JSON parsing, security log analysis,
cloud infrastructure (AWS CloudTrail), SOC workflows.

## Usage

```bash
python3 analyze_cloudtrail.py cloudtrail_sample.json
```

## Sample Output

```
Loading: cloudtrail_sample.json
Timestamp: 2024-xx-xx xx:xx:xx UTC

Total records loaded: 3

============================================================
  CLOUDTRAIL ERROR EVENT SUMMARY
============================================================
  Total error events : 2

  Error code breakdown:
    AccessDenied                        1 event(s)
    NoSuchEntityException               1 event(s)

  Affected users:
    Nikki                               1 event(s)
    AdminBot                            1 event(s)

  Detailed events:
------------------------------------------------------------
Time       : 2023-07-19T22:05:11Z
  User       : Nikki
  Action     : GetObject
  Service    : s3.amazonaws.com
  Error Code : AccessDenied
  Error Msg  : Access Denied
  Source IP  : 203.0.113.42
  Region     : us-east-1
------------------------------------------------------------
  Time       : 2023-07-19T23:59:01Z
  User       : AdminBot
  Action     : DeleteUser
  Service    : iam.amazonaws.com
  Error Code : NoSuchEntityException
  Error Msg  : The user with name target-user cannot be found.
  Source IP  : 198.51.100.99
  Region     : us-east-1
------------------------------------------------------------
```

## What the errors mean

- **AccessDenied** — a user attempted an action they don't have IAM
  permission for. High-priority in SOC triage: could be misconfiguration
  or lateral movement by a threat actor.

- **NoSuchEntityException** — a delete/modify call targeted a resource
  that doesn't exist. Could indicate automated enumeration or a botched
  script.

## Files

| File | Purpose |
|---|---|
| `analyze_cloudtrail.py` | Main analyzer script |
| `cloudtrail_sample.json` | Sample CloudTrail log (from AWS docs) |

## Data source

Sample log structure from the
[AWS CloudTrail documentation](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-examples.html).
