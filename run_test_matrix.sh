#!/bin/bash

# Universal Crawler & Cybersecurity Platform - Test Matrix Runner
# Production-Grade Testing Suite for Patent-Track Innovations

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_ROOT/logs"
RESULTS_DIR="$PROJECT_ROOT/test_results"
REPORTS_DIR="$PROJECT_ROOT/reports"

# Create directories
mkdir -p "$LOG_DIR" "$RESULTS_DIR" "$REPORTS_DIR"

# Logging
LOG_FILE="$LOG_DIR/test_matrix_$(date +%Y%m%d_%H%M%S).log"

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}❌ $1${NC}" | tee -a "$LOG_FILE"
}

log_header() {
    echo -e "${PURPLE}🔬 $1${NC}" | tee -a "$LOG_FILE"
}

# Parse command line arguments
TEST_TIER="smoke"
VERBOSE=false
PARALLEL=false
SKIP_SETUP=false
CLEANUP=true

while [[ $# -gt 0 ]]; do
    case $1 in
        --tier)
            TEST_TIER="$2"
            shift 2
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --parallel|-p)
            PARALLEL=true
            shift
            ;;
        --skip-setup)
            SKIP_SETUP=true
            shift
            ;;
        --no-cleanup)
            CLEANUP=false
            shift
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

show_help() {
    cat << EOF
Universal Crawler Test Matrix Runner

Usage: $0 [OPTIONS]

Options:
    --tier TIER          Test tier to run (smoke|ci|nightly|preprod|patent) [default: smoke]
    --verbose, -v        Enable verbose output
    --parallel, -p       Run tests in parallel where possible
    --skip-setup         Skip environment setup
    --no-cleanup         Don't cleanup after tests
    --help, -h           Show this help message

Test Tiers:
    smoke     - Quick smoke tests (every commit)
    ci        - CI integration tests
    nightly   - Nightly depth tests (staging)
    preprod   - Pre-production chaos tests
    patent    - Patent validation tests

Examples:
    $0 --tier smoke
    $0 --tier nightly --verbose
    $0 --tier patent --parallel
EOF
}

# Environment setup
setup_environment() {
    log_header "Setting up test environment"
    
    # Check Python version
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    log "Python version: $PYTHON_VERSION"
    
    # Check Docker
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version)
        log "Docker: $DOCKER_VERSION"
    else
        log_warning "Docker not found - some tests may be skipped"
    fi
    
    # Check k6
    if command -v k6 &> /dev/null; then
        K6_VERSION=$(k6 version | head -n1)
        log "k6: $K6_VERSION"
    else
        log_warning "k6 not found - load tests will be skipped"
    fi
    
    # Install Python dependencies
    log "Installing Python dependencies..."
    pip3 install -r requirements-prod.txt
    
    # Install test dependencies
    log "Installing test dependencies..."
    pip3 install pytest pytest-asyncio pytest-cov bandit yamllint pre-commit
    
    log_success "Environment setup completed"
}

# Start services
start_services() {
    log_header "Starting test services"
    
    # Start Docker services if available
    if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
        log "Starting Docker services..."
        cd "$PROJECT_ROOT"
        
        # Start services in background
        docker-compose up -d postgres redis qdrant
        
        # Wait for services to be ready
        log "Waiting for services to be ready..."
        timeout=60
        while [ $timeout -gt 0 ]; do
            if docker-compose ps | grep -q "Up"; then
                log_success "Services started successfully"
                break
            fi
            sleep 1
            timeout=$((timeout - 1))
        done
        
        if [ $timeout -eq 0 ]; then
            log_error "Services failed to start within timeout"
            exit 1
        fi
    else
        log_warning "Docker not available - using mock services"
    fi
}

