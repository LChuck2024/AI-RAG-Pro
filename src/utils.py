"""
公共工具函数模块
统一管理项目中使用的工具函数
"""
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Optional


def setup_project_path() -> Path:
    """
    将项目根目录添加到Python路径中
    
    Returns:
        Path: 项目根目录路径
    """
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
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
                # 已经是本地时间格式，直接使用
                max_len = 19 if include_seconds else 16
                return time_str[:max_len] if len(time_str) > max_len else time_str
        else:
            return str(time_str)
    except Exception:
        # 如果解析失败，直接返回原始值的字符串形式
        return str(time_str)

