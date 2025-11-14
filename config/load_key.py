"""
配置加载模块
统一管理API密钥和模型配置
"""
import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# 配置日志
logging.basicConfig(level=logging.INFO)

# 配置文件路径
CONFIG_FILE = Path(__file__).parent / "config.json"

def load_config() -> Dict[str, Any]:
    """
    加载配置文件
    
    Returns:
        Dict: 配置字典
    """
    if not CONFIG_FILE.exists():
        # 如果配置文件不存在，创建一个默认配置
        default_config = {
            "api_keys": {
                "DEEPSEEK_API_KEY": "",
                "OPENAI_API_KEY": "",
                "DASHSCOPE_API_KEY": ""
            },
            "models": {
                "deepseek": {
                    "model_name": "deepseek-chat",
                    "base_url": "https://api.deepseek.com/v1",
                    "api_key_env": "DEEPSEEK_API_KEY",
                    "temperature": 0.1,
                    "max_tokens": 2000
                },
                "openai": {
                    "model_name": "gpt-3.5-turbo",
                    "base_url": "https://api.openai.com/v1",
                    "api_key_env": "OPENAI_API_KEY",
                    "temperature": 0.1,
                    "max_tokens": 2000
                },
                "qwen": {
                    "model_name": "qwen-plus",
                    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                    "api_key_env": "DASHSCOPE_API_KEY",
                    "temperature": 0.1,
                    "max_tokens": 2000
                }
            },
            "embedding": {
                "provider": "dashscope",
                "model_name": "text-embedding-v2",
                "api_key_env": "DASHSCOPE_API_KEY"
            },
            "rag": {
                "knowledge_space_dir": "./rag_source/knowledge_space",
                "intent_space_dir": "./rag_source/intent_space",
                "persist_dir_knowledge": "./storage/knowledge_space",
                "persist_dir_intent": "./storage/intent_space",
                "default_k_knowledge": 3,
                "default_k_intent": 1,
                "default_intent_threshold": 0.85
            },
            "default_llm": "deepseek",
            "priority_order": ["deepseek", "openai", "qwen"]
        }
        save_config(default_config)
        return default_config
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except (FileNotFoundError, json.JSONDecodeError, IOError) as e:
        print(f"加载配置文件失败: {e}")
        return {}

def save_config(config: Dict[str, Any]) -> None:
    """
    保存配置到文件
    
    Args:
        config: 配置字典
    """
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except (IOError, OSError, PermissionError) as e:
        print(f"保存配置文件失败: {e}")

def get_api_key(key_name: str) -> Optional[str]:
    """
    获取API密钥
    优先从环境变量获取，如果环境变量不存在，则从配置文件获取
    
    Args:
        key_name: API密钥名称（如 DEEPSEEK_API_KEY）
    
    Returns:
        str: API密钥，如果不存在则返回None
    """
    # 首先尝试从环境变量获取
    api_key = os.getenv(key_name)
    if api_key:
        return api_key
    
    # 如果环境变量不存在，从配置文件获取
    config = load_config()
    api_keys = config.get("api_keys", {})
    api_key = api_keys.get(key_name, "")
    
    # 如果配置文件中存在，设置到环境变量
    if api_key:
        os.environ[key_name] = api_key
        return api_key
    
    return None

def get_model_config(model_name: str) -> Optional[Dict[str, Any]]:
    """
    获取模型配置
    
    Args:
        model_name: 模型名称（如 deepseek, openai, qwen）
    
    Returns:
        Dict: 模型配置字典
    """
    config = load_config()
    models = config.get("models", {})
    return models.get(model_name)

def get_available_llm() -> Optional[str]:
    """
    获取可用的LLM模型名称
    按照优先级顺序检查API密钥
    
    Returns:
        str: 可用的模型名称，如果都不可用则返回None
    """
    config = load_config()
    priority_order = config.get("priority_order", ["deepseek", "openai", "qwen"])
    
    for model_name in priority_order:
        model_config = get_model_config(model_name)
        if model_config:
            api_key_env = model_config.get("api_key_env")
            if api_key_env and get_api_key(api_key_env):
                return model_name
    
    return None

def load_key():
    """
    加载API密钥到环境变量
    兼容旧版本的load_key函数
    """
    config = load_config()
    api_keys = config.get("api_keys", {})
    
    # 将配置中的API密钥设置到环境变量
    for key_name, key_value in api_keys.items():
        if key_value and not os.getenv(key_name):
            os.environ[key_name] = key_value
    
    # 兼容旧代码：设置DASHSCOPE_API_KEY到dashscope
    try:
        import dashscope
        dashscope_api_key = get_api_key("DASHSCOPE_API_KEY")
        if dashscope_api_key:
            dashscope.api_key = dashscope_api_key
    except ImportError:
        pass
    
    # 配置LangSmith（如果启用）
    monitoring_config = config.get("monitoring", {})
    langsmith_config = monitoring_config.get("langsmith", {})
    if langsmith_config.get("enabled", False):
        langsmith_api_key = get_api_key("LANGCHAIN_API_KEY")
        if langsmith_api_key:
            os.environ["LANGCHAIN_API_KEY"] = langsmith_api_key
            os.environ["LANGCHAIN_TRACING"] = "true" if langsmith_config.get("tracing", True) else "false"
            os.environ["LANGCHAIN_PROJECT"] = langsmith_config.get("project", "ai-rag-pro")
            logging.info(f"✅ LangSmith已启用，项目: {langsmith_config.get('project', 'ai-rag-pro')}")
        else:
            logging.warning("⚠️ LangSmith已配置但未找到LANGCHAIN_API_KEY，请检查配置")

def update_api_key(key_name: str, key_value: str) -> bool:
    """
    更新API密钥
    
    Args:
        key_name: API密钥名称
        key_value: API密钥值
    
    Returns:
        bool: 是否更新成功
    """
    try:
        config = load_config()
        if "api_keys" not in config:
            config["api_keys"] = {}
        config["api_keys"][key_name] = key_value
        save_config(config)
        
        # 同时更新环境变量
        os.environ[key_name] = key_value
        return True
    except (IOError, OSError, PermissionError, json.JSONDecodeError) as e:
        print(f"更新API密钥失败: {e}")
        return False

