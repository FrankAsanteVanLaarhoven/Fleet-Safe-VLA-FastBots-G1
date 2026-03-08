import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Custom metrics
const crawlSuccessRate = new Rate('crawl_success_rate');
const crawlDuration = new Trend('crawl_duration');
const wafBlockRate = new Rate('waf_block_rate');
const dataExtractionRate = new Rate('data_extraction_rate');

// Test configuration
export const options = {
  stages: [
    { duration: '2m', target: 100 },  // Ramp up
    { duration: '5m', target: 100 },  // Steady load
    { duration: '2m', target: 200 },  // Spike test
    { duration: '5m', target: 200 },  // High load
    { duration: '2m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'],  // 95% of requests under 2s
    http_req_failed: ['rate<0.05'],     // Less than 5% failed requests
    crawl_success_rate: ['rate>0.95'],  // 95% crawl success rate
    waf_block_rate: ['rate<0.005'],     // Less than 0.5% WAF blocks
  },
};

// Test data
const testUrls = [
  'https://example.com',
  'https://test-site.com',
  'https://demo-app.com',
  'https://sample-web.com',
  'https://mock-service.com',
];

const sectors = [
  'technology',
  'finance',
  'healthcare',
  'retail',
  'education',
];

// Helper function to generate random test data
function generateTestData() {
  return {
    target_urls: [testUrls[Math.floor(Math.random() * testUrls.length)]],
    sector: sectors[Math.floor(Math.random() * sectors.length)],
    depth: Math.floor(Math.random() * 5) + 1,
    max_pages: Math.floor(Math.random() * 1000) + 100,
    priority: ['low', 'normal', 'high'][Math.floor(Math.random() * 3)],
    stealth_level: ['low', 'medium', 'high', 'extreme'][Math.floor(Math.random() * 4)],
  };
}

