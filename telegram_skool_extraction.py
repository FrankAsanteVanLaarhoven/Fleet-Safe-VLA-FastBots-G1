#!/usr/bin/env python3
"""
Iron Cloud Nexus AI - Telegram & Skool Extraction System
Dedicated extraction of Telegram profiles and Skool accounts with validation
"""

import requests
import json
import re
import time
import os
from datetime import datetime
from typing import Dict, List, Any
import urllib.parse

class TelegramSkoolExtractor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
        
    def extract_telegram_profiles(self, name: str, social_profiles: Dict[str, Any]) -> Dict[str, Any]:
        """Extract Telegram profiles and validate them"""
        print(f"  📱 Extracting Telegram profiles for {name}...")
        
        telegram_data = {
            "profiles": {},
            "usernames": [],
            "channels": {},
            "groups": {},
            "validation_results": {}
        }
        
        # Generate Telegram username variations
        name_parts = name.lower().split()
        first_name = name_parts[0] if name_parts else ""
        last_name = name_parts[-1] if len(name_parts) > 1 else ""
        
        username_variations = [
            f"{first_name}{last_name}",
            f"{first_name}.{last_name}",
            f"{first_name}_{last_name}",
            f"{first_name[0]}{last_name}",
            f"{first_name}{last_name[0]}",
            f"{first_name}",
            f"{last_name}",
            f"{first_name}{last_name}1",
            f"{first_name}{last_name}2",
            f"{first_name}{last_name}3",
            f"t{first_name}{last_name}",
            f"t{first_name}",
            f"t{last_name}",
            f"{first_name}official",
            f"{last_name}official",
            f"{first_name}real",
            f"{last_name}real"
        ]
        
        # Test each Telegram username variation
        for username in username_variations:
            try:
                # Test Telegram web link
                telegram_url = f"https://t.me/{username}"
                
                response = self.session.get(telegram_url, timeout=10, allow_redirects=False)
                
                if response.status_code == 200:
                    # Profile exists
                    content = response.text.lower()
                    
                    # Extract profile information
                    profile_info = {
                        "username": username,
                        "url": telegram_url,
                        "status": "active",
                        "verified": True,
                        "type": "user"
                    }
                    
                    # Check if it's a channel or group
                    if "channel" in content or "subscribers" in content:
                        profile_info["type"] = "channel"
                        # Extract subscriber count
                        subscriber_match = re.search(r'(\d+(?:,\d+)*)\s*subscribers?', content)
                        if subscriber_match:
                            profile_info["subscribers"] = subscriber_match.group(1)
                    
                    elif "group" in content or "members" in content:
                        profile_info["type"] = "group"
                        # Extract member count
                        member_match = re.search(r'(\d+(?:,\d+)*)\s*members?', content)
                        if member_match:
                            profile_info["members"] = member_match.group(1)
                    
                    # Extract bio/description
                    bio_match = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', content)
                    if bio_match:
                        profile_info["bio"] = bio_match.group(1)
                    
                    telegram_data["profiles"][username] = profile_info
                    telegram_data["usernames"].append(username)
                    telegram_data["validation_results"][username] = "active"
                    
                    print(f"      ✅ Telegram: @{username} ({profile_info['type']})")
                    
                elif response.status_code == 301 or response.status_code == 302:
                    # Profile exists but redirects
                    redirect_url = response.headers.get('Location', '')
                    profile_info = {
                        "username": username,
                        "url": telegram_url,
                        "redirect_url": redirect_url,
                        "status": "redirect",
                        "verified": True,
                        "type": "user"
                    }
                    
                    telegram_data["profiles"][username] = profile_info
                    telegram_data["usernames"].append(username)
                    telegram_data["validation_results"][username] = "redirect"
                    
                    print(f"      ⚠️  Telegram: @{username} (Redirect)")
                    
                else:
                    telegram_data["validation_results"][username] = "inactive"
                    print(f"      ❌ Telegram: @{username} (Inactive)")
                    
            except Exception as e:
                telegram_data["validation_results"][username] = "error"
                print(f"      ❌ Telegram: @{username} (Error: {str(e)})")
            
            time.sleep(0.5)  # Rate limiting
        
        return telegram_data
    
    def extract_skool_profiles(self, name: str, social_profiles: Dict[str, Any]) -> Dict[str, Any]:
        """Extract Skool profiles and validate them"""
        print(f"  🎓 Extracting Skool profiles for {name}...")
        
        skool_data = {
            "profiles": {},
            "usernames": [],
            "courses": {},
            "communities": {},
            "validation_results": {}
        }
        
        # Generate Skool username variations
        name_parts = name.lower().split()
        first_name = name_parts[0] if name_parts else ""
        last_name = name_parts[-1] if len(name_parts) > 1 else ""
        
        username_variations = [
            f"{first_name}{last_name}",
            f"{first_name}.{last_name}",
            f"{first_name}_{last_name}",
            f"{first_name[0]}{last_name}",
            f"{first_name}{last_name[0]}",
            f"{first_name}",
            f"{last_name}",
            f"{first_name}{last_name}1",
            f"{first_name}{last_name}2",
            f"{first_name}{last_name}3",
            f"{first_name}official",
            f"{last_name}official",
            f"{first_name}real",
            f"{last_name}real",
            f"{first_name}academy",
            f"{last_name}academy",
            f"{first_name}school",
            f"{last_name}school"
        ]
        
        # Test each Skool username variation
        for username in username_variations:
            try:
                # Test Skool profile link
                skool_url = f"https://skool.com/{username}"
                
                response = self.session.get(skool_url, timeout=10, allow_redirects=False)
                
                if response.status_code == 200:
                    # Profile exists
                    content = response.text.lower()
                    
                    # Extract profile information
                    profile_info = {
                        "username": username,
                        "url": skool_url,
                        "status": "active",
                        "verified": True,
                        "type": "user"
                    }
                    
                    # Check if it's a course or community
                    if "course" in content or "lesson" in content:
                        profile_info["type"] = "course"
                        # Extract course information
                        course_match = re.search(r'(\d+)\s*lessons?', content)
                        if course_match:
                            profile_info["lessons"] = course_match.group(1)
                    
                    elif "community" in content or "members" in content:
                        profile_info["type"] = "community"
                        # Extract member count
                        member_match = re.search(r'(\d+(?:,\d+)*)\s*members?', content)
                        if member_match:
                            profile_info["members"] = member_match.group(1)
                    
                    # Extract bio/description
                    bio_match = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', content)
                    if bio_match:
                        profile_info["bio"] = bio_match.group(1)
                    
                    # Extract title/headline
                    title_match = re.search(r'<title>([^<]+)</title>', content)
                    if title_match:
                        profile_info["title"] = title_match.group(1)
                    
                    skool_data["profiles"][username] = profile_info
                    skool_data["usernames"].append(username)
                    skool_data["validation_results"][username] = "active"
                    
                    print(f"      ✅ Skool: @{username} ({profile_info['type']})")
                    
                elif response.status_code == 301 or response.status_code == 302:
                    # Profile exists but redirects
                    redirect_url = response.headers.get('Location', '')
                    profile_info = {
                        "username": username,
                        "url": skool_url,
                        "redirect_url": redirect_url,
                        "status": "redirect",
                        "verified": True,
                        "type": "user"
                    }
                    
                    skool_data["profiles"][username] = profile_info
                    skool_data["usernames"].append(username)
                    skool_data["validation_results"][username] = "redirect"
                    
                    print(f"      ⚠️  Skool: @{username} (Redirect)")
                    
                else:
                    skool_data["validation_results"][username] = "inactive"
                    print(f"      ❌ Skool: @{username} (Inactive)")
                    
            except Exception as e:
                skool_data["validation_results"][username] = "error"
                print(f"      ❌ Skool: @{username} (Error: {str(e)})")
            
            time.sleep(0.5)  # Rate limiting
        
        return skool_data
    
    def extract_telegram_skool_profiles(self, targets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract Telegram and Skool profiles for all targets"""
        print("🔍 Iron Cloud Nexus AI - Telegram & Skool Extraction")
        print("=" * 70)
        
        results = {
            "operation_timestamp": datetime.now().isoformat(),
            "targets_analyzed": len(targets),
            "telegram_data": {},
            "skool_data": {},
            "summary": {
                "telegram_profiles": 0,
                "skool_profiles": 0,
                "active_telegram": 0,
                "active_skool": 0
            }
        }
        
        for target in targets:
            print(f"\n🎯 Telegram & Skool Analysis: {target['name']}")
            
            target_data = {
                "name": target['name'],
                "telegram": {},
                "skool": {}
            }
            
            # 1. Extract Telegram profiles
            telegram_results = self.extract_telegram_profiles(
                target['name'], 
                target.get('social_media_profiles', {})
            )
            target_data["telegram"] = telegram_results
            
            # 2. Extract Skool profiles
            skool_results = self.extract_skool_profiles(
                target['name'], 
                target.get('social_media_profiles', {})
            )
            target_data["skool"] = skool_results
            
            # Update summary
            results["summary"]["telegram_profiles"] += len(telegram_results["profiles"])
            results["summary"]["skool_profiles"] += len(skool_results["profiles"])
            results["summary"]["active_telegram"] += len([p for p in telegram_results["profiles"].values() if p.get('status') == 'active'])
            results["summary"]["active_skool"] += len([p for p in skool_results["profiles"].values() if p.get('status') == 'active'])
            
            results["telegram_data"][target['name']] = telegram_results
            results["skool_data"][target['name']] = skool_results
            
            print(f"  🎯 Summary:")
            print(f"    • Telegram Profiles: {len(telegram_results['profiles'])}")
            print(f"    • Skool Profiles: {len(skool_results['profiles'])}")
            print(f"    • Active Telegram: {len([p for p in telegram_results['profiles'].values() if p.get('status') == 'active'])}")
            print(f"    • Active Skool: {len([p for p in skool_results['profiles'].values() if p.get('status') == 'active'])}")
            
            time.sleep(2)  # Rate limiting
        
        return results
    
    def save_telegram_skool_report(self, results: Dict[str, Any], filename: str = None) -> str:
        """Save Telegram and Skool profile report"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"~/Desktop/iron_cloud_telegram_skool_report_{timestamp}.md"
        
        # Expand home directory
        filename = filename.replace("~/", f"{os.path.expanduser('~')}/")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# 🔍 Iron Cloud Nexus AI - Telegram & Skool Extraction Report\n\n")
            f.write(f"**Operation Timestamp:** {results['operation_timestamp']}\n")
            f.write(f"**Targets Analyzed:** {results['targets_analyzed']}\n")
            f.write(f"**Telegram Profiles:** {results['summary']['telegram_profiles']}\n")
            f.write(f"**Skool Profiles:** {results['summary']['skool_profiles']}\n")
            f.write(f"**Active Telegram:** {results['summary']['active_telegram']}\n")
            f.write(f"**Active Skool:** {results['summary']['active_skool']}\n\n")
            
            f.write("## 🎯 Telegram & Skool Profile Analysis\n\n")
            
            for target_name in results['telegram_data'].keys():
                f.write(f"### {target_name}\n\n")
                
                # Telegram Profiles
                telegram_profiles = results['telegram_data'][target_name]['profiles']
                if telegram_profiles:
                    f.write("**📱 Telegram Profiles:**\n")
                    for username, profile_info in telegram_profiles.items():
                        f.write(f"- **@{username}** ({profile_info.get('type', 'user')})\n")
                        f.write(f"  - URL: {profile_info.get('url', 'N/A')}\n")
                        f.write(f"  - Status: {profile_info.get('status', 'N/A')}\n")
                        if profile_info.get('bio'):
                            f.write(f"  - Bio: {profile_info.get('bio', 'N/A')}\n")
                        if profile_info.get('subscribers'):
                            f.write(f"  - Subscribers: {profile_info.get('subscribers', 'N/A')}\n")
                        if profile_info.get('members'):
                            f.write(f"  - Members: {profile_info.get('members', 'N/A')}\n")
                        f.write("\n")
                else:
                    f.write("**📱 Telegram Profiles:** None found\n\n")
                
                # Skool Profiles
                skool_profiles = results['skool_data'][target_name]['profiles']
                if skool_profiles:
                    f.write("**🎓 Skool Profiles:**\n")
                    for username, profile_info in skool_profiles.items():
                        f.write(f"- **@{username}** ({profile_info.get('type', 'user')})\n")
                        f.write(f"  - URL: {profile_info.get('url', 'N/A')}\n")
                        f.write(f"  - Status: {profile_info.get('status', 'N/A')}\n")
                        if profile_info.get('bio'):
                            f.write(f"  - Bio: {profile_info.get('bio', 'N/A')}\n")
                        if profile_info.get('title'):
                            f.write(f"  - Title: {profile_info.get('title', 'N/A')}\n")
                        if profile_info.get('lessons'):
                            f.write(f"  - Lessons: {profile_info.get('lessons', 'N/A')}\n")
                        if profile_info.get('members'):
                            f.write(f"  - Members: {profile_info.get('members', 'N/A')}\n")
                        f.write("\n")
                else:
                    f.write("**🎓 Skool Profiles:** None found\n\n")
                
                f.write("---\n\n")
            
            f.write("## 🔧 Telegram & Skool Extraction Methodology\n\n")
            f.write("This extraction utilized:\n")
            f.write("- **Username Generation:** Pattern-based username variations\n")
            f.write("- **Profile Validation:** Direct URL testing and status verification\n")
            f.write("- **Content Analysis:** Bio, subscriber, and member count extraction\n")
            f.write("- **Type Classification:** User, channel, group, course, community identification\n")
            f.write("- **Status Verification:** Active vs inactive vs redirect determination\n\n")
            
            f.write("## 📋 Platform Information\n\n")
            f.write("### Telegram\n")
            f.write("- **Platform:** Messaging and social media platform\n")
            f.write("- **URL Format:** https://t.me/username\n")
            f.write("- **Profile Types:** Users, Channels, Groups\n")
            f.write("- **Features:** Direct messaging, broadcasting, community building\n\n")
            
            f.write("### Skool\n")
            f.write("- **Platform:** Online learning and community platform\n")
            f.write("- **URL Format:** https://skool.com/username\n")
            f.write("- **Profile Types:** Users, Courses, Communities\n")
            f.write("- **Features:** Course creation, community building, online education\n\n")
            
            f.write("*Report generated by Iron Cloud Nexus AI - Telegram & Skool Extraction Platform*\n")
        
        print(f"\n📄 Telegram & Skool report saved to: {filename}")
        return filename

def main():
    """Main Telegram and Skool extraction operation"""
    print("🔍 Iron Cloud Nexus AI - Telegram & Skool Extraction")
    print("=" * 70)
    
    # Initialize our extractor
    extractor = TelegramSkoolExtractor()
    
    # Define targets with social media data from previous analysis
    targets = [
        {
            "name": "Timothy Armoo",
            "social_media_profiles": {
                "verified_profiles": {
                    "linkedin": {"url": "https://www.linkedin.com/in/timothyarmoo/"},
                    "tiktok": {"url": "https://www.tiktok.com/@timothyarmoo"},
                    "twitch": {"url": "https://www.twitch.tv/timothyarmoo"},
                    "github": {"url": "https://github.com/tarmoo"},
                    "medium": {"url": "https://medium.com/@timothyarmoo"},
                    "substack": {"url": "https://timothya.substack.com"}
                }
            }
        },
        {
            "name": "Alex Martin",
            "social_media_profiles": {
                "verified_profiles": {
                    "tiktok": {"url": "https://www.tiktok.com/@alexmartin"},
                    "twitch": {"url": "https://www.twitch.tv/alexmartin"},
                    "github": {"url": "https://github.com/alexmartin"},
                    "medium": {"url": "https://medium.com/@alexmartin"},
                    "substack": {"url": "https://alexmartin.substack.com"}
                }
            }
        }
    ]
    
    # Execute Telegram and Skool extraction
    results = extractor.extract_telegram_skool_profiles(targets)
    
    # Save report
    report_file = extractor.save_telegram_skool_report(results)
    
    # Print summary
    print("\n" + "=" * 70)
    print("🎉 Telegram & Skool Extraction Complete!")
    print(f"📊 Summary:")
    print(f"   • Targets Analyzed: {results['targets_analyzed']}")
    print(f"   • Telegram Profiles: {results['summary']['telegram_profiles']}")
    print(f"   • Skool Profiles: {results['summary']['skool_profiles']}")
    print(f"   • Active Telegram: {results['summary']['active_telegram']}")
    print(f"   • Active Skool: {results['summary']['active_skool']}")
    print(f"📄 Report saved to: {report_file}")
    print("=" * 70)
    
    # Print key findings
    print("\n🎯 Key Telegram & Skool Findings:")
    for target_name in results['telegram_data'].keys():
        print(f"\n{target_name}:")
        
        # Telegram profiles
        telegram_profiles = results['telegram_data'][target_name]['profiles']
        if telegram_profiles:
            print(f"  📱 Telegram profiles:")
            for username, profile_info in telegram_profiles.items():
                if profile_info.get('status') == 'active':
                    print(f"    • @{username} ({profile_info.get('type', 'user')})")
                    if profile_info.get('subscribers'):
                        print(f"      - Subscribers: {profile_info.get('subscribers')}")
                    if profile_info.get('members'):
                        print(f"      - Members: {profile_info.get('members')}")
        else:
            print(f"  📱 No active Telegram profiles found")
        
        # Skool profiles
        skool_profiles = results['skool_data'][target_name]['profiles']
        if skool_profiles:
            print(f"  🎓 Skool profiles:")
            for username, profile_info in skool_profiles.items():
                if profile_info.get('status') == 'active':
                    print(f"    • @{username} ({profile_info.get('type', 'user')})")
                    if profile_info.get('lessons'):
                        print(f"      - Lessons: {profile_info.get('lessons')}")
                    if profile_info.get('members'):
                        print(f"      - Members: {profile_info.get('members')}")
        else:
            print(f"  🎓 No active Skool profiles found")

if __name__ == "__main__":
    main()
