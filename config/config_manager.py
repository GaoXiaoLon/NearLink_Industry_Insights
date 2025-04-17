import json
import os
from typing import Dict, Any

class ConfigManager:
    def __init__(self, config_path: str = "config/default.json"):
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.load_config()

    def load_config(self) -> None:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"配置文件 {self.config_path} 不存在")
        except json.JSONDecodeError:
            raise ValueError(f"配置文件 {self.config_path} 格式错误")

    def save_config(self) -> None:
        """保存配置到文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            raise Exception(f"保存配置文件失败: {str(e)}")

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项，支持点号分隔的路径"""
        if '.' not in key:
            return self.config.get(key, default)
        
        # 处理点号分隔的路径
        parts = key.split('.')
        value = self.config
        for part in parts:
            if not isinstance(value, dict):
                return default
            value = value.get(part, default)
        return value

    def set(self, key: str, value: Any) -> None:
        """设置配置项，支持点号分隔的路径"""
        if '.' not in key:
            self.config[key] = value
            self.save_config()
            return
        
        # 处理点号分隔的路径
        parts = key.split('.')
        current = self.config
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value
        self.save_config()

    def update(self, new_config: Dict[str, Any]) -> None:
        """更新配置"""
        self.config.update(new_config)
        self.save_config()
