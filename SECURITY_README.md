# DataMinerAI Security Platform

## 🔒 Advanced Security & Penetration Testing Framework

DataMinerAI now includes a comprehensive security platform with advanced hacking techniques, penetration testing tools, and cybersecurity capabilities. This platform is designed for ethical hacking, security research, and educational purposes.

## ⚠️ **IMPORTANT LEGAL NOTICE**

**This platform contains advanced security testing tools. Only use against systems you own or have explicit written permission to test. Unauthorized testing may be illegal in your jurisdiction. The developers are not responsible for any misuse of these tools.**

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18.0+
- Git

### Installation & Startup

```bash
# Clone the repository
git clone <repository-url>
cd dataminerAI

# Start all security services
./start_security.sh

# Access the Security Dashboard
open http://localhost:3000/security
```

### Stop Services
```bash
./stop_security.sh
```

## 🛡️ Security Modules Overview

### 1. Network Scanner
**Advanced network reconnaissance and port scanning capabilities**

- **Ping Sweep**: Discover live hosts on network
- **Port Scanning**: TCP/UDP port enumeration
- **OS Detection**: Operating system fingerprinting
- **Service Detection**: Identify running services
- **Mass Scanning**: High-speed network scanning

**API Endpoints:**
```bash
# Network scan
curl -X POST http://localhost:8001/api/network/scan \
  -H 'Content-Type: application/json' \
  -d '{"target": "192.168.1.1", "scan_type": "comprehensive"}'

# OS detection
curl -X POST http://localhost:8001/api/network/os-detection \
  -H 'Content-Type: application/json' \
  -d '{"target": "192.168.1.1"}'
```

### 2. Web Pentester
**Comprehensive web application security testing**

- **Vulnerability Scanning**: SQL injection, XSS, CSRF testing
- **Directory Enumeration**: Discover hidden files and directories
- **Subdomain Enumeration**: Find subdomains
- **WordPress Scanning**: WordPress-specific vulnerabilities
- **Technology Detection**: Identify web technologies

**API Endpoints:**
```bash
# Web security scan
curl -X POST http://localhost:8001/api/web/scan \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://example.com"}'

# Directory enumeration
curl -X POST http://localhost:8001/api/web/directory-enumeration \
  -H 'Content-Type: application/json' \
  -d '{"base_url": "https://example.com"}'
```

### 3. Social Engineering Toolkit
**Advanced psychological manipulation techniques**

- **Phishing Campaigns**: Automated phishing email campaigns
- **Credential Harvesting**: Capture login credentials
- **Pretexting Attacks**: Social engineering pretexts
- **Psychological Profiling**: Target personality analysis
- **Baiting Attacks**: Physical and digital baiting

**API Endpoints:**
```bash
# Create phishing campaign
curl -X POST http://localhost:8001/api/social/campaign \
  -H 'Content-Type: application/json' \
  -d '{
    "campaign_name": "Password Reset",
    "target_emails": ["target@example.com"],
    "template_name": "password_reset"
  }'

# Launch campaign
curl -X POST http://localhost:8001/api/social/launch \
  -H 'Content-Type: application/json' \
  -d '{"campaign_id": "campaign_123"}'
```

### 4. Cryptographic Analyzer
**Advanced cryptographic operations and analysis**

- **Hash Analysis**: MD5, SHA1, SHA256, SHA512, bcrypt
- **Hash Cracking**: Rainbow table and dictionary attacks
- **Key Generation**: Encryption key creation
- **Encryption/Decryption**: AES, Fernet, RSA
- **Frequency Analysis**: Cryptanalysis techniques

**API Endpoints:**
```bash
# Hash analysis
curl -X POST http://localhost:8001/api/crypto/hash \
  -H 'Content-Type: application/json' \
  -d '{"data": "password", "algorithm": "md5"}'

# Hash cracking
curl -X POST http://localhost:8001/api/crypto/crack \
  -H 'Content-Type: application/json' \
  -d '{"hash_value": "5f4dcc3b5aa765d61d8327deb882cf99"}'

# Generate encryption key
curl -X POST http://localhost:8001/api/crypto/generate-key \
  -H 'Content-Type: application/json' \
  -d '{"key_type": "fernet"}'
```

### 5. Exploitation Framework
**Automated exploit execution and payload generation**

- **Payload Generation**: Custom exploit payloads
- **Exploit Execution**: Automated vulnerability exploitation
- **Privilege Escalation**: Automated privilege escalation testing
- **Reverse Shells**: Remote access capabilities
- **Web Shells**: Web-based command execution

