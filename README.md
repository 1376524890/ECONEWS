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

- `POST /api/v1/analyze`
  输入新闻标题、正文、来源、发布时间和可选资产代码，输出符合规范的 JSON 结果。
- `POST /api/v1/crawlers/run-once`
  手动触发采集周期；网络不可用时自动降级为内置样本。
- `GET /api/v1/dashboard/overview`
- `GET /api/v1/dashboard/feed`
- `GET /api/v1/dashboard/analyses`
- `GET /api/v1/system/heartbeats`

## 前端页面

- `/` 数据看板：资讯滚播、NIS 雷达、传导链路图、心跳面板、最新分析结果。
- `/analyzer` 新闻分析：提交单条新闻并查看结构化 JSON 输出。

## 启动方式

### 1. 后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

### 2. 前端

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## 当前实现策略

- NLP 层采用“接口预留 + 规则平替”结构。
- 当前默认使用 `HeuristicNLPProvider` 做事件分类、主体提取和情绪强度估计。
- 后续可在 `backend/app/services/` 下替换为 Chinese-FinBERT 或兼容 OpenAI / GLM 的流式模型接口。
- 事件研究模块优先尝试 `AkShare`，再尝试 `Tushare`。
- 若缺少资产代码、接口不可用或行情不足，`verification_result` 会按要求回落为：
  `当前缺少市场数据，暂无法进行事件研究法验证`

## 建议的下一步增强

- 将 `HeuristicNLPProvider` 替换为真实 BERT 多任务模型，补齐 NER、多标签分类和情绪打分。
- 为两个爬虫加详情页解析、代理池、增量指纹持久化和重试限速。
- 将内存存储切换为 PostgreSQL + Redis，并加入 Celery 或消息队列。
- 接入真实资产映射规则，把“新闻主体 -> 行业/标的池”的关系从静态模板提升为知识库配置。
