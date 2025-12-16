# Broken Links Checker

A Python-based tool that crawls websites to identify broken links using the Universal Sandbox browser environment.

## Installation

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Ensure you have the necessary environment variables set up (if any).

## Usage

Run the script with the target URL:

```bash
python link_checker.py <URL>
```

## Example Output

```text
➜  broken-links-checker git:(master) ✗ python link_checker.py https://ai-infra.org
2025-12-16 20:47:19,212 - INFO - Starting broken link check for https://ai-infra.org
2025-12-16 20:47:19,212 - INFO - Starting link check for: https://ai-infra.org
2025-12-16 20:47:19,212 - INFO - Provider: alibaba
2025-12-16 20:47:19,212 - INFO - Max pages to check: 50
2025-12-16 20:47:19,212 - INFO - ------------------------------------------------------------
2025-12-16 20:47:19,551 - INFO - Creating browser sandbox...
2025-12-16 20:47:23,981 - INFO - HTTP Request: POST https://api.sandbox.ai-infra.org/sandboxes/browser "HTTP/1.1 201 Created"
2025-12-16 20:47:23,991 - INFO - ✓ Browser sandbox created: 01KCKK6X74EFAWN83GPENV160E
2025-12-16 20:47:29,268 - INFO - Starting link checking with Playwright...

→ Crawling: https://ai-infra.org
  → Checking: https://ai-infra.org/
    ✓ OK: https://ai-infra.org/
  → Checking: https://ai-infra.org/about
    ✓ OK: https://ai-infra.org/about
  → Checking: https://ai-infra.org/showcases
    ✓ OK: https://ai-infra.org/showcases
  → Checking: https://ai-infra.org/pricing
    ✓ OK: https://ai-infra.org/pricing
  → Checking: https://ai-infra.org/api-docs
    ✓ OK: https://ai-infra.org/api-docs
  → Checking: https://ai-infra.org/sign-up
    ✓ OK: https://ai-infra.org/sign-up
  → Checking: https://ai-infra.org/dashboard?tab=billing
    ✓ OK: https://ai-infra.org/dashboard?tab=billing
2025-12-16 20:47:42,447 - INFO -   Pages checked: 1/50
2025-12-16 20:47:43,453 - INFO - Link checking completed
2025-12-16 20:47:47,045 - INFO - HTTP Request: DELETE https://api.sandbox.ai-infra.org/sandboxes/01KCKK6X74EFAWN83GPENV160E "HTTP/1.1 200 OK"
2025-12-16 20:47:47,046 - INFO - Sandbox cleaned up successfully
======================================================================
BROKEN LINK CHECK REPORT
======================================================================
Base URL: https://ai-infra.org
Provider: alibaba
Total links checked: 7
Working links: 7
Broken links: 0

No broken links found! ✓
======================================================================
2025-12-16 20:47:47,046 - INFO - Link checking completed
```
