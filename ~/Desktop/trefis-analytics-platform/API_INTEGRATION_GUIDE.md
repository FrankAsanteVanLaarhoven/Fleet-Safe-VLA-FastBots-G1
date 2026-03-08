# Trefis Analytics Platform - API Integration Guide

## Overview

This guide provides comprehensive instructions for integrating real Trefis data sources and external APIs to power your analytics platform with live data feeds.

## API Architecture

### Core API Endpoints

The platform is designed to work with the following API structure:

```
https://api.trefis.com/v1/
├── /companies/           # Company profiles and financial data
├── /markets/            # Market data and sector analysis
├── /reports/            # Analyst reports and research
├── /charts/             # Chart data and visualizations
├── /analytics/          # Financial metrics and analytics
├── /dashboard/          # Dashboard data and summaries
├── /live/               # Real-time data feeds
├── /search/             # Global search functionality
└── /user/               # User preferences and watchlists
```

## Environment Configuration

### 1. API Keys Setup

Create a `.env.local` file in your project root:

```bash
# Trefis API Configuration
NEXT_PUBLIC_TREFIS_API_URL=https://api.trefis.com/v1
NEXT_PUBLIC_TREFIS_API_KEY=your_trefis_api_key_here

# Alternative Data Sources
NEXT_PUBLIC_ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
NEXT_PUBLIC_FINNHUB_API_KEY=your_finnhub_key
NEXT_PUBLIC_POLYGON_API_KEY=your_polygon_key
NEXT_PUBLIC_YAHOO_FINANCE_API_KEY=your_yahoo_key

# Real-time Data
NEXT_PUBLIC_WEBSOCKET_URL=wss://stream.trefis.com/v1
NEXT_PUBLIC_REDIS_URL=redis://localhost:6379

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/trefis_analytics
```

### 2. API Key Sources

#### Primary Data Sources:
- **Trefis API**: Main data source for company analysis and reports
- **Alpha Vantage**: Real-time stock prices and market data
- **Finnhub**: Financial statements and company fundamentals
- **Polygon.io**: Real-time market data and news
- **Yahoo Finance**: Historical data and market information

#### Alternative Sources:
- **IEX Cloud**: Financial data and news
- **Quandl**: Economic and financial datasets
- **FRED**: Federal Reserve economic data
- **World Bank API**: Global economic indicators

## Real-Time Data Integration

### 1. WebSocket Connection

```typescript
// src/lib/websocket.ts
class TrefisWebSocket {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;

  connect() {
    this.ws = new WebSocket(process.env.NEXT_PUBLIC_WEBSOCKET_URL!);
    
    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
    };

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleMessage(data);
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
      this.reconnect();
    };
  }

  private handleMessage(data: any) {
    switch (data.type) {
      case 'price_update':
        this.updateStockPrice(data);
        break;
      case 'news_alert':
        this.handleNewsAlert(data);
        break;
      case 'market_update':
        this.updateMarketData(data);
        break;
    }
  }

  private reconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      setTimeout(() => this.connect(), 1000 * this.reconnectAttempts);
    }
  }
}
```

### 2. Real-Time Price Updates

```typescript
// src/hooks/useLivePrices.ts
import { useState, useEffect } from 'react';
import { trefisApi } from '@/lib/api';

export function useLivePrices(symbols: string[]) {
  const [prices, setPrices] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPrices = async () => {
      try {
        const livePrices = await trefisApi.getLivePrices(symbols);
        const priceMap = livePrices.reduce((acc, price) => {
          acc[price.symbol] = price;
          return acc;
        }, {} as Record<string, any>);
        
        setPrices(priceMap);
      } catch (error) {
        console.error('Error fetching live prices:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPrices();
    
    // Set up polling for price updates
    const interval = setInterval(fetchPrices, 30000); // 30 seconds
    
    return () => clearInterval(interval);
  }, [symbols]);

  return { prices, loading };
}
```

## Data Synchronization

### 1. Background Data Sync