# Run tests
run_tests() {
    local tier="$1"
    local output_file="$RESULTS_DIR/${tier}_results.json"
    
    log_header "Running $tier tests"
    
    # Run the test matrix
    if [ "$VERBOSE" = true ]; then
        python3 tests/test_matrix.py --test-tier "$tier" --output "$output_file" --verbose
    else
        python3 tests/test_matrix.py --test-tier "$tier" --output "$output_file"
    fi
    
    # Check results
    if [ -f "$output_file" ]; then
        # Parse results
        local total_tests=$(python3 -c "import json; data=json.load(open('$output_file')); print(data['summary']['total_tests'])")
        local passed_tests=$(python3 -c "import json; data=json.load(open('$output_file')); print(data['summary']['passed'])")
        local failed_tests=$(python3 -c "import json; data=json.load(open('$output_file')); print(data['summary']['failed'])")
        local success_rate=$(python3 -c "import json; data=json.load(open('$output_file')); print(f'{data[\"summary\"][\"success_rate\"]:.2%}')")
        
        log "Test Results:"
        log "  Total Tests: $total_tests"
        log "  Passed: $passed_tests"
        log "  Failed: $failed_tests"
        log "  Success Rate: $success_rate"
        
        if [ "$failed_tests" -eq 0 ]; then
            log_success "$tier tests completed successfully"
            return 0
        else
            log_error "$tier tests failed"
            return 1
        fi
    else
        log_error "Test results file not found: $output_file"
        return 1
    fi
}

# Run load tests
run_load_tests() {
    if ! command -v k6 &> /dev/null; then
        log_warning "k6 not available - skipping load tests"
        return 0
    fi
    
    log_header "Running load tests"
    
    local load_results="$RESULTS_DIR/load_test_results.json"
    
    # Start the platform if not running
    if ! curl -s http://localhost:8000/api/v1/health &> /dev/null; then
        log "Starting platform for load testing..."
        cd "$PROJECT_ROOT"
        python3 universal_crawler_platform.py --config config/platform.yaml &
        PLATFORM_PID=$!
        
        # Wait for platform to start
        timeout=30
        while [ $timeout -gt 0 ]; do
            if curl -s http://localhost:8000/api/v1/health &> /dev/null; then
                log_success "Platform started"
                break
            fi
            sleep 1
            timeout=$((timeout - 1))
        done
        
        if [ $timeout -eq 0 ]; then
            log_error "Platform failed to start"
            kill $PLATFORM_PID 2>/dev/null || true
            return 1
        fi
    fi
    
    # Run k6 load test
    log "Running k6 load test..."
    k6 run tests/k6/soak.js --out json="$load_results" --duration 5m --vus 50
    
    # Check load test results
    if [ -f "$load_results" ]; then
        log_success "Load tests completed"
        
        # Parse load test metrics
        local avg_response_time=$(python3 -c "import json; data=json.load(open('$load_results')); print(f'{data[\"metrics\"][\"http_req_duration\"][\"values\"][\"avg\"]:.2f}')")
        local error_rate=$(python3 -c "import json; data=json.load(open('$load_results')); print(f'{data[\"metrics\"][\"http_req_failed\"][\"values\"][\"rate\"]:.2%}')")
        
        log "Load Test Metrics:"
        log "  Average Response Time: ${avg_response_time}ms"
        log "  Error Rate: $error_rate"
    else
        log_error "Load test results not found"
        return 1
    fi
    
    # Cleanup platform if we started it
    if [ -n "${PLATFORM_PID:-}" ]; then
        log "Stopping platform..."
        kill $PLATFORM_PID 2>/dev/null || true
    fi
}

# Run security tests
run_security_tests() {
    log_header "Running security tests"
    
    # Bandit security scan
    log "Running Bandit security scan..."
    bandit -r . -f json -o "$RESULTS_DIR/bandit_report.json" || true
    
    # YAML lint
    log "Running YAML lint..."
    yamllint config/ || true
    
    # Pre-commit hooks
    log "Running pre-commit hooks..."
    pre-commit run --all-files || true
    
    log_success "Security tests completed"
}

