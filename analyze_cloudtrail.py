#!/usr/bin/env python3
"""
CloudTrail Error Event Analyzer
Real SOC task: parse CloudTrail JSON logs and surface error events.
Author: [Mukesh Kumar]
"""

import json
import sys
from collections import Counter
from datetime import datetime


def load_cloudtrail_log(filepath: str) -> list:
    """Load and return Records from a CloudTrail JSON export."""
    with open(filepath, "r") as f:
        data = json.load(f)
    return data.get("Records", [])


def filter_error_events(records: list) -> list:
    """Return only records that contain an errorCode field."""
    return [r for r in records if "errorCode" in r]


def summarize(error_records: list) -> None:
    """Print a SOC-style summary of error events."""
    total = len(error_records)
    if total == 0:
        print("No error events found. Environment looks clean.")
        return

    print("=" * 60)
    print("  CLOUDTRAIL ERROR EVENT SUMMARY")
    print("=" * 60)
    print(f"  Total error events : {total}")
    print()

    # breakdown by error code
    error_codes = Counter(r["errorCode"] for r in error_records)
    print("  Error code breakdown:")
    for code, count in error_codes.most_common():
        print(f"    {code:<35} {count} event(s)")
    print()

    # breakdown by user
    users = Counter(
        r.get("userIdentity", {}).get("userName", "Unknown")
        for r in error_records
    )
    print("  Affected users:")
    for user, count in users.most_common():
        print(f"    {user:<35} {count} event(s)")
    print()

    # detailed event listing
    print("  Detailed events:")
    print("-" * 60)
    for r in error_records:
        user = r.get("userIdentity", {}).get("userName", "Unknown")
        print(f"  Time       : {r.get('eventTime', 'N/A')}")
        print(f"  User       : {user}")
        print(f"  Action     : {r.get('eventName', 'N/A')}")
        print(f"  Service    : {r.get('eventSource', 'N/A')}")
        print(f"  Error Code : {r.get('errorCode', 'N/A')}")
        print(f"  Error Msg  : {r.get('errorMessage', 'N/A')}")
        print(f"  Source IP  : {r.get('sourceIPAddress', 'N/A')}")
        print(f"  Region     : {r.get('awsRegion', 'N/A')}")
        print("-" * 60)


def main():
    filepath = sys.argv[1] if len(sys.argv) > 1 else "cloudtrail_sample.json"
    print(f"\nLoading: {filepath}")
    print(f"Timestamp: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n")

    records = load_cloudtrail_log(filepath)
    print(f"Total records loaded: {len(records)}")

    error_events = filter_error_events(records)
    summarize(error_events)


if __name__ == "__main__":
    main()
