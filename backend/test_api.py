#!/usr/bin/env python3
"""
Minimal Test API for Iron Cloud
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Iron Cloud Test")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Iron Cloud API is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/agents/test")
def test_agents():
    return {
        "business_insights": "Agent ready",
        "stock_market": "Agent ready", 
        "resource_agent": "Agent ready",
        "sports_betting": "Agent ready"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