// Main test function
export default function () {
  const baseUrl = __ENV.BASE_URL || 'http://localhost:8000';
  
  // Test 1: Health check
  const healthCheck = http.get(`${baseUrl}/api/v1/health`);
  check(healthCheck, {
    'health check status is 200': (r) => r.status === 200,
    'health check response time < 500ms': (r) => r.timings.duration < 500,
  });
  
  // Test 2: Start crawl request
  const testData = generateTestData();
  const crawlPayload = JSON.stringify(testData);
  
  const crawlResponse = http.post(`${baseUrl}/api/v1/crawl`, crawlPayload, {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${__ENV.API_TOKEN || 'test-token'}`,
    },
  });
  
  const crawlStartTime = Date.now();
  
  check(crawlResponse, {
    'crawl request status is 200': (r) => r.status === 200,
    'crawl request response time < 1s': (r) => r.timings.duration < 1000,
    'crawl request returns request_id': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.request_id && body.request_id.length > 0;
      } catch {
        return false;
      }
    },
  });
  
  // Record crawl success/failure
  crawlSuccessRate.add(crawlResponse.status === 200);
  
  // Check for WAF blocks
  if (crawlResponse.status === 403 || crawlResponse.status === 429) {
    wafBlockRate.add(true);
  } else {
    wafBlockRate.add(false);
  }
  
  // Test 3: Get crawl status (if crawl was started successfully)
  if (crawlResponse.status === 200) {
    try {
      const responseBody = JSON.parse(crawlResponse.body);
      const requestId = responseBody.request_id;
      
      // Poll for status updates
      let attempts = 0;
      const maxAttempts = 10;
      
      while (attempts < maxAttempts) {
        sleep(2); // Wait 2 seconds between polls
        
        const statusResponse = http.get(`${baseUrl}/api/v1/crawl/${requestId}`);
        
        check(statusResponse, {
          'status request successful': (r) => r.status === 200,
        });
        
        if (statusResponse.status === 200) {
          try {
            const statusBody = JSON.parse(statusResponse.body);
            
            if (statusBody.status === 'completed') {
              // Record successful completion
              dataExtractionRate.add(true);
              crawlDuration.add(Date.now() - crawlStartTime);
              break;
            } else if (statusBody.status === 'failed') {
              dataExtractionRate.add(false);
              break;
            }
          } catch {
            // Invalid JSON response
            dataExtractionRate.add(false);
            break;
          }
        }
        
        attempts++;
      }
    } catch {
      // Failed to parse response
      dataExtractionRate.add(false);
    }
  }
  
  // Test 4: Get system status
  const statusResponse = http.get(`${baseUrl}/api/v1/status`);
  check(statusResponse, {
    'system status status is 200': (r) => r.status === 200,
    'system status response time < 500ms': (r) => r.timings.duration < 500,
    'system status returns health score': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.overall_health !== undefined;
      } catch {
        return false;
      }
    },
  });
  
  // Test 5: Get metrics
  const metricsResponse = http.get(`${baseUrl}/api/v1/metrics`);
  check(metricsResponse, {
    'metrics status is 200': (r) => r.status === 200,
    'metrics response time < 500ms': (r) => r.timings.duration < 500,
  });
  
  // Random sleep between requests
  sleep(Math.random() * 2 + 1); // 1-3 seconds
}

// Setup function (runs once at the beginning)
export function setup() {
  const baseUrl = __ENV.BASE_URL || 'http://localhost:8000';
  
  // Verify the service is running
  const healthCheck = http.get(`${baseUrl}/api/v1/health`);
  
  if (healthCheck.status !== 200) {
    throw new Error(`Service not available at ${baseUrl}`);
  }
  
  console.log(`✅ Service is available at ${baseUrl}`);
  
  // Optional: Pre-warm the system
  const warmupRequests = 10;
  for (let i = 0; i < warmupRequests; i++) {
    const testData = generateTestData();
    const response = http.post(`${baseUrl}/api/v1/crawl`, JSON.stringify(testData), {
      headers: { 'Content-Type': 'application/json' },
    });
    
    if (response.status !== 200) {
      console.warn(`⚠️ Warmup request ${i + 1} failed with status ${response.status}`);
    }
  }
  
  console.log(`✅ Completed ${warmupRequests} warmup requests`);
}

// Teardown function (runs once at the end)
export function teardown(data) {
  console.log('🧹 Test completed, cleaning up...');
  
  // Optional: Clean up test data
  const baseUrl = __ENV.BASE_URL || 'http://localhost:8000';
  
  // Get final metrics
  const finalMetrics = http.get(`${baseUrl}/api/v1/metrics`);
  
  if (finalMetrics.status === 200) {
    try {
      const metrics = JSON.parse(finalMetrics.body);
      console.log('📊 Final metrics:', JSON.stringify(metrics, null, 2));
    } catch {
      console.log('📊 Final metrics available but could not parse');
    }
  }
}

// Handle different scenarios
export function handleSummary(data) {
  const summary = {
    'load-test-summary.json': JSON.stringify(data, null, 2),
    stdout: `
# Universal Crawler Load Test Results

## Test Configuration
- Duration: ${data.state.testRunDuration}ms
- Virtual Users: ${data.metrics.vus.values.max}
- Requests: ${data.metrics.http_reqs.values.count}

## Performance Metrics
- Average Response Time: ${data.metrics.http_req_duration.values.avg.toFixed(2)}ms
- 95th Percentile: ${data.metrics.http_req_duration.values['p(95)'].toFixed(2)}ms
- Error Rate: ${(data.metrics.http_req_failed.values.rate * 100).toFixed(2)}%

## Business Metrics
- Crawl Success Rate: ${(data.metrics.crawl_success_rate.values.rate * 100).toFixed(2)}%
- WAF Block Rate: ${(data.metrics.waf_block_rate.values.rate * 100).toFixed(2)}%
- Data Extraction Rate: ${(data.metrics.data_extraction_rate.values.rate * 100).toFixed(2)}%

## Threshold Results
${Object.entries(data.thresholds).map(([name, result]) => 
  `- ${name}: ${result.ok ? '✅ PASS' : '❌ FAIL'}`
).join('\n')}

## Recommendations
${generateRecommendations(data)}
    `,
  };
  
  return summary;
}

function generateRecommendations(data) {
  const recommendations = [];
  
  // Check response time
  if (data.metrics.http_req_duration.values['p(95)'] > 2000) {
    recommendations.push('- Consider optimizing response times for 95th percentile');
  }
  
  // Check error rate
  if (data.metrics.http_req_failed.values.rate > 0.05) {
    recommendations.push('- Investigate high error rate and improve error handling');
  }
  
  // Check WAF blocks
  if (data.metrics.waf_block_rate.values.rate > 0.005) {
    recommendations.push('- Review WAF evasion strategies and stealth mechanisms');
  }
  
  // Check crawl success
  if (data.metrics.crawl_success_rate.values.rate < 0.95) {
    recommendations.push('- Investigate crawl failures and improve success rate');
  }
  
  if (recommendations.length === 0) {
    recommendations.push('- All performance targets met! 🎉');
  }
  
  return recommendations.join('\n');
} 