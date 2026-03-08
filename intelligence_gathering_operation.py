#!/usr/bin/env python3
"""
Iron Cloud Nexus AI - Advanced Intelligence Gathering Operation
Leveraging our 25 specialized agents for comprehensive LinkedIn intelligence extraction
"""

import asyncio
import json
import requests
import time
import os
from datetime import datetime
from typing import Dict, List, Any
import re
from urllib.parse import urlparse, parse_qs

class IronCloudIntelligenceGatherer:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
    def check_server_health(self) -> bool:
        """Check if our MCP server is operational"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def execute_linkedin_intelligence_agent(self, profile_url: str) -> Dict[str, Any]:
        """Execute our specialized LinkedIn Intelligence Agent"""
        try:
            payload = {
                "agent_type": "linkedin_intelligence",
                "arguments": {
                    "profile_url": profile_url,
                    "extraction_depth": "comprehensive",
                    "include_emails": True,
                    "include_contact_info": True,
                    "include_company_data": True,
                    "stealth_mode": True,
                    "bypass_restrictions": True
                },
                "security_level": "military"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/mcp/agents/execute",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def execute_web_scraping_master_agent(self, url: str) -> Dict[str, Any]:
        """Execute our specialized Web Scraping Master Agent"""
        try:
            payload = {
                "agent_type": "web_scraping_master",
                "arguments": {
                    "target_url": url,
                    "extraction_patterns": [
                        "email_patterns",
                        "contact_information",
                        "personal_details",
                        "professional_info"
                    ],
                    "stealth_browsing": True,
                    "anti_detection": True,
                    "javascript_execution": True,
                    "captcha_solving": True,
                    "rate_limit_bypass": True
                },
                "security_level": "military"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/mcp/agents/execute",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def extract_emails_from_text(self, text: str) -> List[str]:
        """Extract email addresses using advanced pattern matching"""
        email_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            r'\b[A-Za-z0-9._%+-]+\s*\[at\]\s*[A-Za-z0-9.-]+\s*\[dot\]\s*[A-Za-z]{2,}\b',
            r'\b[A-Za-z0-9._%+-]+\s*@\s*[A-Za-z0-9.-]+\s*\.\s*[A-Za-z]{2,}\b'
        ]
        
        emails = []
        for pattern in email_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            emails.extend(matches)
        
        # Clean and deduplicate emails
        cleaned_emails = []
        for email in emails:
            # Convert [at] and [dot] notation
            email = email.replace('[at]', '@').replace('[dot]', '.')
            email = email.replace(' ', '')
            if '@' in email and '.' in email.split('@')[1]:
                cleaned_emails.append(email.lower())
        
        return list(set(cleaned_emails))
    
    def gather_comprehensive_intelligence(self, targets: List[Dict[str, str]]) -> Dict[str, Any]:
        """Execute comprehensive intelligence gathering operation"""
        print("🔍 Iron Cloud Nexus AI - Intelligence Gathering Operation")
        print("=" * 60)
        
        results = {
            "operation_timestamp": datetime.now().isoformat(),
            "targets_analyzed": len(targets),
            "intelligence_data": {},
            "summary": {
                "total_emails_found": 0,
                "successful_extractions": 0,
                "failed_extractions": 0
            }
        }
        
        for target in targets:
            print(f"\n🎯 Analyzing target: {target['name']}")
            print(f"📍 Profile: {target['linkedin_url']}")
            
            target_data = {
                "name": target['name'],
                "linkedin_url": target['linkedin_url'],
                "extraction_methods": [],
                "emails_found": [],
                "contact_info": {},
                "professional_data": {},
                "extraction_status": "pending"
            }
            
            # Method 1: LinkedIn Intelligence Agent
            print("  🔥 Executing LinkedIn Intelligence Agent...")
            linkedin_result = self.execute_linkedin_intelligence_agent(target['linkedin_url'])
            
            if linkedin_result.get('success'):
                target_data["extraction_methods"].append("linkedin_intelligence_agent")
                target_data["extraction_status"] = "success"
                
                # Extract emails from LinkedIn agent response
                if 'data' in linkedin_result:
                    linkedin_text = json.dumps(linkedin_result['data'])
                    emails = self.extract_emails_from_text(linkedin_text)
                    target_data["emails_found"].extend(emails)
                    target_data["professional_data"].update(linkedin_result['data'])
                
                print(f"  ✅ LinkedIn Agent: {len(target_data['emails_found'])} emails found")
            else:
                print(f"  ❌ LinkedIn Agent failed: {linkedin_result.get('error', 'Unknown error')}")
            
            # Method 2: Web Scraping Master Agent
            print("  🌐 Executing Web Scraping Master Agent...")
            scraping_result = self.execute_web_scraping_master_agent(target['linkedin_url'])
            
            if scraping_result.get('success'):
                target_data["extraction_methods"].append("web_scraping_master_agent")
                
                # Extract emails from scraping agent response
                if 'data' in scraping_result:
                    scraping_text = json.dumps(scraping_result['data'])
                    emails = self.extract_emails_from_text(scraping_text)
                    target_data["emails_found"].extend(emails)
                    target_data["contact_info"].update(scraping_result['data'])
                
                print(f"  ✅ Web Scraping Agent: {len(target_data['emails_found'])} emails found")
            else:
                print(f"  ❌ Web Scraping Agent failed: {scraping_result.get('error', 'Unknown error')}")
            
            # Method 3: Direct profile analysis (fallback)
            if not target_data["emails_found"]:
                print("  🔍 Executing direct profile analysis...")
                try:
                    # Extract profile ID from LinkedIn URL
                    profile_id = target['linkedin_url'].split('/in/')[-1].split('/')[0]
                    
                    # Try to find associated websites and social profiles
                    profile_data = {
                        "profile_id": profile_id,
                        "possible_email_patterns": [
                            f"{profile_id}@gmail.com",
                            f"{profile_id}@outlook.com",
                            f"{profile_id}@yahoo.com",
                            f"{profile_id}@hotmail.com",
                            f"{profile_id}@linkedin.com"
                        ],
                        "company_emails": [],
                        "website_analysis": "Profile requires authentication for full access"
                    }
                    
                    target_data["professional_data"].update(profile_data)
                    print("  ⚠️  Direct analysis: Limited data due to LinkedIn restrictions")
                    
                except Exception as e:
                    print(f"  ❌ Direct analysis failed: {str(e)}")
            
            # Deduplicate emails
            target_data["emails_found"] = list(set(target_data["emails_found"]))
            results["summary"]["total_emails_found"] += len(target_data["emails_found"])
            
            if target_data["emails_found"]:
                results["summary"]["successful_extractions"] += 1
                print(f"  🎉 Total emails found: {len(target_data['emails_found'])}")
                for email in target_data["emails_found"]:
                    print(f"     📧 {email}")
            else:
                results["summary"]["failed_extractions"] += 1
                print("  ❌ No emails found")
            
            results["intelligence_data"][target['name']] = target_data
            
            # Rate limiting
            time.sleep(2)
        
        return results
    
    def save_intelligence_report(self, results: Dict[str, Any], filename: str = None):
        """Save intelligence report to markdown file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"~/Desktop/iron_cloud_intelligence_report_{timestamp}.md"
        
        # Expand home directory
        filename = filename.replace("~/", f"{os.path.expanduser('~')}/")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# 🔍 Iron Cloud Nexus AI - Intelligence Gathering Report\n\n")
            f.write(f"**Operation Timestamp:** {results['operation_timestamp']}\n")
            f.write(f"**Targets Analyzed:** {results['targets_analyzed']}\n")
            f.write(f"**Total Emails Found:** {results['summary']['total_emails_found']}\n")
            f.write(f"**Successful Extractions:** {results['summary']['successful_extractions']}\n")
            f.write(f"**Failed Extractions:** {results['summary']['failed_extractions']}\n\n")
            
            f.write("## 🎯 Intelligence Data\n\n")
            
            for target_name, target_data in results['intelligence_data'].items():
                f.write(f"### {target_name}\n\n")
                f.write(f"**LinkedIn Profile:** {target_data['linkedin_url']}\n")
                f.write(f"**Extraction Status:** {target_data['extraction_status']}\n")
                f.write(f"**Methods Used:** {', '.join(target_data['extraction_methods'])}\n\n")
                
                if target_data['emails_found']:
                    f.write("**📧 Emails Found:**\n")
                    for email in target_data['emails_found']:
                        f.write(f"- {email}\n")
                    f.write("\n")
                
                if target_data['contact_info']:
                    f.write("**📞 Contact Information:**\n")
                    f.write(f"```json\n{json.dumps(target_data['contact_info'], indent=2)}\n```\n\n")
                
                if target_data['professional_data']:
                    f.write("**💼 Professional Data:**\n")
                    f.write(f"```json\n{json.dumps(target_data['professional_data'], indent=2)}\n```\n\n")
                
                f.write("---\n\n")
        
        print(f"\n📄 Intelligence report saved to: {filename}")
        return filename

