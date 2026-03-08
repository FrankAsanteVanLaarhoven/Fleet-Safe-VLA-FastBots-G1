#!/usr/bin/env python3
"""
Universal Crawler API Server
============================

FastAPI server providing REST API endpoints for the universal crawler system.
Supports all crawling modes, real-time status updates, and comprehensive reporting.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pathlib import Path
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, HttpUrl, validator
import aiofiles
import zipfile
import io

from universal_crawler_system import UniversalCrawler, CrawlRequest, CrawlMode, CrawlResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for API requests/responses
class CrawlRequestModel(BaseModel):
    url: HttpUrl
    mode: str = "enhanced"
    max_depth: int = 3
    max_pages: int = 100
    delay: float = 1.0
    timeout: int = 30
    user_agent: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    cookies: Optional[Dict[str, str]] = None
    proxy: Optional[str] = None
    extract_images: bool = True
    extract_links: bool = True
    extract_forms: bool = True
    extract_scripts: bool = True
    extract_styles: bool = True
    extract_meta: bool = True
    ocr_enabled: bool = False
    ast_analysis: bool = False
    network_analysis: bool = False
    compliance_mode: bool = True
    stealth_mode: bool = False
    custom_js: Optional[str] = None
    wait_for_selectors: Optional[List[str]] = None
    screenshot: bool = False
    pdf_export: bool = False

    @validator('mode')
    def validate_mode(cls, v):
        valid_modes = [mode.value for mode in CrawlMode]
        if v not in valid_modes:
            raise ValueError(f'Mode must be one of: {valid_modes}')
        return v

class CrawlResponseModel(BaseModel):
    id: str
    url: str
    status: str
    start_time: str
    end_time: Optional[str] = None
    total_pages: int = 0
    successful_pages: int = 0
    failed_pages: int = 0
    total_size: int = 0
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class CrawlStatsModel(BaseModel):
    total_crawls: int
    active_crawls: int
    completed_crawls: int
    failed_crawls: int
    total_pages_crawled: int
    total_size_crawled: int
    average_crawl_time: float

# Initialize FastAPI app
app = FastAPI(
    title="Universal Crawler API",
    description="Comprehensive web crawling API with advanced capabilities",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global crawler instance
crawler: Optional[UniversalCrawler] = None

# WebSocket connections for real-time updates
websocket_connections: List[WebSocket] = []

@app.on_event("startup")
async def startup_event():
    """Initialize the crawler on startup."""
    global crawler
    crawler = UniversalCrawler()
    await crawler.start_session()
    logger.info("Universal Crawler API started")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown."""
    global crawler
    if crawler:
        await crawler.close_session()
    logger.info("Universal Crawler API stopped")

async def notify_websockets(message: Dict[str, Any]):
    """Send message to all connected WebSocket clients."""
    disconnected = []
    for websocket in websocket_connections:
        try:
            await websocket.send_text(json.dumps(message))
        except:
            disconnected.append(websocket)
    
    # Remove disconnected clients
    for websocket in disconnected:
        websocket_connections.remove(websocket)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "crawler_available": crawler is not None
    }

