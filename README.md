# myrag - 个人 RAG 知识库系统

基于 MinerU + DashScope + Streamlit 的个人知识库问答系统。

## 阶段一 MVP 功能

✅ PDF 文档解析（支持 MinerU 或简单解析器）  
✅ 文档分块与元数据保留  
✅ 向量化存储（FAISS）  
✅ 语义检索  
✅ RAG 问答（基于 DashScope/Qwen）  
✅ 引用来源展示  
✅ Streamlit 图形界面  
✅ 文档导入与管理

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
cd myrag

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置 API Key

复制 `.env.example` 为 `.env`，并填入你的 DashScope API Key：

```bash
cp .env.example .env
# 编辑 .env 文件，填入 DASHSCOPE_API_KEY
```

获取 API Key：https://dashscope.console.aliyun.com/

### 3. （可选）安装 MinerU

如果需要高质量的 PDF 解析（推荐）：

```bash
# 安装 MinerU
# 参考：https://github.com/opendatalab/MinerU
pip install pdf-extract
```

### 4. 运行系统

```bash
# 启动 Streamlit 前端
streamlit run app/streamlit_app.py
```

然后在浏览器中打开显示的地址（通常是 http://localhost:8501）。

### 5. 使用流程

1. 在侧边栏上传 PDF 文档
2. 点击「导入文档」处理文档
3. 在主界面开始提问！

## 项目结构

```
myrag/
├── app/
│   └── streamlit_app.py          # Streamlit 前端
├── src/
│   ├── __init__.py
│   ├── config.py                 # 配置管理
│   ├── pipeline.py               # 主流程
│   ├── pdf_parsing.py            # PDF 解析（MinerU）
│   ├── text_splitter.py          # 文本分块
│   ├── ingestion.py              # 向量化与存储
│   ├── retrieval.py              # 检索
│   ├── api_requests.py           # API 请求（DashScope）
│   └── prompts.py                # 提示词
├── data/                         # 数据目录（自动创建）
│   └── stock_data/
│       ├── pdf_reports/          # PDF 文档
│       ├── debug_data/           # 中间结果
│       └── databases/            # 向量库
├── spec/                         # 需求规格
├── requirements.txt
├── .env.example
└── README.md
```

## 技术栈

- **PDF 解析**：MinerU（推荐）或 PyPDF2（备用）
- **LLM & Embedding**：DashScope（通义千问）
- **向量存储**：FAISS
- **前端**：Streamlit
- **文本处理**：LangChain

## 开发路线

### 阶段一：MVP（进行中）
- ✅ 基础 RAG 流程
- ✅ Streamlit 前端
- ⏳ 测试与优化

### 阶段二：检索增强
- 🔲 OCR 支持扫描版 PDF
- 🔲 表格识别与处理
- 🔲 查询重写
- 🔲 混合检索（BM25 + 向量）
- 🔲 父文档检索
- 🔲 LLM 重排

### 阶段三：智能编排
- 🔲 意图识别
- 🔲 任务路由
- 🔲 多模型支持
- 🔲 多知识库管理
- 🔲 对话历史
- 🔲 可视化管理界面

## 常见问题

### Q: MinerU 安装失败怎么办？
A: 可以使用备用的简单解析器，系统会自动降级使用 PyPDF2。

### Q: 向量库在哪里？
A: 默认保存在 `data/stock_data/databases/vector_dbs/`。

### Q: 支持哪些文档格式？
A: 阶段一主要支持 PDF，后续会支持 TXT、Markdown 等。

## 许可证

MIT License
