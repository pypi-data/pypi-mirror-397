from typing import Dict, Any, Callable, List, Optional
from pathlib import Path
from fastapi import FastAPI
from importlib import import_module
import json
import os
from .decorators import singleton
from .schemas import PluginConfigItem
from .logging import get_logger


class Plugin:
    """插件实例"""

    def __init__(
        self,
        app: FastAPI,
        module_configs: List[PluginConfigItem],
        attach: Callable,
        detach: Optional[Callable] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        初始化插件实例

        Args:
            app (FastAPI): FastAPI应用实例
            module_configs (List[PluginConfigItem]): 模块配置列表
            attach (Callable): 附加方法
            config (Optional[Dict[str, Any]]): 配置
        """
        self.app = app
        self.module_configs = module_configs or []
        self.attach = attach
        
        self.default_config = {
            c.key: c.default for c in module_configs
        }
        self.config = config or self.default_config
        self.detach = detach

    def setup(self):
        """启用插件"""
        if self.attach and callable(self.attach):
            self.attach(self.app, self.config)

    def teardown(self):
        """禁用插件"""
        if self.detach and callable(self.detach):
            self.detach(self.app, self.config)

    def __repr__(self):
        return f"Plugin(app={self.app}, module_configs={self.module_configs}, attach={self.attach}, config={self.config})"

    def __str__(self):
        return f"Plugin(app={self.app}, module_configs={self.module_configs}, attach={self.attach}, config={self.config})"


class PluginConfig:
    """插件配置"""

    def __init__(self, config_path: str):
        """
        初始化插件配置，加载配置文件并验证配置文件

        Args:
            config_path (str): 配置文件路径
        """
        self.logger = get_logger("neocore.plugin-config")
        self.base_dir = Path.cwd()  # 程序启动时的目录
        self.config_path = Path(
            self.base_dir, config_path
        ).resolve()  # 加载配置文件位置

        # 初始化数据
        self.config = {}
        self.version = "0.0.1"
        self.description = ""
        self.modules = []

    def load_configs(self):
        """加载配置"""
        self.config = self.validate_config()
        # 加载配置
        self.version = self.config.get("version", "")
        self.description = self.config.get("description", "")
        self.modules = self.validate_modules() or []

    def validate_modules(self):
        """验证模块配置"""
        modules = self.config.get("modules", [])
        _target_modules: List[Dict[str, Any]] = []
        if not modules:
            self.logger.error("配置文件中没有找到 modules 字段")
            return
        for module in modules:
            if not module.get("name"):
                self.logger.error("模块配置中没有找到 name 字段")
                continue
            if not module.get("version"):
                self.logger.error("模块配置中没有找到 version 字段")
                continue
            if not module.get("config"):
                self.logger.error("模块配置中没有找到 config 字段")
                continue
            _target_modules.append(module)
        return _target_modules

    def validate_config(self) -> Dict:
        """加载配置文件"""
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                config = json.load(f)
                return config
        self.logger.error(f"配置文件 {self.config_path} 不存在")
        return {}

    def get_config(self, plugin_name: str) -> Dict:
        """获取插件配置"""
        for module in self.modules:
            if module["name"] == plugin_name:
                return module["config"]
        return {}

    def __repr__(self):
        return f"PluginConfig(version={self.version}, description={self.description}, modules={self.modules})"

    def __str__(self):
        return f"PluginConfig(version={self.version}, description={self.description}, modules={self.modules})"


@singleton
class PluginManager:
    """插件管理器，用于管理FastAPI插件"""

    def __init__(self, app: FastAPI, config_path: str = "module.config.json"):
        """
        初始化插件管理器

        Args:
            app (FastAPI): FastAPI应用实例
            config_path (str): 配置文件路径
        """
        self.app = app
        self.plugin_config = PluginConfig(config_path)
        self.plugins: Dict[str, Plugin] = {}
        self.logger = get_logger('neocore.plugin-mananger')

    def load_config(self):
        """加载插件配置文件"""
        return self.plugin_config.load_configs()

    def get_config(self, plugin_name: str) -> Dict:
        """获取插件配置"""
        return self.plugin_config.get_config(plugin_name)

    def setup_moudule(self, module: Dict):
        """初始化模块"""
        plugin_name = module.get("name")
        init_func = module.get("init_func") or "init"
        config = module.get("config") or {}
        plugin_type = module.get("type") or "pip"  # 插件类型： pip | local | git | file
        plugin_path = module.get("path") or ""  # 插件路径/url地址
        plugin_version = module.get("version") or ""  # 插件版本

        if not plugin_name:
            self.logger.error("Failed to register plugin: plugin_name not found")
            return
        if not init_func:
            self.logger.error("Failed to register plugin: init_func not found")
            return

        self.logger.info(f"Loading plugin {plugin_name}")

        try:
            mod = import_module(plugin_name)
        except Exception as e:
            self.logger.error(f"Failed to import plugin {plugin_name}: {e}")
            # TODO: 安装依赖
            import subprocess

            # 获取依赖
            if plugin_type == "pip":
                subprocess.call(["pip", "install", plugin_name])
            elif plugin_type == "local":
                subprocess.call(["pip", "install", plugin_path])
            elif plugin_type == "git":
                subprocess.call(
                    [
                        "pip",
                        "install",
                        f"git+{plugin_path}@{plugin_version or 'master'}#{plugin_name}",
                    ]
                )
            elif plugin_type == "file":
                # TODO: 安装文件依赖[在线url或者本地文件，全路径]
                subprocess.call(["pip", "install", plugin_path])

            mod = import_module(plugin_name)

        if not mod or not hasattr(mod, init_func):
            self.logger.warning(
                f"Failed to register plugin {plugin_name}: {init_func} not found"
            )
            return

        plugin: Optional[Plugin] = self.register_plugin(
            plugin_name, getattr(mod, init_func), config
        )
        if plugin:
            self.logger.info(f"Plugin {plugin_name} setup")
            plugin.setup()

    def setup(self):
        """初始化插件"""
        self.load_config()
        for module in self.plugin_config.modules:
            self.setup_moudule(module)

    def register_plugin(
        self, name: str, init_func: Callable, config: Dict = {}
    ) -> Optional[Plugin]:
        """注册插件"""
        try:
            plugin_instance = init_func(self.app, config or self.get_config(name))

            if not plugin_instance:
                self.logger.error(
                    f"Failed to register plugin {name}: {init_func} not found"
                )
                return

            if not isinstance(plugin_instance, Plugin):
                self.logger.error(
                    f"Failed to register plugin {name}:  Plugin { name } is not a Plugin instance"
                )
                return

            self.plugins[name] = plugin_instance
            self.logger.info(f"Registered plugin {name}")
            return plugin_instance
        except Exception as e:
            self.logger.error(f"Failed to register plugin {name}: {e}")
            return None

    def get_plugin(self, name: str) -> Optional[Plugin]:
        """获取已注册的插件"""
        return self.plugins.get(name) or None