**API Endpoints:**
```bash
# Generate exploit payload
curl -X POST http://localhost:8001/api/exploit/generate-payload \
  -H 'Content-Type: application/json' \
  -d '{
    "target": "192.168.1.1",
    "exploit_type": "rce",
    "custom_params": {"command": "whoami"}
  }'

# Execute exploit
curl -X POST http://localhost:8001/api/exploit/execute \
  -H 'Content-Type: application/json' \
  -d '{"payload_data": {...}}'
```

### 6. Client-Server Manager
**Advanced client-server communication protocols**

- **TCP/UDP Servers**: Multi-protocol server creation
- **Chat Servers**: Real-time communication
- **Reverse Shells**: Remote command execution
- **SOCKS Proxies**: Network tunneling
- **WebSocket Servers**: Real-time web communication

**API Endpoints:**
```bash
# Create chat server
curl -X POST http://localhost:8001/api/client-server/create \
  -H 'Content-Type: application/json' \
  -d '{
    "host": "0.0.0.0",
    "port": 8080,
    "server_type": "chat"
  }'

# Connect to server
curl -X POST http://localhost:8001/api/client-server/connect \
  -H 'Content-Type: application/json' \
  -d '{"host": "localhost", "port": 8080, "protocol": "tcp"}'
```

### 7. Packet Analyzer
**Network traffic analysis and monitoring**

- **Packet Capture**: Real-time network monitoring
- **HTTP Traffic Analysis**: Web traffic inspection
- **PCAP Analysis**: Packet capture file analysis
- **Connection Tracking**: TCP connection monitoring
- **Protocol Analysis**: Deep packet inspection

**API Endpoints:**
```bash
# Start packet capture
curl -X POST http://localhost:8001/api/packet/capture \
  -H 'Content-Type: application/json' \
  -d '{
    "interface": "eth0",
    "max_packets": 1000,
    "output_file": "capture.pcap"
  }'

# Analyze PCAP file
curl -X POST http://localhost:8001/api/packet/analyze \
  -H 'Content-Type: application/json' \
  -d '{"filename": "capture.pcap"}'
```

### 8. Vulnerability Scanner
**Comprehensive vulnerability assessment**

- **Exploit Database Integration**: Search known vulnerabilities
- **Automated Testing**: Vulnerability verification
- **Report Generation**: Detailed security reports
- **Risk Assessment**: Vulnerability prioritization

**API Endpoints:**
```bash
# Vulnerability scan
curl -X POST http://localhost:8001/api/vulnerability/scan \
  -H 'Content-Type: application/json' \
  -d '{"target": "192.168.1.1"}'

# Search exploits
curl -X POST http://localhost:8001/api/vulnerability/search-exploits \
  -H 'Content-Type: application/json' \
  -d '{"query": "apache struts", "platform": "web"}'
```

### 9. Advanced Reconnaissance
**OSINT and information gathering**

- **Domain Reconnaissance**: Comprehensive domain analysis
- **Subdomain Discovery**: Automated subdomain enumeration
- **Technology Detection**: Web technology identification
- **Email Harvesting**: Email address discovery
- **Social Media Discovery**: Social media account finding

**API Endpoints:**
```bash
# Domain reconnaissance
curl -X POST http://localhost:8001/api/recon/domain \
  -H 'Content-Type: application/json' \
  -d '{"domain": "example.com"}'

# Technology detection
curl -X POST http://localhost:8001/api/recon/technology-detection \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://example.com"}'
```

## 🎯 Advanced Features

### Straightforward Client-Server Communication
The platform includes comprehensive client-server communication capabilities:

- **Netcat-style Communication**: Simple TCP/UDP communication
- **Chat Servers**: Multi-client chat functionality
- **Reverse Shells**: Remote command execution
- **SOCKS Proxies**: Network tunneling and anonymization
- **WebSocket Servers**: Real-time web communication

### Network Analysis Commands
Equivalent to popular network analysis tools:

```bash
# Ping sweep (equivalent to: ping 192.168.0.1)
POST /api/network/scan {"target": "192.168.0.1", "scan_type": "ping"}

# Port scanning (equivalent to: nmap -sV 192.168.1.1)
POST /api/network/scan {"target": "192.168.1.1", "scan_type": "port"}

# Mass scanning (equivalent to: masscan -p80,443,22 10.77.14.0/24 --rate=1000)
POST /api/network/scan {"target": "10.77.14.0/24", "scan_type": "mass", "ports": [80,443,22], "rate": 1000}

# OS detection (equivalent to: nmap -O 192.168.1.1)
POST /api/network/os-detection {"target": "192.168.1.1"}
```

