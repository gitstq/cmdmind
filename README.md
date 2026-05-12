<div align="center">

# 🧠 CmdMind

**AI-Powered Terminal Command Intelligence**

**智能终端命令历史管理工具**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/gitstq/cmdmind?style=social)](https://github.com/gitstq/cmdmind/stargazers)

[English](#english) | [简体中文](#简体中文) | [繁體中文](#繁體中文)

</div>

---

<a name="english"></a>
## 🇺🇸 English

### 🎉 Introduction

**CmdMind** is an intelligent terminal command history management tool that revolutionizes how you interact with your command line. Unlike traditional history tools that only store commands, CmdMind understands your commands semantically and helps you find, organize, and reuse them efficiently.

**Key Pain Points Solved:**
- 🔍 **Can't find that command** you ran last week? Semantic search finds it by description
- 📊 **No insights** into your command patterns? Get detailed analytics and productivity scores
- 🏷️ **Messy history**? Auto-categorization keeps everything organized
- 💡 **Forget complex commands**? Save favorites and templates for quick access

### ✨ Core Features

| Feature | Description |
|---------|-------------|
| 🧠 **Semantic Search** | Search commands using natural language - "find docker commands" or "list files" |
| 📊 **Smart Analytics** | Visualize your command patterns, peak productivity hours, and category distribution |
| 🏷️ **Auto-Categorization** | Commands automatically classified into Git, Docker, NPM, Python, and 15+ categories |
| ⭐ **Favorites System** | Mark frequently used commands for instant access |
| 🔍 **Fuzzy Matching** | Find commands even with typos or partial matches |
| 💾 **Local-First** | All data stored locally in SQLite - no cloud required |
| 🎨 **Beautiful TUI** | Interactive terminal interface built with Textual |
| 📈 **Productivity Score** | Track your command-line proficiency over time |

### 🚀 Quick Start

#### Requirements
- Python 3.10 or higher
- pip (Python package manager)

#### Installation

```bash
# Install from PyPI (recommended)
pip install cmdmind

# Or install from source
git clone https://github.com/gitstq/cmdmind.git
cd cmdmind
pip install -e .
```

#### Basic Usage

```bash
# Launch interactive TUI
cmdmind tui

# Add a command
cmdmind add "docker ps -a"

# Search commands
cmdmind search "git"

# List recent commands
cmdmind list

# View statistics
cmdmind stats

# Get help
cmdmind --help
```

### 📖 Detailed Usage Guide

#### Interactive TUI Mode

Launch the beautiful terminal interface:

```bash
cmdmind tui
```

**Keyboard Shortcuts:**
| Key | Action |
|-----|--------|
| `s` | Focus search |
| `r` | Refresh list |
| `f` | Toggle favorite |
| `d` | Delete command |
| `Enter` | Copy to clipboard |
| `q` | Quit |

#### Command Line Interface

```bash
# Add with metadata
cmdmind add "npm run build" --shell bash --desc "Build the project"

# Search with filters
cmdmind search "docker" --category docker --limit 20

# View command details
cmdmind show 42

# Export history
cmdmind export --output history.json

# Clear all history
cmdmind clear --force
```

### 💡 Design Philosophy

CmdMind was built with these principles:

1. **Privacy First**: All data stays on your machine
2. **Speed Matters**: SQLite + FTS5 for instant search
3. **Developer Friendly**: CLI-first with optional TUI
4. **Extensible**: Modular architecture for easy customization

### 📦 Deployment

CmdMind is a pure Python package with no external services required:

```bash
# Development
pip install -e ".[dev]"

# Run tests
pytest tests/

# Build package
python -m build
```

### 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'feat: add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<a name="简体中文"></a>
## 🇨🇳 简体中文

### 🎉 项目介绍

**CmdMind** 是一款智能终端命令历史管理工具，彻底改变您与命令行的交互方式。传统历史工具只能存储命令，而 CmdMind 能够语义化理解您的命令，帮助您高效查找、组织和复用它们。

**解决的核心痛点：**
- 🔍 **找不到上周执行过的命令？** 语义搜索通过描述即可找到
- 📊 **不了解自己的命令模式？** 获取详细的分析和生产力评分
- 🏷️ **历史记录混乱？** 自动分类让一切井井有条
- 💡 **忘记复杂命令？** 收藏夹和模板系统快速访问

### ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🧠 **语义搜索** | 使用自然语言搜索命令 - "查找docker命令" 或 "列出文件" |
| 📊 **智能分析** | 可视化命令模式、高峰工作时段和类别分布 |
| 🏷️ **自动分类** | 命令自动归类到 Git、Docker、NPM、Python 等15+类别 |
| ⭐ **收藏系统** | 标记常用命令，即时访问 |
| 🔍 **模糊匹配** | 即使有拼写错误或部分匹配也能找到命令 |
| 💾 **本地优先** | 所有数据存储在本地 SQLite - 无需云端 |
| 🎨 **精美TUI** | 基于 Textual 构建的交互式终端界面 |
| 📈 **生产力评分** | 追踪您的命令行熟练度提升 |

### 🚀 快速开始

#### 环境要求
- Python 3.10 或更高版本
- pip (Python 包管理器)

#### 安装方式

```bash
# 从 PyPI 安装（推荐）
pip install cmdmind

# 或从源码安装
git clone https://github.com/gitstq/cmdmind.git
cd cmdmind
pip install -e .
```

#### 基本使用

```bash
# 启动交互式TUI界面
cmdmind tui

# 添加命令
cmdmind add "docker ps -a"

# 搜索命令
cmdmind search "git"

# 列出最近命令
cmdmind list

# 查看统计
cmdmind stats

# 获取帮助
cmdmind --help
```

### 📖 详细使用指南

#### 交互式TUI模式

启动精美的终端界面：

```bash
cmdmind tui
```

**快捷键：**
| 按键 | 操作 |
|------|------|
| `s` | 聚焦搜索 |
| `r` | 刷新列表 |
| `f` | 切换收藏 |
| `d` | 删除命令 |
| `Enter` | 复制到剪贴板 |
| `q` | 退出 |

#### 命令行界面

```bash
# 添加带元数据的命令
cmdmind add "npm run build" --shell bash --desc "构建项目"

# 带过滤条件的搜索
cmdmind search "docker" --category docker --limit 20

# 查看命令详情
cmdmind show 42

# 导出历史记录
cmdmind export --output history.json

# 清空所有历史
cmdmind clear --force
```

### 💡 设计理念

CmdMind 基于以下原则构建：

1. **隐私优先**：所有数据保留在本地
2. **速度至上**：SQLite + FTS5 实现即时搜索
3. **开发者友好**：CLI优先，可选TUI
4. **可扩展**：模块化架构，易于定制

### 📦 部署指南

CmdMind 是纯 Python 包，无需外部服务：

```bash
# 开发环境
pip install -e ".[dev]"

# 运行测试
pytest tests/

# 构建包
python -m build
```

### 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: 添加新功能'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 提交 Pull Request

### 📄 开源协议

本项目采用 MIT 协议开源 - 详见 [LICENSE](LICENSE) 文件。

---

<a name="繁體中文"></a>
## 🇹🇼 繁體中文

### 🎉 專案介紹

**CmdMind** 是一款智慧型終端命令歷史管理工具，徹底改變您與命令列的互動方式。傳統歷史工具只能儲存命令，而 CmdMind 能夠語意化理解您的命令，幫助您高效查找、組織和複用它們。

**解決的核心痛點：**
- 🔍 **找不到上週執行過的命令？** 語意搜尋透過描述即可找到
- 📊 **不了解自己的命令模式？** 取得詳細的分析和生產力評分
- 🏷️ **歷史記錄混亂？** 自動分類讓一切井然有序
- 💡 **忘記複雜命令？** 收藏夾和範本系統快速存取

### ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🧠 **語意搜尋** | 使用自然語言搜尋命令 - 「尋找docker命令」或「列出檔案」 |
| 📊 **智慧分析** | 視覺化命令模式、高峰工作時段和類別分佈 |
| 🏷️ **自動分類** | 命令自動歸類到 Git、Docker、NPM、Python 等15+類別 |
| ⭐ **收藏系統** | 標記常用命令，即時存取 |
| 🔍 **模糊匹配** | 即使有拼寫錯誤或部分匹配也能找到命令 |
| 💾 **本地優先** | 所有資料儲存在本地 SQLite - 無需雲端 |
| 🎨 **精美TUI** | 基於 Textual 建構的互動式終端介面 |
| 📈 **生產力評分** | 追蹤您的命令列熟練度提升 |

### 🚀 快速開始

#### 環境要求
- Python 3.10 或更高版本
- pip (Python 套件管理器)

#### 安裝方式

```bash
# 從 PyPI 安裝（推薦）
pip install cmdmind

# 或從原始碼安裝
git clone https://github.com/gitstq/cmdmind.git
cd cmdmind
pip install -e .
```

#### 基本使用

```bash
# 啟動互動式TUI介面
cmdmind tui

# 新增命令
cmdmind add "docker ps -a"

# 搜尋命令
cmdmind search "git"

# 列出最近命令
cmdmind list

# 查看統計
cmdmind stats

# 取得說明
cmdmind --help
```

### 📖 詳細使用指南

#### 互動式TUI模式

啟動精美的終端介面：

```bash
cmdmind tui
```

**快速鍵：**
| 按鍵 | 操作 |
|------|------|
| `s` | 聚焦搜尋 |
| `r` | 重新整理列表 |
| `f` | 切換收藏 |
| `d` | 刪除命令 |
| `Enter` | 複製到剪貼簿 |
| `q` | 離開 |

#### 命令列介面

```bash
# 新增帶元資料的命令
cmdmind add "npm run build" --shell bash --desc "建置專案"

# 帶過濾條件的搜尋
cmdmind search "docker" --category docker --limit 20

# 查看命令詳情
cmdmind show 42

# 匯出歷史記錄
cmdmind export --output history.json

# 清空所有歷史
cmdmind clear --force
```

### 💡 設計理念

CmdMind 基於以下原則建構：

1. **隱私優先**：所有資料保留在本地
2. **速度至上**：SQLite + FTS5 實現即時搜尋
3. **開發者友善**：CLI優先，可選TUI
4. **可擴展**：模組化架構，易於客製化

### 📦 部署指南

CmdMind 是純 Python 套件，無需外部服務：

```bash
# 開發環境
pip install -e ".[dev]"

# 執行測試
pytest tests/

# 建置套件
python -m build
```

### 🤝 貢獻指南

歡迎貢獻程式碼！請遵循以下步驟：

1. Fork 本儲存庫
2. 建立功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交變更 (`git commit -m 'feat: 新增功能'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 提交 Pull Request

### 📄 開源授權

本專案採用 MIT 授權條款開源 - 詳見 [LICENSE](LICENSE) 檔案。

---

<div align="center">

**Made with ❤️ by the CmdMind Team**

[⬆ Back to Top](#cmdmind)

</div>
