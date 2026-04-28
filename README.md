# EconoNews Intelligence Hub

面向经济新闻自动化分析与量化看板的全栈骨架工程，包含：

- `backend/`: FastAPI 后端、新闻分析服务、爬虫调度、事件研究降级验证。
- `frontend/`: Vue 3 + Vite + ECharts 数据大屏与新闻分析页。

## 项目结构

```text
backend/
  app/
    api/          # REST API
    core/         # 配置
    crawlers/     # 东方财富 / 第一财经采集适配器
    schemas/      # 请求响应模型
    services/     # NLP、评分、事件研究、内存存储
    tasks/        # APScheduler 调度任务
  tests/
frontend/
  src/
    api/          # 接口调用
    components/   # 大屏组件
    router/       # 路由
    views/        # 看板与分析页
```

## 后端能力

- `GET /api/v1/health`
  健康检查端点，返回服务状态。
- `POST /api/v1/analyze`
  输入新闻标题、正文、来源、发布时间和可选资产代码，输出符合规范的 JSON 结果。
- `POST /api/v1/crawlers/run-once`
  手动触发采集周期；网络不可用时自动降级为内置样本。
- `GET /api/v1/dashboard/overview`
  获取看板概览数据。
- `GET /api/v1/dashboard/feed`
  获取新闻资讯流。
- `GET /api/v1/dashboard/analyses`
  获取最近的分析结果列表。
- `GET /api/v1/system/heartbeats`
  获取系统心跳状态。

## 前端页面

- `/` 数据看板：资讯滚播、NIS 雷达、传导链路图、心跳面板、最新分析结果。
- `/analyzer` 新闻分析：提交单条新闻并查看结构化 JSON 输出。

## 快速启动

### 一键启动脚本

项目提供跨平台一键启动脚本，自动完成虚拟环境创建、依赖安装和配置文件生成。

#### macOS / Linux

```bash
# 完整安装并启动所有服务
./start.sh

# 仅安装依赖，不启动服务
./start.sh --setup-only

# 仅启动后端服务
./start.sh --backend-only

# 仅启动前端服务
./start.sh --frontend-only

# 停止所有服务
./start.sh --stop

# 查看服务状态
./start.sh --status
```

#### Windows

```batch
# 完整安装并启动所有服务
start.bat

# 仅安装依赖，不启动服务
start.bat --setup-only

# 仅启动后端服务
start.bat --backend-only

# 仅启动前端服务
start.bat --frontend-only

# 停止所有服务
start.bat --stop

# 查看服务状态
start.bat --status
```

### 首次运行配置

1. 脚本会自动从 `.env.example` 复制创建 `.env` 配置文件
2. 编辑 `backend/.env` 配置必要参数：
   ```ini
   # NLP 提供者类型: heuristic (默认，规则引擎) | bert (预训练模型)
   MODEL_PROVIDER=heuristic
   
   # BERT 模型配置 (仅在 MODEL_PROVIDER=bert 时生效)
   BERT_MODEL_NAME=Chinese-FinBERT
   # 启用 FP16 推理以降低显存占用 (需要 GPU 支持)
   BERT_FP16=false
   
   # Tushare Token (用于事件研究法的行情数据获取)
   TUSHARE_TOKEN=your_token_here
   
   # 默认基准指数
   DEFAULT_BENCHMARK=000300.SH
   ```
3. 访问 http://localhost:5173 使用应用

### 访问地址

| 服务 | 地址 |
|------|------|
| 前端应用 | http://localhost:5173 |
| 后端 API | http://127.0.0.1:8000 |
| API 文档 | http://127.0.0.1:8000/docs |

### 手动启动（可选）

若需要手动启动，可按以下步骤操作：

**后端：**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

**前端：**

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## 经济分析模型与方法

### 分析流程架构

```text
新闻输入 -> NLP分类 -> 事件模板匹配 -> 影响评分计算 -> 传导链路生成 -> 事件研究验证 -> 决策支持输出
```

### 新闻影响评分模型 (NIS)

采用多因子加权模型计算新闻的综合影响力指数：

**核心公式：**

$$NIS = 0.30 \times E + 0.25 \times S + 0.20 \times R + 0.15 \times C + 0.10 \times A$$

**因子定义：**

