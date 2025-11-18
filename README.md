# AI-RAG-Pro 🤖

基于大语言模型（LLM）和检索增强生成（RAG）技术的智能问答系统，采用三层知识空间架构（知识空间、意图空间、反馈空间），提供精准、可追溯、可进化的问答服务。

## ✨ 核心特性

### 🎯 三层知识空间架构
- **知识空间（Knowledge Space）**: 存储原始知识文档，提供权威信息源
- **意图空间（Intent Space）**: 存储高质量问答对，实现快速响应和意图引导
- **反馈空间（Feedback Space）**: 收集用户反馈，形成持续学习和优化的闭环

### 🚀 主要功能

#### 💬 智能问答系统
- **双模式助手**:
  - **通用助手**: 直接使用大模型回答，适合一般性问题
  - **行业助手**: 基于RAG技术，从知识空间和意图空间检索相关信息后回答
- **智能检索**: 支持向量相似度检索，可配置检索参数（TopK、相似度阈值）
- **思考过程展示**: 可选的思考过程展示，帮助用户理解AI的推理过程
- **实时流式输出**: 流畅的打字机效果，提升交互体验
- **多模型支持**: 支持 DeepSeek、OpenAI、Qwen 等多种大模型

#### 📚 知识空间管理
- **可视化文档管理**: 卡片式文档列表，支持查看、删除操作
- **多格式文件上传**: 支持 TXT、MD、PDF、DOCX、CSV 等多种格式
- **统计分析**: 文件类型分布、字数分布、文档统计
- **一键刷新索引**: 快速更新向量数据库
- **文件预览**: 直接查看文档内容

#### 🎯 意图空间管理
- **问答对管理**: 可折叠卡片列表展示所有问答对
- **文件上传**: 支持上传 TXT、MD 格式的问答对文件
- **文件筛选**: 多选筛选器，按文件查看问答对
- **关键词搜索**: 在问题和答案中快速搜索
- **高频问题识别**: 自动识别反馈空间中的高频问题
- **优质问答对提取**: 自动提取高评分的问答对

#### 📊 反馈空间分析
- **可视化统计**: 评分分布柱状图、问题类型饼图
- **卡片式列表**: 美观的反馈卡片展示，支持展开查看详情
- **多维度筛选**: 按关键词、评分范围、问题类型筛选
- **反馈数据导出**: 支持导出反馈数据用于进一步分析
- **高频问题统计**: 识别用户关注的热点问题
- **优质内容提取**: 自动识别高质量问答对

#### 📈 评估与优化
- **多维度评估指标**: 提供置信度、精确率、召回率、F1分数等评估指标
- **用户反馈系统**: 支持评分、标签和改进建议
- **持续学习闭环**: 反馈 → 识别优质内容 → 更新意图空间 → 提升系统性能
- **LangSmith监控**: 可选的LLM调用追踪和监控，支持性能分析和调试

#### 🎨 现代化UI设计
- **卡片式布局**: 渐变背景、彩色边框、阴影效果
- **可折叠详情**: 两层折叠结构，整体列表和单条详情都可折叠
- **响应式设计**: 适配不同屏幕尺寸
- **流畅动画**: 悬停效果、渐入动画提升用户体验

## 📁 项目结构

```
AI-RAG-Pro/
├── pages/                    # Streamlit 页面模块
│   ├── 1_问答系统.py         # 主问答界面
│   ├── 2_知识空间.py         # 知识空间管理
│   ├── 3_意图空间.py         # 意图空间管理
│   └── 4_反馈空间.py         # 反馈数据管理
├── src/                      # 核心源代码
│   ├── retriever.py          # RAG检索管理器
│   ├── feedback.py           # 反馈存储管理
│   ├── evaluation.py         # 评估指标计算
│   ├── general_assistant.py  # 通用助手处理
│   ├── industry_assistant.py # 行业助手处理
│   ├── llm.py               # LLM服务封装
│   └── utils.py             # 工具函数
├── config/                   # 配置文件
│   ├── config.json          # 主配置文件
│   └── load_key.py          # API密钥加载
├── rag_source/              # 知识源文件
│   ├── knowledge_space/     # 知识空间文档
│   └── intent_space/        # 意图空间文档
├── data/                    # 数据存储
│   ├── chroma_db/           # Chroma向量数据库
│   └── feedback.db          # 反馈数据库（SQLite）
├── prompt/                  # 提示词模板
│   ├── general_assistant.txt
│   └── industry_assistant.txt
├── docs/                    # 项目文档
│   └── AI_RAG_PRO_解决方案.md
├── 首页.py                  # 应用入口
├── requirements.txt         # 依赖包列表
└── README.md               # 项目说明文档
```

