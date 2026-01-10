from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio
from backend.rag.engines.vector_engine import VectorEngine
from backend.rag.engines.graph_engine import GraphEngine
from backend.rag.engines.neural_engine import NeuralEngine
from backend.rag.engines.symbolic_engine import SymbolicEngine
from backend.rag.enterprise_ai.orchestrator import EnterpriseAIOrchestrator

app = FastAPI(title="Viral Marketing GraphRAG API")

# Initialize on startup
engines = {}
enterprise = None

@app.on_event("startup")
async def startup():
    global engines, enterprise
    engines = {
        'vector': VectorEngine(vector_store=None),
        'graph': GraphEngine(graph_store=None, vector_engine=None),
        'neural': NeuralEngine(graph_engine=None, vector_engine=None),
        'symbolic': SymbolicEngine()
    }
    engines['graph'].vector_engine = engines['vector']
    engines['neural'].graph = engines['graph']
    engines['neural'].vector = engines['vector']
    enterprise = EnterpriseAIOrchestrator(engines)

class QueryRequest(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None

@app.post("/api/query")
async def process_query(request: QueryRequest):
    result = await enterprise.process_business_request(
        request.query,
        request.context
    )
    return result

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "GraphRAG Enterprise AI"}

@app.get("/")
async def root():
    return {
        "service": "Viral Marketing GraphRAG API",
        "version": "1.0.0",
        "endpoints": {
            "query": "/api/query",
            "health": "/api/health"
        }
    }
