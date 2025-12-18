"""
终端颜色定义模块
支持ANSI转义码实现彩色输出
"""

from enum import Enum


class Color(Enum):
    """ANSI颜色代码枚举"""
    # 基础颜色
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # 亮色版本
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    
    # 重置
    RESET = "\033[0m"
    
    # 样式
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"


def colorize(text: str, color: Color, bold: bool = False) -> str:
    """
    给文本添加颜色
    
    Args:
        text: 要着色的文本
        color: 颜色枚举值
        bold: 是否加粗
        
    Returns:
        带颜色的文本字符串
    """
    prefix = Color.BOLD.value if bold else ""
    return f"{prefix}{color.value}{text}{Color.RESET.value}"


class ColorScheme:
    """
    日志颜色方案配置类
    定义各个日志组件的颜色
    """
    
    def __init__(
        self,
        timestamp_color: Color = Color.BRIGHT_BLACK,
        level_colors: dict | None = None,
        filename_color: Color = Color.CYAN,
        lineno_color: Color = Color.BRIGHT_CYAN,
        funcname_color: Color = Color.YELLOW,
        classname_color: Color = Color.MAGENTA,
        message_color: Color = Color.WHITE,
    ):
        self.timestamp_color = timestamp_color
        self.level_colors = level_colors or {
            "DEBUG": Color.BLUE,
            "INFO": Color.GREEN,
            "WARNING": Color.YELLOW,
            "ERROR": Color.RED,
            "CRITICAL": Color.BRIGHT_RED,
        }
        self.filename_color = filename_color
        self.lineno_color = lineno_color
        self.funcname_color = funcname_color
        self.classname_color = classname_color
        self.message_color = message_color
    
    def get_level_color(self, level: str) -> Color:
        """获取日志级别对应的颜色"""
        return self.level_colors.get(level.upper(), Color.WHITE)


# 预定义的颜色方案
DEFAULT_SCHEME = ColorScheme()

DARK_SCHEME = ColorScheme(
    timestamp_color=Color.DIM,
    filename_color=Color.BRIGHT_BLUE,
    lineno_color=Color.BLUE,
    funcname_color=Color.BRIGHT_YELLOW,
    classname_color=Color.BRIGHT_MAGENTA,
)

VIBRANT_SCHEME = ColorScheme(
    timestamp_color=Color.BRIGHT_BLACK,
    level_colors={
        "DEBUG": Color.BRIGHT_BLUE,
        "INFO": Color.BRIGHT_GREEN,
        "WARNING": Color.BRIGHT_YELLOW,
        "ERROR": Color.BRIGHT_RED,
        "CRITICAL": Color.BRIGHT_MAGENTA,
    },
    filename_color=Color.BRIGHT_CYAN,
    lineno_color=Color.CYAN,
    funcname_color=Color.BRIGHT_YELLOW,
    classname_color=Color.BRIGHT_MAGENTA,
)

