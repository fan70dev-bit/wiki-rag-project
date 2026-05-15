# 🚀 Wiki Pro RAG System
### 维基百科双引擎混合检索与流式 AI 智能研读系统

本系统是一款专为处理海量维基百科数据设计的 **混合检索增强生成 (Hybrid RAG) 系统**。系统核心采用前后端分离架构，通过高效的 **ETL 数据清洗管道** 将分布式 **Kafka** 流式数据流落库，构建了 **“SQLite 精准文本匹配 + ChromaDB 向量语义检索”** 的高性能混合检索双引擎。应用层全面打通了基于阿里云通义千问大模型的 **Server-Sent Events (SSE) 流式打字机响应管道**，支持全文一键智能总结与多轮片段深度研读对话。

本项目作为软件工程/大数据技术课程的优秀期末大作业设计，在系统解耦、高并发缓存、高维向量降维检索、大模型提示词工程等维度均具备完整的准工业级实战参考价值。

---

## 🛠️ 技术栈选型 (Technical Stack)

* **前端应用 (Frontend)**：Vue 3 (Composition API) + Vite + Vue Router 4 (多页面路由) + TailwindCSS (响应式 UI) + Tailwind Typography (`marked` 实时富文本渲染) + Vue-i18n (中日双语国际化)
* **后端应用 (Backend)**：FastAPI (Python 高性能异步 Web 框架) + Uvicorn (ASGI 服务器) + `python-dotenv` (准生产级环境隔离配置管理)
* **分布式消息层 (Message Queue)**：Apache Kafka (处理维基百科海量流式高吞吐输入，实现架构层面的彻底解耦)
* **双引擎数据库层 (Hybrid Databases)**：
    * **关系型结构化存储**：SQLite 3 (支持毫秒级高频精准 `LIKE` 模糊匹配、全文存储与 ID 快速索引)
    * **非结构化向量存储**：ChromaDB (持久化本地向量库，用于存储及查询 384 维 BGE 语义嵌入向量)
* **文本向量化算法 (Embedding Model)**：`BAAI/bge-small-zh-v1.5` (离线高精度的中文语义表示归一化)
* **大模型生成引擎 (LLM Engine)**：Alibaba Cloud DashScope (阿里云通义千问 `qwen-plus` 商业级大模型，开启 `stream=True` 管道)

---

## 📂 项目目录结构 (Project Structure)

```text
wiki-rag-project/
├── .gitignore                  # Git 全局保镖（排除数据库、依赖包与私密环境配置）
├── README.md                   # 项目核心技术文档
│
├── wiki-backend/               # 🐍 Python 后端系统根目录
│   ├── .env                    # 后端私密环境变量配置（包含 API Key 与本地路径，不上传 GitHub）
│   ├── main.py                 # 后端主程序入口（全量路由挂载与 CORS 跨域中央件配置）
│   ├── ingest_v2.py            # 分布式 Kafka 流式数据 ETL 清洗、语义嵌入与混合落库脚本
│   ├── core/
│   │   └── config.py           # 环境变量中央加载器
│   ├── database/
│   │   └── manager.py          # 双引擎数据库联合管理器
│   └── routers/
│       ├── search.py           # 精准/语义混合搜索路由模块
│       └── ai_agent.py         # 智能大模型研读 Agent 路由（支持 SSE 协议流式文本生成）
│
└── wiki-rag-web/               # ⚡ Vue 3 前端系统根目录
    ├── .env                    # 前端局部环境变量（控制 API 请求基准地址，不上传 GitHub）
    ├── package.json            # 前端项目依赖与构建脚本配置
    ├── vite.config.js          # Vite 构建核心配置
    └── src/
        ├── main.js             # 前端主入口
        ├── App.vue             # 根骨架组件（集成全局顶部导航与 KeepAlive 状态保活逻辑）
        ├── router.js           # Vue Router 4 核心路由拦截分配器
        ├── style.css           # 全局样式
        └── views/
            ├── Home.vue        # 搜索主页面（集成双检索模式切换、分页器及空状态兜底）
            └── Article.vue     # 沉浸式阅读与 AI 智能助页面（集成左侧长文、底部一键总结与右侧 Copilot 对话框）