```typescript
// src/lib/dataSync.ts
import { trefisApi } from './api';

class DataSynchronizer {
  private syncIntervals: NodeJS.Timeout[] = [];

  startSync() {
    // Sync company data every hour
    this.syncIntervals.push(
      setInterval(() => this.syncCompanyData(), 60 * 60 * 1000)
    );

    // Sync market data every 15 minutes
    this.syncIntervals.push(
      setInterval(() => this.syncMarketData(), 15 * 60 * 1000)
    );

    // Sync analyst reports daily
    this.syncIntervals.push(
      setInterval(() => this.syncAnalystReports(), 24 * 60 * 60 * 1000)
    );
  }

  private async syncCompanyData() {
    try {
      const companies = await trefisApi.searchCompanies('', '');
      // Store in local database or cache
      await this.storeCompanyData(companies);
    } catch (error) {
      console.error('Error syncing company data:', error);
    }
  }

  private async syncMarketData() {
    try {
      const marketData = await trefisApi.getMarketOverview();
      await this.storeMarketData(marketData);
    } catch (error) {
      console.error('Error syncing market data:', error);
    }
  }

  private async syncAnalystReports() {
    try {
      const reports = await trefisApi.getLatestReports(100);
      await this.storeAnalystReports(reports);
    } catch (error) {
      console.error('Error syncing analyst reports:', error);
    }
  }

  stopSync() {
    this.syncIntervals.forEach(clearInterval);
    this.syncIntervals = [];
  }
}
```

### 2. Caching Strategy

```typescript
// src/lib/cache.ts
import Redis from 'ioredis';

class CacheManager {
  private redis: Redis;

  constructor() {
    this.redis = new Redis(process.env.NEXT_PUBLIC_REDIS_URL!);
  }

  async get(key: string): Promise<any> {
    const data = await this.redis.get(key);
    return data ? JSON.parse(data) : null;
  }

  async set(key: string, value: any, ttl: number = 3600): Promise<void> {
    await this.redis.setex(key, ttl, JSON.stringify(value));
  }

  async invalidate(pattern: string): Promise<void> {
    const keys = await this.redis.keys(pattern);
    if (keys.length > 0) {
      await this.redis.del(...keys);
    }
  }

  // Cache company data for 1 hour
  async cacheCompanyData(companyId: string, data: any): Promise<void> {
    await this.set(`company:${companyId}`, data, 3600);
  }

  // Cache market data for 15 minutes
  async cacheMarketData(marketId: string, data: any): Promise<void> {
    await this.set(`market:${marketId}`, data, 900);
  }

  // Cache analyst reports for 24 hours
  async cacheAnalystReports(reports: any[]): Promise<void> {
    await this.set('analyst_reports:latest', reports, 86400);
  }
}
```

## External API Integration

### 1. Alpha Vantage Integration

```typescript
// src/lib/alphaVantage.ts
class AlphaVantageAPI {
  private apiKey: string;
  private baseUrl = 'https://www.alphavantage.co/query';

  constructor() {
    this.apiKey = process.env.NEXT_PUBLIC_ALPHA_VANTAGE_API_KEY!;
  }

  async getStockPrice(symbol: string) {
    const response = await fetch(
      `${this.baseUrl}?function=GLOBAL_QUOTE&symbol=${symbol}&apikey=${this.apiKey}`
    );
    return response.json();
  }

  async getCompanyOverview(symbol: string) {
    const response = await fetch(
      `${this.baseUrl}?function=OVERVIEW&symbol=${symbol}&apikey=${this.apiKey}`
    );
    return response.json();
  }

  async getIncomeStatement(symbol: string) {
    const response = await fetch(
      `${this.baseUrl}?function=INCOME_STATEMENT&symbol=${symbol}&apikey=${this.apiKey}`
    );
    return response.json();
  }
}
```

### 2. Finnhub Integration

