import { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { Card, Row, Col, Button, Spin, Empty, Typography, Space, Tag, message } from "antd";
import { ReloadOutlined, StarFilled, DownloadOutlined } from "@ant-design/icons";
import type {
  NovaStudioOverview,
  NovaStudioMarketplaceSection,
} from "../../api/types";
import { novaStudioApi, NovaProviderItem } from "../../api/modules/novaStudio";
import api from "../../api";
import styles from "./index.module.less";

const { Title, Text, Paragraph } = Typography;

interface ItemCardProps {
  item: {
    id: string;
    name: string;
    description: string;
    version: string;
    author: string;
    installed?: boolean;
    configured?: boolean;
    installed_version?: string;
    has_update?: boolean;
    category?: string;
  };
  sectionId: string;
  onInstall?: (id: string) => void;
  onUpdate?: (id: string) => void;
  installingId?: string | null;
}

function ItemCard({ item, sectionId, onInstall, onUpdate, installingId }: ItemCardProps) {
  const { t } = useTranslation();

  return (
    <Card hoverable size="small" className={styles.itemCard}>
      <div className={styles.itemIcon}>
        <StarFilled style={{ fontSize: 24, color: "#faad14" }} />
      </div>
      <Title level={5} className={styles.itemTitle}>
        {item.name}
      </Title>
      <Paragraph type="secondary" ellipsis={{ rows: 2 }} className={styles.itemDesc}>
        {item.description || "No description"}
      </Paragraph>
      {item.category && (
        <div className={styles.itemCategory}>
          <Text type="secondary" style={{ fontSize: 11 }}>{item.category}</Text>
        </div>
      )}
      <div className={styles.itemMeta}>
        {item.installed_version && (
          <Text type="secondary" style={{ fontSize: 12 }}>
            v{item.installed_version}
            {item.has_update && item.version && <> → v{item.version}</>}
          </Text>
        )}
        {!item.installed_version && (
          <Text type="secondary" style={{ fontSize: 12 }}>
            v{item.version}
          </Text>
        )}
        {item.installed !== undefined && (
          <Tag color={item.installed ? "green" : "default"}>
            {item.installed ? t("novaStudio.installed") : t("novaStudio.notInstalled")}
          </Tag>
        )}
        {item.configured !== undefined && (
          <Tag color={item.configured ? "green" : "default"}>
            {item.configured ? t("novaStudio.configured") : t("novaStudio.notConfigured")}
          </Tag>
        )}
        {item.has_update && onUpdate && (
          <Button
            type="primary"
            size="small"
            icon={<ReloadOutlined />}
            onClick={() => onUpdate(item.id)}
            loading={installingId === item.id}
          >
            {t("novaStudio.update")}
          </Button>
        )}
        {!item.has_update && !item.installed && onInstall && sectionId === "skills" && (
          <Button
            type="primary"
            size="small"
            icon={<DownloadOutlined />}
            onClick={() => onInstall(item.id)}
            loading={installingId === item.id}
          >
            {t("novaStudio.install")}
          </Button>
        )}
        {!item.has_update && !item.configured && onInstall && sectionId === "mcp" && (
          <Button
            type="primary"
            size="small"
            icon={<DownloadOutlined />}
            onClick={() => onInstall(item.id)}
            loading={installingId === item.id}
          >
            {t("novaStudio.install")}
          </Button>
        )}
      </div>
    </Card>
  );
}

interface SectionCardProps {
  section: NovaStudioMarketplaceSection;
  onRefresh: () => void;
  loading: boolean;
  onInstall?: (id: string) => void;
  onUpdate?: (id: string) => void;
  installingId?: string | null;
}

function SectionCard({
  section,
  onRefresh,
  loading,
  onInstall,
  onUpdate,
  installingId,
}: SectionCardProps) {
  const { t } = useTranslation();

  return (
    <Card
      className={styles.sectionCard}
      title={
        <Space>
          <span>{section.title}</span>
          <Tag color="blue">{section.total_count}</Tag>
        </Space>
      }
      extra={
        <Space>
          <Button icon={<ReloadOutlined />} onClick={onRefresh} loading={loading}>
            {t("novaStudio.refresh")}
          </Button>
        </Space>
      }
    >
      <Paragraph type="secondary">{section.description}</Paragraph>
      {section.items.length > 0 ? (
        <Row gutter={[16, 16]}>
          {section.items.slice(0, 8).map((item: unknown) => {
            const itemData = item as {
              id: string;
              name: string;
              description: string;
              version: string;
              author: string;
              installed?: boolean;
              configured?: boolean;
              installed_version?: string;
              has_update?: boolean;
              category?: string;
            };
            return (
              <Col xs={24} sm={12} md={6} key={itemData.id}>
                <ItemCard
                  item={itemData}
                  sectionId={section.id}
                  onInstall={onInstall}
                  onUpdate={onUpdate}
                  installingId={installingId}
                />
              </Col>
            );
          })}
        </Row>
      ) : (
        <Empty description={t("novaStudio.noItems")} image={Empty.PRESENTED_IMAGE_SIMPLE} />
      )}
    </Card>
  );
}

interface ProviderCardProps {
  item: NovaProviderItem;
  onInstall: (providerId: string) => void;
  installing: boolean;
}

function ProviderCard({ item, onInstall, installing }: ProviderCardProps) {
  const { t } = useTranslation();

  return (
    <Card hoverable size="small" className={styles.itemCard}>
      <div className={styles.itemIcon}>
        <StarFilled style={{ fontSize: 24, color: "#faad14" }} />
      </div>
      <Title level={5} className={styles.itemTitle}>
        {item.name}
      </Title>
      <Paragraph type="secondary" ellipsis={{ rows: 2 }} className={styles.itemDesc}>
        {item.description || "No description"}
      </Paragraph>
      <div className={styles.providerModels}>
        <Text type="secondary" style={{ fontSize: 11 }}>
          {t("novaStudio.models")}: {item.models?.map((m) => m.name).join(", ") || "N/A"}
        </Text>
      </div>
      <div className={styles.itemMeta}>
        <Text type="secondary" style={{ fontSize: 12 }}>
          v{item.version}
        </Text>
        {item.installed ? (
          <Tag color="green">{t("novaStudio.installed")}</Tag>
        ) : (
          <Button
            type="primary"
            size="small"
            icon={<DownloadOutlined />}
            onClick={() => onInstall(item.id)}
            loading={installing}
          >
            {t("novaStudio.install")}
          </Button>
        )}
      </div>
    </Card>
  );
}

export default function NovaStudioPage() {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState<string | null>(null);
  const [overview, setOverview] = useState<NovaStudioOverview | null>(null);
  const [providersSection, setProvidersSection] = useState<NovaStudioMarketplaceSection | null>(null);
  const [installingItem, setInstallingItem] = useState<{ id: string; type: string } | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    setError(null);
    try {
      const [data, providers] = await Promise.all([
        api.getNovaStudioOverview(),
        novaStudioApi.getProvidersSection(),
      ]);
      setOverview(data);
      setProvidersSection(providers);
    } catch (err) {
      console.error("Failed to load Nova Studio data:", err);
      setError(err instanceof Error ? err.message : "Failed to load data");
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async (sectionId: string) => {
    setRefreshing(sectionId);
    try {
      if (sectionId === "skills") {
        const data = await api.getSkillsSection();
        setOverview((prev) => (prev ? { ...prev, skills: data } : prev));
      } else if (sectionId === "mcp") {
        const data = await api.getMcpSection();
        setOverview((prev) => (prev ? { ...prev, mcp: data } : prev));
      } else if (sectionId === "configs") {
        const data = await api.getConfigsSection();
        setOverview((prev) => (prev ? { ...prev, configs: data } : prev));
      } else if (sectionId === "providers") {
        const data = await novaStudioApi.getProvidersSection();
        setProvidersSection(data);
      }
    } catch (error) {
      console.error("Failed to refresh section:", error);
    } finally {
      setRefreshing(null);
    }
  };

  const handleInstallProvider = async (providerId: string) => {
    try {
      const result = await novaStudioApi.installProvider(providerId, true);
      message.success(result.message);
      await handleRefresh("providers");
    } catch (error) {
      console.error("Failed to install provider:", error);
      message.error(t("novaStudio.installFailed"));
    }
  };

  const handleInstallSkill = async (skillId: string) => {
    setInstallingItem({ id: skillId, type: "skill" });
    try {
      const result = await novaStudioApi.installSkill(skillId);
      message.success(result.message);
      await handleRefresh("skills");
    } catch (error) {
      console.error("Failed to install skill:", error);
      message.error(t("novaStudio.installFailed"));
    } finally {
      setInstallingItem(null);
    }
  };

  const handleUpdateSkill = async (skillId: string) => {
    await handleInstallSkill(skillId);
  };

  const handleInstallMcp = async (mcpId: string) => {
    setInstallingItem({ id: mcpId, type: "mcp" });
    try {
      const result = await novaStudioApi.installMcp(mcpId);
      message.success(result.message);
      await handleRefresh("mcp");
    } catch (error) {
      console.error("Failed to install MCP:", error);
      message.error(t("novaStudio.installFailed"));
    } finally {
      setInstallingItem(null);
    }
  };

  const handleUpdateMcp = async (mcpId: string) => {
    await handleInstallMcp(mcpId);
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) {
    return (
      <div className={styles.loadingContainer}>
        <Spin size="large" />
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.container}>
        <div className={styles.header}>
          <Title level={2}>{t("novaStudio.title")}</Title>
        </div>
        <Card>
          <div style={{ textAlign: "center", padding: "40px 0" }}>
            <Typography.Text type="danger" style={{ fontSize: 16 }}>
              {error}
            </Typography.Text>
            <div style={{ marginTop: 16 }}>
              <Button type="primary" onClick={loadData} icon={<ReloadOutlined />}>
                {t("novaStudio.retry")}
              </Button>
            </div>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <Title level={2}>{t("novaStudio.title")}</Title>
        <Paragraph type="secondary">{t("novaStudio.description")}</Paragraph>
      </div>

      <div className={styles.sections}>
        {providersSection && (
          <Card
            className={styles.sectionCard}
            title={
              <Space>
                <span>{providersSection.title}</span>
                <Tag color="blue">{providersSection.total_count}</Tag>
              </Space>
            }
            extra={
              <Button
                icon={<ReloadOutlined />}
                onClick={() => handleRefresh("providers")}
                loading={refreshing === "providers"}
              >
                {t("novaStudio.refresh")}
              </Button>
            }
          >
            <Paragraph type="secondary">{providersSection.description}</Paragraph>
            {(providersSection.items as NovaProviderItem[]).length > 0 ? (
              <Row gutter={[16, 16]}>
                {(providersSection.items as NovaProviderItem[]).map((item) => {
                  const isInstalling = installingItem !== null && installingItem.id === item.id && installingItem.type === "provider";
                  return (
                    <Col xs={24} sm={12} md={8} key={item.id}>
                      <ProviderCard
                        item={item}
                        onInstall={(id) => handleInstallProvider(id)}
                        installing={isInstalling}
                      />
                    </Col>
                  );
                })}
              </Row>
            ) : (
              <Empty description={t("novaStudio.noItems")} image={Empty.PRESENTED_IMAGE_SIMPLE} />
            )}
          </Card>
        )}

        {overview?.skills && (
          <SectionCard
            section={overview.skills}
            onRefresh={() => handleRefresh("skills")}
            loading={refreshing === "skills"}
            onInstall={handleInstallSkill}
            onUpdate={handleUpdateSkill}
            installingId={installingItem?.type === "skill" ? installingItem.id : null}
          />
        )}

        {overview?.mcp && (
          <SectionCard
            section={overview.mcp}
            onRefresh={() => handleRefresh("mcp")}
            loading={refreshing === "mcp"}
            onInstall={handleInstallMcp}
            onUpdate={handleUpdateMcp}
            installingId={installingItem?.type === "mcp" ? installingItem.id : null}
          />
        )}

        {overview?.configs && (
          <SectionCard
            section={overview.configs}
            onRefresh={() => handleRefresh("configs")}
            loading={refreshing === "configs"}
          />
        )}
      </div>
    </div>
  );
}
