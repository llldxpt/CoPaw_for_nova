import { Layout, Space, Tooltip, Dropdown } from "antd";
import type { MenuProps } from "antd";
import LanguageSwitcher from "../components/LanguageSwitcher/index";
import ThemeToggleButton from "../components/ThemeToggleButton";
import CodingModeToggle from "../components/CodingModeToggle";
import { useTranslation } from "react-i18next";
import { Button } from "@agentscope-ai/design";
import styles from "./index.module.less";
import api from "../api";
import { openExternalLink } from "../utils/openExternalLink";
import {
  GITHUB_URL,
  getDocsUrl,
  getFeatureDemosUrl,
  getFaqUrl,
  getReleaseNotesUrl,
} from "./constants";
import { useTheme } from "../contexts/ThemeContext";
import { useState, useEffect } from "react";
import { Slot } from "../plugins/registry/Slot";
import {
  GithubOutlined,
  FileTextOutlined,
  ReadOutlined,
  PlayCircleOutlined,
  QuestionCircleOutlined,
  DownOutlined,
} from "@ant-design/icons";

const { Header: AntHeader } = Layout;

export default function Header() {
  const { t, i18n } = useTranslation();
  const { isDark } = useTheme();
  const [version, setVersion] = useState<string>("");

  useEffect(() => {
    api
      .getVersion()
      .then((res) => setVersion(res?.version ?? ""))
      .catch(() => {});
  }, []);

  const handleNavClick = (url: string) => {
    openExternalLink(url);
  };

  return (
    <>
      <AntHeader className={styles.header}>
        <Slot name="header.left" kind="fill" />
        <div className={styles.logoWrapper}>
          <Slot name="header.logo" kind="replace">
            <img
              src={isDark ? "/logo-dark.png" : "/logo-light.png"}
              alt="NovaPaw"
              className={styles.logoImg}
            />
          </Slot>
          <div className={styles.logoDivider} />
          {version && (
            <span className={`${styles.versionBadge} ${styles.versionBadgeDefault}`}>
              v{version}
            </span>
          )}
        </div>
        <Slot name="header.right" kind="fill" />
        <Space size="middle">
          <Dropdown
            menu={{
              items: [
                {
                  key: "tutorial",
                  icon: <ReadOutlined />,
                  label: t("header.tutorial"),
                  onClick: () => handleNavClick(getDocsUrl(i18n.language)),
                },
                {
                  key: "featureDemos",
                  icon: <PlayCircleOutlined />,
                  label: t("header.featureDemos"),
                  onClick: () =>
                    handleNavClick(getFeatureDemosUrl(i18n.language)),
                },
                {
                  key: "changelog",
                  icon: <FileTextOutlined />,
                  label: t("header.changelog"),
                  onClick: () =>
                    handleNavClick(getReleaseNotesUrl(i18n.language)),
                },
                {
                  key: "faq",
                  icon: <QuestionCircleOutlined />,
                  label: t("header.faq"),
                  onClick: () => handleNavClick(getFaqUrl(i18n.language)),
                },
              ] as MenuProps["items"],
            }}
          >
            <Button type="text">
              {t("header.resources")} <DownOutlined />
            </Button>
          </Dropdown>
          <Tooltip title={t("header.github")}>
            <Button
              type="text"
              icon={<GithubOutlined />}
              onClick={() => handleNavClick(GITHUB_URL)}
            >
              {t("header.github")}
            </Button>
          </Tooltip>
          <div className={styles.headerDivider} />
          <CodingModeToggle />
          <div className={styles.headerDivider} />
          <LanguageSwitcher />
          <ThemeToggleButton />
        </Space>
      </AntHeader>
    </>
  );
}