```typescript
// src/lib/finnhub.ts
class FinnhubAPI {
  private apiKey: string;
  private baseUrl = 'https://finnhub.io/api/v1';

  constructor() {
    this.apiKey = process.env.NEXT_PUBLIC_FINNHUB_API_KEY!;
  }

  async getCompanyProfile(symbol: string) {
    const response = await fetch(
      `${this.baseUrl}/stock/profile2?symbol=${symbol}&token=${this.apiKey}`
    );
    return response.json();
  }

  async getFinancialStatements(symbol: string) {
    const response = await fetch(
      `${this.baseUrl}/stock/financials-reported?symbol=${symbol}&token=${this.apiKey}`
    );
    return response.json();
  }

  async getNews(symbol: string) {
    const response = await fetch(
      `${this.baseUrl}/company-news?symbol=${symbol}&from=2024-01-01&to=2024-12-31&token=${this.apiKey}`
    );
    return response.json();
  }
}
```

## Error Handling and Fallbacks

### 1. API Error Handling

```typescript
// src/lib/apiErrorHandler.ts
export class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public code: string
  ) {
    super(message);
    this.name = 'APIError';
  }
}

export function handleAPIError(error: any): APIError {
  if (error.response) {
    return new APIError(
      error.response.data?.message || 'API request failed',
      error.response.status,
      error.response.data?.code || 'UNKNOWN_ERROR'
    );
  }
  
  return new APIError(
    error.message || 'Network error',
    500,
    'NETWORK_ERROR'
  );
}
```

### 2. Fallback Data Sources

```typescript
// src/lib/fallbackData.ts
export class FallbackDataManager {
  private fallbackSources = [
    'alpha_vantage',
    'finnhub',
    'polygon',
    'yahoo_finance'
  ];

  async getCompanyData(symbol: string) {
    for (const source of this.fallbackSources) {
      try {
        const data = await this.fetchFromSource(source, symbol);
        if (data) return data;
      } catch (error) {
        console.warn(`Failed to fetch from ${source}:`, error);
        continue;
      }
    }
    
    throw new Error('All data sources failed');
  }

  private async fetchFromSource(source: string, symbol: string) {
    switch (source) {
      case 'alpha_vantage':
        return await this.alphaVantage.getCompanyOverview(symbol);
      case 'finnhub':
        return await this.finnhub.getCompanyProfile(symbol);
      // Add other sources...
    }
  }
}
```

## Performance Optimization

### 1. Request Batching

```typescript
// src/lib/requestBatcher.ts
export class RequestBatcher {
  private batchQueue: Array<{ id: string; resolve: Function; reject: Function }> = [];
  private batchTimeout: NodeJS.Timeout | null = null;
  private batchSize = 10;
  private batchDelay = 100;

  async batchRequest<T>(id: string, requestFn: () => Promise<T>): Promise<T> {
    return new Promise((resolve, reject) => {
      this.batchQueue.push({ id, resolve, reject });
      
      if (this.batchQueue.length >= this.batchSize) {
        this.processBatch();
      } else if (!this.batchTimeout) {
        this.batchTimeout = setTimeout(() => this.processBatch(), this.batchDelay);
      }
    });
  }

  private async processBatch() {
    if (this.batchTimeout) {
      clearTimeout(this.batchTimeout);
      this.batchTimeout = null;
    }

    const batch = this.batchQueue.splice(0, this.batchSize);
    // Process batch requests...
  }
}
```

### 2. Data Prefetching

```typescript
// src/lib/prefetcher.ts
export class DataPrefetcher {
  private prefetchQueue: string[] = [];
  private isPrefetching = false;

  async prefetchCompanyData(symbols: string[]) {
    this.prefetchQueue.push(...symbols);
    
    if (!this.isPrefetching) {
      this.isPrefetching = true;
      await this.processPrefetchQueue();
      this.isPrefetching = false;
    }
  }

  private async processPrefetchQueue() {
    while (this.prefetchQueue.length > 0) {
      const batch = this.prefetchQueue.splice(0, 5);
      await Promise.all(
        batch.map(symbol => this.prefetchCompany(symbol))
      );
    }
  }

  private async prefetchCompany(symbol: string) {
    try {
      const [profile, financials, news] = await Promise.all([
        trefisApi.getCompanyProfile(symbol),
        trefisApi.getCompanyFinancials(symbol),
        trefisApi.getLiveNews()
      ]);
      
      // Store in cache
      await cache.set(`prefetch:${symbol}`, { profile, financials, news }, 1800);
    } catch (error) {
      console.error(`Failed to prefetch ${symbol}:`, error);
    }
  }
}
```