### Web Security Testing
Comprehensive web application security testing:

```bash
# Web vulnerability scan (equivalent to: nikto networkchuck.coffee)
POST /api/web/scan {"url": "https://example.com"}

# Directory enumeration (equivalent to: gobuster dir -u https://networkchuck.com -w wordlist.txt)
POST /api/web/directory-enumeration {"base_url": "https://example.com"}

# Subdomain enumeration (equivalent to: gobuster dns -d networkchuck.com -w dns-jhaddix.txt)
POST /api/web/subdomain-enumeration {"domain": "example.com"}

# WordPress scan (equivalent to: wpscan --url chuckkeith.com --enumerate u)
POST /api/web/wordpress-scan {"url": "https://example.com"}
```

### Packet Analysis
Advanced network traffic analysis:

```bash
# Packet capture (equivalent to: tcpdump -i eth0 -c 100)
POST /api/packet/capture {"interface": "eth0", "max_packets": 100}

# HTTP traffic capture (equivalent to: tshark -Y 'http.request.method == "GET"' -i eth0)
POST /api/packet/http-capture {"interface": "eth0"}

# PCAP analysis (equivalent to: tcpdump -r capture_file.pcap)
POST /api/packet/analyze {"filename": "capture.pcap"}
```

## 📊 Reporting & Analytics

### Report Generation
Generate comprehensive security reports:

```bash
# Network scan report
curl -X POST http://localhost:8001/api/reports/network

# Web security report
curl -X POST http://localhost:8001/api/reports/web

# Social engineering report
curl -X POST http://localhost:8001/api/reports/social

# Cryptographic analysis report
curl -X POST http://localhost:8001/api/reports/crypto

# Exploit execution report
curl -X POST http://localhost:8001/api/reports/exploit

# Reconnaissance report
curl -X POST http://localhost:8001/api/reports/recon
```

### Real-time Monitoring
Monitor active operations:

```bash
# Check service status
./check_security_status.sh

# View active connections
curl http://localhost:8001/api/connections

# Get overall status
curl http://localhost:8001/api/status
```

## 🔧 Configuration

### Environment Variables
```bash
# API Configuration
SECURITY_API_PORT=8001
FRONTEND_PORT=3000
BACKEND_PORT=3001
CRAWLER_API_PORT=8000

# Security Settings
ENABLE_LOGGING=true
LOG_LEVEL=INFO
MAX_CONCURRENT_SCANS=10
```

### Custom Wordlists
Add custom wordlists for enhanced scanning:

```bash
# Create custom wordlist directory
mkdir -p wordlists/custom

# Add your wordlists
echo "admin" >> wordlists/custom/passwords.txt
echo "password" >> wordlists/custom/passwords.txt
```

## 🛠️ Development

### Adding New Security Modules
1. Create module in `my-crawler-py/my_crawler_py/security/`
2. Add to `__init__.py` exports
3. Create API endpoints in `api_server_security.py`
4. Add frontend components in `crawl-frontend/src/app/security/`

### Custom Payloads
Extend the exploitation framework with custom payloads:

```python
from my_crawler_py.security.exploitation import ExploitPayload, ExploitType

custom_payload = ExploitPayload(
    name="Custom RCE",
    type=ExploitType.REMOTE_CODE_EXECUTION,
    target="192.168.1.1",
    payload="custom_exploit_code",
    description="Custom remote code execution",
    success_criteria="Command execution",
    risk_level="High"
)
```

## 📚 Educational Resources

### Learning Path
1. **Network Fundamentals**: Start with network scanning
2. **Web Security**: Learn web application testing
3. **Social Engineering**: Understand human factors
4. **Cryptography**: Study encryption and hashing
5. **Exploitation**: Learn vulnerability exploitation
6. **Advanced Techniques**: Master advanced security testing

### Best Practices
- Always obtain proper authorization before testing
- Document all testing activities
- Use isolated test environments
- Follow responsible disclosure practices
- Stay updated with security trends

## 🤝 Contributing

We welcome contributions to improve the security platform:

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests and documentation
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚖️ Legal Disclaimer

This software is provided for educational and authorized security testing purposes only. Users are responsible for ensuring they have proper authorization before using these tools. The developers are not liable for any misuse or illegal activities.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the API documentation at `http://localhost:8001/docs`

---

**Remember: With great power comes great responsibility. Use these tools ethically and legally.** 