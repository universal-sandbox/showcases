# Broken Links Checker (Node.js)

A Node.js-based tool that crawls websites to identify broken links using the Universal Sandbox browser environment.

## Installation

1. Install the required dependencies:
   ```bash
   npm install
   ```

2. Set up your environment variables:
   - Copy `.env.example` to `.env`
   - Add your `SANDBOX_API_TOKEN` to the `.env` file

## Usage

Run the script with the target URL:

```bash
node linkChecker.js <URL> [options]
```

### Options

- `--timeout <minutes>` - Sandbox timeout in minutes (default: 10)
- `--max-pages <number>` - Maximum number of pages to check (default: 50)
- `--output <file>` - Output file for the report (default: print to console)
- `--verbose` - Enable verbose logging

### Examples

Check a website with default settings:
```bash
node linkChecker.js https://example.com
```

Check with custom settings:
```bash
node linkChecker.js https://example.com --max-pages 100 --timeout 15
```

Save report to a file:
```bash
node linkChecker.js https://example.com --output report.txt
```

## Example Output

```text
Starting broken link check for https://ai-infra.org
Starting link check for: https://ai-infra.org
Provider: alibaba
Max pages to check: 50
------------------------------------------------------------
Creating browser sandbox...
✓ Browser sandbox created: 01KCKK6X74EFAWN83GPENV160E
Starting link checking with Playwright...

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
  Pages checked: 1/50
Link checking completed
Sandbox cleaned up successfully
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
Link checking completed
```

## Features

- Crawl a website to find all internal links
- Check each link for broken status (404, 500, etc.)
- Generate a report of broken links
- Support for Alibaba cloud provider
- Command-line interface for easy usage
- Production-ready error handling and logging

## Dependencies

- `@universal-sandbox/sdk` - Universal Sandbox SDK for Node.js
- `cheerio` - HTML parsing library (similar to BeautifulSoup in Python)
- `dotenv` - Environment variable management

## How It Works

1. The tool creates a browser sandbox using the Universal Sandbox service
2. It starts crawling from the provided base URL
3. For each page, it extracts all internal links using Cheerio
4. Each link is checked by attempting to navigate to it with Playwright
5. Results are collected and a report is generated
6. The sandbox is automatically cleaned up after completion

## Environment Variables

- `SANDBOX_API_TOKEN` - Your Universal Sandbox API token (required)