@app.post("/crawl", response_model=CrawlResponseModel)
async def start_crawl(request: CrawlRequestModel, background_tasks: BackgroundTasks):
    """Start a new crawl operation."""
    if not crawler:
        raise HTTPException(status_code=503, detail="Crawler not available")
    
    try:
        # Convert Pydantic model to CrawlRequest
        crawl_request = CrawlRequest(
            url=str(request.url),
            mode=CrawlMode(request.mode),
            max_depth=request.max_depth,
            max_pages=request.max_pages,
            delay=request.delay,
            timeout=request.timeout,
            user_agent=request.user_agent,
            headers=request.headers,
            cookies=request.cookies,
            proxy=request.proxy,
            extract_images=request.extract_images,
            extract_links=request.extract_links,
            extract_forms=request.extract_forms,
            extract_scripts=request.extract_scripts,
            extract_styles=request.extract_styles,
            extract_meta=request.extract_meta,
            ocr_enabled=request.ocr_enabled,
            ast_analysis=request.ast_analysis,
            network_analysis=request.network_analysis,
            compliance_mode=request.compliance_mode,
            stealth_mode=request.stealth_mode,
            custom_js=request.custom_js,
            wait_for_selectors=request.wait_for_selectors,
            screenshot=request.screenshot,
            pdf_export=request.pdf_export
        )
        
        # Start the crawl
        result = await crawler.start_crawl(crawl_request)
        
        # Notify WebSocket clients
        await notify_websockets({
            "type": "crawl_started",
            "crawl_id": result.id,
            "url": result.url,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        return CrawlResponseModel(**asdict(result))
        
    except Exception as e:
        logger.error(f"Failed to start crawl: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{crawl_id}", response_model=CrawlResponseModel)
async def get_crawl_status(crawl_id: str):
    """Get the status of a crawl operation."""
    if not crawler:
        raise HTTPException(status_code=503, detail="Crawler not available")
    
    result = await crawler.get_crawl_status(crawl_id)
    if not result:
        raise HTTPException(status_code=404, detail="Crawl not found")
    
    return CrawlResponseModel(**asdict(result))

@app.get("/results/{crawl_id}")
async def get_crawl_results(crawl_id: str):
    """Get the results of a completed crawl."""
    if not crawler:
        raise HTTPException(status_code=503, detail="Crawler not available")
    
    results = await crawler.get_crawl_results(crawl_id)
    if not results:
        raise HTTPException(status_code=404, detail="Crawl results not found")
    
    return results

@app.post("/stop/{crawl_id}")
async def stop_crawl(crawl_id: str):
    """Stop an active crawl operation."""
    if not crawler:
        raise HTTPException(status_code=503, detail="Crawler not available")
    
    success = await crawler.stop_crawl(crawl_id)
    if not success:
        raise HTTPException(status_code=404, detail="Crawl not found")
    
    # Notify WebSocket clients
    await notify_websockets({
        "type": "crawl_stopped",
        "crawl_id": crawl_id,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    return {"status": "stopped", "crawl_id": crawl_id}

@app.delete("/crawl/{crawl_id}")
async def delete_crawl(crawl_id: str):
    """Delete a crawl and its data."""
    if not crawler:
        raise HTTPException(status_code=503, detail="Crawler not available")
    
    success = await crawler.delete_crawl(crawl_id)
    if not success:
        raise HTTPException(status_code=404, detail="Crawl not found")
    
    return {"status": "deleted", "crawl_id": crawl_id}

@app.get("/crawls", response_model=List[CrawlResponseModel])
async def get_all_crawls():
    """Get all crawl operations."""
    if not crawler:
        raise HTTPException(status_code=503, detail="Crawler not available")
    
    crawls = await crawler.get_all_crawls()
    return [CrawlResponseModel(**asdict(crawl)) for crawl in crawls]

@app.get("/stats", response_model=CrawlStatsModel)
async def get_crawl_stats():
    """Get crawling statistics."""
    if not crawler:
        raise HTTPException(status_code=503, detail="Crawler not available")
    
    crawls = await crawler.get_all_crawls()
    
    total_crawls = len(crawls)
    active_crawls = len([c for c in crawls if c.status == "running"])
    completed_crawls = len([c for c in crawls if c.status == "completed"])
    failed_crawls = len([c for c in crawls if c.status == "failed"])
    
    total_pages = sum(c.successful_pages + c.failed_pages for c in crawls)
    total_size = sum(c.total_size for c in crawls)
    
    # Calculate average crawl time
    completed_times = []
    for crawl in crawls:
        if crawl.end_time and crawl.start_time:
            start = datetime.fromisoformat(crawl.start_time.replace('Z', '+00:00'))
            end = datetime.fromisoformat(crawl.end_time.replace('Z', '+00:00'))
            duration = (end - start).total_seconds()
            completed_times.append(duration)
    
    average_time = sum(completed_times) / len(completed_times) if completed_times else 0
    
    return CrawlStatsModel(
        total_crawls=total_crawls,
        active_crawls=active_crawls,
        completed_crawls=completed_crawls,
        failed_crawls=failed_crawls,
        total_pages_crawled=total_pages,
        total_size_crawled=total_size,
        average_crawl_time=average_time
    )

@app.get("/export/{crawl_id}/json")
async def export_crawl_json(crawl_id: str):
    """Export crawl results as JSON."""
    if not crawler:
        raise HTTPException(status_code=503, detail="Crawler not available")
    
    results = await crawler.get_crawl_results(crawl_id)
    if not results:
        raise HTTPException(status_code=404, detail="Crawl results not found")
    
    return StreamingResponse(
        io.StringIO(json.dumps(results, indent=2)),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=crawl_{crawl_id}.json"}
    )

@app.get("/export/{crawl_id}/zip")
async def export_crawl_zip(crawl_id: str):
    """Export crawl results as ZIP archive."""
    if not crawler:
        raise HTTPException(status_code=503, detail="Crawler not available")
    
    crawl_dir = crawler.storage_dir / crawl_id
    if not crawl_dir.exists():
        raise HTTPException(status_code=404, detail="Crawl data not found")
    
    # Create ZIP file in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_path in crawl_dir.rglob("*"):
            if file_path.is_file():
                arc_name = file_path.relative_to(crawl_dir)
                zip_file.write(file_path, arc_name)
    
    zip_buffer.seek(0)
    
    return StreamingResponse(
        io.BytesIO(zip_buffer.getvalue()),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=crawl_{crawl_id}.zip"}
    )

@app.get("/download/{crawl_id}/{filename:path}")
async def download_crawl_file(crawl_id: str, filename: str):
    """Download a specific file from crawl results."""
    if not crawler:
        raise HTTPException(status_code=503, detail="Crawler not available")
    
    file_path = crawler.storage_dir / crawl_id / filename
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/octet-stream"
    )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await websocket.accept()
    websocket_connections.append(websocket)
    
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_connections.remove(websocket)

@app.get("/modes")
async def get_available_modes():
    """Get available crawling modes."""
    return {
        "modes": [
            {
                "value": mode.value,
                "name": mode.name,
                "description": {
                    "basic": "Simple HTML extraction",
                    "enhanced": "OCR, AST, Network analysis",
                    "full_site": "Complete source extraction",
                    "deep": "Multi-level crawling",
                    "stealth": "Anti-detection mode",
                    "enterprise": "Full compliance and audit"
                }.get(mode.value, "Advanced crawling mode")
            }
            for mode in CrawlMode
        ]
    }

@app.get("/")
async def root():
    """API root endpoint with documentation."""
    return {
        "name": "Universal Crawler API",
        "version": "1.0.0",
        "description": "Comprehensive web crawling API with advanced capabilities",
        "endpoints": {
            "POST /crawl": "Start a new crawl",
            "GET /status/{crawl_id}": "Get crawl status",
            "GET /results/{crawl_id}": "Get crawl results",
            "POST /stop/{crawl_id}": "Stop a crawl",
            "DELETE /crawl/{crawl_id}": "Delete a crawl",
            "GET /crawls": "Get all crawls",
            "GET /stats": "Get crawling statistics",
            "GET /export/{crawl_id}/json": "Export as JSON",
            "GET /export/{crawl_id}/zip": "Export as ZIP",
            "GET /modes": "Get available modes",
            "WS /ws": "Real-time updates"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "universal_crawler_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 