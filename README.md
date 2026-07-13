# IdeaHub - GitHub Project Discovery Tool

[English](#english) | [中文](#中文)

---

<a id="english"></a>
## 🌟 Overview

IdeaHub is an intelligent tool that helps you discover relevant public GitHub projects based on your ideas. It combines AI-powered search with a beautiful showcase interface, allowing you to explore, chat about, and save project discoveries.

## Current implementation

The repository now contains a working local-first implementation:

- FastAPI searches GitHub's public repository API and saves every search as a SQLite dataset.
- The React dashboard lists saved datasets, shows project owner avatars and `owner/repository` paths, and provides dataset-grounded chat answers.
- The reusable [`search-github-projects`](.codex/skills/search-github-projects/SKILL.md) skill documents safe public search, immutable dataset saving, and IdeaHub deployment boundaries.
- Docker Compose runs the frontend behind Nginx and proxies `/api` to the backend. Copy `.env.example` to `.env`, optionally set `GITHUB_TOKEN`, then run `docker compose up --build -d`.

For a remote deployment, build and health-check locally first, then provide the target host, access method, domain/port, and rollback expectation. IdeaHub deliberately does not deploy repositories found by a search.

## ✨ Features

### 🔍 Smart GitHub Search
- Search public GitHub repositories using natural language
- AI-enhanced query understanding for better results
- Filter by language, stars, license, and more

### 💾 Dataset Management
- Automatically save search results as structured datasets
- Export datasets in JSON/CSV formats
- Track search history and discoveries

### 💬 AI Chat Interface
- Chat about discovered projects
- Get insights and comparisons
- Refine your search through conversation

### 🖼️ Project Showcase
- Visual project cards with screenshots/images
- Quick access to repository links
- Detailed project information display

### 🌐 Bilingual Support
- Full English and Chinese interface
- Seamless language switching

## 🏗️ Tech Stack

### Frontend
- **React 18** with TypeScript
- **Vite** - Fast build tool
- **Tailwind CSS** - Modern styling
- **React Query** - Data fetching
- **i18next** - Internationalization
- **Zustand** - State management

### Backend
- **FastAPI** - Modern Python API framework
- **Pydantic** - Data validation
- **SQLAlchemy** - Database ORM
- **GitHub API** - Repository search
- **SQLite/PostgreSQL** - Data storage

### Deployment
- Docker & Docker Compose
- Nginx reverse proxy
- Environment-based configuration

## 📁 Project Structure

```
goldHub/
├── frontend/                 # React + TypeScript frontend
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/           # Page components
│   │   ├── hooks/           # Custom React hooks
│   │   ├── services/        # API services
│   │   ├── stores/          # State management
│   │   ├── i18n/            # Internationalization
│   │   ├── types/           # TypeScript types
│   │   └── utils/           # Utility functions
│   ├── public/              # Static assets
│   └── package.json
│
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── api/             # API routes
│   │   ├── models/          # Database models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic
│   │   ├── core/            # Core config & security
│   │   └── utils/           # Utilities
│   ├── datasets/            # Saved datasets
│   ├── requirements.txt
│   └── main.py
│
├── docker/                   # Docker configurations
│   ├── Dockerfile.frontend
│   ├── Dockerfile.backend
│   └── nginx.conf
│
├── docs/                     # Documentation
├── README.md
├── docker-compose.yml
└── .gitignore
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.10+
- Docker & Docker Compose (for deployment)

### Development Setup

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Docker Deployment
```bash
docker-compose up -d
```

Access the app at `http://localhost:80`

## 🔧 Configuration

### Environment Variables

Create `.env` file in root directory:

```env
# GitHub API
GITHUB_TOKEN=your_github_token_here

# Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
DATABASE_URL=sqlite:///./ideahub.db

# Frontend
VITE_API_URL=http://localhost:8000

# Deployment
DOMAIN=yourdomain.com
```

## 📊 Dataset Format

Saved datasets follow this structure:

```json
{
  "id": "uuid",
  "query": "search query",
  "timestamp": "2026-07-10T12:00:00Z",
  "results": [
    {
      "name": "repo-name",
      "owner": "owner",
      "description": "description",
      "url": "https://github.com/owner/repo",
      "stars": 1000,
      "language": "TypeScript",
      "topics": ["react", "typescript"],
      "screenshot": "path/to/screenshot.png"
    }
  ]
}
```

## 🎯 API Endpoints

### Search
- `POST /api/search` - Search GitHub repositories
- `GET /api/search/history` - Get search history

### Datasets
- `GET /api/datasets` - List all datasets
- `GET /api/datasets/{id}` - Get specific dataset
- `POST /api/datasets/save` - Save search results
- `DELETE /api/datasets/{id}` - Delete dataset

### Chat
- `POST /api/chat` - Chat with AI about projects
- `GET /api/chat/history` - Get chat history

### Projects
- `GET /api/projects` - List showcased projects
- `POST /api/projects` - Add project to showcase
- `GET /api/projects/{id}/screenshot` - Get project screenshot

## 🌍 Internationalization

Supported languages:
- English (en)
- 中文 (zh)

Add translations in `frontend/src/i18n/locales/`

## 📝 License

MIT

---

<a id="中文"></a>
## 🌟 项目概述

IdeaHub 是一个智能工具,帮助你根据想法发现相关的公开 GitHub 项目。它结合了 AI 驱动的搜索和美观的展示界面,让你能够探索、讨论和保存项目发现。

## ✨ 功能特性

### 🔍 智能 GitHub 搜索
- 使用自然语言搜索公开 GitHub 仓库
- AI 增强的查询理解,获得更好的结果
- 按语言、星标、许可证等筛选

### 💾 数据集管理
- 自动将搜索结果保存为结构化数据集
- 支持导出 JSON/CSV 格式
- 跟踪搜索历史和发现

### 💬 AI 聊天界面
- 就发现的项目进行聊天
- 获取洞察和比较
- 通过对话优化搜索

### 🖼️ 项目展示
- 带有截图/图片的可视化项目卡片
- 快速访问仓库链接
- 详细的项目信息展示

### 🌐 双语支持
- 完整的中英文界面
- 无缝语言切换

## 🏗️ 技术栈

### 前端
- **React 18** + TypeScript
- **Vite** - 快速构建工具
- **Tailwind CSS** - 现代样式
- **React Query** - 数据获取
- **i18next** - 国际化
- **Zustand** - 状态管理

### 后端
- **FastAPI** - 现代 Python API 框架
- **Pydantic** - 数据验证
- **SQLAlchemy** - 数据库 ORM
- **GitHub API** - 仓库搜索
- **SQLite/PostgreSQL** - 数据存储

### 部署
- Docker & Docker Compose
- Nginx 反向代理
- 基于环境的配置

## 🚀 快速开始

### 前置要求
- Node.js 18+
- Python 3.10+
- Docker & Docker Compose(用于部署)

### 开发环境设置

#### 后端
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

#### 前端
```bash
cd frontend
npm install
npm run dev
```

### Docker 部署
```bash
docker-compose up -d
```

访问应用:`http://localhost:80`

## 🔧 配置

### 环境变量

在根目录创建 `.env` 文件:

```env
# GitHub API
GITHUB_TOKEN=your_github_token_here

# 后端
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
DATABASE_URL=sqlite:///./ideahub.db

# 前端
VITE_API_URL=http://localhost:8000

# 部署
DOMAIN=yourdomain.com
```

## 📊 数据集格式

保存的数据集遵循以下结构:

```json
{
  "id": "uuid",
  "query": "搜索查询",
  "timestamp": "2026-07-10T12:00:00Z",
  "results": [
    {
      "name": "仓库名称",
      "owner": "所有者",
      "description": "描述",
      "url": "https://github.com/owner/repo",
      "stars": 1000,
      "language": "TypeScript",
      "topics": ["react", "typescript"],
      "screenshot": "screenshot/path.png"
    }
  ]
}
```

## 🎯 API 接口

### 搜索
- `POST /api/search` - 搜索 GitHub 仓库
- `GET /api/search/history` - 获取搜索历史

### 数据集
- `GET /api/datasets` - 列出所有数据集
- `GET /api/datasets/{id}` - 获取特定数据集
- `POST /api/datasets/save` - 保存搜索结果
- `DELETE /api/datasets/{id}` - 删除数据集

### 聊天
- `POST /api/chat` - 与 AI 聊天讨论项目
- `GET /api/chat/history` - 获取聊天历史

### 项目
- `GET /api/projects` - 列出展示的项目
- `POST /api/projects` - 添加项目到展示
- `GET /api/projects/{id}/screenshot` - 获取项目截图

## 🌍 国际化

支持的语言:
- English (en)
- 中文 (zh)

在 `frontend/src/i18n/locales/` 添加翻译

## 📝 许可证

MIT
