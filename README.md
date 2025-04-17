# 星闪行业洞察

一个用于监控和分析星闪行业信息的工具，可以定时搜集互联网上的行业信息，并生成报告发送到指定邮箱。

## 功能特点

- 定时监控指定网站
- 关键词匹配和内容提取
- 自动生成分析报告
- 邮件通知
- 友好的图形界面
- 完整的日志记录

## 安装说明

1. 克隆项目到本地：
```bash
git clone https://github.com/yourusername/starflash-insight.git
cd starflash-insight
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置：
- 复制 `config/default.json` 为 `config/config.json`
- 修改配置文件中的邮件和监控设置

## 使用说明

1. 运行程序：
```bash
python main.py
```

2. 在图形界面中：
- 配置邮件服务器信息
- 设置监控关键词和来源
- 设置定时任务时间
- 查看监控日志

## 目录结构

```
星闪行业洞察/
├── config/                      # 配置文件目录
│   ├── __init__.py
│   ├── default.json             # 主配置文件（需gitignore）
│   └── config_manager.py        # 配置加载器
│
├── core/                       # 核心业务逻辑
│   ├── __init__.py
│   ├── monitor.py               # 监测主逻辑
│   └── analyzer.py              # 数据分析模块
│
├── gui/                        # 图形界面
│   ├── __init__.py
│   ├── app.py                   # 主窗口
│   ├── components/              # 自定义组件
│   │   ├── __init__.py
│   │   ├── config_panel.py
│   │   ├── log_panel.py
│   │   └── widgets.py           # 自定义TKinter组件
│   └── resources/               # 静态资源
│       ├── icons/
│       └── styles/
│
├── services/                   # 服务层
│   ├── __init__.py
│   ├── email_sender.py          # 邮件服务
│   └── storage.py               # 数据存储
│
├── utils/                      # 工具函数
│   ├── __init__.py
│   ├── logger.py                # 日志配置
│   ├── scheduler.py             # 定时任务
│   └── network.py               # 网络工具
│
├── logs/                       # 日志目录（自动生成）
│   ├── app.log                  
│   └── errors.log
│
├── tests/                      # 测试代码
│   ├── __init__.py
│   ├── test_monitor.py
│   └── test_email.py
│
├── main.py                     # 程序入口
├── requirements.txt            # 依赖列表
└── README.md                   # 项目说明
```

## 注意事项

1. 请确保配置文件中的邮件服务器信息正确
2. 监控网站可能会限制爬虫访问，请合理设置访问间隔
3. 建议定期清理旧数据，避免占用过多磁盘空间

## 许可证

MIT License
