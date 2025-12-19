"""FastAPI router for PraisonAI."""

from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from fastapi_praisonai.client import PraisonAIClient


class QueryRequest(BaseModel):
    """Request model for PraisonAI queries."""
    query: str
    agent: Optional[str] = None


class QueryResponse(BaseModel):
    """Response model for PraisonAI queries."""
    response: str


class AgentInfo(BaseModel):
    """Agent information model."""
    name: str
    id: str


class AgentsResponse(BaseModel):
    """Response model for listing agents."""
    agents: list[AgentInfo]


def create_router(
    api_url: str = "http://localhost:8080",
    prefix: str = "/praisonai",
    tags: list[str] = None,
) -> APIRouter:
    """Create a FastAPI router for PraisonAI.

    Args:
        api_url: PraisonAI API server URL.
        prefix: URL prefix for the router.
        tags: Tags for OpenAPI documentation.

    Returns:
        A configured FastAPI router.
    """
    if tags is None:
        tags = ["PraisonAI"]

    router = APIRouter(prefix=prefix, tags=tags)
    client = PraisonAIClient(api_url=api_url)

    @router.post("/query", response_model=QueryResponse)
    async def query_praisonai(request: QueryRequest) -> QueryResponse:
        """Send a query to PraisonAI agents."""
        try:
            if request.agent:
                response = await client.run_agent(request.query, request.agent)
            else:
                response = await client.run_workflow(request.query)
            return QueryResponse(response=response)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/agents", response_model=AgentsResponse)
    async def list_agents() -> AgentsResponse:
        """List available PraisonAI agents."""
        try:
            agents = await client.list_agents()
            return AgentsResponse(
                agents=[AgentInfo(name=a.get("name", ""), id=a.get("id", "")) for a in agents]
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return router
