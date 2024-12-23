#!/bin/bash

set -x

ROOT=$(git rev-parse --show-toplevel)

if [[ ! -d "${ROOT}/venv" ]]; then
    python3.12 -m venv "$ROOT"/venv
    source "$ROOT"/venv/bin/activate
    pip install -r "$ROOT"/requirements.txt
    deactivate
fi

if ! source "${ROOT}/venv/bin/activate"; then
    echo "Failed to activate virtual environment"
    exit 1
fi

# takes a few minutes to run on all 250+ repos
echo
python3 "$ROOT"/scripts/build_check.py
sleep 0.5

echo
python3 "$ROOT"/scripts/github_issue_scraper.py
sleep 0.5

echo
python3 "$ROOT"/scripts/classify_github_issue.py
sleep 0.5

echo
python3 "$ROOT"/scripts/new_repo.py
sleep 0.5

# Rate limits with 3000+ second backoff period
# echo
# python3 "$ROOT"/scripts/process_errors.py
# sleep 0.5

echo
python3 "$ROOT"/scripts/get_contributor_emails.py
sleep 0.5

echo
python3 "$ROOT"/scripts/tweet.py
sleep 0.5