## 🛠️ 技术栈

| 类别 | 技术/工具 | 说明 |
|------|----------|------|
| **Web框架** | Streamlit | 快速构建交互式Web界面 |
| **RAG框架** | LlamaIndex | 提供完整的RAG管道组件 |
| **向量数据库** | ChromaDB | 高性能向量存储和检索 |
| **关系数据库** | SQLite | 轻量级反馈数据存储 |
| **LLM** | DeepSeek / OpenAI / Qwen | 支持多种大语言模型 |
| **Embedding** | DashScope Text Embedding | 中文文本向量化 |
| **监控** | LangSmith | LLM调用追踪和性能监控（可选） |
| **Python版本** | Python 3.8+ | 推荐使用 Python 3.10+ |

## 🚀 快速开始

### 1. 环境要求

- Python 3.8+ (推荐 3.10+)
- pip 或 conda

### 2. 安装依赖

```bash
# 克隆项目（如果从Git仓库）
# git clone <repository-url>
# cd AI-RAG-Pro

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置API密钥

编辑 `config/config.json` 文件，配置你的API密钥：

```json
{
    "api_keys": {
        "DEEPSEEK_API_KEY": "your-deepseek-api-key",
        "OPENAI_API_KEY": "your-openai-api-key",
        "DASHSCOPE_API_KEY": "your-dashscope-api-key",
        "LANGCHAIN_API_KEY": "your-langchain-api-key"
    },
    "default_llm": "deepseek",
    "priority_order": ["deepseek", "openai", "qwen"],
    "monitoring": {
        "langsmith": {
            "enabled": false,
            "project": "ai-rag-pro",
            "tracing": true
        }
    }
}
```

**注意**: 
- 至少需要配置一个可用的LLM API密钥
- DashScope API Key 是必需的（用于Embedding模型）
- LangSmith API Key 是可选的（用于LLM调用监控）

### 4. 准备知识文档

将你的知识文档放入 `rag_source/knowledge_space/` 目录：
- 支持格式：`.txt`, `.md`, `.pdf` 等
- 系统会自动加载并构建向量索引

### 5. 运行应用

```bash
streamlit run 首页.py
```

应用将在浏览器中自动打开，默认地址：`http://localhost:8501`

## 📖 使用指南

### 💬 问答系统

1. **选择助手模式**:
   - **通用助手**: 直接使用大模型，适合一般性问题，快速响应
   - **行业助手**: 基于RAG检索，适合需要专业知识的问题，答案更准确

2. **调整检索参数**（仅行业助手）:
   - **知识空间TopK**: 从知识空间检索的文档数量（默认3，范围1-10）
   - **意图空间TopK**: 从意图空间检索的问答对数量（默认1，范围1-5）
   - **意图直返阈值**: 相似度超过此值时直接返回答案（默认0.85，范围0.5-1.0）

3. **查看思考过程**: 勾选"显示思考过程"可查看AI的推理步骤和检索到的内容

4. **评估指标**: 系统自动计算并展示置信度、精确率、召回率、F1分数等指标

5. **提交反馈**: 
   - **评分**: 对回答质量打分（0-5星）
   - **标签**: 选择问题类型标签（如：技术问题、产品咨询等）
   - **改进建议**: 提供文字反馈帮助系统优化

### 📚 知识空间管理

1. **查看文档**:
   - 卡片式列表展示所有文档
   - 查看文件类型分布和字数统计
   - 点击"查看"按钮预览文档内容

2. **上传文档**:
   - 支持 TXT、MD、PDF、DOCX、CSV 等格式
   - 支持批量上传多个文件
   - 上传后自动提示刷新索引

3. **管理文档**:
   - 点击"删除"按钮删除文档
   - 点击"刷新知识索引"更新向量数据库
   - 查看文档统计信息

### 🎯 意图空间管理

1. **查看问答对**:
   - 使用文件筛选器按文件查看
   - 使用搜索框按关键词查找
   - 点击"展开"查看完整问答详情

2. **上传问答对文件**:
   - 支持 TXT、MD 格式
   - 文件格式：`Q: 问题` + `A: 答案`
   - 查看示例格式说明

