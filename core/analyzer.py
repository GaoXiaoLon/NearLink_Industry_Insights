from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging
from ..services.storage import Storage

class Analyzer:
    def __init__(self, storage: Storage):
        self.storage = storage
        self.logger = logging.getLogger(__name__)

    def analyze_trends(self, days: int = 30) -> Dict[str, Any]:
        """分析趋势数据"""
        try:
            trends = {
                'daily_findings': [],
                'keyword_trends': {},
                'source_trends': {}
            }
            
            # 收集每日数据
            for i in range(days):
                date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                findings = self.storage.load_findings(date)
                statistics = self.storage.load_statistics(date)
                
                if findings and statistics:
                    trends['daily_findings'].append({
                        'date': date,
                        'count': len(findings),
                        'statistics': statistics
                    })
                    
                    # 更新关键词趋势
                    for keyword, count in statistics.get('keyword_stats', {}).items():
                        if keyword not in trends['keyword_trends']:
                            trends['keyword_trends'][keyword] = []
                        trends['keyword_trends'][keyword].append({
                            'date': date,
                            'count': count
                        })
                    
                    # 更新来源趋势
                    for finding in findings:
                        source = finding['source']
                        if source not in trends['source_trends']:
                            trends['source_trends'][source] = []
                        trends['source_trends'][source].append({
                            'date': date,
                            'count': 1
                        })
            
            return trends
        except Exception as e:
            self.logger.error(f"趋势分析失败: {str(e)}")
            return {}

    def get_keyword_insights(self, keyword: str, days: int = 7) -> Dict[str, Any]:
        """获取关键词洞察"""
        try:
            insights = {
                'total_mentions': 0,
                'daily_mentions': [],
                'top_sources': {},
                'related_keywords': {}
            }
            
            # 收集关键词相关数据
            for i in range(days):
                date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                findings = self.storage.load_findings(date)
                
                if findings:
                    keyword_findings = [f for f in findings if f['keyword'] == keyword]
                    daily_count = len(keyword_findings)
                    
                    insights['total_mentions'] += daily_count
                    insights['daily_mentions'].append({
                        'date': date,
                        'count': daily_count
                    })
                    
                    # 统计来源
                    for finding in keyword_findings:
                        source = finding['source']
                        insights['top_sources'][source] = insights['top_sources'].get(source, 0) + 1
                    
                    # 收集相关关键词
                    for finding in keyword_findings:
                        title = finding['title']
                        other_keywords = [k for k in self._extract_keywords(title) if k != keyword]
                        for other_keyword in other_keywords:
                            insights['related_keywords'][other_keyword] = insights['related_keywords'].get(other_keyword, 0) + 1
            
            # 排序
            insights['top_sources'] = dict(sorted(
                insights['top_sources'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5])
            
            insights['related_keywords'] = dict(sorted(
                insights['related_keywords'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:10])
            
            return insights
        except Exception as e:
            self.logger.error(f"关键词洞察分析失败: {str(e)}")
            return {}

    def _extract_keywords(self, text: str) -> List[str]:
        """从文本中提取关键词"""
        # 这里可以添加更复杂的关键词提取逻辑
        # 目前只是简单分词
        import jieba
        words = jieba.cut(text)
        return [word for word in words if len(word) > 1]

    def generate_report(self, days: int = 7) -> Dict[str, Any]:
        """生成分析报告"""
        try:
            report = {
                'summary': {},
                'trends': self.analyze_trends(days),
                'keyword_insights': {}
            }
            
            # 获取所有关键词
            all_keywords = set()
            for i in range(days):
                date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                findings = self.storage.load_findings(date)
                if findings:
                    all_keywords.update(f['keyword'] for f in findings)
            
            # 为每个关键词生成洞察
            for keyword in all_keywords:
                report['keyword_insights'][keyword] = self.get_keyword_insights(keyword, days)
            
            # 生成摘要
            report['summary'] = {
                'total_keywords': len(all_keywords),
                'total_findings': sum(len(report['keyword_insights'][k]['daily_mentions']) 
                                    for k in all_keywords),
                'period': f"最近{days}天"
            }
            
            return report
        except Exception as e:
            self.logger.error(f"报告生成失败: {str(e)}")
            return {}
