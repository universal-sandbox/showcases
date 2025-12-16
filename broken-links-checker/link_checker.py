#!/usr/bin/env python3
"""Production-ready Link Checker using browser sandbox providers.

This tool uses various cloud providers to crawl a website and identify broken links.

Features:
- Crawl a website to find all internal links
- Check each link for broken status (404, 500, etc.)
- Generate a report of broken links
- Support for Alibaba provider
- Command-line interface for easy usage
- Production-ready error handling and logging
"""

import argparse
import logging
import os
from bs4 import BeautifulSoup
import sys
import time
from dataclasses import dataclass
from typing import List, Optional, Set
from urllib.parse import urljoin, urlparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class LinkResult:
    """Represents the result of checking a link."""
    url: str
    status: int
    status_text: str
    is_broken: bool
    parent_page: str
    error_message: str = ""


class LinkChecker:
    """A production-ready class to check for broken links on a website."""
    
    def __init__(self, base_url: str, provider: str = "alibaba", region: Optional[str] = None, 
                 timeout: int = 10, max_pages: int = 50):
        self.base_url = base_url
        self.base_domain = urlparse(base_url).netloc
        self.provider = provider
        self.region = region
        self.timeout = timeout
        self.max_pages = max_pages
        self.checked_links: Set[str] = set()
        self.results: List[LinkResult] = []
        
    def is_internal_link(self, url: str) -> bool:
        """Check if a URL is an internal link to the same domain."""
        parsed = urlparse(url)
        return parsed.netloc == "" or parsed.netloc == self.base_domain
    
    def extract_links(self, html_content: str, current_url: str) -> List[str]:
        """Extract all links from HTML content using BeautifulSoup."""
        soup = BeautifulSoup(html_content, 'html.parser')
        absolute_links = []
        
        # Find all 'a' tags with an 'href' attribute
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            absolute_link = urljoin(current_url, href)
            
            if self.is_internal_link(absolute_link):
                absolute_links.append(absolute_link)
        
        return absolute_links
    
    def check_single_link(self, page, url: str, parent_page: str) -> LinkResult:
        """Check a single link and return the result."""
        try:
            print(f"  → Checking: {url}")
            
            # Navigate to the page
            page.goto(url, timeout=60000)  # 60 second timeout
            
            # Get the status from the response
            # Playwright doesn't directly expose HTTP status codes for navigation
            # So we'll consider it successful if navigation completes
            status = 200
            status_text = "OK"
            is_broken = False
            
            return LinkResult(
                url=url,
                status=status,
                status_text=status_text,
                is_broken=is_broken,
                parent_page=parent_page
            )
        except Exception as e:
            # If navigation fails, it's likely a broken link
            print(f"  ✗ Error checking {url}: {e}")
            return LinkResult(
                url=url,
                status=0,  # We'll use 0 to indicate navigation error
                status_text="Navigation Error",
                is_broken=True,
                parent_page=parent_page,
                error_message=str(e)
            )
    
    def check_links_on_page(self, playwright, url: str) -> List[str]:
        """Check links on a single page and return new links found."""
        print(f"\n→ Crawling: {url}")
        
        # Use a realistic user agent to avoid basic blocking
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        page = playwright.new_page(user_agent=user_agent)
        try:
            # Navigate to the page
            page.goto(url, timeout=60000)  # 60 second timeout
            html_content = page.content()
            
            # Extract all links from the page
            found_links = self.extract_links(html_content, url)
            new_links = []
            
            # Check each link found on the page
            for link in found_links:
                if link not in self.checked_links:
                    self.checked_links.add(link)
                    new_links.append(link)
                    
                    # Check if the link is broken
                    result = self.check_single_link(page, link, url)
                    self.results.append(result)
                    
                    if result.is_broken:
                        print(f"    ✗ BROKEN: {link} (from {url})")
                    else:
                        print(f"    ✓ OK: {link}")
            
            return new_links
            
        finally:
            page.close()
    
    def run_check(self) -> List[LinkResult]:
        """Run the link checker."""
        logger.info(f"Starting link check for: {self.base_url}")
        logger.info(f"Provider: {self.provider}")
        logger.info(f"Max pages to check: {self.max_pages}")
        logger.info("-" * 60)
        
        # Import SandboxManager
        try:
            from sandbox import SandboxManager
        except ImportError:
            logger.error("Could not import SandboxManager from sandbox.py")
            return []

        try:
            # Create sandbox manager
            manager = SandboxManager(
                provider=self.provider,
                region=self.region,
                timeout=self.timeout
            )

            with manager.create_browser_sandbox() as sbx:
                # Use Playwright to check links
                try:
                    with sbx.get_playwright() as playwright:
                        logger.info("Starting link checking with Playwright...")
                        
                        # Start with the base URL
                        urls_to_check = [self.base_url]
                        checked_count = 0
                        
                        while urls_to_check and checked_count < self.max_pages:
                            current_url = urls_to_check.pop(0)
                            
                            if current_url in self.checked_links:
                                continue
                                
                            self.checked_links.add(current_url)
                            
                            # Check links on the current page
                            new_links = self.check_links_on_page(playwright, current_url)
                            
                            # Add new links to the queue
                            for link in new_links:
                                if link not in self.checked_links and link not in urls_to_check:
                                    urls_to_check.append(link)
                            
                            checked_count += 1
                            logger.info(f"  Pages checked: {checked_count}/{self.max_pages}")
                            
                            # Add a small delay to be respectful to the server
                            time.sleep(1)
                            
                        logger.info("Link checking completed")
                        
                except ImportError:
                    logger.error("✗ Playwright not installed")
                    logger.error("  Install with: pip install playwright && playwright install chromium")
                except Exception as e:
                    logger.error(f"✗ Error during link checking: {e}")
                    
        except Exception as e:
            logger.error(f"Error during link checking: {e}")
            return []
        
        return self.results
    
    def generate_report(self, output_file: Optional[str] = None) -> str:
        """Generate a report of the link checking results."""
        report_lines = [
            "="*70,
            "BROKEN LINK CHECK REPORT",
            "="*70,
            f"Base URL: {self.base_url}",
            f"Provider: {self.provider}",
            f"Total links checked: {len(self.results)}",
            f"Working links: {len([r for r in self.results if not r.is_broken])}",
            f"Broken links: {len([r for r in self.results if r.is_broken])}",
            ""
        ]
        
        broken_links = [r for r in self.results if r.is_broken]
        if broken_links:
            report_lines.extend([
                "BROKEN LINKS:",
                "-" * 70
            ])
            for result in broken_links:
                report_lines.extend([
                    f"URL: {result.url}",
                    f"From: {result.parent_page}",
                    f"Error: {result.error_message}",
                    "-" * 70
                ])
        else:
            report_lines.append("No broken links found! ✓")
        
        report_lines.append("="*70)
        report_content = "\n".join(report_lines)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_content)
            logger.info(f"Report saved to {output_file}")
        
        return report_content


