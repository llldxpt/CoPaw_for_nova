# -*- coding: utf-8 -*-
"""API schemas for Nova Studio integration."""

from typing import Optional
from pydantic import BaseModel, Field


class NovaStudioConfig(BaseModel):
    """Nova Studio configuration item."""

    id: str = Field(..., description="Unique configuration identifier")
    name: str = Field(..., description="Configuration name")
    description: str = Field(default="", description="Configuration description")
    category: str = Field(..., description="Configuration category")
    enabled: bool = Field(default=True, description="Whether enabled")
    config_data: dict = Field(
        default_factory=dict,
        description="Configuration data",
    )


class NovaStudioConfigCreateRequest(BaseModel):
    """Request body for creating a Nova Studio configuration."""

    name: str = Field(..., description="Configuration name")
    description: str = Field(default="", description="Configuration description")
    category: str = Field(..., description="Configuration category")
    enabled: bool = Field(default=True, description="Whether enabled")
    config_data: dict = Field(
        default_factory=dict,
        description="Configuration data",
    )


class NovaStudioConfigUpdateRequest(BaseModel):
    """Request body for updating a Nova Studio configuration."""

    name: Optional[str] = Field(None, description="Configuration name")
    description: Optional[str] = Field(None, description="Configuration description")
    category: Optional[str] = Field(None, description="Configuration category")
    enabled: Optional[bool] = Field(None, description="Whether enabled")
    config_data: Optional[dict] = Field(None, description="Configuration data")


class NovaStudioSkillItem(BaseModel):
    """Nova Studio skill item for marketplace display."""

    id: str = Field(..., description="Skill identifier")
    name: str = Field(..., description="Skill name")
    description: str = Field(default="", description="Skill description")
    version: str = Field(default="", description="Skill version (remote latest)")
    author: str = Field(default="", description="Skill author")
    icon: str = Field(default="", description="Skill icon URL")
    installed: bool = Field(default=False, description="Whether installed")
    installed_version: str = Field(default="", description="Installed skill version")
    has_update: bool = Field(default=False, description="Whether a newer version is available")
    category: str = Field(default="general", description="Skill category")


class NovaStudioMcpItem(BaseModel):
    """Nova Studio MCP client item for marketplace display."""

    id: str = Field(..., description="MCP client identifier")
    name: str = Field(..., description="MCP client name")
    description: str = Field(default="", description="MCP client description")
    version: str = Field(default="", description="MCP client version (remote latest)")
    author: str = Field(default="", description="MCP client author")
    icon: str = Field(default="", description="MCP client icon URL")
    configured: bool = Field(default=False, description="Whether configured")
    installed_version: str = Field(default="", description="Installed MCP version")
    has_update: bool = Field(default=False, description="Whether a newer version is available")
    category: str = Field(default="general", description="MCP category")


class NovaStudioMarketplaceSection(BaseModel):
    """Marketplace section with items."""

    id: str = Field(..., description="Section identifier")
    title: str = Field(..., description="Section title")
    description: str = Field(default="", description="Section description")
    items: list = Field(default_factory=list, description="Section items")
    total_count: int = Field(default=0, description="Total items count")
    marketplace_url: str = Field(default="", description="Link to online marketplace")
