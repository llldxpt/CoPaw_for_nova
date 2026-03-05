import { request } from "../request";
import type {
  NovaStudioOverview,
  NovaStudioMarketplaceSection,
  NovaStudioConfig,
  MarketplaceUrls,
} from "../types";

export interface NovaProviderItem {
  id: string;
  name: string;
  description: string;
  version: string;
  author: string;
  installed: boolean;
  models: Array<{
    id: string;
    name: string;
    description: string;
  }>;
  default_base_url: string;
  chat_model: string;
}

export interface ProviderInstallRequest {
  provider_id: string;
  set_as_default: boolean;
}

export interface ProviderInstallResponse {
  message: string;
  provider_id: string;
  set_as_default: boolean;
}

export const novaStudioApi = {
  getNovaStudioOverview: () => request<NovaStudioOverview>("/nova-studio"),
  getOverview: () => request<NovaStudioOverview>("/nova-studio"),

  getSkillsSection: () =>
    request<NovaStudioMarketplaceSection>("/nova-studio/skills"),

  getMcpSection: () => request<NovaStudioMarketplaceSection>("/nova-studio/mcp"),

  getConfigsSection: () =>
    request<NovaStudioMarketplaceSection>("/nova-studio/configs"),

  getConfig: (configId: string) =>
    request<NovaStudioConfig>(`/nova-studio/configs/${encodeURIComponent(configId)}`),

  createConfig: (config: Omit<NovaStudioConfig, "id">) =>
    request<NovaStudioConfig>("/nova-studio/configs", {
      method: "POST",
      body: JSON.stringify(config),
    }),

  updateConfig: (configId: string, config: Partial<NovaStudioConfig>) =>
    request<NovaStudioConfig>(
      `/nova-studio/configs/${encodeURIComponent(configId)}`,
      {
        method: "PUT",
        body: JSON.stringify(config),
      },
    ),

  deleteConfig: (configId: string) =>
    request<{ message: string }>(
      `/nova-studio/configs/${encodeURIComponent(configId)}`,
      {
        method: "DELETE",
      },
    ),

  getMarketplaceUrls: () => request<MarketplaceUrls>("/nova-studio/marketplace/urls"),

  getProvidersSection: () =>
    request<NovaStudioMarketplaceSection>("/nova-studio/providers"),

  getProviderInfo: (providerId: string) =>
    request<NovaProviderItem>(`/nova-studio/providers/${encodeURIComponent(providerId)}`),

  installProvider: (providerId: string, setAsDefault: boolean = true) =>
    request<ProviderInstallResponse>("/nova-studio/providers/install", {
      method: "POST",
      body: JSON.stringify({
        provider_id: providerId,
        set_as_default: setAsDefault,
      }),
    }),

  getProvidersConfigSource: () =>
    request<{ source_file: string; exists: boolean }>(
      "/nova-studio/providers/config/source",
    ),

  getMarketSource: () =>
    request<{ source_file: string; exists: boolean }>(
      "/nova-studio/market/source",
    ),

  installSkill: (skillId: string) =>
    request<{ message: string; skill_id: string; download_url: string }>(
      "/nova-studio/skills/install",
      {
        method: "POST",
        body: JSON.stringify({ skill_id: skillId }),
      },
    ),

  installMcp: (mcpId: string) =>
    request<{
      message: string;
      mcp_id: string;
      download_url: string;
      type: string;
      command: string;
      args: string[];
    }>("/nova-studio/mcp/install", {
      method: "POST",
      body: JSON.stringify({ mcp_id: mcpId }),
    }),
};
