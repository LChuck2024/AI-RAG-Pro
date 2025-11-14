# 提示词管理

本目录包含AI RAG Pro系统的提示词配置文件。

## 文件说明

### `general_assistant.txt`
通用助手的提示词，用于通用问答模式。

**特点：**
- 将大模型认知修正为由凡梦文化创建的智能助手小艾
- 友好、亲切的对话风格
- 适合一般性问题的回答

### `industry_assistant.txt`
行业助手的提示词，用于RAG知识库问答模式。

**特点：**
- 综合考虑知识空间、意图空间和反馈空间
- 专业的行业知识问答
- 参考历史问答的用户反馈，持续优化回答质量

## 使用方法

### 在代码中加载提示词

```python
from prompt import get_general_assistant_prompt, get_industry_assistant_prompt

# 获取通用助手提示词
general_prompt = get_general_assistant_prompt()

# 获取行业助手提示词
industry_prompt = get_industry_assistant_prompt()
```

### 提示词格式说明

提示词文件使用纯文本格式，支持：
- 多行文本
- Markdown格式（在代码中渲染时）
- 占位符（如 `{context_str}`, `{query_str}` 等，由LlamaIndex自动填充）

## 自定义提示词

如需修改提示词，直接编辑对应的`.txt`文件即可。修改后重启应用即可生效。

## 提示词设计原则

1. **明确身份定位**：清楚定义助手的身份和角色
2. **明确核心原则**：列出助手应遵循的基本原则
3. **明确回答要求**：说明回答的格式、风格和质量要求
4. **考虑使用场景**：根据不同的使用场景调整提示词内容

