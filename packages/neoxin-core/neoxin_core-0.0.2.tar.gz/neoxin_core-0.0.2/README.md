# neo-core

## 介绍
`neo-core` 是一个基于 FastAPI 构建的基础底层依赖库，旨在提供高效、可扩展的核心功能模块，支持快速开发现代 Web 应用程序。

## 功能模块

### 1. 核心模块
- **db.py**: 数据库连接与操作的核心逻辑。
- **http.py**: HTTP 请求与响应的封装。
- **logging.py**: 日志记录与管理。
- **security.py**: 安全相关功能，包括认证与授权。
- **settings.py**: 配置管理模块。
- **plugin.py**: 插件管理模块。

### 2. 装饰器与依赖
- **decorators.py**: 提供常用的装饰器函数，简化代码逻辑。
- **dependencies.py**: 定义全局依赖项，便于在 FastAPI 路由中复用。

### 3. 缓存模块
- **cache/**: 
  - **base.py**: 缓存的基础类。
  - **config.py**: 缓存配置管理。
  - **file.py**: 文件缓存实现。
  - **memory.py**: 内存缓存实现。
  - **redis_cache.py**: 基于 Redis 的缓存实现。
  - **stores.py**: 缓存存储管理。

### 4. 存储模块
- **storage/**:
  - **aliyun.py**: 阿里云存储实现。
  - **local.py**: 本地存储实现。
  - **manager.py**: 存储管理器。
  - **qiniu.py**: 七牛云存储实现。
  - **tencent.py**: 腾讯云存储实现。

## 使用方法

### 安装依赖
确保已安装 `poetry`，然后运行以下命令安装依赖：

```bash
poetry install
```

###  运行测试
使用以下命令运行测试：
```bash
poetry run pytest
```
### 快速开始
```python
from neoxin_core.plugin import PluginManager
from fastapi import FastAPI

app = FastAPI()
plugin_manager = PluginManager(app)
plugin_manager.setup()
```


### 系统依赖插件配置文件
```json

{
    "version": "1.0.0",
    "description": "模块配置",
    "modules": [
        {
            "name": "neo-attachment",
            "type": "pip",  
            "path": "neo-attachment", 
            "version": "0.0.1",
            "description": "附件模块",
            "init_func": "init_attachment",
            "config": {
                "key": "value"
            }
        }
    ]
}
```

字段说明：
- name: 模块名称
- type: 模块类型，pip | local | git | file
- path: 模块路径
- version: 模块版本
- description: 模块描述
- init_func: 模块初始化函数
- config: 模块配置
