# -*- coding: utf-8 -*-
"""API routes for embedding configuration.

Reads/writes the agent's ReMeLight memory embedding model config:
``agent_config.running.reme_light_memory_config.embedding_model_config``
"""

import json
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from novapaw.app.agent_context import get_agent_for_request
from novapaw.config.config import load_agent_config, save_agent_config

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/embeddings", tags=["embeddings"])


class EmbeddingConfigRequest(BaseModel):
    provider_id: str
    model_name: str
    dimensions: int = 1024
    enable_cache: bool = True
    use_dimensions: bool = False
    max_input_length: int = 8192
    max_batch_size: int = 10
    base_url: str
    api_key: str = ""


class EmbeddingConfigResponse(BaseModel):
    provider_id: Optional[str] = None
    model_name: Optional[str] = None
    dimensions: int = 1024
    enable_cache: bool = True
    use_dimensions: bool = False
    max_input_length: int = 8192
    max_batch_size: int = 10
    base_url: str = ""
    api_key: str = ""


class SetActiveRequest(BaseModel):
    provider_id: str
    base_url: str
    model_name: str
    dimensions: int = 1024
    enable_cache: bool = True
    use_dimensions: bool = False
    max_input_length: int = 8192
    max_batch_size: int = 10
    api_key: str = ""


class TestEmbeddingRequest(BaseModel):
    provider_id: str
    base_url: str
    model_name: str


class TestEmbeddingResponse(BaseModel):
    success: bool
    message: str


def _get_embedding_config(agent_id: str) -> dict:
    """Read embedding model config from agent config."""
    agent_config = load_agent_config(agent_id)
    emb = agent_config.running.reme_light_memory_config.embedding_model_config
    # provider_id is a UI concept; ReMe backend must remain "openai" for
    # OpenAI-compatible providers. Derive provider_id from base_url.
    base = emb.base_url or ""
    provider_id = "nova-embedding" if "1278" in base else "nova-embedding-cluster"
    return {
        "provider_id": provider_id,
        "model_name": emb.model_name,
        "dimensions": emb.dimensions,
        "enable_cache": emb.enable_cache,
        "use_dimensions": emb.use_dimensions,
        "max_input_length": emb.max_input_length,
        "max_batch_size": emb.max_batch_size,
        "base_url": emb.base_url,
        "api_key": emb.api_key,
    }


def _save_embedding_config(agent_id: str, config_data: dict) -> dict:
    """Write embedding model config to agent config and persist.

    IMPORTANT: ``emb.backend`` is always set to ``"openai"`` because
    all currently supported Nova Embedding services are OpenAI-compatible.
    The ``provider_id`` field sent by the frontend is only used for UI
    provider card selection — it is NOT stored as the ReMe backend type.
    """
    agent_config = load_agent_config(agent_id)
    emb = agent_config.running.reme_light_memory_config.embedding_model_config

    if "base_url" in config_data:
        emb.base_url = config_data["base_url"]
    if "model_name" in config_data:
        emb.model_name = config_data["model_name"]
    if "dimensions" in config_data:
        emb.dimensions = config_data["dimensions"]
    if "enable_cache" in config_data:
        emb.enable_cache = config_data["enable_cache"]
    if "use_dimensions" in config_data:
        emb.use_dimensions = config_data["use_dimensions"]
    if "max_input_length" in config_data:
        emb.max_input_length = config_data["max_input_length"]
    if "max_batch_size" in config_data:
        emb.max_batch_size = config_data["max_batch_size"]
    if "api_key" in config_data:
        emb.api_key = config_data["api_key"]

    save_agent_config(agent_id, agent_config)
    return _get_embedding_config(agent_id)


@router.get("/config", response_model=EmbeddingConfigResponse)
async def get_embedding_config(request: Request) -> EmbeddingConfigResponse:
    """Get current embedding configuration."""
    try:
        workspace = await get_agent_for_request(request)
        return EmbeddingConfigResponse(**_get_embedding_config(workspace.agent_id))
    except Exception as e:
        logger.exception("Error getting embedding config")
        raise HTTPException(500, detail=f"Failed to get embedding config: {str(e)}")


@router.put("/config", response_model=EmbeddingConfigResponse)
async def save_embedding_config(
    body: EmbeddingConfigRequest,
    request: Request,
) -> EmbeddingConfigResponse:
    """Save embedding configuration."""
    try:
        workspace = await get_agent_for_request(request)
        return EmbeddingConfigResponse(**_save_embedding_config(workspace.agent_id, body.model_dump()))
    except Exception as e:
        logger.exception("Error saving embedding config")
        raise HTTPException(500, detail=f"Failed to save embedding config: {str(e)}")


@router.put("/active", response_model=EmbeddingConfigResponse)
async def set_active_embedding(
    body: SetActiveRequest,
    request: Request,
) -> EmbeddingConfigResponse:
    """Set active embedding provider."""
    try:
        workspace = await get_agent_for_request(request)
        return EmbeddingConfigResponse(**_save_embedding_config(workspace.agent_id, body.model_dump()))
    except Exception as e:
        logger.exception("Error setting active embedding")
        raise HTTPException(500, detail=f"Failed to set active embedding: {str(e)}")


@router.post("/test", response_model=TestEmbeddingResponse)
async def test_embedding_connection(
    body: TestEmbeddingRequest,
) -> TestEmbeddingResponse:
    """Test embedding connection."""
    try:
        import urllib.request

        test_url = f"{body.base_url}/embeddings"
        test_data = json.dumps(
            {
                "input": "test",
                "model": body.model_name,
            }
        ).encode("utf-8")

        req = urllib.request.Request(
            test_url,
            data=test_data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    return TestEmbeddingResponse(
                        success=True, message="Connection successful"
                    )
                else:
                    return TestEmbeddingResponse(
                        success=False, message=f"HTTP {response.status}"
                    )
        except urllib.error.URLError as e:
            return TestEmbeddingResponse(
                success=False, message=f"Connection failed: {str(e)}"
            )
        except Exception as e:
            return TestEmbeddingResponse(
                success=False, message=f"Test failed: {str(e)}"
            )

    except Exception as e:
        logger.exception("Error testing embedding connection")
        return TestEmbeddingResponse(success=False, message=f"Test failed: {str(e)}")
