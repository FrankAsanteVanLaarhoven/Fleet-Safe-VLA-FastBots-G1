#!/usr/bin/env python3
"""
Simple Iron Cloud Backend API Test
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Iron Cloud Test API",
    description="Simple test API",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Iron Cloud API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Iron Cloud API"}

@app.get("/test")
async def test_endpoint():
    return {"message": "Test endpoint working!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