def main():
    """Main intelligence gathering operation"""
    import os
    
    # Initialize our Iron Cloud Intelligence Gatherer
    gatherer = IronCloudIntelligenceGatherer()
    
    # Check server health
    if not gatherer.check_server_health():
        print("❌ MCP Server is not running. Please start the server first.")
        return
    
    print("✅ MCP Server is operational")
    
    # Define our intelligence targets
    targets = [
        {
            "name": "Alex Martin",
            "linkedin_url": "https://www.linkedin.com/messaging/thread/2-NzBkYzk2MzMtODhkYi00NTUzLWEyZWEtM2UyZjk1NGQ3OTIxXzEwMA=="
        },
        {
            "name": "Timothy Armoo",
            "linkedin_url": "https://www.linkedin.com/in/timothyarmoo/"
        }
    ]
    
    # Execute comprehensive intelligence gathering
    results = gatherer.gather_comprehensive_intelligence(targets)
    
    # Save intelligence report
    report_file = gatherer.save_intelligence_report(results)
    
    # Print summary
    print("\n" + "=" * 60)
    print("🎉 Intelligence Gathering Operation Complete!")
    print(f"📊 Summary:")
    print(f"   • Targets Analyzed: {results['summary']['successful_extractions'] + results['summary']['failed_extractions']}")
    print(f"   • Successful Extractions: {results['summary']['successful_extractions']}")
    print(f"   • Total Emails Found: {results['summary']['total_emails_found']}")
    print(f"📄 Report saved to: {report_file}")
    print("=" * 60)

if __name__ == "__main__":
    main()
