# -*- coding: utf-8 -*-
"""API routes for Nova Studio integration."""

import logging
import os
import urllib.request
import zipfile
import io
from typing import List, Dict
from pathlib import Path

from fastapi import APIRouter, HTTPException, Path as PathParam
from pydantic import BaseModel

try:
    from packaging import version
except ImportError:
    version = None

from ...config import load_config, save_config
from ...constant import WORKING_DIR
from .schemas_nova_studio import (
    NovaStudioConfig,
    NovaStudioConfigCreateRequest,
    NovaStudioConfigUpdateRequest,
    NovaStudioSkillItem,
    NovaStudioMcpItem,
    NovaStudioMarketplaceSection,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/nova-studio", tags=["nova-studio"])

NOVA_STUDIO_CONFIG_FILE = WORKING_DIR / "nova_studio_configs.json"

REMOTE_BASE_URL = os.environ.get(
    "NOVA_STUDIO_BASE_URL",
    "https://www.firstarpc.com/download/aipc_files/skills_markets"
)

MARKETPLACE_URLS = {
    "skills": f"{REMOTE_BASE_URL}/skills",
    "mcp": f"{REMOTE_BASE_URL}/mcps",
    "configs": f"{REMOTE_BASE_URL}/configs",
}


def _fetch_remote_json(relative_path: str) -> Dict:
    """Fetch JSON data from remote server."""
    url = f"{REMOTE_BASE_URL}/{relative_path}"
    try:
        logger.info(f"Fetching {url}")
        with urllib.request.urlopen(url, timeout=30) as response:
            import json
            data = json.loads(response.read().decode("utf-8"))
            logger.info(f"Successfully fetched {url}")
            return data
    except Exception as e:
        logger.error(f"Failed to fetch {url}: {e}")
        return {}


def _load_nova_market_index() -> Dict:
    """Load Nova Studio market index from remote server or local fallback."""
    remote_data = _fetch_remote_json("market.json")
    if remote_data:
        return remote_data
    
    local_file = Path(__file__).parent.parent.parent.parent.parent / "nova_skills_markets" / "market.json"
    if local_file.exists():
        import json
        with open(local_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"version": "1.0"}


def _load_skills_from_remote() -> List[Dict]:
    """Load skills list from remote server."""
    index = _load_nova_market_index()
    skills_url = "skills/skills.json"
    
    remote_data = _fetch_remote_json(skills_url)
    if remote_data:
        return remote_data.get("skills", [])
    
    local_file = Path(__file__).parent.parent.parent.parent.parent / "nova_skills_markets" / skills_url
    if local_file.exists():
        import json
        with open(local_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("skills", [])
    return []


def _load_mcps_from_remote() -> List[Dict]:
    """Load MCPs list from remote server."""
    mcps_url = "mcps/mcps.json"
    
    remote_data = _fetch_remote_json(mcps_url)
    if remote_data:
        return remote_data.get("mcps", [])
    
    local_file = Path(__file__).parent.parent.parent.parent.parent / "nova_skills_markets" / mcps_url
    if local_file.exists():
        import json
        with open(local_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("mcps", [])
    return []


def _load_providers_from_remote() -> Dict:
    """Load providers config from remote server."""
    configs_url = "configs/configs.json"
    
    remote_configs = _fetch_remote_json(configs_url)
    if not remote_configs:
        local_file = Path(__file__).parent.parent.parent.parent.parent / "nova_skills_markets" / configs_url
        if local_file.exists():
            import json
            with open(local_file, "r", encoding="utf-8") as f:
                remote_configs = json.load(f)
        else:
            return {"version": "1.0.0", "providers": {}, "default_provider": {}}
    
    for config in remote_configs.get("configs", []):
        if config.get("id") == "nova-providers":
            download_url = config.get("download_url", "")
            if download_url:
                providers_data = _fetch_remote_json(download_url)
                if providers_data:
                    return providers_data
    
    return {"version": "1.0.0", "providers": {}, "default_provider": {}}


def _load_configs_from_remote() -> List[Dict]:
    """Load configs list from remote server."""
    configs_url = "configs/configs.json"
    
    remote_configs = _fetch_remote_json(configs_url)
    if not remote_configs:
        local_file = Path(__file__).parent.parent.parent.parent.parent / "nova_skills_markets" / configs_url
        if local_file.exists():
            import json
            with open(local_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("configs", [])
    return remote_configs.get("configs", [])


def _load_nova_market_data() -> Dict:
    """Load Nova Studio market data (combined for backward compatibility)."""
    return {
        "skills": _load_skills_from_remote(),
        "mcps": _load_mcps_from_remote(),
    }


def _load_nova_providers_config() -> Dict:
    """Load Nova providers configuration from remote server or local fallback."""
    return _load_providers_from_remote()


def _load_nova_studio_configs() -> List[Dict]:
    """Load Nova Studio configurations from file."""
    if NOVA_STUDIO_CONFIG_FILE.exists():
        import json
        with open(NOVA_STUDIO_CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _save_nova_studio_configs(configs: List[Dict]) -> None:
    """Save Nova Studio configurations to file."""
    import json
    with open(NOVA_STUDIO_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(configs, f, indent=2, ensure_ascii=False)


@router.get("", response_model=Dict)
async def get_nova_studio_overview() -> Dict:
    """Get Nova Studio overview with all sections."""
    try:
        skills_section = await get_skills_section()
        mcp_section = await get_mcp_section()
        configs_section = await get_configs_section()

        return {
            "skills": skills_section,
            "mcp": mcp_section,
            "configs": configs_section,
        }
    except Exception as e:
        logger.exception("Error loading Nova Studio overview")
        raise HTTPException(500, detail=f"Failed to load Nova Studio data: {str(e)}")


@router.get("/skills", response_model=NovaStudioMarketplaceSection)
async def get_skills_section() -> NovaStudioMarketplaceSection:
    """Get skills section with marketplace-style display."""
    try:
        market_data = _load_nova_market_data()
        from ...agents.skills_manager import list_installed_skills_with_versions, get_builtin_skills_dir

        installed_skills = list_installed_skills_with_versions()
        installed_ids = set(installed_skills.keys())

        builtin_skills_dir = get_builtin_skills_dir()
        builtin_skill_ids = set()
        if builtin_skills_dir.exists():
            builtin_skill_ids = {d.name for d in builtin_skills_dir.iterdir() if d.is_dir()}

        items = []
        for skill in market_data.get("skills", []):
            skill_id = skill.get("id", "")

            if skill_id in builtin_skill_ids:
                continue

            is_installed = skill_id in installed_ids
            remote_version = skill.get("version", "1.0.0")
            installed_ver = installed_skills.get(skill_id, "")

            has_update = False
            if is_installed and installed_ver and remote_version:
                try:
                    has_update = version.parse(remote_version) > version.parse(installed_ver)
                except Exception:
                    has_update = remote_version != installed_ver
            elif is_installed and not installed_ver and remote_version:
                has_update = True

            items.append(
                NovaStudioSkillItem(
                    id=skill_id,
                    name=skill.get("name", ""),
                    description=skill.get("description", ""),
                    version=remote_version,
                    author=skill.get("author", "Nova Markets"),
                    icon="",
                    installed=is_installed,
                    installed_version=installed_ver,
                    has_update=has_update,
                    category=", ".join(skill.get("tags", [])),
                ).model_dump()
            )

        return NovaStudioMarketplaceSection(
            id="skills",
            title="Skills",
            description="Extend agent capabilities with skills from Nova Studio",
            items=items,
            total_count=len(items),
            marketplace_url=f"{REMOTE_BASE_URL}/skills",
        )
    except Exception as e:
        logger.exception("Error loading skills section")
        raise HTTPException(500, detail=f"Failed to load skills: {str(e)}")


@router.get("/mcp", response_model=NovaStudioMarketplaceSection)
async def get_mcp_section() -> NovaStudioMarketplaceSection:
    """Get MCP clients section with marketplace-style display."""
    try:
        market_data = _load_nova_market_data()
        from ...config import load_config

        config = load_config()
        configured_mcps = {}
        if hasattr(config, "mcp") and config.mcp and hasattr(config.mcp, "clients"):
            configured_mcps = dict(config.mcp.clients)

        items = []
        for mcp in market_data.get("mcps", []):
            mcp_id = mcp.get("id", "")
            is_configured = mcp_id in configured_mcps

            installed_ver = ""
            if is_configured:
                client_config = configured_mcps.get(mcp_id)
                if client_config:
                    installed_ver = getattr(client_config, "version", "")

            items.append(
                NovaStudioMcpItem(
                    id=mcp_id,
                    name=mcp.get("name", ""),
                    description=mcp.get("description", ""),
                    version=mcp.get("version", "1.0.0"),
                    author=mcp.get("author", "Nova Markets"),
                    icon="",
                    configured=is_configured,
                    installed_version=installed_ver,
                    has_update=False,
                    category=mcp.get("type", "general"),
                ).model_dump()
            )

        return NovaStudioMarketplaceSection(
            id="mcp",
            title="MCP Clients",
            description="Model Context Protocol clients from Nova Studio",
            items=items,
            total_count=len(items),
            marketplace_url=f"{REMOTE_BASE_URL}/mcps",
        )
    except Exception as e:
        logger.exception("Error loading MCP section")
        raise HTTPException(500, detail=f"Failed to load MCP clients: {str(e)}")


@router.get("/configs", response_model=NovaStudioMarketplaceSection)
async def get_configs_section() -> NovaStudioMarketplaceSection:
    """Get configuration areas section."""
    try:
        configs = _load_configs_from_remote()
        return NovaStudioMarketplaceSection(
            id="configs",
            title="Configuration Areas",
            description="Nova Studio integration configurations",
            items=configs,
            total_count=len(configs),
            marketplace_url=f"{REMOTE_BASE_URL}/configs",
        )
    except Exception as e:
        logger.exception("Error loading configs section")
        raise HTTPException(500, detail=f"Failed to load configs: {str(e)}")


@router.get(
    "/configs/{config_id}",
    response_model=NovaStudioConfig,
)
async def get_config(config_id: str = PathParam(...)) -> NovaStudioConfig:
    """Get a specific Nova Studio configuration."""
    configs = _load_nova_studio_configs()
    for cfg in configs:
        if cfg.get("id") == config_id:
            return NovaStudioConfig(**cfg)
    raise HTTPException(404, detail=f"Configuration '{config_id}' not found")


@router.post("/configs", response_model=NovaStudioConfig)
async def create_config(
    request: NovaStudioConfigCreateRequest,
) -> NovaStudioConfig:
    """Create a new Nova Studio configuration."""
    configs = _load_nova_studio_configs()

    config_id = request.name.lower().replace(" ", "-")
    for cfg in configs:
        if cfg.get("id") == config_id:
            raise HTTPException(
                400,
                detail=f"Configuration '{config_id}' already exists",
            )

    new_config = NovaStudioConfig(
        id=config_id,
        name=request.name,
        description=request.description,
        category=request.category,
        enabled=request.enabled,
        config_data=request.config_data,
    )

    configs.append(new_config.model_dump())
    _save_nova_studio_configs(configs)

    return new_config


@router.put(
    "/configs/{config_id}",
    response_model=NovaStudioConfig,
)
async def update_config(
    config_id: str,
    request: NovaStudioConfigUpdateRequest,
) -> NovaStudioConfig:
    """Update an existing Nova Studio configuration."""
    configs = _load_nova_studio_configs()

    for i, cfg in enumerate(configs):
        if cfg.get("id") == config_id:
            update_data = request.model_dump(exclude_unset=True)
            cfg.update(update_data)
            _save_nova_studio_configs(configs)
            return NovaStudioConfig(**cfg)

    raise HTTPException(404, detail=f"Configuration '{config_id}' not found")


@router.delete(
    "/configs/{config_id}",
    response_model=Dict[str, str],
)
async def delete_config(config_id: str) -> Dict[str, str]:
    """Delete a Nova Studio configuration."""
    configs = _load_nova_studio_configs()

    original_count = len(configs)
    configs = [cfg for cfg in configs if cfg.get("id") != config_id]

    if len(configs) == original_count:
        raise HTTPException(404, detail=f"Configuration '{config_id}' not found")

    _save_nova_studio_configs(configs)
    return {"message": f"Configuration '{config_id}' deleted successfully"}


@router.get("/marketplace/urls")
async def get_marketplace_urls() -> Dict[str, str]:
    """Get marketplace URLs."""
    return {
        "base_url": REMOTE_BASE_URL,
        "skills": f"{REMOTE_BASE_URL}/skills",
        "mcp": f"{REMOTE_BASE_URL}/mcps",
        "configs": f"{REMOTE_BASE_URL}/configs",
    }


NOVA_PROVIDERS_FILE = Path(__file__).parent.parent.parent.parent.parent / "nova_skills_markets" / "configs" / "nova_providers.json"
NOVA_SKILLS_MARKET_FILE = Path(__file__).parent.parent.parent.parent.parent / "nova_skills_markets" / "market.json"


def _get_installed_providers():
    """Get currently installed providers from providers.json."""
    from ...providers.store import load_providers_json
    from ...providers.models import ProvidersData
    return load_providers_json()


@router.get("/providers")
async def get_providers_section() -> NovaStudioMarketplaceSection:
    """Get available providers from marketplace (local config)."""
    try:
        nova_config = _load_nova_providers_config()
        installed_data = _get_installed_providers()
        installed_ids = set(installed_data.providers.keys())

        items = []
        for provider_id, provider_info in nova_config.get("providers", {}).items():
            is_installed = provider_id in installed_ids
            model_list = provider_info.get("models", [])
            items.append(
                {
                    "id": provider_id,
                    "name": provider_info.get("name", provider_id),
                    "description": provider_info.get("description", ""),
                    "version": nova_config.get("version", "1.0.0"),
                    "author": "Nova Studio",
                    "installed": is_installed,
                    "models": model_list,
                    "default_base_url": provider_info.get("default_base_url", ""),
                    "chat_model": provider_info.get("chat_model", "OpenAIChatModel"),
                }
            )

        return NovaStudioMarketplaceSection(
            id="providers",
            title="LLM Providers",
            description="Available LLM providers from Nova Studio",
            items=items,
            total_count=len(items),
            marketplace_url="https://marketplace.nova-studio.example.com/providers",
        )
    except Exception as e:
        logger.exception("Error loading providers section")
        raise HTTPException(500, detail=f"Failed to load providers: {str(e)}")


@router.get("/providers/{provider_id}")
async def get_provider_info(provider_id: str = PathParam(...)) -> Dict:
    """Get specific provider info from marketplace."""
    nova_config = _load_nova_providers_config()
    provider_info = nova_config.get("providers", {}).get(provider_id)

    if not provider_info:
        raise HTTPException(404, detail=f"Provider '{provider_id}' not found")

    installed_data = _get_installed_providers()
    is_installed = provider_id in installed_data.providers

    return {
        **provider_info,
        "installed": is_installed,
    }


class ProviderInstallRequest(BaseModel):
    """Request to install a provider."""

    provider_id: str
    set_as_default: bool = True


@router.post("/providers/install")
async def install_provider(request: ProviderInstallRequest) -> Dict:
    """Install a provider from marketplace to local providers.json."""
    nova_config = _load_nova_providers_config()
    provider_info = nova_config.get("providers", {}).get(request.provider_id)

    if not provider_info:
        raise HTTPException(
            404,
            detail=f"Provider '{request.provider_id}' not found in marketplace",
        )

    installed_data = _get_installed_providers()

    installed_data.providers[request.provider_id] = {
        "base_url": provider_info.get("default_base_url", ""),
        "api_key": provider_info.get("api_key", ""),
        "extra_models": [],
        "chat_model": provider_info.get("chat_model", "OpenAIChatModel"),
    }

    if request.set_as_default:
        installed_data.active_llm.provider_id = request.provider_id
        default_model = nova_config.get("default_provider", {}).get("model")
        if default_model:
            installed_data.active_llm.model = default_model

    from ...providers.store import save_providers_json

    save_providers_json(installed_data)

    return {
        "message": f"Provider '{request.provider_id}' installed successfully",
        "provider_id": request.provider_id,
        "set_as_default": request.set_as_default,
    }


@router.get("/providers/config/source")
async def get_providers_config_source() -> Dict:
    """Get the source file path for providers config."""
    return {
        "source_file": str(NOVA_PROVIDERS_FILE),
        "exists": NOVA_PROVIDERS_FILE.exists(),
    }


@router.get("/market/source")
async def get_market_source() -> Dict:
    """Get the source file path for market data."""
    return {
        "source_file": str(NOVA_SKILLS_MARKET_FILE),
        "exists": NOVA_SKILLS_MARKET_FILE.exists(),
    }


class SkillInstallRequest(BaseModel):
    """Request to install a skill."""

    skill_id: str


class McpInstallRequest(BaseModel):
    """Request to install an MCP."""

    mcp_id: str


@router.post("/skills/install")
async def install_skill(request: SkillInstallRequest) -> Dict:
    """Install a skill from marketplace by downloading from remote server."""
    market_data = _load_nova_market_data()
    
    skill = None
    for s in market_data.get("skills", []):
        if s.get("id") == request.skill_id:
            skill = s
            break
    
    if not skill:
        raise HTTPException(404, detail=f"Skill '{request.skill_id}' not found in marketplace")
    
    download_url = skill.get("download_url", "")
    if not download_url:
        raise HTTPException(400, detail="No download URL available")
    
    full_url = f"{REMOTE_BASE_URL}/{download_url}"
    skills_dir = WORKING_DIR / "active_skills" / request.skill_id
    skills_dir.mkdir(parents=True, exist_ok=True)

    try:
        logger.info(f"Downloading skill from {full_url}")
        with urllib.request.urlopen(full_url, timeout=60) as response:
            zip_data = io.BytesIO(response.read())

        with zipfile.ZipFile(zip_data, "r") as zf:
            zf.extractall(skills_dir)

        if not (skills_dir / "SKILL.md").exists():
            for f in skills_dir.rglob("*.md"):
                if "skill" in f.name.lower():
                    break
            else:
                md_files = list(skills_dir.glob("*.md"))
                if md_files:
                    (skills_dir / "SKILL.md").write_text(md_files[0].read_text())

        remote_version = skill.get("version", "")
        remote_name = skill.get("name", request.skill_id)
        remote_description = skill.get("description", "")
        if (skills_dir / "SKILL.md").exists():
            try:
                import frontmatter
                content = (skills_dir / "SKILL.md").read_text(encoding="utf-8")
                if content.startswith("---"):
                    post = frontmatter.loads(content)
                    if remote_version:
                        post.metadata["version"] = remote_version
                    if remote_name:
                        post.metadata["name"] = remote_name
                    if remote_description:
                        post.metadata["description"] = remote_description
                    with open(skills_dir / "SKILL.md", "w", encoding="utf-8") as f:
                        f.write(str(post))
                else:
                    metadata_lines = []
                    if remote_version:
                        metadata_lines.append(f'version: "{remote_version}"')
                    if remote_name:
                        metadata_lines.append(f"name: {remote_name}")
                    if remote_description:
                        metadata_lines.append(f'description: "{remote_description}"')

                    new_content = "---\n"
                    new_content += "\n".join(metadata_lines)
                    new_content += "\n---\n\n"
                    new_content += content
                    (skills_dir / "SKILL.md").write_text(new_content, encoding="utf-8")
            except Exception as e:
                logger.warning(f"Failed to update skill metadata in SKILL.md: {e}")
        
        logger.info(f"Skill '{request.skill_id}' installed to {skills_dir}")
        
        return {
            "message": f"Skill '{request.skill_id}' installed successfully",
            "skill_id": request.skill_id,
            "install_path": str(skills_dir),
        }
    except Exception as e:
        logger.exception(f"Failed to install skill '{request.skill_id}'")
        raise HTTPException(500, detail=f"Failed to install skill: {str(e)}")


@router.post("/mcp/install")
async def install_mcp(request: McpInstallRequest) -> Dict:
    """Install an MCP from marketplace by downloading from remote server."""
    market_data = _load_nova_market_data()
    
    mcp = None
    for m in market_data.get("mcps", []):
        if m.get("id") == request.mcp_id:
            mcp = m
            break
    
    if not mcp:
        raise HTTPException(404, detail=f"MCP '{request.mcp_id}' not found in marketplace")
    
    download_url = mcp.get("download_url", "")
    if not download_url:
        raise HTTPException(400, detail="No download URL available")
    
    full_url = f"{REMOTE_BASE_URL}/{download_url}"
    mcp_dir = WORKING_DIR / "mcp_servers" / request.mcp_id
    mcp_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        logger.info(f"Downloading MCP from {full_url}")
        with urllib.request.urlopen(full_url, timeout=60) as response:
            zip_data = io.BytesIO(response.read())
        
        with zipfile.ZipFile(zip_data, "r") as zf:
            zf.extractall(mcp_dir)
        
        mcp_type = mcp.get("type", "stdio")
        mcp_command = mcp.get("command", "")
        mcp_args = mcp.get("args", [])
        
        from ...config import load_config, save_config
        from ...config.config import MCPClientConfig
        
        config = load_config()
        if not hasattr(config, "mcp") or config.mcp is None:
            from ...config.config import MCPConfig
            config.mcp = MCPConfig()
        if not hasattr(config.mcp, "clients"):
            config.mcp.clients = {}
        
        config.mcp.clients[request.mcp_id] = MCPClientConfig(
            name=mcp.get("name", request.mcp_id),
            description=mcp.get("description", ""),
            enabled=True,
            transport=mcp_type,
            command=mcp_command,
            args=mcp_args,
        )
        
        save_config(config)
        
        logger.info(f"MCP '{request.mcp_id}' installed and registered to {mcp_dir}")
        
        return {
            "message": f"MCP '{request.mcp_id}' installed successfully",
            "mcp_id": request.mcp_id,
            "install_path": str(mcp_dir),
            "type": mcp.get("type", "stdio"),
            "command": mcp.get("command", ""),
            "args": mcp.get("args", []),
        }
    except Exception as e:
        logger.exception(f"Failed to install MCP '{request.mcp_id}'")
        raise HTTPException(500, detail=f"Failed to install MCP: {str(e)}")
