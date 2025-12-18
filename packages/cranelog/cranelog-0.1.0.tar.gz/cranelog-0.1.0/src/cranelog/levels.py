"""
日志级别定义模块
"""

from enum import IntEnum


class LogLevel(IntEnum):
    """日志级别枚举，数值越大优先级越高"""
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50
    
    @classmethod
    def from_string(cls, level: str) -> "LogLevel":
        """
        从字符串转换为日志级别
        
        Args:
            level: 日志级别字符串，如 "DEBUG", "INFO" 等
            
        Returns:
            对应的 LogLevel 枚举值
            
        Raises:
            ValueError: 如果级别字符串无效
        """
        level_upper = level.upper()
        try:
            return cls[level_upper]
        except KeyError:
            valid_levels = ", ".join(cls.__members__.keys())
            raise ValueError(
                f"无效的日志级别: {level}。有效级别: {valid_levels}"
            )
    
    def __str__(self) -> str:
        return self.name


# 便于导入的常量别名
DEBUG = LogLevel.DEBUG
INFO = LogLevel.INFO
WARNING = LogLevel.WARNING
ERROR = LogLevel.ERROR
CRITICAL = LogLevel.CRITICAL