## Monitoring and Analytics

### 1. API Usage Monitoring

```typescript
// src/lib/monitoring.ts
export class APIMonitor {
  private metrics: Record<string, any> = {};

  trackRequest(endpoint: string, duration: number, success: boolean) {
    if (!this.metrics[endpoint]) {
      this.metrics[endpoint] = {
        totalRequests: 0,
        successfulRequests: 0,
        failedRequests: 0,
        averageResponseTime: 0,
        totalResponseTime: 0
      };
    }

    const metric = this.metrics[endpoint];
    metric.totalRequests++;
    metric.totalResponseTime += duration;
    metric.averageResponseTime = metric.totalResponseTime / metric.totalRequests;

    if (success) {
      metric.successfulRequests++;
    } else {
      metric.failedRequests++;
    }
  }

  getMetrics() {
    return this.metrics;
  }

  getSuccessRate(endpoint: string) {
    const metric = this.metrics[endpoint];
    if (!metric) return 0;
    return (metric.successfulRequests / metric.totalRequests) * 100;
  }
}
```

## Deployment Configuration

### 1. Production Environment

```bash
# Production environment variables
NEXT_PUBLIC_TREFIS_API_URL=https://api.trefis.com/v1
NEXT_PUBLIC_TREFIS_API_KEY=prod_api_key_here
NEXT_PUBLIC_WEBSOCKET_URL=wss://stream.trefis.com/v1
NEXT_PUBLIC_REDIS_URL=redis://prod-redis:6379

# Database
DATABASE_URL=postgresql://user:password@prod-db:5432/trefis_analytics

# Monitoring
NEXT_PUBLIC_SENTRY_DSN=your_sentry_dsn
NEXT_PUBLIC_ANALYTICS_ID=your_analytics_id
```

### 2. Docker Configuration

```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    depends_on:
      - redis
      - postgres

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: trefis_analytics
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## Testing

### 1. API Testing

```typescript
// tests/api.test.ts
import { trefisApi } from '@/lib/api';

describe('Trefis API', () => {
  test('should fetch company profile', async () => {
    const profile = await trefisApi.getCompanyProfile('MSFT');
    expect(profile).toHaveProperty('company_id');
    expect(profile).toHaveProperty('name');
  });

  test('should handle API errors gracefully', async () => {
    await expect(trefisApi.getCompanyProfile('INVALID')).rejects.toThrow();
  });
});
```

### 2. Integration Testing

```typescript
// tests/integration.test.ts
describe('Data Integration', () => {
  test('should sync data from multiple sources', async () => {
    const syncManager = new DataSynchronizer();
    await syncManager.syncCompanyData();
    
    // Verify data was stored
    const cachedData = await cache.get('company:MSFT');
    expect(cachedData).toBeDefined();
  });
});
```

## Security Considerations

### 1. API Key Management

- Store API keys in environment variables
- Use different keys for development and production
- Rotate keys regularly
- Monitor API usage for anomalies

### 2. Rate Limiting

```typescript
// src/lib/rateLimiter.ts
export class RateLimiter {
  private requests: Map<string, number[]> = new Map();
  private limit = 100; // requests per minute
  private window = 60000; // 1 minute

  canMakeRequest(apiKey: string): boolean {
    const now = Date.now();
    const requests = this.requests.get(apiKey) || [];
    
    // Remove old requests
    const recentRequests = requests.filter(time => now - time < this.window);
    
    if (recentRequests.length >= this.limit) {
      return false;
    }
    
    recentRequests.push(now);
    this.requests.set(apiKey, recentRequests);
    return true;
  }
}
```

## Conclusion

This API integration guide provides a comprehensive framework for connecting your Trefis Analytics Platform to real data sources. The modular architecture allows for easy addition of new data sources and ensures high availability through fallback mechanisms.

For production deployment, ensure you have:
- Valid API keys for all data sources
- Proper error handling and monitoring
- Rate limiting and security measures
- Caching strategy for optimal performance
- Backup data sources for reliability

The platform is designed to scale with your needs and can accommodate additional data sources as required. 