| 因子 | 名称 | 说明 | 数据来源 |
|------|------|------|----------|
| E | 事件重要性 | 事件类型固有的市场影响力权重 | 事件模板库 |
| S | 情绪强度 | 新闻文本情绪倾向的量化得分 | NLP 情感分析 |
| R | 信源权威度 | 发布渠道的可信度评分 | 来源权威度矩阵 |
| C | 覆盖广度 | 事件影响的宏观覆盖范围 | 事件模板库 |
| A | 资产相关性 | 事件与特定资产的关联程度 | 事件模板库 |

**情绪强度计算公式：**

$$S = \text{clamp}(baseline + 0.2 \times imbalance)$$

其中：
- $baseline = 0.5 + \min(\frac{total}{20}, 0.3)$
- $imbalance = \frac{|positive - negative|}{total}$
- $total = positive\_hits + negative\_hits$

**影响等级划分：**

| NIS 区间 | 影响等级 |
|----------|----------|
| (0, 0.2] | 弱影响 |
| (0.2, 0.4] | 轻度影响 |
| (0.4, 0.6] | 中等影响 |
| (0.6, 0.8] | 较强影响 |
| (0.8, 1.0] | 强影响 |

### 事件研究法验证

采用经典的事件研究法 (Event Study) 验证新闻事件的市场反应：

**异常收益率 (Abnormal Return)：**

$$AR_t = R_{asset,t} - R_{benchmark,t}$$

**累计异常收益率 (Cumulative Abnormal Return)：**

$$CAR_{[T, T+5]} = \sum_{t=T}^{T+5} AR_t$$

**窗口定义：** T日（事件日）至 T+5 日（事件后5个交易日）

**验证逻辑：**
- CAR > 0：市场反应与正向分析一致
- CAR < 0：市场反应偏弱，需警惕逻辑兑现不足

### 事件分类与传导链路

系统支持六类核心经济事件的自动识别与传导分析：

| 事件类型 | 关键词示例 | 典型传导链路 |
|----------|------------|--------------|
| 货币政策 | 降准、降息、MLF、LPR | 货币政策信号 → 流动性改善 → 金融条件宽松 → 宽基指数修复 |
| 财政政策 | 专项债、赤字率、减税 | 财政加码 → 投资消费改善 → 盈利预期修复 → 周期消费受益 |
| 宏观数据 | CPI、PMI、GDP、社融 | 数据公布 → 增长通胀重估 → 股债汇调整 → 风格轮动 |
| 行业政策 | 补贴、监管、限产、牌照 | 政策出台 → 供需变化 → 盈利调整 → 估值重估 |
| 公司经营 | 业绩、回购、并购、减持 | 经营变化 → 盈利修正 → 个股反应 → 行业联动 |
| 国际冲击 | 关税、制裁、美联储、油价 | 冲击发生 → 汇率波动 → 出口链重估 → 风格分化 |

### 信源权威度矩阵

| 来源 | 权威度 (R) |
|------|-----------|
| 中国政府网 | 0.98 |
| 人民银行 | 0.98 |
| 新华社 | 0.95 |
| 统计局 | 0.95 |
| 第一财经 | 0.86 |
| 东方财富 | 0.76 |
| 手动录入 | 0.65 |
| 未知来源 | 0.60 |

## 当前实现策略

### NLP 提供者架构

采用”接口预留 + 动态切换”结构，支持两种模式：

| 模式 | 提供者 | 功能 | 适用场景 |
|------|--------|------|----------|
| `heuristic` | `HeuristicNLPProvider` | 基于关键词规则的事件分类、主体提取、情绪强度估计 | 快速部署，无需 GPU |
| `bert` | `BertNLPProvider` | Zero-Shot 分类、NER 实体识别、金融情感分析 | 高精度分析，需要 GPU |

**BERT 模型组件：**
- Zero-Shot 分类：`mDeBERTa-v3-base-mnli-xnli`
- NER 实体识别：`bert-base-chinese-ner`
- 金融情感分析：`chinese-finbert`

### 数据源降级策略

- 事件研究模块优先尝试 `AkShare`，再尝试 `Tushare`
- 若缺少资产代码、接口不可用或行情不足，`verification_result` 回落为：
  `当前缺少市场数据，暂无法进行事件研究法验证`
- 爬虫网络不可用时自动降级为内置样本数据

## 建议的下一步增强

- 为爬虫添加详情页解析、代理池、增量指纹持久化和重试限速机制
- 将内存存储切换为 PostgreSQL + Redis，并引入 Celery 或消息队列
- 接入真实资产映射规则，将”新闻主体 -> 行业/标的池”的关系从静态模板提升为知识库配置
- 扩展事件模板库，支持更多细分事件类型和传导链路
- 添加用户认证和历史分析记录持久化