3. **高频问题**:
   - 查看反馈空间中的高频问题
   - 查看出现次数、平均评分
   - 一键添加到意图空间

4. **优质问答对**:
   - 查看高评分（≥4分）的问答对
   - 筛选有改进建议的问答
   - 查看原始答案和改进版本

### 📊 反馈空间管理

1. **查看统计**:
   - 评分分布柱状图（0-5分）
   - 问题类型分布饼图（Top 5）
   - 反馈总数、平均评分、有帮助占比

2. **筛选反馈**:
   - **关键词搜索**: 在问题和答案中搜索
   - **评分范围**: 滑块选择评分区间
   - **问题类型**: 多选筛选器按标签过滤

3. **查看详情**:
   - 卡片式列表展示
   - 彩色边框标识评分等级（绿/橙/红）
   - 展开查看完整问题、答案、改进建议
   - 查看参考来源文档

4. **数据分析**:
   - 识别高频问题
   - 提取优质问答对
   - 评估系统整体质量

## ⚙️ 配置说明

### 模型配置

在 `config/config.json` 中可以配置：

- **LLM模型**: 支持 DeepSeek、OpenAI、Qwen
- **Embedding模型**: 默认使用 DashScope Text Embedding V2
- **优先级顺序**: 系统按优先级顺序选择可用的模型

### RAG配置

```json
{
    "rag": {
        "knowledge_space_dir": "./rag_source/knowledge_space",
        "intent_space_dir": "./rag_source/intent_space",
        "chroma_db_path": "./data/chroma_db",
        "use_chroma": true,
        "default_k_knowledge": 3,
        "default_k_intent": 1,
        "default_intent_threshold": 0.85
    }
}
```

### LangSmith监控配置

LangSmith 是 LangChain 提供的 LLM 调用追踪和监控平台，可以帮助你：
- 追踪每次 LLM 调用
- 分析性能和成本
- 调试和优化提示词
- 监控系统运行状态

配置方法：