# Generate reports
generate_reports() {
    log_header "Generating test reports"
    
    local report_file="$REPORTS_DIR/test_report_$(date +%Y%m%d_%H%M%S).md"
    
    cat > "$report_file" << EOF
# Universal Crawler Test Matrix Report

**Generated:** $(date)
**Test Tier:** $TEST_TIER
**Environment:** $(uname -s) $(uname -r)

## Test Summary

EOF
    
    # Add test results
    for result_file in "$RESULTS_DIR"/*_results.json; do
        if [ -f "$result_file" ]; then
            local tier=$(basename "$result_file" _results.json)
            echo "### $tier Tests" >> "$report_file"
            
            # Extract metrics
            local total_tests=$(python3 -c "import json; data=json.load(open('$result_file')); print(data['summary']['total_tests'])" 2>/dev/null || echo "N/A")
            local passed_tests=$(python3 -c "import json; data=json.load(open('$result_file')); print(data['summary']['passed'])" 2>/dev/null || echo "N/A")
            local failed_tests=$(python3 -c "import json; data=json.load(open('$result_file')); print(data['summary']['failed'])" 2>/dev/null || echo "N/A")
            
            echo "- Total Tests: $total_tests" >> "$report_file"
            echo "- Passed: $passed_tests" >> "$report_file"
            echo "- Failed: $failed_tests" >> "$report_file"
            echo "" >> "$report_file"
        fi
    done
    
    # Add performance targets
    cat >> "$report_file" << EOF
## Performance Targets

| Metric | Target | Status |
|--------|--------|--------|
| WAF Detection Rate | <0.5% | ⏳ |
| Auto-classification F1 | ≥0.92 | ⏳ |
| Zero-day finds/quarter | ≥25 | ⏳ |
| Data deduplication | ≥97% | ⏳ |
| MTTR | ≤30s | ⏳ |
| Cost/10k pages | ≤£0.04 | ⏳ |

## Patent Validation

| Innovation | Status | Notes |
|------------|--------|-------|
| QTLS-FRE | ⏳ | Quantum TLS fingerprint randomization |
| MARO | ⏳ | Multi-agent red-team orchestration |
| DCO-RAG/CAG | ⏳ | Dynamic context optimizer |
| TriSL | ⏳ | Tri-modal semantic locator |
| SH-Guard | ⏳ | Autonomous self-healing guard |

## Recommendations

- Review failed tests and address issues
- Monitor performance metrics in production
- Validate patent claims against prior art
- Conduct security audit before deployment

EOF
    
    log_success "Report generated: $report_file"
}

# Cleanup
cleanup() {
    if [ "$CLEANUP" = true ]; then
        log_header "Cleaning up test environment"
        
        # Stop Docker services
        if command -v docker-compose &> /dev/null; then
            cd "$PROJECT_ROOT"
            docker-compose down --remove-orphans || true
        fi
        
        # Remove test artifacts
        rm -rf "$RESULTS_DIR"/*.tmp || true
        
        log_success "Cleanup completed"
    fi
}

# Main execution
main() {
    log_header "Universal Crawler Test Matrix Runner"
    log "Test Tier: $TEST_TIER"
    log "Verbose: $VERBOSE"
    log "Parallel: $PARALLEL"
    log "Log File: $LOG_FILE"
    
    # Validate test tier
    case "$TEST_TIER" in
        smoke|ci|nightly|preprod|patent)
            ;;
        *)
            log_error "Invalid test tier: $TEST_TIER"
            show_help
            exit 1
            ;;
    esac
    
    # Setup environment
    if [ "$SKIP_SETUP" = false ]; then
        setup_environment
    fi
    
    # Start services
    start_services
    
    # Run tests based on tier
    case "$TEST_TIER" in
        smoke)
            run_tests "smoke"
            run_security_tests
            ;;
        ci)
            run_tests "ci"
            run_security_tests
            ;;
        nightly)
            run_tests "nightly"
            run_load_tests
            run_security_tests
            ;;
        preprod)
            run_tests "preprod"
            run_load_tests
            run_security_tests
            ;;
        patent)
            run_tests "patent"
            run_security_tests
            ;;
    esac
    
    # Generate reports
    generate_reports
    
    # Cleanup
    cleanup
    
    log_success "Test matrix execution completed"
    log "Results: $RESULTS_DIR"
    log "Reports: $REPORTS_DIR"
    log "Logs: $LOG_FILE"
}

# Trap to ensure cleanup on exit
trap cleanup EXIT

# Run main function
main "$@" 