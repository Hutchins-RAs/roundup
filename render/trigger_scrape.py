"""Start the GitHub Actions scrape ("Daily Run") via workflow_dispatch.

Run by the Render cron job. Needs GITHUB_TOKEN: a fine-grained PAT scoped to
Hutchins-RAs/roundup with Actions: Read and write.
"""
import json
import os
import sys
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

# Render cron is UTC-only, so it fires at both 12:15 and 13:15 UTC and we keep
# whichever one is 8 AM Eastern (12:15 in EDT, 13:15 in EST).
now = datetime.now(ZoneInfo("America/New_York"))
if now.hour != 8:
    print(f"{now:%H:%M} ET is not the 8 AM slot; skipping")
    sys.exit(0)

REPO = "Hutchins-RAs/roundup"
WORKFLOW = "main.yml"
HEADERS = {
    "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

# Dispatch on whatever the default branch is, so a rename needs no code change
repo_req = urllib.request.Request(f"https://api.github.com/repos/{REPO}", headers=HEADERS)
with urllib.request.urlopen(repo_req, timeout=30) as resp:
    BRANCH = json.load(resp)["default_branch"]

req = urllib.request.Request(
    f"https://api.github.com/repos/{REPO}/actions/workflows/{WORKFLOW}/dispatches",
    data=f'{{"ref": "{BRANCH}"}}'.encode(),
    method="POST",
    headers=HEADERS,
)
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        print(f"Dispatched {WORKFLOW} on {BRANCH}: HTTP {resp.status}")
except urllib.error.HTTPError as e:
    print(f"Dispatch failed: HTTP {e.code} {e.read().decode()}")
    sys.exit(1)
