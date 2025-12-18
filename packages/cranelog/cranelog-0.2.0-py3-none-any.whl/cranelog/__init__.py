"""
CraneLog - 一个现代化的 Python 彩色日志工具

特性:
- 彩色输出时间戳、日志级别、文件名、行号
- 自动检测并显示函数名和类名
- 支持多种日志级别
- 可自定义颜色方案
- 简洁的 API 设计

基本用法:
    >>> import cranelog
    >>> cranelog.info("Hello, CraneLog!")
    
    # 或创建专用的 Logger 实例
    >>> from cranelog import get_logger
    >>> logger = get_logger("myapp", level="DEBUG")
    >>> logger.debug("Debug message")
"""

from .levels import (
    LogLevel,
    DEBUG,
    INFO,
    WARNING,
    ERROR,
    CRITICAL,
)

from .colors import (
    Color,
    ColorScheme,
    colorize,
    DEFAULT_SCHEME,
    DARK_SCHEME,
    VIBRANT_SCHEME,
)

from .logger import (
    Logger,
    get_logger,
    set_default_level,
    add_file_handler,
    remove_file_handler,
    get_log_files,
    debug,
    info,
    warning,
    warn,
    error,
    critical,
    fatal,
)

__version__ = "0.2.0"
__author__ = "weizhang124"

__all__ = [
    # 日志级别
    "LogLevel",
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
    # 颜色相关
    "Color",
    "ColorScheme",
    "colorize",
    "DEFAULT_SCHEME",
    "DARK_SCHEME",
    "VIBRANT_SCHEME",
    # Logger 类和工厂函数
    "Logger",
    "get_logger",
    "set_default_level",
    # 文件输出相关
    "add_file_handler",
    "remove_file_handler",
    "get_log_files",
    # 模块级日志函数
    "debug",
    "info",
    "warning",
    "warn",
    "error",
    "critical",
    "fatal",
]

