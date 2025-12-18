"""
核心日志模块
提供 Logger 类和全局日志函数
"""

import inspect
import os
import sys
from datetime import datetime
from typing import TextIO

from .colors import Color, ColorScheme, DEFAULT_SCHEME, colorize
from .levels import LogLevel, DEBUG, INFO, WARNING, ERROR, CRITICAL


class Logger:
    """
    高级日志记录器
    
    特性:
    - 彩色输出时间、日志级别、文件名、行号
    - 自动检测并显示函数名和类名
    - 支持多种日志级别
    - 可配置的颜色方案
    """
    
    def __init__(
        self,
        name: str = "cranelog",
        level: LogLevel = INFO,
        color_scheme: ColorScheme | None = None,
        stream: TextIO | None = None,
        time_format: str = "%Y-%m-%d %H:%M:%S",
        show_colors: bool = True,
    ):
        """
        初始化日志记录器
        
        Args:
            name: 日志记录器名称
            level: 最低日志级别
            color_scheme: 颜色方案，默认使用 DEFAULT_SCHEME
            stream: 输出流，默认使用 sys.stderr
            time_format: 时间格式字符串
            show_colors: 是否显示颜色
        """
        self.name = name
        self.level = level
        self.color_scheme = color_scheme or DEFAULT_SCHEME
        self.stream = stream or sys.stderr
        self.time_format = time_format
        self.show_colors = show_colors and self._supports_color()
    
    def _supports_color(self) -> bool:
        """检测终端是否支持颜色"""
        # 检查是否是TTY
        if not hasattr(self.stream, 'isatty'):
            return False
        if not self.stream.isatty():
            return False
        
        # 检查环境变量
        if os.environ.get('NO_COLOR'):
            return False
        if os.environ.get('FORCE_COLOR'):
            return True
        
        # 检查终端类型
        term = os.environ.get('TERM', '')
        if term == 'dumb':
            return False
        
        return True
    
    def _get_caller_info(self, stack_level: int = 3) -> dict:
        """
        获取调用者信息
        
        Args:
            stack_level: 调用栈层级
            
        Returns:
            包含文件名、行号、函数名、类名的字典
        """
        frame = inspect.currentframe()
        try:
            # 回溯到调用日志方法的位置
            for _ in range(stack_level):
                if frame is not None:
                    frame = frame.f_back
            
            if frame is None:
                return {
                    "filename": "unknown",
                    "lineno": 0,
                    "funcname": None,
                    "classname": None,
                }
            
            # 获取基本信息
            filename = os.path.basename(frame.f_code.co_filename)
            lineno = frame.f_lineno
            funcname = frame.f_code.co_name
            
            # 特殊函数名处理
            if funcname == "<module>":
                funcname = None
            
            # 尝试获取类名
            classname = None
            local_vars = frame.f_locals
            if 'self' in local_vars:
                classname = local_vars['self'].__class__.__name__
            elif 'cls' in local_vars:
                classname = local_vars['cls'].__name__
            
            return {
                "filename": filename,
                "lineno": lineno,
                "funcname": funcname,
                "classname": classname,
            }
        finally:
            del frame
    
    def _format_message(
        self,
        level: LogLevel,
        message: str,
        caller_info: dict,
    ) -> str:
        """
        格式化日志消息
        
        Args:
            level: 日志级别
            message: 日志消息
            caller_info: 调用者信息
            
        Returns:
            格式化后的日志字符串
        """
        parts = []
        
        # 时间戳
        timestamp = datetime.now().strftime(self.time_format)
        if self.show_colors:
            timestamp = colorize(timestamp, self.color_scheme.timestamp_color)
        parts.append(f"[{timestamp}]")
        
        # 日志级别
        level_str = f"{level.name:8}"  # 固定宽度对齐
        if self.show_colors:
            level_color = self.color_scheme.get_level_color(level.name)
            level_str = colorize(level_str, level_color, bold=True)
        parts.append(f"[{level_str}]")
        
        # 文件名
        filename = caller_info["filename"]
        if self.show_colors:
            filename = colorize(filename, self.color_scheme.filename_color)
        parts.append(f"[{filename}")
        
        # 行号
        lineno = str(caller_info["lineno"])
        if self.show_colors:
            lineno = colorize(lineno, self.color_scheme.lineno_color)
        parts[-1] += f":{lineno}]"
        
        # 类名和函数名
        location_parts = []
        if caller_info["classname"]:
            classname = caller_info["classname"]
            if self.show_colors:
                classname = colorize(classname, self.color_scheme.classname_color)
            location_parts.append(classname)
        
        if caller_info["funcname"]:
            funcname = caller_info["funcname"]
            if self.show_colors:
                funcname = colorize(funcname, self.color_scheme.funcname_color)
            location_parts.append(funcname)
        
        if location_parts:
            location = ".".join(location_parts) if not self.show_colors else (
                colorize(".", Color.WHITE).join(location_parts) if caller_info["classname"] else location_parts[0]
            )
            parts.append(f"[{location}]")
        
        # 消息内容
        if self.show_colors:
            message = colorize(message, self.color_scheme.message_color)
        parts.append(message)
        
        return " ".join(parts)
    
    def _log(self, level: LogLevel, message: str, *args, **kwargs) -> None:
        """
        内部日志方法
        
        Args:
            level: 日志级别
            message: 日志消息模板
            *args: 格式化参数
            **kwargs: 格式化关键字参数
        """
        if level < self.level:
            return
        
        # 格式化消息
        if args:
            message = message % args
        elif kwargs:
            message = message.format(**kwargs)
        
        # 获取调用者信息
        caller_info = self._get_caller_info()
        
        # 格式化并输出
        formatted = self._format_message(level, message, caller_info)
        print(formatted, file=self.stream)
    
    def debug(self, message: str, *args, **kwargs) -> None:
        """输出 DEBUG 级别日志"""
        self._log(DEBUG, message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs) -> None:
        """输出 INFO 级别日志"""
        self._log(INFO, message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs) -> None:
        """输出 WARNING 级别日志"""
        self._log(WARNING, message, *args, **kwargs)
    
    def warn(self, message: str, *args, **kwargs) -> None:
        """warning 的别名"""
        self.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs) -> None:
        """输出 ERROR 级别日志"""
        self._log(ERROR, message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs) -> None:
        """输出 CRITICAL 级别日志"""
        self._log(CRITICAL, message, *args, **kwargs)
    
    def fatal(self, message: str, *args, **kwargs) -> None:
        """critical 的别名"""
        self.critical(message, *args, **kwargs)
    
    def set_level(self, level: LogLevel | str) -> None:
        """
        设置日志级别
        
        Args:
            level: 日志级别（枚举值或字符串）
        """
        if isinstance(level, str):
            level = LogLevel.from_string(level)
        self.level = level
    
    def set_color_scheme(self, scheme: ColorScheme) -> None:
        """
        设置颜色方案
        
        Args:
            scheme: 颜色方案对象
        """
        self.color_scheme = scheme
    
    def enable_colors(self) -> None:
        """启用颜色输出"""
        self.show_colors = True
    
    def disable_colors(self) -> None:
        """禁用颜色输出"""
        self.show_colors = False


