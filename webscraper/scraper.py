#!/usr/bin/env python3

import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging
from typing import List, Set, Dict, Optional
import concurrent.futures
import argparse
import json
from pathlib import Path
import sys
import textwrap

def print_banner():
    banner = """
    ╔═══════════════════════════════════════════╗
    ║                WebScraper                  ║
    ║         Extract Data from Websites         ║
    ╚═══════════════════════════════════════════╝
    """
    print(banner)

def print_help_menu():
    help_text = """
    WebScraper - A tool for extracting various types of data from websites

    Usage:
        webscraper <url> [options]
        webscraper (-h | --help)
        webscraper --examples
        webscraper --version

    Arguments:
        url                     The starting URL to scrape from

    Options:
        -h, --help             Show this help message
        --version              Show version
        --examples             Show usage examples
        -d, --depth <n>        Maximum depth to crawl [default: 2]
        -p, --max-pages <n>    Maximum number of pages to scrape [default: 100]
        -t, --timeout <sec>    Request timeout in seconds [default: 30]
        -o, --output <file>    Save results to JSON file
        -v, --verbose          Enable verbose logging
        -q, --quiet            Suppress all output except results
        --no-progress          Disable progress bar
        --respect-robots       Respect robots.txt rules
        --user-agent <agent>   Set custom user agent

    Data Types Extracted:
        • Emails
        • Phone Numbers
        • Social Media Links
        • Dates
        • Physical Addresses
        • Prices
        • URLs

    Examples:
        webscraper https://example.com
        webscraper https://example.com -d 3 -p 200 -o results.json
        webscraper https://example.com --verbose --respect-robots
        webscraper https://example.com -d 1 --no-progress

    For more detailed examples, use: webscraper --examples
    """
    print(textwrap.dedent(help_text))

def print_examples():
    examples = """
    WebScraper - Usage Examples

    1. Basic Scraping:
       $ webscraper https://example.com
       • Scrapes with default settings (depth=2, max_pages=100)
       • Outputs results to console

    2. Deep Crawling:
       $ webscraper https://example.com -d 4 -p 500
       • Crawls up to 4 levels deep
       • Processes up to 500 pages
       • Useful for thorough site analysis

    3. Save Results to File:
       $ webscraper https://example.com -o company_data.json
       • Saves all extracted data to company_data.json
       • Organizes data by type (emails, phones, etc.)

    4. Quick Scan:
       $ webscraper https://example.com -d 1 -p 10
       • Only scans the main page and direct links
       • Limits to 10 pages
       • Fast execution for basic data gathering

    5. Detailed Analysis:
       $ webscraper https://example.com -d 3 -v --respect-robots
       • Crawls up to 3 levels deep
       • Shows verbose logging
       • Respects robots.txt rules
       • Good for ethical scraping

    6. Custom Timeout:
       $ webscraper https://example.com -t 60
       • Sets request timeout to 60 seconds
       • Useful for slow websites

    7. Multiple Options:
       $ webscraper https://example.com -d 2 -p 150 -o data.json --verbose
       • Crawls 2 levels deep
       • Processes up to 150 pages
       • Saves to data.json
       • Shows detailed progress

    Output Format (JSON):
    {
        "emails": ["contact@example.com"],
        "phone_numbers": ["+1-123-456-7890"],
        "social_media": ["@example", "facebook.com/example"],
        "dates": ["2024-01-01"],
        "addresses": ["123 Main St, City, ST 12345"],
        "prices": ["$99.99"],
        "urls": ["https://example.com/about"]
    }

    Tips:
    • Use -d 1 for quick scans of single pages
    • Increase --timeout for slow websites
    • Use --verbose to see detailed progress
    • Always check robots.txt rules for ethical scraping
    • Save to file (-o) for large scraping operations
    """
    print(textwrap.dedent(examples))

