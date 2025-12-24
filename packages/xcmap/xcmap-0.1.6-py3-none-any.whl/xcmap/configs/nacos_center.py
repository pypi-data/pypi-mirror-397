import threading
import threading
import time
import weakref
from typing import Optional, List, Union

import nacos
import yaml
from nacos.client import logger
from pydantic import BaseModel
from yaml.resolver import ResolverError


class NacosConfig(BaseModel):
    """Nacos配置模型"""
    
    class ConfigItem(BaseModel):
        """配置项模型"""
        data_id: str
        group: Optional[str] = "DEFAULT_GROUP"
        data_type: Optional[str] = "yaml"
    
    server_addresses: str
    namespace: Optional[str] = "public"
    username: str
    password: str
    configs: List[ConfigItem]


class NacosWatcherSingle:
    """Nacos单一配置监听器"""
    
    def __init__(self, nacos_config: NacosConfig, config_info: Union[dict, NacosConfig.ConfigItem], update_callback):
        self.nacos_config = nacos_config
        self.config_info = config_info
        self.update_callback = update_callback
        self.client = None

    def _init_client(self):
        if not self.client:
            self.client = nacos.NacosClient(
                server_addresses=self.nacos_config.server_addresses,
                namespace=self.nacos_config.namespace,
                username=self.nacos_config.username,
                password=self.nacos_config.password
            )

    def _callback(self, cb_config):
        content = cb_config.get("content")
        # 处理ConfigItem对象或字典
        if hasattr(self.config_info, 'data_type'):
            data_type = self.config_info.data_type
            data_id = self.config_info.data_id
        else:
            data_type = self.config_info.get("data_type", "yaml")
            data_id = self.config_info["data_id"]
        logger.info(f"接收到来自 {data_id} 的配置更新")
        if data_type == "yaml":
            try:
                if content is not None:
                    parsed = yaml.safe_load(content)
                    self.update_callback(parsed)
                else:
                    logger.warning(f"Received None content for config {self.config_info}")
            except Exception as e:
                logger.error(f"YAML 解析失败: {e}")

    def start(self):
        self._init_client()
        # 处理ConfigItem对象或字典
        if hasattr(self.config_info, 'data_id'):
            data_id = self.config_info.data_id
            group = getattr(self.config_info, 'group', "DEFAULT_GROUP")
        else:
            data_id = self.config_info["data_id"]
            group = self.config_info.get("group", "DEFAULT_GROUP")
        logger.info(f"为 {data_id} 添加配置监听器")
        self.client.add_config_watcher(
            data_id=data_id,
            group=group,
            cb=self._callback
        )
        logger.info(f"已为 {data_id} 添加配置监听器")


