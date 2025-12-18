# CraneLog 🪵

一个现代化的 Python 彩色日志工具，用于替代原生 logging 模块。

## ✨ 特性

- 🎨 **彩色输出** - 时间戳、日志级别、文件名、行号等信息使用不同颜色显示
- 📍 **丰富的上下文** - 自动显示文件名、行号、函数名、类名
- 🔧 **简洁 API** - 既支持模块级快捷函数，也支持创建独立的 Logger 实例
- 🎯 **零依赖** - 纯 Python 实现，无需安装额外依赖
- 🖥️ **智能检测** - 自动检测终端是否支持颜色输出

## 📦 安装

```bash
pip install cranelog
```

或使用 PDM：

```bash
pdm add cranelog
```

## 🚀 快速开始

### 基本用法

```python
import cranelog

# 使用模块级函数（最简单的方式）
cranelog.debug("这是一条调试信息")
cranelog.info("这是一条普通信息")
cranelog.warning("这是一条警告信息")
cranelog.error("这是一条错误信息")
cranelog.critical("这是一条严重错误信息")
```

### 在函数中使用

```python
import cranelog

def process_data():
    cranelog.info("开始处理数据")
    # ... 处理逻辑
    cranelog.info("数据处理完成")

process_data()
# 输出会自动包含函数名 process_data
```

### 在类中使用

```python
import cranelog

class DataProcessor:
    def process(self):
        cranelog.info("类方法中的日志")
        # 输出会包含类名 DataProcessor 和方法名 process

processor = DataProcessor()
processor.process()
```

### 创建专用的 Logger 实例

```python
from cranelog import get_logger, DEBUG

# 创建一个 DEBUG 级别的 logger
logger = get_logger("myapp", level=DEBUG)

logger.debug("调试信息")
logger.info("普通信息")
logger.warning("警告信息")
logger.error("错误信息")
```

### 自定义颜色方案

```python
from cranelog import get_logger, ColorScheme, Color

# 创建自定义颜色方案
custom_scheme = ColorScheme(
    timestamp_color=Color.BRIGHT_BLACK,
    filename_color=Color.BRIGHT_BLUE,
    lineno_color=Color.BLUE,
    funcname_color=Color.BRIGHT_YELLOW,
    classname_color=Color.BRIGHT_MAGENTA,
)

logger = get_logger("myapp", color_scheme=custom_scheme)
logger.info("使用自定义颜色方案")
```

### 使用预定义的颜色方案

```python
from cranelog import get_logger, DARK_SCHEME, VIBRANT_SCHEME

# 使用暗色方案
dark_logger = get_logger("dark", color_scheme=DARK_SCHEME)

# 使用鲜艳方案
vibrant_logger = get_logger("vibrant", color_scheme=VIBRANT_SCHEME)
```

## 📋 日志级别

| 级别 | 数值 | 说明 |
|------|------|------|
| DEBUG | 10 | 调试信息 |
| INFO | 20 | 普通信息 |
| WARNING | 30 | 警告信息 |
| ERROR | 40 | 错误信息 |
| CRITICAL | 50 | 严重错误 |

## 🎨 输出格式

每条日志包含以下信息（使用不同颜色）：

```
[时间戳] [级别] [文件名:行号] [类名.函数名] 消息内容
```

示例输出：
```
[2024-01-15 10:30:45] [INFO    ] [main.py:25] [DataProcessor.process] 开始处理数据
```

## 📄 License

MIT License
