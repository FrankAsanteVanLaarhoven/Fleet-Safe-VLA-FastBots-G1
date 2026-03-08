# Universal Crawler Test Matrix Guide

## 🚀 Production-Grade Testing Suite for Patent-Track Innovations

This guide provides comprehensive documentation for the Universal Crawler & Cybersecurity Platform test matrix, designed to validate all five patent-track innovations under real-world conditions.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Test Tiers](#test-tiers)
3. [Quick Start](#quick-start)
4. [Test Scenarios](#test-scenarios)
5. [Performance Targets](#performance-targets)
6. [Patent Validation](#patent-validation)
7. [CI/CD Integration](#cicd-integration)
8. [Troubleshooting](#troubleshooting)
9. [Advanced Usage](#advanced-usage)

## 🎯 Overview

The Universal Crawler Test Matrix is a world-class testing framework that validates every layer of the universal crawler, data-locator, and quantum-stealth security stack. It provides:

- **Five-tier testing strategy** from smoke tests to patent validation
- **Performance benchmarking** against industry-leading targets
- **Patent validation** for all five core innovations
- **Security scanning** and compliance checking
- **Load testing** with k6 and chaos engineering
- **Automated reporting** and metrics collection

### Five Patent-Track Innovations Tested

1. **Quantum TLS Fingerprint Randomization Engine (QTLS-FRE)**
2. **Multi-Agent Red-Team Orchestrator (MARO)**
3. **Dynamic Context Optimizer for Hybrid RAG-CAG (DCO-RAG/CAG)**
4. **Tri-Modal Semantic Locator (TriSL)**
5. **Autonomous Self-Healing Guard (SH-Guard)**

## 🏗️ Test Tiers

### 1. Smoke Tests (Every Commit)
**Purpose:** Quick validation of core functionality
**Duration:** 2-5 minutes
**Frequency:** Every commit and pull request

```bash
./run_test_matrix.sh --tier smoke
```

**Tests Included:**
- Lint & static security analysis
- Unit tests with coverage
- Quantum TLS fingerprint sanity
- Template schema validation

**Success Criteria:**
- No high-severity security findings
- ≥90% code coverage
- All unit tests pass
- Schema validation passes

### 2. CI Integration Tests
**Purpose:** Validate integration between components
**Duration:** 10-15 minutes
**Frequency:** Every push to main/develop

```bash
./run_test_matrix.sh --tier ci
```

**Tests Included:**
- Framework matrix testing (Playwright, Selenium, Puppeteer)
- Data-locator tri-hash collision testing
- Self-healing guard injection testing
- Database integration tests

**Success Criteria:**
- All frameworks functional
- <0.1% hash collision rate
- Self-healing triggers correctly
- Database operations successful

### 3. Nightly Depth Tests (Staging)
**Purpose:** Comprehensive validation under load
**Duration:** 30-60 minutes
**Frequency:** Daily at 2 AM UTC

```bash
./run_test_matrix.sh --tier nightly
```

**Tests Included:**
- WAF evasion testing
- Load testing with k6
- Zero-day vulnerability discovery
- Data pipeline quality validation

**Success Criteria:**
- <0.5% WAF detection rate
- 95% of requests under 2s
- Zero-day discovery functional
- Data quality metrics met

### 4. Pre-Production Chaos Tests
**Purpose:** Validate resilience and recovery
**Duration:** 60-120 minutes
**Frequency:** Weekly or before major releases

```bash
./run_test_matrix.sh --tier preprod
```

**Tests Included:**
- Multi-cloud fail-over testing
- Data loss protection validation
- Red-team loop testing
- Regulatory compliance scanning

**Success Criteria:**
- <90s fail-over recovery
- Data protection mechanisms active
- Auto-patching functional
- Zero critical compliance gaps

### 5. Patent Validation Tests
**Purpose:** Validate patent-track innovations
**Duration:** 30-60 minutes
**Frequency:** Monthly or before patent filings

```bash
./run_test_matrix.sh --tier patent
```

**Tests Included:**
- QTLS-FRE fingerprint diffusion testing
- TriSL uniqueness validation
- DCO-RAG/CAG decision latency testing
- SH-Guard recovery time validation

**Success Criteria:**
- <0.1% fingerprint collision rate
- <0.3% duplicate rate
- ≤50ms decision latency
- ≤30s mean time to recovery

## 🚀 Quick Start

### Prerequisites

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y python3 python3-pip docker.io docker-compose

# Install k6 for load testing
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6
```

### Basic Usage

```bash
# Run smoke tests
./run_test_matrix.sh --tier smoke

# Run with verbose output
./run_test_matrix.sh --tier nightly --verbose

# Run patent validation
./run_test_matrix.sh --tier patent --parallel

# Skip setup (if environment already configured)
./run_test_matrix.sh --tier ci --skip-setup
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--tier TIER` | Test tier to run | `smoke` |
| `--verbose, -v` | Enable verbose output | `false` |
| `--parallel, -p` | Run tests in parallel | `false` |
| `--skip-setup` | Skip environment setup | `false` |
| `--no-cleanup` | Don't cleanup after tests | `false` |
| `--help, -h` | Show help message | - |

## 🧪 Test Scenarios

### WAF Evasion Testing

```bash
# Test against known WAF-protected sites
python tests/test_matrix.py --test-tier nightly --output waf_results.json

# Validate WAF evasion metrics
python -c "
import json
with open('waf_results.json') as f:
    results = json.load(f)
for test in results['detailed_results']:
    if test['test_name'] == 'waf_evasion':
        block_rate = test['metrics']['block_rate']
        print(f'WAF Block Rate: {block_rate:.2%}')
        assert block_rate < 0.005, 'WAF block rate too high'
"
```

### Load Testing with k6

```bash
# Run k6 load test
k6 run tests/k6/soak.js --vus 100 --duration 10m

# Custom load test
k6 run tests/k6/soak.js \
  --env BASE_URL=http://localhost:8000 \
  --env API_TOKEN=your-token \
  --vus 200 \
  --duration 30m
```

### Chaos Engineering

```bash
# Simulate cloud failure
gremlin cpu spike --length 300 --hosts tag=region:eu-west-1

# Test data loss protection
aws s3 rm s3://lake/bronze/ --recursive --dryrun

# Validate recovery
python tests/chaos_engineering.py
```

## 📊 Performance Targets

### Core Performance Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| WAF Detection Rate | <0.5% | Blocked requests / Total requests |
| Auto-classification F1 | ≥0.92 | Precision × Recall / (Precision + Recall) |
| Zero-day finds/quarter | ≥25 | Unique vulnerabilities discovered |
| Data deduplication | ≥97% | Unique documents / Total documents |
| MTTR | ≤30s | Mean time to recovery |
| Cost/10k pages | ≤£0.04 | Infrastructure cost per 10k pages |

### Load Testing Thresholds

| Metric | Threshold | k6 Configuration |
|--------|-----------|------------------|
| Response Time (95th percentile) | <2s | `p(95)<2000` |
| Error Rate | <5% | `rate<0.05` |
| Crawl Success Rate | >95% | `rate>0.95` |
| WAF Block Rate | <0.5% | `rate<0.005` |

### Patent Validation Criteria

| Innovation | Test | Success Criteria |
|------------|------|------------------|
| QTLS-FRE | Fingerprint collision | <0.1% collision rate |
| TriSL | Uniqueness | <0.3% duplicate rate |
| DCO-RAG/CAG | Decision latency | ≤50ms average |
| SH-Guard | Recovery time | ≤30s MTTR |

## 🔬 Patent Validation

### QTLS-FRE Validation

```python
# Test quantum entropy generation
async def test_quantum_entropy():
    engine = QuantumTLSFingerprintEngine()
    entropy = await engine.generate_quantum_entropy(256)
    assert len(entropy) == 256
    assert entropy.hex() != '0' * 64  # Not all zeros

# Test fingerprint diffusion
async def test_fingerprint_diffusion():
    fingerprints = []
    for _ in range(1000):
        session = await engine.build_session("example.com", "high")
        fingerprint = await engine.generate_fingerprint(session)
        fingerprints.append(fingerprint)
    
    unique_fingerprints = set(fingerprints)
    collision_rate = 1 - (len(unique_fingerprints) / len(fingerprints))
    assert collision_rate < 0.001  # <0.1% collision rate
```

### TriSL Validation

```python
# Test tri-modal hashing
async def test_tri_modal_hashing():
    locator = TriModalSemanticLocator()
    
    # Test different content types
    test_data = [
        "Sample text for hashing",
        "Another sample text",
        "Completely different content"
    ]
    
    hashes = []
    for data in test_data:
        tri_hash = await locator.generate_composite_fingerprint(data)
        hashes.append(tri_hash)
    
    # Verify uniqueness
    unique_hashes = set(hashes)
    duplicate_rate = 1 - (len(unique_hashes) / len(hashes))
    assert duplicate_rate < 0.003  # <0.3% duplicate rate
```

### DCO-RAG/CAG Validation

```python
# Test decision latency
async def test_decision_latency():
    optimizer = DynamicContextOptimizer()
    
    latencies = []
    for _ in range(100):
        start_time = time.time()
        await optimizer.optimize_context(["https://example.com"], "technology")
        latency = time.time() - start_time
        latencies.append(latency)
    
    avg_latency = statistics.mean(latencies)
    assert avg_latency < 0.05  # <50ms average
```

### SH-Guard Validation

```python
# Test recovery time
async def test_recovery_time():
    guard = SelfHealingGuard()
    
    recovery_times = []
    for _ in range(50):
        start_time = time.time()
        await guard.simulate_threat_injection()
        recovery_time = time.time() - start_time
        recovery_times.append(recovery_time)
    
    avg_recovery_time = statistics.mean(recovery_times)
    assert avg_recovery_time < 30  # <30s average
```

## 🔄 CI/CD Integration

### GitHub Actions Workflow

The test matrix is integrated into GitHub Actions with the following workflow:

```yaml
# .github/workflows/test-matrix.yml
name: Universal Crawler Test Matrix

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * *'  # Nightly at 2 AM UTC
  workflow_dispatch:
    inputs:
      test_tier:
        description: 'Test tier to run'
        required: true
        default: 'smoke'
        type: choice
        options:
        - smoke
        - ci
        - nightly
        - preprod
        - patent
```

### Automated Testing Triggers

| Event | Test Tier | Purpose |
|-------|-----------|---------|
| Push to main/develop | smoke + ci | Validate changes |
| Pull request | smoke + ci | Pre-merge validation |
| Scheduled (daily) | nightly | Comprehensive testing |
| Manual trigger | Any tier | On-demand testing |

### Test Results Integration

```bash
# Check test results in CI
python -c "
import json
with open('test_results.json') as f:
    results = json.load(f)
if results['summary']['failed'] > 0:
    print('❌ Tests failed')
    exit(1)
print('✅ All tests passed')
"

# Generate test summary
python tests/generate_test_summary.py test_results.json
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Service Startup Failures

```bash
# Check Docker services
docker-compose ps
docker-compose logs postgres
docker-compose logs redis

# Restart services
docker-compose down
docker-compose up -d
```

#### 2. Test Timeout Issues

```bash
# Increase timeout for long-running tests
export TEST_TIMEOUT=300
./run_test_matrix.sh --tier nightly --verbose

# Check system resources
htop
df -h
free -h
```

#### 3. Performance Test Failures

```bash
# Check system load during tests
sar -u 1 60  # CPU usage
sar -r 1 60  # Memory usage
iostat 1 60  # Disk I/O

# Adjust k6 parameters
k6 run tests/k6/soak.js --vus 50 --duration 5m  # Reduce load
```

#### 4. Patent Validation Failures

```bash
# Check quantum entropy source
python -c "
from quantum_tls_engine import QuantumTLSFingerprintEngine
engine = QuantumTLSFingerprintEngine()
print('Quantum device:', engine.quantum_device)
print('Entropy available:', engine.check_entropy_availability())
"

# Verify ML model availability
python -c "
import torch
print('PyTorch version:', torch.__version__)
print('CUDA available:', torch.cuda.is_available())
"
```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
./run_test_matrix.sh --tier smoke --verbose

# Check detailed logs
tail -f logs/test_matrix_*.log
```

### Performance Profiling

```bash
# Profile Python tests
python -m cProfile -o profile.stats tests/test_matrix.py --test-tier smoke

# Analyze profile
python -c "
import pstats
p = pstats.Stats('profile.stats')
p.sort_stats('cumulative').print_stats(20)
"
```

## 🔧 Advanced Usage

### Custom Test Configuration

```yaml
# config/test_config.yaml
test_matrix:
  smoke:
    timeout: 300
    parallel: false
    services: []
  
  nightly:
    timeout: 3600
    parallel: true
    services: [postgres, redis, qdrant, prometheus, grafana]
  
  patent:
    timeout: 2400
    parallel: false
    services: [postgres, redis, qdrant]
    ml_models: true
```

### Custom Load Test Scenarios

```javascript
// tests/k6/custom_scenario.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '1m', target: 50 },   // Ramp up
    { duration: '3m', target: 50 },   // Steady state
    { duration: '1m', target: 100 },  // Spike
    { duration: '3m', target: 100 },  // High load
    { duration: '1m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<1500'],  // Stricter threshold
    http_req_failed: ['rate<0.02'],     // Lower error rate
  },
};

export default function () {
  // Custom test logic
  const response = http.get('http://localhost:8000/api/v1/health');
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
  sleep(1);
}
```

### Custom Patent Validation

```python
# tests/custom_patent_validation.py
import asyncio
from quantum_tls_engine import QuantumTLSFingerprintEngine

async def custom_qtls_validation():
    """Custom QTLS-FRE validation for specific use case"""
    engine = QuantumTLSFingerprintEngine()
    
    # Test specific stealth levels
    stealth_levels = ['low', 'medium', 'high', 'extreme']
    
    for level in stealth_levels:
        session = await engine.build_session("example.com", level)
        fingerprint = await engine.generate_fingerprint(session)
        
        # Custom validation logic
        assert len(fingerprint) >= 64, f"Fingerprint too short for {level}"
        assert fingerprint != '0' * 64, f"Zero fingerprint for {level}"
        
        print(f"✅ {level} stealth level validated")

if __name__ == "__main__":
    asyncio.run(custom_qtls_validation())
```

### Integration with External Tools

```bash
# Integrate with Prometheus
curl -X POST http://localhost:9090/api/v1/admin/tsdb/snapshot

# Export metrics to Grafana
curl -X POST http://localhost:3000/api/datasources \
  -H "Content-Type: application/json" \
  -d '{"name":"Prometheus","type":"prometheus","url":"http://prometheus:9090"}'

# Send alerts to Slack
curl -X POST $SLACK_WEBHOOK_URL \
  -H "Content-Type: application/json" \
  -d '{"text":"Test matrix completed with results"}'
```

## 📈 Monitoring and Metrics

### Key Performance Indicators (KPIs)

```python
# Monitor KPI targets
kpis = {
    "waf_detection_rate": 0.005,      # <0.5%
    "autonomous_branch_accuracy": 0.98, # >98%
    "context_switch_latency": 0.05,   # ≤50ms
    "deduplication_hit_rate": 0.97,   # >97%
    "mttr_seconds": 30.0,             # <30s
    "cost_per_10k_pages": 0.04        # ≤£0.04
}

# Validate KPI compliance
def validate_kpis(test_results):
    for kpi, target in kpis.items():
        actual = test_results.get(kpi, 0)
        if actual > target:
            print(f"❌ {kpi}: {actual} > {target}")
        else:
            print(f"✅ {kpi}: {actual} ≤ {target}")
```

### Continuous Monitoring

```bash
# Set up continuous monitoring
crontab -e

# Add monitoring job
0 */6 * * * /path/to/run_test_matrix.sh --tier smoke --no-cleanup

# Monitor test results
watch -n 60 'tail -n 20 logs/test_matrix_*.log'
```

## 🎯 Conclusion

The Universal Crawler Test Matrix provides comprehensive validation of all five patent-track innovations, ensuring:

- **Patent-grade validation** of novel technical approaches
- **Production readiness** through extensive testing
- **Performance benchmarking** against industry targets
- **Security validation** and compliance checking
- **Automated testing** with CI/CD integration

This testing framework sets a new benchmark for universal crawlers and multi-agent security platforms, providing the confidence needed for patent filings and production deployment.

For questions or support, refer to the project documentation or contact the development team. 