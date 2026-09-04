import { useState, useCallback } from "react";
import { message } from "antd";
import { useTranslation } from "react-i18next";
import api from "../../../api";

export interface EmbeddingProvider {
  id: string;
  name: string;
  description: string;
  base_url: string;
  api_key: string;
  is_local: boolean;
  is_configured: boolean;
  model_name: string;
  dimensions: number;
  enable_cache: boolean;
  max_input_length: number;
  max_batch_size: number;
  use_dimensions: boolean;
}

export interface EmbeddingConfig {
  provider_id: string;
  model_name: string;
  dimensions: number;
  enable_cache: boolean;
  use_dimensions: boolean;
  max_input_length: number;
  max_batch_size: number;
  base_url: string;
  api_key: string;
}

export function useEmbeddings() {
  const { t } = useTranslation();
  const [providers, setProviders] = useState<EmbeddingProvider[]>([]);
  const [activeConfig, setActiveConfig] = useState<EmbeddingConfig | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAll = useCallback(async (showLoading = true) => {
    if (showLoading) {
      setLoading(true);
    }
    setError(null);

    try {
      const config = await api.getEmbeddingConfig();
      setActiveConfig(config as EmbeddingConfig | null);

      const defaultProviders: EmbeddingProvider[] = [
        {
          id: "nova-embedding",
          name: "Nova Embedding",
          description: "novaEmbeddingDesc",
          base_url: "http://127.0.0.1:1278/v1",
          api_key: "",
          is_local: true,
          is_configured: false,
          model_name: "Nova Embedding",
          dimensions: 1024,
          enable_cache: true,
          max_input_length: 8192,
          max_batch_size: 10,
          use_dimensions: false,
        },
        {
          id: "nova-embedding-cluster",
          name: "Nova Embedding (Cluster)",
          description: "novaEmbeddingClusterDesc",
          base_url: "http://127.0.0.1:15050/v1",
          api_key: "",
          is_local: true,
          is_configured: false,
          model_name: "Nova Embedding",
          dimensions: 1024,
          enable_cache: true,
          max_input_length: 8192,
          max_batch_size: 10,
          use_dimensions: false,
        },
      ];

      if (config?.base_url) {
        const providerIndex = defaultProviders.findIndex(
          (p) => p.base_url === config.base_url,
        );
        if (providerIndex !== -1) {
          defaultProviders[providerIndex].is_configured = true;
          defaultProviders[providerIndex].model_name =
            config.model_name || defaultProviders[providerIndex].model_name;
          defaultProviders[providerIndex].dimensions =
            config.dimensions || defaultProviders[providerIndex].dimensions;
          defaultProviders[providerIndex].enable_cache =
            config.enable_cache ?? true;
          defaultProviders[providerIndex].use_dimensions =
            config.use_dimensions ?? false;
          defaultProviders[providerIndex].max_input_length =
            config.max_input_length || 8192;
          defaultProviders[providerIndex].max_batch_size =
            config.max_batch_size || 10;
          defaultProviders[providerIndex].api_key =
            config.api_key || "";
        }
      }

      setProviders(defaultProviders);
    } catch (err) {
      const msg =
        err instanceof Error ? err.message : t("embeddings.loadError");
      console.error("Failed to load embedding config:", err);
      setError(msg);
    } finally {
      if (showLoading) {
        setLoading(false);
      }
    }
  }, [t]);

  const setActive = useCallback(
    async (provider: EmbeddingProvider) => {
      try {
        setLoading(true);
        const result = await api.setActiveEmbedding({
          provider_id: provider.id,
          base_url: provider.base_url,
          model_name: provider.model_name,
          dimensions: provider.dimensions,
          enable_cache: provider.enable_cache,
          use_dimensions: provider.use_dimensions,
          max_input_length: provider.max_input_length,
          max_batch_size: provider.max_batch_size,
          api_key: provider.api_key,
        });

        setActiveConfig(result as EmbeddingConfig);
        message.success(t("embeddings.activateSuccess", { name: provider.name }));
        await fetchAll(false);
        return true;
      } catch (err) {
        const msg =
          err instanceof Error ? err.message : t("embeddings.activateFailed");
        message.error(msg);
        return false;
      } finally {
        setLoading(false);
      }
    },
    [fetchAll, t],
  );

  const saveConfig = useCallback(
    async (providerId: string, config: Partial<EmbeddingConfig>) => {
      try {
        setLoading(true);
        const provider = providers.find((p) => p.id === providerId);
        if (!provider) return false;

        await api.saveEmbeddingConfig({
          provider_id: providerId,
          model_name: config.model_name || provider.model_name,
          dimensions: config.dimensions || provider.dimensions,
          enable_cache: config.enable_cache ?? provider.enable_cache,
          use_dimensions: config.use_dimensions ?? provider.use_dimensions,
          max_input_length: config.max_input_length || provider.max_input_length,
          max_batch_size: config.max_batch_size || provider.max_batch_size,
          base_url: provider.base_url,
          api_key: config.api_key || provider.api_key,
        });
        message.success(t("embeddings.saveSuccess"));
        await fetchAll(false);
        return true;
      } catch (err) {
        const msg =
          err instanceof Error ? err.message : t("embeddings.saveFailed");
        message.error(msg);
        return false;
      } finally {
        setLoading(false);
      }
    },
    [providers, fetchAll, t],
  );

  const testConnection = useCallback(
    async (
      providerId: string,
      baseUrl: string,
      modelName: string,
    ): Promise<{ success: boolean; message: string }> => {
      try {
        setLoading(true);
        const result = await api.testEmbeddingConnection({
          provider_id: providerId,
          base_url: baseUrl,
          model_name: modelName,
        });
        if (result.success) {
          message.success(t("embeddings.testSuccess"));
        } else {
          message.error(result.message || t("embeddings.testFailed"));
        }
        return result;
      } catch (err) {
        const msg = err instanceof Error ? err.message : t("embeddings.testFailed");
        message.error(msg);
        return { success: false, message: msg };
      } finally {
        setLoading(false);
      }
    },
    [t],
  );

  return {
    providers,
    activeConfig,
    loading,
    error,
    fetchAll,
    setActive,
    saveConfig,
    testConnection,
  };
}
