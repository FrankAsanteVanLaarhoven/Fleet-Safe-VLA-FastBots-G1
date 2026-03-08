#!/bin/bash

# QuantumOps AI Enterprise - World Leading Test Suite
# Comprehensive testing automation for the frontend application

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$PROJECT_DIR"
REPORTS_DIR="$PROJECT_DIR/test-reports"
COVERAGE_DIR="$PROJECT_DIR/coverage"
PERFORMANCE_DIR="$PROJECT_DIR/performance-reports"

# Test configuration
NODE_VERSION="18"
CHROME_VERSION="latest"
FIREFOX_VERSION="latest"
SAFARI_VERSION="latest"

# Performance thresholds
LIGHTHOUSE_PERFORMANCE=90
LIGHTHOUSE_ACCESSIBILITY=95
LIGHTHOUSE_BEST_PRACTICES=95
LIGHTHOUSE_SEO=90

# Load testing configuration
K6_VUS=100
K6_DURATION="5m"

# Logging
LOG_FILE="$PROJECT_DIR/test-suite.log"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# Functions
log() {
    echo -e "${BLUE}[$TIMESTAMP]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}✅ $1${NC}" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}❌ $1${NC}" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${CYAN}ℹ️  $1${NC}" | tee -a "$LOG_FILE"
}

header() {
    echo -e "${PURPLE}🚀 $1${NC}" | tee -a "$LOG_FILE"
}

# Initialize test environment
init_test_environment() {
    header "Initializing QuantumOps AI Enterprise Test Environment"
    
    # Create directories
    mkdir -p "$REPORTS_DIR"
    mkdir -p "$COVERAGE_DIR"
    mkdir -p "$PERFORMANCE_DIR"
    
    # Check Node.js version
    if ! command -v node &> /dev/null; then
        error "Node.js is not installed. Please install Node.js $NODE_VERSION or higher."
        exit 1
    fi
    
    NODE_CURRENT=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_CURRENT" -lt "$NODE_VERSION" ]; then
        error "Node.js version $NODE_VERSION or higher is required. Current version: $(node --version)"
        exit 1
    fi
    
    success "Node.js version check passed: $(node --version)"
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        error "npm is not installed."
        exit 1
    fi
    
    success "npm version: $(npm --version)"
    
    # Install dependencies
    log "Installing project dependencies..."
    cd "$FRONTEND_DIR"
    npm ci --silent
    
    # Install testing dependencies
    log "Installing testing dependencies..."
    npm install --save-dev @testing-library/react @testing-library/jest-dom jest cypress @testing-library/cypress lighthouse k6 @axe-core/react pa11y-ci --silent
    
    success "Test environment initialized successfully"
}

# Run unit tests
run_unit_tests() {
    header "Running Unit Tests"
    
    cd "$FRONTEND_DIR"
    
    log "Running Jest unit tests with coverage..."
    npm test -- --coverage --watchAll=false --passWithNoTests --silent > "$REPORTS_DIR/unit-tests.log" 2>&1
    
    if [ $? -eq 0 ]; then
        success "Unit tests completed successfully"
        
        # Check coverage
        COVERAGE_SUMMARY=$(cat "$REPORTS_DIR/unit-tests.log" | grep -A 10 "All files" | tail -n 10)
        log "Coverage Summary:\n$COVERAGE_SUMMARY"
        
        # Extract coverage percentages
        STATEMENTS=$(echo "$COVERAGE_SUMMARY" | grep "Statements" | grep -o '[0-9.]*%' | head -1)
        BRANCHES=$(echo "$COVERAGE_SUMMARY" | grep "Branches" | grep -o '[0-9.]*%' | head -1)
        FUNCTIONS=$(echo "$COVERAGE_SUMMARY" | grep "Functions" | grep -o '[0-9.]*%' | head -1)
        LINES=$(echo "$COVERAGE_SUMMARY" | grep "Lines" | grep -o '[0-9.]*%' | head -1)
        
        log "Coverage Results:"
        log "  Statements: $STATEMENTS"
        log "  Branches: $BRANCHES"
        log "  Functions: $FUNCTIONS"
        log "  Lines: $LINES"
        
    else
        error "Unit tests failed. Check $REPORTS_DIR/unit-tests.log for details"
        return 1
    fi
}

