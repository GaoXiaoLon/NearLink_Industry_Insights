import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from datetime import datetime
from utils.logger import get_logger


class ReportGenerator:
    def __init__(self):
        self.logger = get_logger("report")
        self.template = """
        <html>
        <head>
            <meta charset="UTF-8">
            <title>星闪行业日报</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; }
                h1 { color: #2c3e50; border-bottom: 2px solid #3498db; }
                h2 { color: #2980b9; }
                .news-item { margin-bottom: 20px; padding: 10px; border-left: 3px solid #3498db; }
                .news-title { font-weight: bold; color: #2c3e50; }
                .news-source { color: #7f8c8d; font-size: 0.9em; }
                .chart { margin: 20px 0; text-align: center; }
                table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
                th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
            <h1>星闪行业日报 - {date}</h1>
            <h2>数据概览</h2>
            {summary}
            <h2>新闻来源分布</h2>
            <div class="chart">
                <img src="data:image/png;base64,{chart1}" alt="新闻来源分布">
            </div>
            <h2>时间趋势</h2>
            <div class="chart">
                <img src="data:image/png;base64,{chart2}" alt="时间趋势">
            </div>
            <h2>热门新闻</h2>
            {news_items}
            <h2>详细数据</h2>
            {table}
            <p style="text-align: right; color: #7f8c8d;">
                报告生成时间: {generated_time}
            </p>
        </body>
        </html>
        """

    def generate(self, articles):
        """生成完整报告"""
        try:
            df = pd.DataFrame(articles)

            # 生成图表
            chart1 = self._generate_source_distribution_chart(df)
            chart2 = self._generate_time_trend_chart(df)

            # 生成报告内容
            summary = self._generate_summary(df)
            news_items = self._generate_news_items(df.head(5))
            table = self._generate_data_table(df)

            report = self.template.format(
                date=datetime.now().strftime('%Y年%m月%d日'),
                summary=summary,
                chart1=chart1,
                chart2=chart2,
                news_items=news_items,
                table=table,
                generated_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )

            return report
        except Exception as e:
            self.logger.error(f"生成报告时出错: {str(e)}")
            return None

    def _generate_summary(self, df):
        """生成摘要信息"""
        total = len(df)
        sources = df['source'].nunique()
        latest_time = df['time'].max()

        return f"""
        <p>今日共收集到 <strong>{total}</strong> 条行业新闻，来自 <strong>{sources}</strong> 个不同来源。</p>
        <p>最新新闻发布时间: <strong>{latest_time}</strong></p>
        """

    def _generate_source_distribution_chart(self, df):
        """生成来源分布图表"""
        plt.figure(figsize=(10, 6))
        df['source'].value_counts().plot(kind='bar', color='#3498db')
        plt.title('新闻来源分布')
        plt.xlabel('来源')
        plt.ylabel('数量')
        plt.tight_layout()

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode('utf-8')

    def _generate_time_trend_chart(self, df):
        """生成时间趋势图表"""
        if 'time' in df.columns:
            df['hour'] = pd.to_datetime(df['time']).dt.hour
            time_counts = df['hour'].value_counts().sort_index()

            plt.figure(figsize=(10, 6))
            time_counts.plot(kind='line', marker='o', color='#e74c3c')
            plt.title('新闻发布时间趋势')
            plt.xlabel('小时')
            plt.ylabel('数量')
            plt.xticks(range(0, 24))
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.tight_layout()

            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            return base64.b64encode(buffer.read()).decode('utf-8')
        return ""

    def _generate_news_items(self, df):
        """生成新闻条目HTML"""
        items = []
        for _, row in df.iterrows():
            items.append(f"""
            <div class="news-item">
                <div class="news-title">{row['title']}</div>
                <div class="news-source">{row['source']} - {row['time']}</div>
                <p>{row['description']}</p>
                <a href="{row['url']}" target="_blank">阅读原文</a>
            </div>
            """)
        return "\n".join(items)

    def _generate_data_table(self, df):
        """生成数据表格"""
        if len(df) > 0:
            return df[['title', 'source', 'time']].to_html(index=False, classes='data-table')
        return "<p>无数据</p>"