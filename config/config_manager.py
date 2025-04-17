import json
import os
from pathlib import Path


class ConfigManager:
    def __init__(self, config_file="config/default.json"):
        self.config_file = Path(__file__).parent / config_file
        self.config = self._load_config()

    def _load_config(self):
        """加载配置文件"""
        if not self.config_file.exists():
            raise FileNotFoundError(f"配置文件 {self.config_file} 不存在")

        with open(self.config_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_config(self, section=None):
        """获取配置"""
        if section:
            return self.config.get(section, {})
        return self.config

    def update_config(self, new_config, section=None):
        """更新配置"""
        if section:
            self.config[section] = new_config
        else:
            self.config = new_config

        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)