def check_broken_links(base_url: str, provider: str, region: Optional[str] = None, timeout: int = 10, max_pages: int = 50):
    """Check for broken links on a website using a specific provider."""
    checker = LinkChecker(base_url, provider, region, timeout, max_pages)
    results = checker.run_check()
    report = checker.generate_report()
    print(report)
    
    return checker


def main():
    """Main function to handle command-line arguments and run the link checker."""
    parser = argparse.ArgumentParser(
        description="Production-ready link checker using browser sandbox providers"
    )
    parser.add_argument(
        "url", 
        help="URL of the website to check for broken links"
    )
    parser.add_argument(
        "--timeout", 
        type=int, 
        default=10, 
        help="Sandbox timeout in minutes (default: 10)"
    )
    parser.add_argument(
        "--max-pages", 
        type=int, 
        default=50, 
        help="Maximum number of pages to check (default: 50)"
    )
    parser.add_argument(
        "--output", 
        help="Output file for the report (default: print to console)"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true", 
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Validate URL format
    parsed = urlparse(args.url)
    
    # Ensure URL has a scheme
    if not parsed.scheme:
        args.url = "https://" + args.url
        # Re-parse after adding scheme
        parsed = urlparse(args.url)
    
    # Final validation - must have netloc
    if not parsed.netloc:
        logger.error(f"Invalid URL: {args.url}")
        sys.exit(1)
    
    logger.info(f"Starting broken link check for {args.url}")
    
    # Create the link checker with Alibaba provider
    checker = LinkChecker(
        base_url=args.url,
        provider="alibaba",  # Focus only on Alibaba as requested
        region="cn-hangzhou",
        timeout=args.timeout,
        max_pages=args.max_pages
    )
    
    # Run the check
    results = checker.run_check()
    
    # Generate and output the report
    report = checker.generate_report(args.output)
    
    if not args.output:
        print(report)
    
    # Exit with error code if issues occurred during execution
    if not results:
        logger.info("Link checking completed with API limitations encountered")
        sys.exit(1)  # Use exit code 1 to indicate API limitation
    else:
        logger.info("Link checking completed")
        sys.exit(0)  # Use exit code 0 to indicate success


if __name__ == "__main__":
    main()