# Run integration tests
run_integration_tests() {
    header "Running Integration Tests"
    
    cd "$FRONTEND_DIR"
    
    log "Starting development server for integration tests..."
    npm run dev &
    DEV_SERVER_PID=$!
    
    # Wait for server to start
    sleep 10
    
    log "Running Cypress integration tests..."
    npx cypress run --headless --config video=false --screenshots=false > "$REPORTS_DIR/integration-tests.log" 2>&1
    
    INTEGRATION_RESULT=$?
    
    # Stop development server
    kill $DEV_SERVER_PID 2>/dev/null || true
    
    if [ $INTEGRATION_RESULT -eq 0 ]; then
        success "Integration tests completed successfully"
    else
        error "Integration tests failed. Check $REPORTS_DIR/integration-tests.log for details"
        return 1
    fi
}

# Run E2E tests
run_e2e_tests() {
    header "Running End-to-End Tests"
    
    cd "$FRONTEND_DIR"
    
    log "Starting development server for E2E tests..."
    npm run dev &
    DEV_SERVER_PID=$!
    
    # Wait for server to start
    sleep 10
    
    log "Running Playwright E2E tests..."
    npx playwright test --reporter=html > "$REPORTS_DIR/e2e-tests.log" 2>&1
    
    E2E_RESULT=$?
    
    # Stop development server
    kill $DEV_SERVER_PID 2>/dev/null || true
    
    if [ $E2E_RESULT -eq 0 ]; then
        success "E2E tests completed successfully"
    else
        error "E2E tests failed. Check $REPORTS_DIR/e2e-tests.log for details"
        return 1
    fi
}

