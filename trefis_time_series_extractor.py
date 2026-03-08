#!/usr/bin/env python3
"""
Trefis Time Series Data Extractor
Specialized extractor for financial time series data from Trefis.com
"""

import asyncio
import aiohttp
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Dict, List, Optional, Any, Tuple
import re
from dataclasses import dataclass
import sqlite3
from concurrent.futures import ThreadPoolExecutor
import time
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TimeSeriesPoint:
    """Time series data point"""
    timestamp: datetime
    value: float
    metric: str
    symbol: str
    currency: str = "USD"
    source: str = "trefis"
    confidence: float = 1.0
    metadata: Dict[str, Any] = None

class TrefisTimeSeriesExtractor:
    """Specialized time series extractor for Trefis.com"""
    
    def __init__(self):
        self.base_url = "https://www.trefis.com"
        self.desktop_path = Path.home() / "Desktop"
        self.output_dir = self.desktop_path / "trefis_time_series_data"
        self.session = None
        self.time_series_data = {}
        self.metrics_mapping = {
            'stock_price': ['price', 'stock', 'share'],
            'revenue': ['revenue', 'sales', 'income'],
            'earnings': ['earnings', 'profit', 'net_income'],
            'market_cap': ['market_cap', 'market_capitalization'],
            'pe_ratio': ['pe_ratio', 'price_earnings'],
            'dividend_yield': ['dividend_yield', 'yield'],
            'beta': ['beta', 'volatility'],
            'volume': ['volume', 'trading_volume'],
            'analyst_rating': ['rating', 'analyst', 'recommendation']
        }
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    async def initialize_session(self):
        """Initialize aiohttp session"""
        connector = aiohttp.TCPConnector(limit=50, limit_per_host=10)
        timeout = aiohttp.ClientTimeout(total=30)
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
        )
    
    async def extract_comprehensive_time_series(self, symbols: List[str] = None):
        """Extract comprehensive time series data for all symbols"""
        logger.info("Starting comprehensive time series extraction")
        
        await self.initialize_session()
        
        try:
            # Get list of symbols if not provided
            if not symbols:
                symbols = await self._get_available_symbols()
            
            logger.info(f"Extracting time series for {len(symbols)} symbols")
            
            # Extract data for each symbol
            for symbol in symbols:
                await self._extract_symbol_time_series(symbol)
                await asyncio.sleep(random.uniform(1, 3))  # Rate limiting
            
            # Process and save all data
            await self._process_and_save_time_series()
            
        finally:
            if self.session:
                await self.session.close()
    
    async def _get_available_symbols(self) -> List[str]:
        """Get list of available symbols from Trefis"""
        logger.info("Getting available symbols")
        
        try:
            # Try to get symbols from main page
            async with self.session.get(f"{self.base_url}/data/companies") as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Extract symbols using regex
                    symbol_pattern = r'/data/companies/([A-Z]+)'
                    symbols = re.findall(symbol_pattern, content)
                    
                    # Remove duplicates and return
                    unique_symbols = list(set(symbols))
                    logger.info(f"Found {len(unique_symbols)} unique symbols")
                    return unique_symbols[:50]  # Limit to first 50 for testing
        
        except Exception as e:
            logger.warning(f"Could not get symbols from main page: {e}")
        
        # Fallback to common symbols
        return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'AMD', 'INTC']
    
    async def _extract_symbol_time_series(self, symbol: str):
        """Extract time series data for a specific symbol"""
        logger.info(f"Extracting time series for {symbol}")
        
        try:
            # Get company page
            company_url = f"{self.base_url}/data/companies/{symbol}"
            
            async with self.session.get(company_url) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Extract time series data from page
                    time_series = await self._extract_time_series_from_page(content, symbol)
                    
                    if time_series:
                        self.time_series_data[symbol] = time_series
                        logger.info(f"Extracted {len(time_series)} data points for {symbol}")
                    
                    # Try to get additional data from API endpoints
                    await self._extract_api_time_series(symbol)
                    
        except Exception as e:
            logger.warning(f"Error extracting time series for {symbol}: {e}")
    
    async def _extract_time_series_from_page(self, content: str, symbol: str) -> List[TimeSeriesPoint]:
        """Extract time series data from page content"""
        time_series = []
        
        try:
            # Look for chart data in script tags
            chart_patterns = [
                r'chartData\s*=\s*(\{.*?\});',
                r'series\s*:\s*(\[.*?\])',
                r'data\s*:\s*(\[.*?\])',
                r'points\s*:\s*(\[.*?\])'
            ]
            
            for pattern in chart_patterns:
                matches = re.findall(pattern, content, re.DOTALL)
                for match in matches:
                    try:
                        # Try to parse as JSON
                        data = json.loads(match)
                        points = self._parse_chart_data(data, symbol)
                        time_series.extend(points)
                    except json.JSONDecodeError:
                        # Try to parse as array
                        try:
                            data = json.loads(f"[{match}]")
                            points = self._parse_chart_data(data, symbol)
                            time_series.extend(points)
                        except json.JSONDecodeError:
                            continue
            
            # Look for data in HTML tables
            table_data = self._extract_table_data(content, symbol)
            time_series.extend(table_data)
            
        except Exception as e:
            logger.warning(f"Error parsing time series from page: {e}")
        
        return time_series
    
    async def _extract_api_time_series(self, symbol: str):
        """Extract time series data from API endpoints"""
        logger.info(f"Extracting API time series for {symbol}")
        
        api_endpoints = [
            f"/api/companies/{symbol}/data",
            f"/api/companies/{symbol}/charts",
            f"/api/companies/{symbol}/metrics",
            f"/api/companies/{symbol}/financials"
        ]
        
        for endpoint in api_endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        points = self._parse_api_data(data, symbol)
                        
                        if symbol not in self.time_series_data:
                            self.time_series_data[symbol] = []
                        
                        self.time_series_data[symbol].extend(points)
                        logger.info(f"Extracted {len(points)} points from API for {symbol}")
                        
            except Exception as e:
                logger.debug(f"API endpoint {endpoint} failed: {e}")
    
    def _parse_chart_data(self, data: Any, symbol: str) -> List[TimeSeriesPoint]:
        """Parse chart data into time series points"""
        points = []
        
        try:
            if isinstance(data, dict):
                # Handle different chart data formats
                if 'series' in data:
                    for series in data['series']:
                        metric = series.get('name', 'unknown')
                        series_data = series.get('data', [])
                        points.extend(self._parse_series_data(series_data, symbol, metric))
                
                elif 'data' in data:
                    points.extend(self._parse_series_data(data['data'], symbol, 'value'))
                
                elif 'points' in data:
                    points.extend(self._parse_series_data(data['points'], symbol, 'value'))
            
            elif isinstance(data, list):
                # Direct array of data points
                points.extend(self._parse_series_data(data, symbol, 'value'))
        
        except Exception as e:
            logger.warning(f"Error parsing chart data: {e}")
        
        return points
    
    def _parse_series_data(self, series_data: List, symbol: str, metric: str) -> List[TimeSeriesPoint]:
        """Parse series data into time series points"""
        points = []
        
        for item in series_data:
            try:
                if isinstance(item, (list, tuple)) and len(item) >= 2:
                    # Format: [timestamp, value]
                    timestamp = self._parse_timestamp(item[0])
                    value = float(item[1]) if item[1] is not None else 0.0
                    
                    points.append(TimeSeriesPoint(
                        timestamp=timestamp,
                        value=value,
                        metric=metric,
                        symbol=symbol
                    ))
                
                elif isinstance(item, dict):
                    # Format: {"date": timestamp, "value": value}
                    timestamp = self._parse_timestamp(item.get('date', item.get('time')))
                    value = float(item.get('value', 0))
                    
                    points.append(TimeSeriesPoint(
                        timestamp=timestamp,
                        value=value,
                        metric=item.get('metric', metric),
                        symbol=symbol
                    ))
            
            except Exception as e:
                logger.debug(f"Error parsing series item: {e}")
                continue
        
        return points
    
    def _parse_api_data(self, data: Any, symbol: str) -> List[TimeSeriesPoint]:
        """Parse API response data"""
        points = []
        
        try:
            if isinstance(data, dict):
                # Handle different API response formats
                for key, value in data.items():
                    if isinstance(value, (list, tuple)):
                        # Time series data
                        points.extend(self._parse_series_data(value, symbol, key))
                    
                    elif isinstance(value, dict) and 'data' in value:
                        # Nested data structure
                        points.extend(self._parse_series_data(value['data'], symbol, key))
            
            elif isinstance(data, list):
                # Direct array response
                points.extend(self._parse_series_data(data, symbol, 'value'))
        
        except Exception as e:
            logger.warning(f"Error parsing API data: {e}")
        
        return points
    
    def _extract_table_data(self, content: str, symbol: str) -> List[TimeSeriesPoint]:
        """Extract data from HTML tables"""
        points = []
        
        try:
            # Look for table patterns in HTML
            table_patterns = [
                r'<table[^>]*>.*?</table>',
                r'<tr[^>]*>.*?</tr>'
            ]
            
            for pattern in table_patterns:
                matches = re.findall(pattern, content, re.DOTALL)
                for match in matches:
                    # Extract data from table rows
                    row_data = self._parse_table_row(match, symbol)
                    points.extend(row_data)
        
        except Exception as e:
            logger.warning(f"Error extracting table data: {e}")
        
        return points
    
    def _parse_table_row(self, row_html: str, symbol: str) -> List[TimeSeriesPoint]:
        """Parse table row data"""
        points = []
        
        try:
            # Extract cells from row
            cell_pattern = r'<td[^>]*>(.*?)</td>'
            cells = re.findall(cell_pattern, row_html, re.DOTALL)
            
            if len(cells) >= 2:
                # Assume first cell is date, second is value
                date_text = re.sub(r'<[^>]+>', '', cells[0]).strip()
                value_text = re.sub(r'<[^>]+>', '', cells[1]).strip()
                
                timestamp = self._parse_timestamp(date_text)
                try:
                    value = float(re.sub(r'[$,%]', '', value_text))
                    points.append(TimeSeriesPoint(
                        timestamp=timestamp,
                        value=value,
                        metric='table_data',
                        symbol=symbol
                    ))
                except ValueError:
                    pass
        
        except Exception as e:
            logger.debug(f"Error parsing table row: {e}")
        
        return points
    
    def _parse_timestamp(self, timestamp) -> datetime:
        """Parse various timestamp formats"""
        if isinstance(timestamp, (int, float)):
            # Unix timestamp
            return datetime.fromtimestamp(timestamp)
        
        elif isinstance(timestamp, str):
            # Try various date formats
            formats = [
                '%Y-%m-%d',
                '%Y-%m-%d %H:%M:%S',
                '%m/%d/%Y',
                '%d/%m/%Y',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%dT%H:%M:%SZ'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(timestamp, fmt)
                except ValueError:
                    continue
            
            # Try to extract date from text
            date_patterns = [
                r'(\d{4}-\d{2}-\d{2})',
                r'(\d{2}/\d{2}/\d{4})',
                r'(\d{4}/\d{2}/\d{2})'
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, timestamp)
                if match:
                    date_str = match.group(1)
                    for fmt in formats[:3]:  # Use first 3 formats
                        try:
                            return datetime.strptime(date_str, fmt)
                        except ValueError:
                            continue
        
        # Default to current time
        return datetime.now()
    
    async def _process_and_save_time_series(self):
        """Process and save all time series data"""
        logger.info("Processing and saving time series data")
        
        # Convert to pandas DataFrames
        for symbol, points in self.time_series_data.items():
            if points:
                df = self._convert_to_dataframe(points)
                self._save_dataframe(symbol, df)
        
        # Create combined dataset
        self._create_combined_dataset()
        
        # Create summary statistics
        self._create_summary_statistics()
        
        # Save to database
        self._save_to_database()
        
        logger.info("Time series data processing completed")
    
    def _convert_to_dataframe(self, points: List[TimeSeriesPoint]) -> pd.DataFrame:
        """Convert time series points to pandas DataFrame"""
        data = []
        
        for point in points:
            data.append({
                'timestamp': point.timestamp,
                'value': point.value,
                'metric': point.metric,
                'symbol': point.symbol,
                'currency': point.currency,
                'source': point.source,
                'confidence': point.confidence
            })
        
        df = pd.DataFrame(data)
        
        if not df.empty:
            # Sort by timestamp
            df = df.sort_values('timestamp')
            
            # Remove duplicates
            df = df.drop_duplicates(subset=['timestamp', 'metric', 'symbol'])
        
        return df
    
    def _save_dataframe(self, symbol: str, df: pd.DataFrame):
        """Save DataFrame to file"""
        if not df.empty:
            # Save as CSV
            csv_path = self.output_dir / f"{symbol}_time_series.csv"
            df.to_csv(csv_path, index=False)
            
            # Save as JSON
            json_path = self.output_dir / f"{symbol}_time_series.json"
            df.to_json(json_path, orient='records', date_format='iso')
            
            # Save as Parquet (for big data)
            parquet_path = self.output_dir / f"{symbol}_time_series.parquet"
            df.to_parquet(parquet_path, index=False)
            
            logger.info(f"Saved time series data for {symbol}: {len(df)} records")
    
    def _create_combined_dataset(self):
        """Create combined dataset with all symbols"""
        all_data = []
        
        for symbol, points in self.time_series_data.items():
            if points:
                df = self._convert_to_dataframe(points)
                all_data.append(df)
        
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            
            # Save combined dataset
            combined_df.to_csv(self.output_dir / "combined_time_series.csv", index=False)
            combined_df.to_json(self.output_dir / "combined_time_series.json", orient='records', date_format='iso')
            combined_df.to_parquet(self.output_dir / "combined_time_series.parquet", index=False)
            
            logger.info(f"Created combined dataset: {len(combined_df)} total records")
    
    def _create_summary_statistics(self):
        """Create summary statistics for time series data"""
        summary = {
            'extraction_date': datetime.now().isoformat(),
            'total_symbols': len(self.time_series_data),
            'total_data_points': sum(len(points) for points in self.time_series_data.values()),
            'symbols': {},
            'metrics_summary': {}
        }
        
        for symbol, points in self.time_series_data.items():
            if points:
                df = self._convert_to_dataframe(points)
                
                summary['symbols'][symbol] = {
                    'data_points': len(df),
                    'date_range': {
                        'start': df['timestamp'].min().isoformat() if not df.empty else None,
                        'end': df['timestamp'].max().isoformat() if not df.empty else None
                    },
                    'metrics': df['metric'].unique().tolist(),
                    'value_stats': {
                        'mean': float(df['value'].mean()) if not df.empty else 0,
                        'std': float(df['value'].std()) if not df.empty else 0,
                        'min': float(df['value'].min()) if not df.empty else 0,
                        'max': float(df['value'].max()) if not df.empty else 0
                    }
                }
                
                # Aggregate metrics
                for metric in df['metric'].unique():
                    metric_data = df[df['metric'] == metric]
                    if metric not in summary['metrics_summary']:
                        summary['metrics_summary'][metric] = {
                            'symbols': [],
                            'total_points': 0
                        }
                    
                    summary['metrics_summary'][metric]['symbols'].append(symbol)
                    summary['metrics_summary'][metric]['total_points'] += len(metric_data)
        
        # Save summary
        with open(self.output_dir / "time_series_summary.json", 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        logger.info("Created time series summary statistics")
    
    def _save_to_database(self):
        """Save time series data to SQLite database"""
        db_path = self.output_dir / "time_series.db"
        
        with sqlite3.connect(db_path) as conn:
            # Create time series table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS time_series (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    value REAL NOT NULL,
                    metric TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    currency TEXT DEFAULT 'USD',
                    source TEXT DEFAULT 'trefis',
                    confidence REAL DEFAULT 1.0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_symbol_timestamp ON time_series(symbol, timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_metric ON time_series(metric)")
            
            # Insert data
            for symbol, points in self.time_series_data.items():
                for point in points:
                    conn.execute("""
                        INSERT INTO time_series 
                        (timestamp, value, metric, symbol, currency, source, confidence)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        point.timestamp.isoformat(),
                        point.value,
                        point.metric,
                        point.symbol,
                        point.currency,
                        point.source,
                        point.confidence
                    ))
            
            conn.commit()
        
        logger.info(f"Saved time series data to database: {db_path}")

async def main():
    """Main execution function"""
    extractor = TrefisTimeSeriesExtractor()
    
    # Extract time series for specific symbols or all available
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']  # Example symbols
    await extractor.extract_comprehensive_time_series(symbols)

if __name__ == "__main__":
    asyncio.run(main()) 