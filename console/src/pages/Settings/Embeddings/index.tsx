import { useEffect } from "react";
import { Button, Card, Form, Input, Switch, Spin, Space, InputNumber, Divider, Tag } from "antd";
import { useTranslation } from "react-i18next";
import { useEmbeddings, type EmbeddingProvider, type EmbeddingConfig } from "./useEmbeddings";
import styles from "./index.module.less";

interface EmbeddingCardProps {
  provider: EmbeddingProvider;
  isActive: boolean;
  onSave: (config: Partial<EmbeddingConfig>) => Promise<boolean>;
  onActivate: () => Promise<boolean>;
  onTest: () => Promise<{ success: boolean; message: string }>;
  loading: boolean;
}

function EmbeddingCard({
  provider,
  isActive,
  onSave,
  onActivate,
  onTest,
  loading,
}: EmbeddingCardProps) {
  const { t } = useTranslation();
  const [form] = Form.useForm();

  useEffect(() => {
    form.setFieldsValue({
      model_name: provider.model_name,
      dimensions: provider.dimensions,
      enable_cache: provider.enable_cache,
      use_dimensions: provider.use_dimensions,
      max_input_length: provider.max_input_length,
      max_batch_size: provider.max_batch_size,
      api_key: provider.api_key,
    });
  }, [provider.id, form]);

  const handleSave = async () => {
    const values = form.getFieldsValue();
    await onSave({
      model_name: values.model_name,
      dimensions: values.dimensions,
      enable_cache: values.enable_cache,
      use_dimensions: values.use_dimensions,
      max_input_length: values.max_input_length,
      max_batch_size: values.max_batch_size,
      api_key: values.api_key,
    });
  };

  const handleActivate = async () => {
    const values = form.getFieldsValue();
    const config = {
      ...values,
      model_name: values.model_name,
      dimensions: values.dimensions,
      enable_cache: values.enable_cache,
      use_dimensions: values.use_dimensions,
      max_input_length: values.max_input_length,
      max_batch_size: values.max_batch_size,
      api_key: values.api_key,
    };
    Object.assign(provider, config);
    await onActivate();
  };

  return (
    <Card
      title={
        <Space>
          <span>{provider.name}</span>
          {isActive && <Tag color="blue">{t("embeddings.active", "Active")}</Tag>}
        </Space>
      }
      extra={
        <Tag>{provider.id}</Tag>
      }
      style={{
        borderColor: isActive ? "#1890ff" : undefined,
        borderWidth: isActive ? 2 : 1,
      }}
    >
      <p style={{ marginBottom: 16, color: "#666" }}>{t(`embeddings.${provider.description}`)}</p>

      <div style={{ marginBottom: 16, padding: 12, backgroundColor: "#f5f5f5", borderRadius: 6 }}>
        <div style={{ fontSize: 12, color: "#888", marginBottom: 4 }}>
          {t("embeddings.baseUrl", "Base URL")}
        </div>
        <div style={{ fontFamily: "monospace", fontSize: 13 }}>{provider.base_url}</div>
      </div>

      <Form
        form={form}
        layout="vertical"
        disabled={loading}
      >
        <Form.Item
          name="model_name"
          label={t("embeddings.modelName", "Model Name")}
          rules={[{ required: true, message: t("embeddings.modelNameRequired", "Model name is required") }]}
        >
          <Input placeholder={t("embeddings.modelNamePlaceholder")} />
        </Form.Item>

        <Form.Item
          name="dimensions"
          label={t("embeddings.dimensions", "Embedding Dimensions")}
          tooltip={t("embeddings.dimensionsTip", "Number of dimensions for the embedding vector")}
        >
          <InputNumber min={1} max={4096} style={{ width: "100%" }} />
        </Form.Item>

        <Form.Item
          name="max_input_length"
          label={t("embeddings.maxInputLength", "Max Input Length")}
          tooltip={t("embeddings.maxInputLengthTip", "Maximum number of tokens for input text")}
        >
          <InputNumber min={1} max={100000} style={{ width: "100%" }} />
        </Form.Item>

        <Form.Item
          name="max_batch_size"
          label={t("embeddings.maxBatchSize", "Max Batch Size")}
          tooltip={t("embeddings.maxBatchSizeTip", "Maximum number of texts to batch in one request")}
        >
          <InputNumber min={1} max={1000} style={{ width: "100%" }} />
        </Form.Item>

        <Form.Item
          name="enable_cache"
          label={t("embeddings.enableCache", "Enable Cache")}
          valuePropName="checked"
          tooltip={t("embeddings.enableCacheTip", "Cache embeddings to avoid recomputation")}
        >
          <Switch />
        </Form.Item>

        <Form.Item
          name="use_dimensions"
          label={t("embeddings.useDimensions", "Use Custom Dimensions")}
          valuePropName="checked"
          tooltip={t("embeddings.useDimensionsTip", "Request specific dimensions from the API (if supported)")}
        >
          <Switch />
        </Form.Item>

        <Divider />

        <Space wrap>
          <Button
            type="primary"
            onClick={handleActivate}
            loading={loading}
            disabled={isActive}
          >
            {isActive ? t("embeddings.activated", "Activated") : t("embeddings.activate", "Activate")}
          </Button>
          <Button
            onClick={handleSave}
            loading={loading}
          >
            {t("embeddings.save", "Save Configuration")}
          </Button>
          <Button
            onClick={onTest}
            loading={loading}
          >
            {t("embeddings.testConnection", "Test Connection")}
          </Button>
        </Space>
      </Form>
    </Card>
  );
}

