export interface NovaStudioSkillItem {
  id: string;
  name: string;
  description: string;
  version: string;
  author: string;
  icon: string;
  installed: boolean;
  installed_version: string;
  has_update: boolean;
  category: string;
}

export interface NovaStudioMcpItem {
  id: string;
  name: string;
  description: string;
  version: string;
  author: string;
  icon: string;
  configured: boolean;
  installed_version: string;
  has_update: boolean;
  category: string;
}

export interface NovaStudioConfig {
  id: string;
  name: string;
  description: string;
  category: string;
  enabled: boolean;
  config_data: Record<string, unknown>;
}

export interface NovaStudioMarketplaceSection {
  id: string;
  title: string;
  description: string;
  items: unknown[];
  total_count: number;
  marketplace_url: string;
}

export interface NovaStudioOverview {
  skills: NovaStudioMarketplaceSection;
  mcp: NovaStudioMarketplaceSection;
  configs: NovaStudioMarketplaceSection;
}

export interface MarketplaceUrls {
  base_url: string;
  skills: string;
  mcp: string;
  configs: string;
}