# Run performance tests
run_performance_tests() {
    header "Running Performance Tests"
    
    cd "$FRONTEND_DIR"
    
    log "Starting development server for performance tests..."
    npm run dev &
    DEV_SERVER_PID=$!
    
    # Wait for server to start
    sleep 10
    
    # Lighthouse performance audit
    log "Running Lighthouse performance audit..."
    npx lighthouse http://localhost:3000 --output=html --output-path="$PERFORMANCE_DIR/lighthouse-report.html" --chrome-flags="--headless" > "$PERFORMANCE_DIR/lighthouse.log" 2>&1
    
    # Extract Lighthouse scores
    PERFORMANCE_SCORE=$(grep -o '"performance": [0-9]*' "$PERFORMANCE_DIR/lighthouse.log" | grep -o '[0-9]*' || echo "0")
    ACCESSIBILITY_SCORE=$(grep -o '"accessibility": [0-9]*' "$PERFORMANCE_DIR/lighthouse.log" | grep -o '[0-9]*' || echo "0")
    BEST_PRACTICES_SCORE=$(grep -o '"best-practices": [0-9]*' "$PERFORMANCE_DIR/lighthouse.log" | grep -o '[0-9]*' || echo "0")
    SEO_SCORE=$(grep -o '"seo": [0-9]*' "$PERFORMANCE_DIR/lighthouse.log" | grep -o '[0-9]*' || echo "0")
    
    log "Lighthouse Scores:"
    log "  Performance: $PERFORMANCE_SCORE/100"
    log "  Accessibility: $ACCESSIBILITY_SCORE/100"
    log "  Best Practices: $BEST_PRACTICES_SCORE/100"
    log "  SEO: $SEO_SCORE/100"
    
    # Check performance thresholds
    if [ "$PERFORMANCE_SCORE" -lt "$LIGHTHOUSE_PERFORMANCE" ]; then
        warning "Performance score ($PERFORMANCE_SCORE) is below threshold ($LIGHTHOUSE_PERFORMANCE)"
    fi
    
    if [ "$ACCESSIBILITY_SCORE" -lt "$LIGHTHOUSE_ACCESSIBILITY" ]; then
        warning "Accessibility score ($ACCESSIBILITY_SCORE) is below threshold ($LIGHTHOUSE_ACCESSIBILITY)"
    fi
    
    # Bundle size analysis
    log "Analyzing bundle size..."
    npm run build > "$PERFORMANCE_DIR/build.log" 2>&1
    
    # Extract bundle sizes
    BUNDLE_SIZE=$(du -sh .next/static/js/*.js | tail -1 | cut -f1)
    log "Bundle size: $BUNDLE_SIZE"
    
    # Stop development server
    kill $DEV_SERVER_PID 2>/dev/null || true
    
    success "Performance tests completed"
}

# Run accessibility tests
run_accessibility_tests() {
    header "Running Accessibility Tests"
    
    cd "$FRONTEND_DIR"
    
    log "Starting development server for accessibility tests..."
    npm run dev &
    DEV_SERVER_PID=$!
    
    # Wait for server to start
    sleep 10
    
    # Run axe-core tests
    log "Running axe-core accessibility tests..."
    npx pa11y-ci http://localhost:3000 > "$REPORTS_DIR/accessibility-tests.log" 2>&1
    
    ACCESSIBILITY_RESULT=$?
    
    # Stop development server
    kill $DEV_SERVER_PID 2>/dev/null || true
    
    if [ $ACCESSIBILITY_RESULT -eq 0 ]; then
        success "Accessibility tests completed successfully"
    else
        warning "Accessibility issues found. Check $REPORTS_DIR/accessibility-tests.log for details"
    fi
}

# Run load tests
run_load_tests() {
    header "Running Load Tests"
    
    cd "$FRONTEND_DIR"
    
    log "Starting development server for load tests..."
    npm run dev &
    DEV_SERVER_PID=$!
    
    # Wait for server to start
    sleep 10
    
    # Create k6 test script
    cat > "$FRONTEND_DIR/load-test.js" << 'EOF'
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 50 },
    { duration: '5m', target: 100 },
    { duration: '2m', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],
    http_req_failed: ['rate<0.1'],
  },
};

export default function () {
  const response = http.get('http://localhost:3000');
  
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
  
  sleep(1);
}
EOF
    
    log "Running k6 load tests..."
    k6 run load-test.js > "$PERFORMANCE_DIR/load-test.log" 2>&1
    
    LOAD_RESULT=$?
    
    # Clean up
    rm -f "$FRONTEND_DIR/load-test.js"
    
    # Stop development server
    kill $DEV_SERVER_PID 2>/dev/null || true
    
    if [ $LOAD_RESULT -eq 0 ]; then
        success "Load tests completed successfully"
    else
        error "Load tests failed. Check $PERFORMANCE_DIR/load-test.log for details"
        return 1
    fi
}

# Run security tests
run_security_tests() {
    header "Running Security Tests"
    
    cd "$FRONTEND_DIR"
    
    # Dependency vulnerability scan
    log "Scanning for dependency vulnerabilities..."
    npm audit --audit-level=moderate > "$REPORTS_DIR/security-audit.log" 2>&1
    
    AUDIT_RESULT=$?
    
    if [ $AUDIT_RESULT -eq 0 ]; then
        success "Security audit passed - no high or moderate vulnerabilities found"
    else
        warning "Security vulnerabilities found. Check $REPORTS_DIR/security-audit.log for details"
    fi
    
    # Content Security Policy test
    log "Testing Content Security Policy..."
    curl -I http://localhost:3000 2>/dev/null | grep -i "content-security-policy" > "$REPORTS_DIR/csp-test.log" 2>&1 || true
    
    if [ -s "$REPORTS_DIR/csp-test.log" ]; then
        success "Content Security Policy is configured"
    else
        warning "Content Security Policy not detected"
    fi
}

# Generate test report
generate_test_report() {
    header "Generating Comprehensive Test Report"
    
    REPORT_FILE="$REPORTS_DIR/test-report-$(date +%Y%m%d-%H%M%S).md"
    
    cat > "$REPORT_FILE" << EOF
# QuantumOps AI Enterprise - Test Report
Generated: $(date)

## Test Summary

### Unit Tests
- Status: $(if [ -f "$REPORTS_DIR/unit-tests.log" ] && grep -q "Test Suites:.*passed" "$REPORTS_DIR/unit-tests.log"; then echo "✅ PASSED"; else echo "❌ FAILED"; fi)
- Coverage: $(if [ -f "$REPORTS_DIR/unit-tests.log" ]; then grep -A 1 "All files" "$REPORTS_DIR/unit-tests.log" | tail -1; else echo "N/A"; fi)

### Integration Tests
- Status: $(if [ -f "$REPORTS_DIR/integration-tests.log" ] && grep -q "cypress:run.*Done in" "$REPORTS_DIR/integration-tests.log"; then echo "✅ PASSED"; else echo "❌ FAILED"; fi)

### E2E Tests
- Status: $(if [ -f "$REPORTS_DIR/e2e-tests.log" ] && grep -q "passed" "$REPORTS_DIR/e2e-tests.log"; then echo "✅ PASSED"; else echo "❌ FAILED"; fi)

### Performance Tests
- Lighthouse Performance: ${PERFORMANCE_SCORE:-N/A}/100
- Lighthouse Accessibility: ${ACCESSIBILITY_SCORE:-N/A}/100
- Lighthouse Best Practices: ${BEST_PRACTICES_SCORE:-N/A}/100
- Lighthouse SEO: ${SEO_SCORE:-N/A}/100
- Bundle Size: ${BUNDLE_SIZE:-N/A}

### Accessibility Tests
- Status: $(if [ -f "$REPORTS_DIR/accessibility-tests.log" ] && grep -q "passed" "$REPORTS_DIR/accessibility-tests.log"; then echo "✅ PASSED"; else echo "⚠️  ISSUES FOUND"; fi)

### Load Tests
- Status: $(if [ -f "$PERFORMANCE_DIR/load-test.log" ] && grep -q "checks.*100.00%" "$PERFORMANCE_DIR/load-test.log"; then echo "✅ PASSED"; else echo "❌ FAILED"; fi)

### Security Tests
- Dependency Audit: $(if [ -f "$REPORTS_DIR/security-audit.log" ] && grep -q "found 0 vulnerabilities" "$REPORTS_DIR/security-audit.log"; then echo "✅ PASSED"; else echo "⚠️  VULNERABILITIES FOUND"; fi)
- CSP Configuration: $(if [ -s "$REPORTS_DIR/csp-test.log" ]; then echo "✅ CONFIGURED"; else echo "⚠️  NOT DETECTED"; fi)

## Detailed Results

### Unit Test Coverage
\`\`\`
$(if [ -f "$REPORTS_DIR/unit-tests.log" ]; then grep -A 10 "All files" "$REPORTS_DIR/unit-tests.log"; else echo "No unit test results available"; fi)
\`\`\`

### Performance Metrics
- First Contentful Paint: $(if [ -f "$PERFORMANCE_DIR/lighthouse.log" ]; then grep -o '"first-contentful-paint": [0-9]*' "$PERFORMANCE_DIR/lighthouse.log" | grep -o '[0-9]*' || echo "N/A"; fi)ms
- Largest Contentful Paint: $(if [ -f "$PERFORMANCE_DIR/lighthouse.log" ]; then grep -o '"largest-contentful-paint": [0-9]*' "$PERFORMANCE_DIR/lighthouse.log" | grep -o '[0-9]*' || echo "N/A"; fi)ms
- Cumulative Layout Shift: $(if [ -f "$PERFORMANCE_DIR/lighthouse.log" ]; then grep -o '"cumulative-layout-shift": [0-9.]*' "$PERFORMANCE_DIR/lighthouse.log" | grep -o '[0-9.]*' || echo "N/A"; fi)

## Recommendations

$(if [ "$PERFORMANCE_SCORE" -lt "$LIGHTHOUSE_PERFORMANCE" ]; then echo "- ⚠️  Performance optimization needed"; fi)
$(if [ "$ACCESSIBILITY_SCORE" -lt "$LIGHTHOUSE_ACCESSIBILITY" ]; then echo "- ⚠️  Accessibility improvements required"; fi)
$(if [ -f "$REPORTS_DIR/security-audit.log" ] && grep -q "found [1-9]" "$REPORTS_DIR/security-audit.log"; then echo "- 🔒 Security vulnerabilities need to be addressed"; fi)

## Next Steps

1. Review failed tests and fix issues
2. Address performance bottlenecks
3. Implement accessibility improvements
4. Update dependencies with security vulnerabilities
5. Monitor performance in production

---
*Generated by QuantumOps AI Enterprise Test Suite*
EOF
    
    success "Test report generated: $REPORT_FILE"
    
    # Display summary
    echo ""
    header "Test Suite Summary"
    echo "📊 Unit Tests: $(if [ -f "$REPORTS_DIR/unit-tests.log" ] && grep -q "Test Suites:.*passed" "$REPORTS_DIR/unit-tests.log"; then echo "✅ PASSED"; else echo "❌ FAILED"; fi)"
    echo "🔗 Integration Tests: $(if [ -f "$REPORTS_DIR/integration-tests.log" ] && grep -q "cypress:run.*Done in" "$REPORTS_DIR/integration-tests.log"; then echo "✅ PASSED"; else echo "❌ FAILED"; fi)"
    echo "🌐 E2E Tests: $(if [ -f "$REPORTS_DIR/e2e-tests.log" ] && grep -q "passed" "$REPORTS_DIR/e2e-tests.log"; then echo "✅ PASSED"; else echo "❌ FAILED"; fi)"
    echo "⚡ Performance: ${PERFORMANCE_SCORE:-N/A}/100"
    echo "♿ Accessibility: ${ACCESSIBILITY_SCORE:-N/A}/100"
    echo "🔒 Security: $(if [ -f "$REPORTS_DIR/security-audit.log" ] && grep -q "found 0 vulnerabilities" "$REPORTS_DIR/security-audit.log"; then echo "✅ PASSED"; else echo "⚠️  ISSUES"; fi)"
    echo ""
    echo "📄 Detailed report: $REPORT_FILE"
}

# Main execution
main() {
    header "QuantumOps AI Enterprise - World Leading Test Suite"
    log "Starting comprehensive test execution..."
    
    # Initialize environment
    init_test_environment
    
    # Run all test suites
    TESTS_PASSED=0
    TESTS_FAILED=0
    
    # Unit tests
    if run_unit_tests; then
        ((TESTS_PASSED++))
    else
        ((TESTS_FAILED++))
    fi
    
    # Integration tests
    if run_integration_tests; then
        ((TESTS_PASSED++))
    else
        ((TESTS_FAILED++))
    fi
    
    # E2E tests
    if run_e2e_tests; then
        ((TESTS_PASSED++))
    else
        ((TESTS_FAILED++))
    fi
    
    # Performance tests
    if run_performance_tests; then
        ((TESTS_PASSED++))
    else
        ((TESTS_FAILED++))
    fi
    
    # Accessibility tests
    if run_accessibility_tests; then
        ((TESTS_PASSED++))
    else
        ((TESTS_FAILED++))
    fi
    
    # Load tests
    if run_load_tests; then
        ((TESTS_PASSED++))
    else
        ((TESTS_FAILED++))
    fi
    
    # Security tests
    if run_security_tests; then
        ((TESTS_PASSED++))
    else
        ((TESTS_FAILED++))
    fi
    
    # Generate report
    generate_test_report
    
    # Final summary
    echo ""
    header "Test Suite Execution Complete"
    echo "✅ Tests Passed: $TESTS_PASSED"
    echo "❌ Tests Failed: $TESTS_FAILED"
    echo "📊 Success Rate: $((TESTS_PASSED * 100 / (TESTS_PASSED + TESTS_FAILED)))%"
    
    if [ $TESTS_FAILED -eq 0 ]; then
        success "All test suites completed successfully! 🎉"
        exit 0
    else
        error "Some test suites failed. Please review the reports and fix issues."
        exit 1
    fi
}

# Handle script arguments
case "${1:-}" in
    "unit")
        init_test_environment
        run_unit_tests
        ;;
    "integration")
        init_test_environment
        run_integration_tests
        ;;
    "e2e")
        init_test_environment
        run_e2e_tests
        ;;
    "performance")
        init_test_environment
        run_performance_tests
        ;;
    "accessibility")
        init_test_environment
        run_accessibility_tests
        ;;
    "load")
        init_test_environment
        run_load_tests
        ;;
    "security")
        init_test_environment
        run_security_tests
        ;;
    "report")
        generate_test_report
        ;;
    "help"|"-h"|"--help")
        echo "QuantumOps AI Enterprise - World Leading Test Suite"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  unit          Run unit tests only"
        echo "  integration   Run integration tests only"
        echo "  e2e          Run end-to-end tests only"
        echo "  performance  Run performance tests only"
        echo "  accessibility Run accessibility tests only"
        echo "  load         Run load tests only"
        echo "  security     Run security tests only"
        echo "  report       Generate test report only"
        echo "  help         Show this help message"
        echo ""
        echo "If no command is specified, all tests will be run."
        exit 0
        ;;
    *)
        main
        ;;
esac 