function LoadingState({
  message: msg,
  error,
  onRetry,
}: {
  message?: string;
  error?: boolean;
  onRetry?: () => void;
}) {
  const { t } = useTranslation();

  return (
    <div style={{ textAlign: "center", padding: 48 }}>
      {error ? (
        <>
          <div style={{ color: "#ff4d4f", marginBottom: 16 }}>{msg}</div>
          {onRetry && (
            <Button type="primary" onClick={onRetry}>
              {t("common.retry", "Retry")}
            </Button>
          )}
        </>
      ) : (
        <>
          <Spin size="large" />
          <div style={{ marginTop: 16, color: "#666" }}>{msg || t("common.loading", "Loading...")}</div>
        </>
      )}
    </div>
  );
}

function PageHeader({
  title,
  description,
}: {
  title: string;
  description?: string;
}) {
  return (
    <div style={{ marginBottom: 16 }}>
      <h2 style={{ fontSize: 20, fontWeight: 600, marginBottom: 8 }}>{title}</h2>
      {description && (
        <p style={{ color: "#666", margin: 0 }}>{description}</p>
      )}
    </div>
  );
}

function EmbeddingsPage() {
  const { t } = useTranslation();
  const { providers, activeConfig, loading, error, fetchAll, setActive, saveConfig, testConnection } =
    useEmbeddings();

  useEffect(() => {
    fetchAll();
  }, [fetchAll]);

  const handleTest = async (provider: EmbeddingProvider) => {
    return await testConnection(
      provider.id,
      provider.base_url,
      provider.model_name,
    );
  };

  const handleSave = async (providerId: string, config: Partial<EmbeddingConfig>) => {
    return await saveConfig(providerId, config);
  };

  const handleActivate = async (provider: EmbeddingProvider) => {
    return await setActive(provider);
  };

  const isProviderActive = (provider: EmbeddingProvider) => {
    if (!activeConfig?.base_url) return false;
    return activeConfig.base_url === provider.base_url;
  };

  return (
    <div className={styles.settingsPage}>
      {loading && !providers.length ? (
        <LoadingState message={t("embeddings.loading", "Loading embedding configuration...")} />
      ) : error && !providers.length ? (
        <LoadingState
          message={error}
          error
          onRetry={fetchAll}
        />
      ) : (
        <>
          <div className={styles.providersBlock}>
            <div className={styles.sectionHeaderRow}>
              <PageHeader
                title={t("embeddings.title", "Embedding Models")}
                description={t(
                  "embeddings.description",
                  "Configure embedding models for semantic search and memory features",
                )}
              />
            </div>

            <div className={styles.providerCards}>
              {providers.map((provider) => (
                <EmbeddingCard
                  key={provider.id}
                  provider={provider}
                  isActive={isProviderActive(provider)}
                  onSave={(config) => handleSave(provider.id, config)}
                  onActivate={() => handleActivate(provider)}
                  onTest={() => handleTest(provider)}
                  loading={loading}
                />
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default EmbeddingsPage;
