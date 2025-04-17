import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

class Storage:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.logger = logging.getLogger(__name__)
        self._ensure_data_dir()

    def _ensure_data_dir(self) -> None:
        """确保数据目录存在"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def _get_data_file(self, date: str) -> str:
        """获取数据文件路径"""
        return os.path.join(self.data_dir, f"{date}.json")

    def save_findings(self, date: str, findings: List[Dict[str, Any]]) -> bool:
        """保存发现的内容"""
        try:
            data = {
                "date": date,
                "findings": findings,
                "last_updated": datetime.now().isoformat()
            }
            
            file_path = self._get_data_file(date)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"数据保存成功: {date}")
            return True
        except Exception as e:
            self.logger.error(f"数据保存失败: {str(e)}")
            return False

    def load_findings(self, date: str) -> Optional[List[Dict[str, Any]]]:
        """加载指定日期的发现内容"""
        try:
            file_path = self._get_data_file(date)
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("findings", [])
        except Exception as e:
            self.logger.error(f"数据加载失败: {str(e)}")
            return None

    def get_recent_findings(self, days: int = 7) -> List[Dict[str, Any]]:
        """获取最近几天的发现内容"""
        all_findings = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            findings = self.load_findings(date)
            if findings:
                all_findings.extend(findings)
        return all_findings

    def save_statistics(self, date: str, statistics: Dict[str, Any]) -> bool:
        """保存统计数据"""
        try:
            data = {
                "date": date,
                "statistics": statistics,
                "last_updated": datetime.now().isoformat()
            }
            
            file_path = self._get_data_file(f"stats_{date}")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"统计数据保存成功: {date}")
            return True
        except Exception as e:
            self.logger.error(f"统计数据保存失败: {str(e)}")
            return False

    def load_statistics(self, date: str) -> Optional[Dict[str, Any]]:
        """加载指定日期的统计数据"""
        try:
            file_path = self._get_data_file(f"stats_{date}")
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("statistics", {})
        except Exception as e:
            self.logger.error(f"统计数据加载失败: {str(e)}")
            return None

    def cleanup_old_data(self, days_to_keep: int = 30) -> None:
        """清理旧数据"""
        try:
            current_time = datetime.now()
            for filename in os.listdir(self.data_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.data_dir, filename)
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if (current_time - file_time).days > days_to_keep:
                        os.remove(file_path)
                        self.logger.info(f"已删除旧数据文件: {filename}")
        except Exception as e:
            self.logger.error(f"清理旧数据失败: {str(e)}")