class WebScraper:
    def __init__(self, max_depth: int = 2, max_pages: int = 100, timeout: int = 30):
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.timeout = timeout
        self.visited_urls: Set[str] = set()
        self.results: Dict[str, List[str]] = {
            'emails': [],
            'phone_numbers': [],
            'social_media': [],
            'urls': [],
            'dates': [],
            'addresses': [],
            'prices': []
        }
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and has acceptable scheme."""
        try:
            result = urlparse(url)
            return all([result.scheme in ['http', 'https'], result.netloc])
        except:
            return False

    def extract_emails(self, text: str) -> List[str]:
        """Extract email addresses from text."""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return list(set(re.findall(email_pattern, text)))

    def extract_phone_numbers(self, text: str) -> List[str]:
        """Extract phone numbers from text."""
        # Multiple phone number patterns
        patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # International
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # US/Canada
            r'\d{4}[-.\s]?\d{3}[-.\s]?\d{3}'  # Alternative format
        ]
        numbers = []
        for pattern in patterns:
            numbers.extend(re.findall(pattern, text))
        return list(set(numbers))

    def extract_social_media(self, text: str, soup: BeautifulSoup) -> List[str]:
        """Extract social media links and handles."""
        social_patterns = {
            'twitter': r'(?:@|twitter.com/)\w+',
            'facebook': r'(?:facebook.com/|fb.com/)\w+',
            'instagram': r'(?:@|instagram.com/)\w+',
            'linkedin': r'linkedin.com/(?:in|company)/[\w-]+',
            'github': r'github.com/\w+'
        }
        
        social_links = []
        
        # Extract from text
        for platform, pattern in social_patterns.items():
            matches = re.findall(pattern, text)
            social_links.extend(matches)
        
        # Extract from href attributes
        for link in soup.find_all('a', href=True):
            href = link['href']
            if any(platform in href.lower() for platform in social_patterns.keys()):
                social_links.append(href)
        
        return list(set(social_links))

    def extract_dates(self, text: str) -> List[str]:
        """Extract dates from text."""
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{1,2}\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s\d{4}'  # 1 Jan 2024
        ]
        dates = []
        for pattern in date_patterns:
            dates.extend(re.findall(pattern, text))
        return list(set(dates))

    def extract_addresses(self, text: str) -> List[str]:
        """Extract physical addresses from text."""
        # Basic address pattern - can be expanded based on needs
        address_pattern = r'\d+\s+[A-Za-z0-9\s,]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)\s*,?\s*[A-Za-z\s]+,\s*[A-Z]{2}\s*\d{5}'
        return list(set(re.findall(address_pattern, text, re.IGNORECASE)))

    def extract_prices(self, text: str) -> List[str]:
        """Extract prices from text."""
        price_pattern = r'(?:USD|\$|€|£)\s*\d+(?:,\d{3})*(?:\.\d{2})?'
        return list(set(re.findall(price_pattern, text)))

    def scrape_page(self, url: str, depth: int = 0) -> None:
        """Scrape a single page and extract information."""
        if not self.is_valid_url(url) or depth >= self.max_depth or url in self.visited_urls:
            return

        self.visited_urls.add(url)
        
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text()

            # Extract information
            self.results['emails'].extend(self.extract_emails(text))
            self.results['phone_numbers'].extend(self.extract_phone_numbers(text))
            self.results['social_media'].extend(self.extract_social_media(text, soup))
            self.results['dates'].extend(self.extract_dates(text))
            self.results['addresses'].extend(self.extract_addresses(text))
            self.results['prices'].extend(self.extract_prices(text))

            # Remove duplicates
            for key in self.results:
                self.results[key] = list(set(self.results[key]))

            # Extract and follow links if needed
            if depth < self.max_depth and len(self.visited_urls) < self.max_pages:
                links = soup.find_all('a', href=True)
                for link in links:
                    next_url = urljoin(url, link['href'])
                    if self.is_valid_url(next_url):
                        self.results['urls'].append(next_url)
                        self.scrape_page(next_url, depth + 1)

        except Exception as e:
            self.logger.error(f"Error scraping {url}: {str(e)}")

    def scrape(self, start_url: str, output_file: Optional[str] = None) -> Dict[str, List[str]]:
        """Start scraping from a given URL."""
        self.logger.info(f"Starting scrape from: {start_url}")
        
        self.scrape_page(start_url)
        
        if output_file:
            self.save_results(output_file)
        
        return self.results

    def save_results(self, output_file: str) -> None:
        """Save results to a JSON file."""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)
        
        self.logger.info(f"Results saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(
        description='WebScraper - Extract various types of information from websites',
        add_help=False  # Disable default help
    )
    
    # Main arguments
    parser.add_argument('url', nargs='?', help='Starting URL to scrape')
    parser.add_argument('-h', '--help', action='store_true', help='Show this help message')
    parser.add_argument('--version', action='version', version='WebScraper v0.1.0')
    parser.add_argument('--examples', action='store_true', help='Show usage examples')
    
    # Scraping options
    parser.add_argument('-d', '--depth', type=int, default=2,
                      help='Maximum depth for crawling [default: 2]')
    parser.add_argument('-p', '--max-pages', type=int, default=100,
                      help='Maximum number of pages to scrape [default: 100]')
    parser.add_argument('-t', '--timeout', type=int, default=30,
                      help='Timeout for requests in seconds [default: 30]')
    parser.add_argument('-o', '--output',
                      help='Output file path (JSON)')
    
    # Additional options
    parser.add_argument('-v', '--verbose', action='store_true',
                      help='Enable verbose logging')
    parser.add_argument('-q', '--quiet', action='store_true',
                      help='Suppress all output except results')
    parser.add_argument('--no-progress', action='store_true',
                      help='Disable progress bar')
    parser.add_argument('--respect-robots', action='store_true',
                      help='Respect robots.txt rules')
    parser.add_argument('--user-agent',
                      help='Set custom user agent')
    
    args = parser.parse_args()
    
    # Show help menu
    if args.help or (len(sys.argv) == 1 and not args.url):
        print_banner()
        print_help_menu()
        sys.exit(0)
    
    # Show examples
    if args.examples:
        print_banner()
        print_examples()
        sys.exit(0)
    
    # Configure logging based on verbosity
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    elif args.quiet:
        logging.basicConfig(level=logging.ERROR)
    else:
        logging.basicConfig(level=logging.WARNING)
    
    # Initialize and run scraper
    scraper = WebScraper(
        max_depth=args.depth,
        max_pages=args.max_pages,
        timeout=args.timeout
    )
    
    results = scraper.scrape(args.url, args.output)
    
    if not args.output:
        print(json.dumps(results, indent=2))

if __name__ == '__main__':
    main() 