1. **获取 LangSmith API Key**:
   - 访问 [LangSmith](https://smith.langchain.com/)
   - 注册账号并获取 API Key

2. **配置项目名称**:
   在 `config/config.json` 的 `monitoring.langsmith.project` 字段中设置你的项目名称：
   ```json
   {
       "monitoring": {
           "langsmith": {
               "enabled": true,
               "project": "your-project-name",
               "tracing": true
           }
       }
   }
   ```

3. **启用监控**:
   - 将 `enabled` 设置为 `true`
   - 确保已配置 `LANGCHAIN_API_KEY`
   - 重启应用后即可在 LangSmith 平台查看追踪数据

**查看追踪数据**: 访问 `https://smith.langchain.com/projects/{your-project-name}` 查看详细的调用追踪和性能分析。

## 🔧 常见问题

### Q: 如何添加新的知识文档？

A: 将文档放入 `rag_source/knowledge_space/` 目录，系统会在启动时自动加载。也可以使用"知识空间"页面手动刷新索引。

### Q: 如何切换使用的LLM模型？

A: 在 `config/config.json` 中修改 `default_llm` 和 `priority_order`，系统会按优先级选择可用的模型。

### Q: 意图空间和知识空间有什么区别？

A: 
- **知识空间**: 存储原始知识文档，提供详细的信息源
- **意图空间**: 存储高质量问答对，用于快速响应相似问题

### Q: 如何查看反馈数据？

A: 使用"反馈空间"页面可以查看所有反馈，支持筛选、搜索和导出。

### Q: 评估指标是如何计算的？

A: 系统提供多维度评估指标：
- **置信度（Confidence）**: 基于检索相似度或意图匹配分数计算
- **精确率（Precision）**: 检索到的相关文档数 / 总检索文档数
- **召回率（Recall）**: 基于平均相似度或意图匹配分数估算
- **F1分数**: 精确率和召回率的调和平均数

这些指标可以帮助你量化问答系统的性能和质量。

### Q: 如何配置 LangSmith 监控？

A: 
1. 在 `config/config.json` 中配置 `LANGCHAIN_API_KEY`
2. 设置 `monitoring.langsmith.enabled` 为 `true`
3. 设置 `monitoring.langsmith.project` 为你的项目名称
4. 重启应用后即可在 LangSmith 平台查看追踪数据

### Q: 系统要求使用ChromaDB吗？

A: 是的，系统现在仅支持ChromaDB作为向量存储。请确保已安装 `chromadb` 包。

### Q: 行业助手提示"LLM未初始化"或"OpenAILike不可用"怎么办？

A: 这通常是由于 NumPy 版本冲突导致的。解决方法：

1. **检查 NumPy 版本**:
   ```bash
   pip show numpy
   ```

2. **如果 NumPy 版本 >= 2.0，需要降级**:
   ```bash
   pip install 'numpy<2'
   ```

3. **重新安装依赖**（推荐）:
   ```bash
   pip install -r requirements.txt
   ```

4. **重启应用**: 重启 Streamlit 应用后即可正常使用。

**注意**: 如果使用 DeepSeek 或 Qwen API（非 OpenAI 官方 API），必须使用 OpenAILike，而 OpenAILike 与 NumPy 2.0+ 存在兼容性问题。

### Q: 线上部署时出现 NLTK PermissionError 怎么办？

A: 这是线上部署时的常见问题，系统已经自动处理。如果仍然遇到问题，请检查：

1. **确保项目目录包含 nltk_data 文件夹**:
   - 项目根目录下应该有 `nltk_data/` 文件夹
   - 其中应包含 `tokenizers/punkt/` 或 `tokenizers/punkt_tab/` 数据

2. **如果数据不存在，系统会自动尝试下载**:
   - 系统会在项目目录中自动下载 NLTK 数据
   - 如果下载失败（如网络问题），请手动下载

3. **手动下载 NLTK 数据**（如果需要）:
   ```python
   import nltk
   nltk.download('punkt_tab', download_dir='./nltk_data')
   ```

4. **系统已自动配置**:
   - `src/utils.py` 和 `src/retriever.py` 中已自动配置 NLTK 数据路径
   - 系统会优先使用项目目录中的 NLTK 数据，避免权限错误

**注意**: 线上环境（如 Streamlit Cloud）可能无法写入系统目录，因此系统会自动将 NLTK 数据路径指向项目目录。

### Q: 出现 ChromaDB 遥测错误（telemetry error）怎么办？

A: 这是 ChromaDB 遥测功能与 posthog 库版本不兼容导致的，不影响系统功能。系统已自动处理：

1. **系统已自动禁用遥测**:
   - 在 `src/retriever.py` 中已设置环境变量和日志过滤器
   - 遥测错误会被自动抑制，不会影响系统运行

2. **如果仍然看到错误日志**:
   - 这些错误是警告性的，不会影响 ChromaDB 的核心功能
   - 可以安全忽略，或者更新 ChromaDB 版本：
     ```bash
     pip install --upgrade chromadb
     ```

3. **完全禁用遥测**（如果需要）:
   - 系统已通过环境变量 `ANONYMIZED_TELEMETRY=False` 禁用遥测
   - 日志过滤器会自动抑制相关错误信息

**注意**: 这些错误不会影响向量数据库的正常使用，可以安全忽略。

## 📝 开发说明

### 代码结构

- `src/retriever.py`: RAG管理器，负责索引创建和检索
- `src/feedback.py`: 反馈存储，使用SQLite管理反馈数据
- `src/evaluation.py`: 评估指标计算模块，提供多维度质量评估
- `src/industry_assistant.py`: 行业助手逻辑，实现意图空间和知识空间的检索
- `src/general_assistant.py`: 通用助手逻辑，直接调用LLM
- `src/llm.py`: LLM服务封装，支持多种模型和流式输出

### 扩展开发

1. **添加新的LLM支持**: 在 `src/llm.py` 中添加新的模型初始化逻辑
2. **自定义提示词**: 修改 `prompt/` 目录下的提示词模板
3. **添加新的检索策略**: 在 `src/retriever.py` 中扩展检索方法

## 📄 许可证

本项目采用 MIT 许可证。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📚 相关文档

- [项目解决方案文档](docs/AI_RAG_PRO_解决方案.md)
- [Chroma迁移文档](docs/Chroma迁移完成.md)
- [代码清理总结](docs/代码清理总结.md)

## 🙏 致谢

- [LlamaIndex](https://www.llamaindex.ai/) - RAG框架
- [Streamlit](https://streamlit.io/) - Web框架
- [ChromaDB](https://www.trychroma.com/) - 向量数据库
- [LangSmith](https://smith.langchain.com/) - LLM监控和追踪平台

---

**注意**: 本项目仅供学习和研究使用。在生产环境中使用时，请注意数据安全和隐私保护。
