"""
公共工具函数模块
统一管理项目中使用的工具函数
"""
import sys
import os
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Optional


def setup_project_path() -> Path:
    """
    将项目根目录添加到Python路径中
    同时配置 NLTK 数据路径，避免线上部署时的权限错误
    
    Returns:
        Path: 项目根目录路径
    """
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # --------------------------------------------------------------------------
    # [重要] 修复线上部署时的 NLTK PermissionError
    # 通过将 NLTK 的数据路径指向项目内部的文件夹，避免在只读环境中下载数据
    # 必须在导入 llama_index 之前配置，因为 llama_index 会在导入时初始化 NLTK
    # --------------------------------------------------------------------------
    try:
        import nltk
        # 构造项目内部的 nltk_data 文件夹路径
        nltk_data_dir = project_root / "nltk_data"
        nltk_data_dir_str = str(nltk_data_dir)
        
        # 设置环境变量 NLTK_DATA，确保 NLTK 和 llama_index 都使用项目目录
        # 这是最可靠的方法，可以避免权限错误
        if "NLTK_DATA" not in os.environ:
            os.environ["NLTK_DATA"] = nltk_data_dir_str
        
        # 将项目内部的 nltk_data 路径添加到 NLTK 的搜索列表的最前面
        # 这样 NLTK 会优先使用项目内的数据，而不是尝试下载到系统目录
        if nltk_data_dir_str not in nltk.data.path:
            # 插入到最前面，确保优先使用
            nltk.data.path.insert(0, nltk_data_dir_str)
        
        # 检查必要的数据是否存在
        punkt_path = nltk_data_dir / "tokenizers" / "punkt"
        punkt_tab_path = nltk_data_dir / "tokenizers" / "punkt_tab"
        
        # 如果数据已存在，说明配置成功
        if punkt_path.exists() or punkt_tab_path.exists():
            # 数据已存在，配置完成
            pass
        else:
            # 数据不存在，尝试创建目录（本地环境）
            # 线上环境可能没有写权限，但不影响使用已有的数据
            if not nltk_data_dir.exists():
                try:
                    nltk_data_dir.mkdir(parents=True, exist_ok=True)
                except (PermissionError, OSError):
                    # 线上环境可能无法创建目录，这是正常的
                    # 只要数据已经存在，就不需要创建
                    pass
    except ImportError:
        # NLTK 未安装，跳过配置（某些环境可能不需要 NLTK）
        pass
    except Exception as e:
        # 配置失败不应该影响主流程，只记录警告
        import logging
        logging.warning(f"NLTK 路径配置失败（不影响主流程）: {e}")
    # --------------------------------------------------------------------------
    
    return project_root


def format_local_time(time_str: Optional[str], include_seconds: bool = False) -> str:
    """
    格式化时间为本地时间（上海时间 UTC+8）
    
    Args:
        time_str: 时间字符串，可以是ISO格式或本地时间格式
        include_seconds: 是否包含秒数，默认False
    
    Returns:
        str: 格式化后的时间字符串
        格式：如果include_seconds=True，返回 "%Y-%m-%d %H:%M:%S"
             如果include_seconds=False，返回 "%Y-%m-%d %H:%M"
    """
    if not time_str:
        return ""
    
    try:
        if isinstance(time_str, str):
            time_str = time_str.strip()
            
            # 如果是ISO格式（可能包含时区信息），转换为本地时间
            if "T" in time_str or "+" in time_str or "Z" in time_str:
                dt_str = time_str.replace("Z", "+00:00")
                dt = datetime.fromisoformat(dt_str)
                # 如果是UTC时间，转换为本地时间（UTC+8）
                if "+00:00" in dt_str or time_str.endswith("Z"):
                    utc_dt = dt.replace(tzinfo=timezone.utc)
                    local_tz = timezone(timedelta(hours=8))  # 上海时间 UTC+8
                    dt = utc_dt.astimezone(local_tz)
                format_str = "%Y-%m-%d %H:%M:%S" if include_seconds else "%Y-%m-%d %H:%M"
                return dt.strftime(format_str)
            else:
                # 尝试解析本地时间格式（YYYY-MM-DD HH:MM:SS 或 YYYY-MM-DD HH:MM）
                try:
                    # 尝试解析完整格式（包含秒）
                    if len(time_str) >= 19:
                        dt = datetime.strptime(time_str[:19], "%Y-%m-%d %H:%M:%S")
                    elif len(time_str) >= 16:
                        dt = datetime.strptime(time_str[:16], "%Y-%m-%d %H:%M")
                    else:
                        # 如果格式不完整，尝试其他常见格式
                        dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                    
                    # 格式化输出
                    format_str = "%Y-%m-%d %H:%M:%S" if include_seconds else "%Y-%m-%d %H:%M"
                    return dt.strftime(format_str)
                except ValueError:
                    # 如果解析失败，尝试直接截断（兼容旧数据）
                    max_len = 19 if include_seconds else 16
                    if len(time_str) >= max_len:
                        return time_str[:max_len]
                    else:
                        # 如果长度不够，补齐格式
                        if include_seconds and len(time_str) == 16:
                            return time_str + ":00"
                        return time_str
        else:
            return str(time_str)
    except Exception as e:
        # 如果解析失败，返回原始值的字符串形式（截断到合适长度）
        max_len = 19 if include_seconds else 16
        result = str(time_str)[:max_len] if time_str else ""
        return result