class NacosStore:
    """Nacos配置存储和监听器管理类"""
    _instance = None
    _lock = threading.Lock()
    _finalizers = []

    def __new__(cls, nacos_config: NacosConfig, is_watcher: bool = True):
        if cls._instance is not None:
            return cls._instance
        with cls._lock:
            if cls._instance is not None:
                return cls._instance
            cls._instance = super().__new__(cls)
            return cls._instance

    def __init__(self, nacos_config: NacosConfig, is_watcher: bool = True):
        # 总是更新配置，即使实例已存在
        self.lock = threading.Lock()
        self._config = {}
        self.nacos_config = nacos_config
        self.watchers: List[NacosWatcherSingle] = []
        self._init_all_configs()
        if is_watcher:
            self._start_watchers()  # 仅在 is_watcher 为 True 时启动监听
            
        # 注册程序退出时的清理函数
        finalizer = weakref.finalize(self, self._cleanup, self.watchers)
        self._finalizers.append(finalizer)

    @staticmethod
    def _cleanup(watchers):
        """静态清理方法，确保在对象销毁时能够正确清理资源"""
        logger.info("开始清理Nacos资源...")
        
        # 先停止订阅
        for watcher in watchers:
            if watcher.client:
                try:
                    watcher.client.stop_subscribe()
                except Exception as e:
                    logger.warning(f"停止订阅时出错: {e}")
        
        # 等待一段时间让订阅停止生效
        time.sleep(0.5)
        
        # 移除配置监听器
        for watcher in watchers:
            if watcher.client:
                try:
                    # 处理ConfigItem对象或字典
                    if hasattr(watcher.config_info, 'data_id'):
                        data_id = watcher.config_info.data_id
                        group = getattr(watcher.config_info, 'group', "DEFAULT_GROUP")
                    else:
                        data_id = watcher.config_info["data_id"]
                        group = watcher.config_info.get("group", "DEFAULT_GROUP")
                    watcher.client.remove_config_watcher(
                        data_id,
                        group,
                        watcher._callback
                    )
                except Exception as e:
                    logger.warning(f"移除监听器时出错: {e}")
        
        # 等待一段时间让所有监听器完全关闭
        time.sleep(2.0)
        logger.info("Nacos资源清理完成")

    def _init_all_configs(self):
        """初始化所有配置，并按照顺序合并，后面的配置覆盖前面的同名配置"""
        self._config = {}  # 重新初始化配置
        # 按顺序加载所有配置，确保后面的配置能覆盖前面的同名配置
        for config_info in self.nacos_config.configs:
            raw_config = self._fetch_config(config_info)
            # 添加检查确保 raw_config 不为空
            if raw_config:
                # 处理ConfigItem对象或字典
                if hasattr(config_info, 'data_type'):
                    data_type = config_info.data_type
                else:
                    data_type = config_info.get("data_type", "yaml")
                parsed = self._parse_config(raw_config, data_type)
                self._merge_config(parsed)
            else:
                logger.warning(f"未能获取到配置: {config_info}")

    def _fetch_config(self, config_info):
        client = nacos.NacosClient(
            server_addresses=self.nacos_config.server_addresses,
            namespace=self.nacos_config.namespace,
            username=self.nacos_config.username,
            password=self.nacos_config.password
        )
        # 处理ConfigItem对象或字典
        if hasattr(config_info, 'data_id'):
            data_id = config_info.data_id
            group = getattr(config_info, 'group', "DEFAULT_GROUP")
        else:
            data_id = config_info["data_id"]
            group = config_info.get("group", "DEFAULT_GROUP")
            
        return client.get_config(
            data_id=data_id,
            group=group,
            timeout=10
        )

    def _parse_config(self, content: str, data_type: str):
        if data_type == "yaml":
            try:
                if content is not None:
                    return yaml.safe_load(content)
                else:
                    logger.warning("尝试解析 None 内容为 YAML")
                    return {}
            except Exception as e:
                raise ResolverError(f"解析 YAML 失败: {e}")
        else:
            raise ValueError(f"不支持的数据类型: {data_type}")

    def _merge_config(self, new_config: dict):
        """后加载的配置覆盖之前的配置"""
        def deep_merge(base: dict, override: dict):
            for key, value in override.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    deep_merge(base[key], value)
                else:
                    base[key] = value
        with self.lock:
            if self._config is None:
                self._config = {}
            deep_merge(self._config, new_config)

    def _start_watchers(self):
        for config_info in self.nacos_config.configs:
            watcher = NacosWatcherSingle(
                self.nacos_config,
                config_info,
                self._on_config_update
            )
            watcher.start()
            self.watchers.append(watcher)

    def _on_config_update(self, new_config: dict):
        """某个配置变更时重新合并所有配置"""
        logger.info(f"检测到配置更新: {new_config}")
        # 当某个配置文件发生变更时，需要重新加载所有配置以确保覆盖规则正确执行
        with self.lock:
            self._config = {}  # 清空当前配置
        self._init_all_configs()  # 重新加载并按顺序合并所有配置
        logger.info(f"更新后的完整配置: {self._config}")

    def __del__(self):
        try:
            self.close()
        except:
            # 在Python关闭过程中可能无法正确执行清理
            pass
    
    def close(self):
        """关闭所有Nacos监听器和客户端连接"""
        logger.info("开始关闭Nacos连接...")
        
        # 先停止订阅，再移除监听器
        for watcher in self.watchers:
            if watcher.client:
                try:
                    # 停止订阅
                    watcher.client.stop_subscribe()
                except Exception as e:
                    logger.warning(f"停止订阅时出错: {e}")
        
        # 等待一段时间让订阅停止生效
        time.sleep(0.5)
        
        # 移除配置监听器
        for watcher in self.watchers:
            if watcher.client:
                try:
                    # 移除配置监听器
                    # 处理ConfigItem对象或字典
                    if hasattr(watcher.config_info, 'data_id'):
                        data_id = watcher.config_info.data_id
                        group = getattr(watcher.config_info, 'group', "DEFAULT_GROUP")
                    else:
                        data_id = watcher.config_info["data_id"]
                        group = watcher.config_info.get("group", "DEFAULT_GROUP")
                    watcher.client.remove_config_watcher(
                        data_id,
                        group,
                        watcher._callback
                    )
                except Exception as e:
                    logger.warning(f"移除监听器时出错: {e}")
        
        self.watchers.clear()
        
        # 清理配置以避免在程序退出时产生异常
        with self.lock:
            self._config = {}
        
        # 等待一段时间让所有监听器完全关闭
        time.sleep(2.0)  # 增加等待时间到2秒，确保后台线程完全结束
        logger.info("Nacos连接已关闭")

    def get_config(self):
        """获取配置（线程安全）"""
        with self.lock:
            return self._config

    def refresh_config(self):
        """手动刷新配置（线程安全）"""
        with self.lock:
            self._config = {}
        self._init_all_configs()
