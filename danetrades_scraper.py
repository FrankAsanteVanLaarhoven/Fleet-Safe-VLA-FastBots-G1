#!/usr/bin/env python3
"""
DaneTrades Website Scraper
Scrapes content from danetrades.com and saves to desktop
"""

import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
from pathlib import Path
import re

class DaneTradesScraper:
    def __init__(self):
        self.base_url = "https://danetrades.com/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.desktop_path = Path.home() / "Desktop"
        self.output_dir = self.desktop_path / "danetrades_scraped"
        
    def create_output_directory(self):
        """Create output directory on desktop"""
        self.output_dir.mkdir(exist_ok=True)
        print(f"Output directory created: {self.output_dir}")
        
    def scrape_main_page(self):
        """Scrape the main page content"""
        try:
            print(f"Scraping {self.base_url}...")
            response = requests.get(self.base_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract structured data
            scraped_data = {
                'url': self.base_url,
                'timestamp': datetime.now().isoformat(),
                'title': self.extract_title(soup),
                'navigation': self.extract_navigation(soup),
                'main_content': self.extract_main_content(soup),
                'pricing': self.extract_pricing(soup),
                'features': self.extract_features(soup),
                'faq': self.extract_faq(soup),
                'contact_info': self.extract_contact_info(soup),
                'downloads': self.extract_downloads(soup),
                'raw_html': response.text
            }
            
            return scraped_data
            
        except requests.RequestException as e:
            print(f"Error scraping main page: {e}")
            return None
    
    def extract_title(self, soup):
        """Extract page title"""
        title_tag = soup.find('title')
        return title_tag.get_text().strip() if title_tag else "DaneTrades"
    
    def extract_navigation(self, soup):
        """Extract navigation menu items"""
        nav_items = []
        menu_items = soup.find_all('a', href=True)
        
        for item in menu_items:
            if item.get_text().strip():
                nav_items.append({
                    'text': item.get_text().strip(),
                    'href': item.get('href'),
                    'is_external': item.get('href', '').startswith('http')
                })
        
        return nav_items
    
    def extract_main_content(self, soup):
        """Extract main content sections"""
        content = {}
        
        # Extract headings and their content
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        for heading in headings:
            heading_text = heading.get_text().strip()
            if heading_text:
                # Get content following this heading
                content_sections = []
                next_element = heading.find_next_sibling()
                
                while next_element and next_element.name not in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    if next_element.name in ['p', 'div', 'span'] and next_element.get_text().strip():
                        content_sections.append({
                            'type': next_element.name,
                            'text': next_element.get_text().strip()
                        })
                    next_element = next_element.find_next_sibling()
                
                content[heading_text] = content_sections
        
        return content
    
    def extract_pricing(self, soup):
        """Extract pricing information"""
        pricing = []
        
        # Look for pricing sections
        pricing_sections = soup.find_all('div', class_=re.compile(r'pricing|price|plan', re.I))
        
        for section in pricing_sections:
            price_text = section.get_text()
            if any(word in price_text.lower() for word in ['$', 'month', 'year', 'free', 'trial']):
                pricing.append({
                    'section': section.get_text().strip(),
                    'html': str(section)
                })
        
        return pricing
    
    def extract_features(self, soup):
        """Extract features and benefits"""
        features = []
        
        # Look for feature sections
        feature_sections = soup.find_all(['div', 'section'], class_=re.compile(r'feature|benefit|advantage', re.I))
        
        for section in feature_sections:
            features.append({
                'title': section.find(['h3', 'h4', 'h5']).get_text().strip() if section.find(['h3', 'h4', 'h5']) else '',
                'description': section.get_text().strip(),
                'html': str(section)
            })
        
        return features
    
    def extract_faq(self, soup):
        """Extract FAQ content"""
        faq = []
        
        # Look for FAQ sections
        faq_sections = soup.find_all(['div', 'section'], class_=re.compile(r'faq|question|answer', re.I))
        
        for section in faq_sections:
            questions = section.find_all(['h3', 'h4', 'h5', 'strong'])
            for question in questions:
                q_text = question.get_text().strip()
                if q_text and len(q_text) > 10:  # Likely a question
                    answer_element = question.find_next_sibling()
                    answer_text = answer_element.get_text().strip() if answer_element else ""
                    
                    faq.append({
                        'question': q_text,
                        'answer': answer_text
                    })
        
        return faq
    
    def extract_contact_info(self, soup):
        """Extract contact information"""
        contact = {}
        
        # Look for email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, soup.get_text())
        if emails:
            contact['emails'] = list(set(emails))
        
        # Look for phone numbers
        phone_pattern = r'[\+]?[1-9][\d]{0,15}'
        phones = re.findall(phone_pattern, soup.get_text())
        if phones:
            contact['phones'] = list(set(phones))
        
        return contact
    
    def extract_downloads(self, soup):
        """Extract download links"""
        downloads = []
        
        download_links = soup.find_all('a', href=re.compile(r'\.(exe|zip|dmg|pkg|msi)$', re.I))
        
        for link in download_links:
            downloads.append({
                'text': link.get_text().strip(),
                'href': link.get('href'),
                'filename': os.path.basename(link.get('href', ''))
            })
        
        return downloads
    
    def save_data(self, data):
        """Save scraped data to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save structured JSON data
        json_file = self.output_dir / f"danetrades_data_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"JSON data saved: {json_file}")
        
        # Save raw HTML
        html_file = self.output_dir / f"danetrades_raw_{timestamp}.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(data['raw_html'])
        print(f"Raw HTML saved: {html_file}")
        
        # Save readable text content
        text_file = self.output_dir / f"danetrades_content_{timestamp}.txt"
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(f"DaneTrades Website Content\n")
            f.write(f"Scraped on: {data['timestamp']}\n")
            f.write(f"URL: {data['url']}\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"TITLE: {data['title']}\n\n")
            
            f.write("MAIN CONTENT:\n")
            for heading, sections in data['main_content'].items():
                f.write(f"\n{heading}\n")
                f.write("-" * len(heading) + "\n")
                for section in sections:
                    f.write(f"{section['text']}\n")
                f.write("\n")
            
            f.write("\nPRICING INFORMATION:\n")
            f.write("-" * 20 + "\n")
            for price in data['pricing']:
                f.write(f"{price['section']}\n\n")
            
            f.write("\nFEATURES:\n")
            f.write("-" * 10 + "\n")
            for feature in data['features']:
                f.write(f"{feature['title']}: {feature['description']}\n\n")
            
            f.write("\nFAQ:\n")
            f.write("-" * 5 + "\n")
            for qa in data['faq']:
                f.write(f"Q: {qa['question']}\n")
                f.write(f"A: {qa['answer']}\n\n")
            
            f.write("\nCONTACT INFORMATION:\n")
            f.write("-" * 20 + "\n")
            for key, value in data['contact_info'].items():
                f.write(f"{key}: {value}\n")
            
            f.write("\nDOWNLOAD LINKS:\n")
            f.write("-" * 15 + "\n")
            for download in data['downloads']:
                f.write(f"{download['text']}: {download['href']}\n")
        
        print(f"Text content saved: {text_file}")
        
        return {
            'json_file': json_file,
            'html_file': html_file,
            'text_file': text_file
        }
    
    def run(self):
        """Main execution method"""
        print("Starting DaneTrades website scraper...")
        
        # Create output directory
        self.create_output_directory()
        
        # Scrape the website
        data = self.scrape_main_page()
        
        if data:
            # Save the data
            saved_files = self.save_data(data)
            
            print("\n" + "=" * 50)
            print("SCRAPING COMPLETED SUCCESSFULLY!")
            print("=" * 50)
            print(f"Files saved to: {self.output_dir}")
            print(f"JSON data: {saved_files['json_file'].name}")
            print(f"Raw HTML: {saved_files['html_file'].name}")
            print(f"Text content: {saved_files['text_file'].name}")
            print("=" * 50)
            
            return saved_files
        else:
            print("Failed to scrape website content")
            return None

def main():
    """Main function"""
    scraper = DaneTradesScraper()
    scraper.run()

if __name__ == "__main__":
    main() 