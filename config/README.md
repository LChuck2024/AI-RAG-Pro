# API密钥配置说明

## 📝 配置方式

### 方式一：在配置文件中填写（推荐）

在 `config.json` 文件的 `api_keys` 部分填写您的 API 密钥：

```json
{
    "api_keys": {
        "DEEPSEEK_API_KEY": "sk-xxxxxxxxxxxxx",
        "OPENAI_API_KEY": "sk-xxxxxxxxxxxxx",
        "DASHSCOPE_API_KEY": "sk-xxxxxxxxxxxxx"
    }
}
```

### 方式二：使用环境变量

在终端中设置环境变量：

**Linux/Mac:**
```bash
export DEEPSEEK_API_KEY="sk-xxxxxxxxxxxxx"
export OPENAI_API_KEY="sk-xxxxxxxxxxxxx"
export DASHSCOPE_API_KEY="sk-xxxxxxxxxxxxx"
```

**Windows (PowerShell):**
```powershell
$env:DEEPSEEK_API_KEY="sk-xxxxxxxxxxxxx"
$env:OPENAI_API_KEY="sk-xxxxxxxxxxxxx"
$env:DASHSCOPE_API_KEY="sk-xxxxxxxxxxxxx"
```

**Windows (CMD):**
```cmd
set DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxx
set OPENAI_API_KEY=sk-xxxxxxxxxxxxx
set DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxx
```

## 🔑 获取API密钥

### DeepSeek API
1. 访问 [DeepSeek 官网](https://platform.deepseek.com/)
2. 注册/登录账号
3. 在控制台创建 API 密钥
4. 复制密钥并填写到配置中

### OpenAI API
1. 访问 [OpenAI 官网](https://platform.openai.com/)
2. 注册/登录账号
3. 在 API Keys 页面创建新密钥
4. 复制密钥并填写到配置中

### 阿里云 DashScope (通义千问)
1. 访问 [阿里云 DashScope](https://dashscope.aliyun.com/)
2. 注册/登录账号
3. 在控制台创建 API 密钥
4. 复制密钥并填写到配置中

## ⚙️ 优先级说明

系统会按照以下优先级查找 API 密钥：
1. **环境变量**（最高优先级）
2. **配置文件** (`config.json`)

如果环境变量已设置，系统会优先使用环境变量中的值。

## 🎯 推荐配置

- **主要使用 DeepSeek**：填写 `DEEPSEEK_API_KEY`
- **需要 RAG 功能**：填写 `DASHSCOPE_API_KEY`（用于嵌入模型）
- **多模型支持**：可以同时填写多个 API 密钥，系统会按优先级自动选择

## ⚠️ 安全提示

1. **不要将包含真实 API 密钥的配置文件提交到 Git**
2. 建议将 `config.json` 添加到 `.gitignore` 文件中
3. 可以使用 `config.json.example` 作为模板，不包含真实密钥
4. 生产环境建议使用环境变量方式配置

## 📋 配置示例

```json
{
    "api_keys": {
        "DEEPSEEK_API_KEY": "sk-1234567890abcdef",
        "OPENAI_API_KEY": "",
        "DASHSCOPE_API_KEY": "sk-abcdef1234567890"
    }
}
```

填写完成后，重启应用即可生效。

