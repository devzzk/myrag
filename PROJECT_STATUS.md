# myrag - 项目状态报告

## 阶段一：MVP - 已完成 ✅

### 已实现的功能

| 功能 | 状态 | 说明 |
|------|------|------|
| 项目架构搭建 | ✅ | 模块化设计，参考 RAG-Challenge-2 |
| PDF 解析 | ✅ | 支持 MinerU（推荐）和 PyPDF2（备用） |
| 文档分块 | ✅ | 基于 LangChain 的递归分块 |
| 向量化存储 | ✅ | DashScope Embedding + FAISS |
| 语义检索 | ✅ | 余弦相似度搜索 |
| RAG 问答 | ✅ | DashScope Qwen 模型 |
| 引用展示 | ✅ | 显示文档名和页码 |
| Streamlit 前端 | ✅ | 友好的图形界面 |
| 文档管理 | ✅ | 上传、导入、重建知识库 |

### 项目文件结构

```
myrag/
├── app/
│   └── streamlit_app.py          # Streamlit 前端界面
├── src/
│   ├── __init__.py
│   ├── config.py                 # 配置管理（PipelineConfig, RunConfig）
│   ├── pipeline.py               # 主流程（RAGPipeline）
│   ├── pdf_parsing.py            # PDF 解析（MinerUParser, SimplePDFParser）
│   ├── text_splitter.py          # 文本分块（TextSplitter, DocumentChunk）
│   ├── ingestion.py              # 向量化与存储（VectorStore, IngestionPipeline）
│   ├── retrieval.py              # 检索（Retriever）
│   ├── api_requests.py           # API 请求（BaseDashscopeProcessor, APIProcessor）
│   └── prompts.py                # 提示词模板
├── scripts/
│   └── test_pipeline.py          # 测试脚本
├── spec/
│   └── planned/
│       └── 20260622-personal-rag-phased-plan.md  # 原始需求规格
├── data/                         # 数据目录（自动创建）
│   └── stock_data/
│       ├── pdf_reports/          # PDF 文档存放
│       ├── debug_data/           # 中间解析结果
│       └── databases/            # 向量库和分块数据
├── requirements.txt              # 依赖包列表
├── .env.example                  # 环境变量示例
├── .gitignore
├── README.md                     # 使用说明
├── start.py                      # 快速启动脚本
└── PROJECT_STATUS.md             # 本文档
```

### 快速开始

#### 1. 安装依赖

```bash
pip install -r requirements.txt
```

#### 2. 配置 API Key

复制 `.env.example` 为 `.env`，填入 DashScope API Key：

```
DASHSCOPE_API_KEY=your_actual_api_key
```

#### 3. 启动系统

方式一：使用启动脚本（推荐）
```bash
python start.py
```

方式二：直接启动 Streamlit
```bash
streamlit run app/streamlit_app.py
```

#### 4. 使用流程

1. 浏览器打开 http://localhost:8501
2. 在侧边栏上传 PDF 文档
3. 点击「导入文档」
4. 在主界面提问！

### 验收标准检查

| 验收项 | 状态 | 说明 |
|--------|------|------|
| PDF 解析并分块 | ✅ | 支持 MinerU 和 PyPDF2 |
| DashScope 集成 | ✅ | Embedding + Chat |
| 问题格式支持 | ✅ | 支持 text+kind |
| 引用来源展示 | ✅ | 显示文档名和页码 |
| 无结果时拒答 | ✅ | 明确提示无相关内容 |
| Streamlit 界面 | ✅ | 完整的交互界面 |
| 文档删除/重建 | ✅ | 支持重建知识库 |
| 端到端闭环 | ✅ | 完整流程可用 |

### 技术选型

- **PDF 解析**：MinerU（高质量）/ PyPDF2（简单）
- **LLM**：DashScope Qwen-Turbo
- **Embedding**：DashScope Text-Embedding-V1
- **向量库**：FAISS
- **前端**：Streamlit
- **分块**：LangChain RecursiveCharacterTextSplitter

### 下一步（阶段二）

- [ ] 扫描版 PDF OCR
- [ ] 表格识别与处理
- [ ] 查询重写
- [ ] 混合检索（BM25 + 向量）
- [ ] 父文档检索
- [ ] LLM 重排
- [ ] 元数据过滤

### 注意事项

1. MinerU 是可选的，系统会自动降级到简单解析器
2. 需要有效的 DashScope API Key
3. 数据默认保存在 `data/` 目录下，已在 .gitignore 中
4. 首次运行会自动创建必要的目录结构

## 总结

阶段一 MVP 已成功实现！系统具备了：
- ✅ 完整的 RAG 流程
- ✅ 用户友好的界面
- ✅ 可扩展的架构

可以安全地进行测试和使用了。
