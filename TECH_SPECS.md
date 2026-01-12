# PolySportsLab 巨鲸追踪器 - 技术规格说明书

## 1. 架构设计

本应用采用 **Serverless（无服务器）** 和 **Edge-first（边缘优先）** 架构，完全部署在 Cloudflare 技术栈上。

```mermaid
graph TD
    User[用户浏览器] -->|HTTPS| Pages[Cloudflare Pages (前端)]
    Pages -->|API 请求| Workers[Cloudflare Workers (后端)]
    Workers -->|Cron 定时触发| PolyAPI[PolySportsLab API]
    Workers -->|读/写| D1[Cloudflare D1 (数据库)]
```

### 1.1 组件
*   **前端**：React (Vite) + Tailwind CSS + Recharts。托管于 **Cloudflare Pages**。
*   **后端**：Cloudflare Workers (TypeScript/Hono)。处理 API 请求和定时任务。
*   **数据库**：Cloudflare D1 (SQLite)。存储历史市场数据。

## 2. 数据库设计 (D1)

数据库包含一个主表 `market_history`（对应原有的 SQLite 设计）。

```sql
CREATE TABLE IF NOT EXISTS market_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    market_id TEXT NOT NULL,
    market_title TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    volume REAL,
    liquidity REAL,
    price_yes REAL,
    price_no REAL,
    whale_concentration REAL,
    smart_money_direction TEXT,
    top10_concentration REAL
);

-- 创建索引以优化按市场和时间的查询
CREATE INDEX IF NOT EXISTS idx_market_timestamp ON market_history (market_id, timestamp);
```

## 3. 后端 API (Workers)

后端提供一套 RESTful API。

### 3.1 接口列表

| 方法 | 路径 | 描述 | 查询参数 |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/markets` | 获取受追踪的市场列表 | `limit` |
| `GET` | `/api/history` | 获取历史数据 | `marketId`, `start`, `end` |
| `GET` | `/api/latest` | 获取所有市场的最新快照 | 无 |
| `POST` | `/api/fetch` | 手动触发数据抓取（需 Admin 密钥） | 无 |

### 3.2 定时任务 (Cron)
*   **频率**：每 5 分钟执行一次（可在 `wrangler.toml` 中配置）。
*   **逻辑**：
    1.  使用 `auth_session_v2`（存储在 Secrets 中）对 PolySportsLab API 进行身份验证。
    2.  获取 Top 20 热门市场。
    3.  对每个市场抓取巨鲸分析数据 (Whale Analysis)。
    4.  将结果批量插入 D1 数据库。

## 4. 本地开发流程

我们使用 `wrangler` 实现统一的本地开发体验。

### 4.1 前置要求
*   Node.js (v18+)
*   Cloudflare 账号
*   Wrangler CLI (`npm install -g wrangler`)

### 4.2 后端设置
1.  初始化 Worker：`npm create cloudflare@latest`
2.  配置 `wrangler.toml`：
    ```toml
    name = "nbawhaletracker-api"
    main = "src/index.ts"
    compatibility_date = "2024-01-01"
    
    [[d1_databases]]
    binding = "DB"
    database_name = "market-history"
    database_id = "<你的_D1_ID>"
    ```
3.  本地运行：`wrangler dev`（模拟 Workers + D1 环境）。

### 4.3 前端设置
1.  初始化 React：`npm create vite@latest frontend -- --template react-ts`
2.  配置代理（在 `vite.config.ts` 中）：将 `/api` 请求转发至 `http://localhost:8787` (Worker)。
3.  本地运行：`npm run dev`

## 5. 部署指南

### 5.1 数据库迁移
```bash
wrangler d1 execute market-history --file=./schema.sql
```

### 5.2 后端部署
```bash
# 设置密钥
wrangler secret put AUTH_COOKIE

# 部署
wrangler deploy
```

### 5.3 前端部署
将 GitHub 仓库连接到 Cloudflare Pages。
*   **构建命令**：`npm run build`
*   **输出目录**：`dist`
*   **环境变量**：`VITE_API_URL`（如果不使用代理）。
