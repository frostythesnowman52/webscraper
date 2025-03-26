# WebScraper (broken)

A comprehensive web scraper that extracts various types of information from websites, including:
- Email addresses
- Phone numbers
- Social media links and handles
- Dates
- Physical addresses
- Prices
- URLs

## Features

- Configurable crawling depth and page limits
- Support for multiple data types
- Concurrent scraping capabilities
- JSON output format
- Logging support
- Command-line interface

## Installation

### From AUR (Arch Linux)
```bash
yay -S webscraper
```

### From Source
```bash
git clone https://github.com/yourusername/webscraper
cd webscraper
pip install -e .
```

### Dependencies
- Python >= 3.6
- requests >= 2.25.0
- beautifulsoup4 >= 4.9.3

## Usage

### Basic Usage
```bash
webscraper https://example.com
```

### With Options
```bash
webscraper https://example.com -d 3 -p 200 -o results.json
```

### Options
- `-d, --depth`: Maximum crawling depth (default: 2)
- `-p, --max-pages`: Maximum number of pages to scrape (default: 100)
- `-t, --timeout`: Request timeout in seconds (default: 30)
- `-o, --output`: Output file path (JSON format)

### Example Output
```json
{
  "emails": ["contact@example.com", "support@example.com"],
  "phone_numbers": ["+1-123-456-7890", "(555) 123-4567"],
  "social_media": ["@example", "facebook.com/example"],
  "urls": ["https://example.com/about", "https://example.com/contact"],
  "dates": ["2024-01-01", "15 Jan 2024"],
  "addresses": ["123 Main St, City, ST 12345"],
  "prices": ["$99.99", "€50.00"]
}
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