# 全局默认日志记录器
_default_logger: Logger | None = None


def get_logger(
    name: str = "cranelog",
    level: LogLevel | str = INFO,
    **kwargs
) -> Logger:
    """
    获取或创建日志记录器
    
    Args:
        name: 日志记录器名称
        level: 日志级别
        **kwargs: 传递给 Logger 构造函数的其他参数
        
    Returns:
        Logger 实例
    """
    if isinstance(level, str):
        level = LogLevel.from_string(level)
    return Logger(name=name, level=level, **kwargs)


def _get_default_logger() -> Logger:
    """获取全局默认日志记录器"""
    global _default_logger
    if _default_logger is None:
        _default_logger = Logger(level=DEBUG)
    return _default_logger


def set_default_level(level: LogLevel | str) -> None:
    """设置全局默认日志级别"""
    _get_default_logger().set_level(level)


# 模块级快捷函数
def debug(message: str, *args, **kwargs) -> None:
    """模块级 DEBUG 日志"""
    logger = _get_default_logger()
    # 需要额外调整栈层级
    caller_info = logger._get_caller_info(stack_level=2)
    if DEBUG >= logger.level:
        if args:
            message = message % args
        elif kwargs:
            message = message.format(**kwargs)
        formatted = logger._format_message(DEBUG, message, caller_info)
        print(formatted, file=logger.stream)


def info(message: str, *args, **kwargs) -> None:
    """模块级 INFO 日志"""
    logger = _get_default_logger()
    caller_info = logger._get_caller_info(stack_level=2)
    if INFO >= logger.level:
        if args:
            message = message % args
        elif kwargs:
            message = message.format(**kwargs)
        formatted = logger._format_message(INFO, message, caller_info)
        print(formatted, file=logger.stream)


def warning(message: str, *args, **kwargs) -> None:
    """模块级 WARNING 日志"""
    logger = _get_default_logger()
    caller_info = logger._get_caller_info(stack_level=2)
    if WARNING >= logger.level:
        if args:
            message = message % args
        elif kwargs:
            message = message.format(**kwargs)
        formatted = logger._format_message(WARNING, message, caller_info)
        print(formatted, file=logger.stream)


def error(message: str, *args, **kwargs) -> None:
    """模块级 ERROR 日志"""
    logger = _get_default_logger()
    caller_info = logger._get_caller_info(stack_level=2)
    if ERROR >= logger.level:
        if args:
            message = message % args
        elif kwargs:
            message = message.format(**kwargs)
        formatted = logger._format_message(ERROR, message, caller_info)
        print(formatted, file=logger.stream)


def critical(message: str, *args, **kwargs) -> None:
    """模块级 CRITICAL 日志"""
    logger = _get_default_logger()
    caller_info = logger._get_caller_info(stack_level=2)
    if CRITICAL >= logger.level:
        if args:
            message = message % args
        elif kwargs:
            message = message.format(**kwargs)
        formatted = logger._format_message(CRITICAL, message, caller_info)
        print(formatted, file=logger.stream)


# 别名
warn = warning
fatal = critical

