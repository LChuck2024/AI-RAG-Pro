"""
提示词管理模块
"""
from pathlib import Path

PROMPT_DIR = Path(__file__).parent

def load_prompt(prompt_name: str) -> str:
    """
    加载提示词文件
    
    Args:
        prompt_name: 提示词文件名（不含扩展名），如 'general_assistant' 或 'industry_assistant'
    
    Returns:
        str: 提示词内容
    """
    prompt_file = PROMPT_DIR / f"{prompt_name}.txt"
    if not prompt_file.exists():
        raise FileNotFoundError(f"提示词文件不存在: {prompt_file}")
    
    with open(prompt_file, 'r', encoding='utf-8') as f:
        return f.read().strip()

def get_general_assistant_prompt() -> str:
    """获取通用助手提示词"""
    return load_prompt("general_assistant")

def get_industry_assistant_prompt() -> str:
    """获取行业助手提示词"""
    return load_prompt("industry_assistant")

