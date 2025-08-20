# Paper retrieval and analysis tools

## 项目简介

本项目是一个用于爬取和检索顶级学术会议论文的工具，旨在解决官方会议网站搜索功能受限的问题。通过本工具，用户可以便捷地获取CVPR、ICCV、ECCV、IJCAI等会议的论文信息，并基于标题和摘要进行关键词检索。

### 项目背景

学术会议官方网站通常存在以下局限性：
- 搜索功能不全面，往往只能基于标题检索
- 无法同时检索多篇会议论文
- 缺乏对论文摘要的高效检索

本项目通过爬取论文信息并建立本地数据库，实现了基于标题和摘要的多关键词检索，帮助研究人员更高效地筛选相关研究。

## 环境配置

### 系统要求
- Python 3.9 或更高版本
- 稳定的网络连接（用于爬取论文数据）

### 安装依赖
```bash
pip install -r requirements.txt
```

## 项目结构

```
e:\paper_viewer/
├── lib/                 # 核心代码库，包含爬虫实现
│   ├── spider_base.py   # 爬虫基类
│   ├── spider_cvpr.py   # CVPR会议爬虫实现
│   ├── spider_iccv.py   # ICCV会议爬虫实现
│   ├── spider_eccv.py   # ECCV会议爬虫实现
│   └── spider_ijcai.py  # IJCAI会议爬虫实现
├── temp/                # 临时文件存储目录
├── spider_run.py        # 原始CVPR爬虫运行脚本
├── spider_run_all.py    # 统一爬虫入口脚本
├── export_markdown.py   # 导出markdown格式结果的工具
├── check_db.py          # 数据库检查工具
├── check_db_simple.py   # 简易数据库检查工具
├── clear_db.py          # 数据库清理工具
└── *.db                 # 各会议论文数据库文件
```

## 文件功能说明

### 核心脚本
- **spider_run_all.py**: 支持爬取多种会议论文的主脚本，可通过命令行参数指定会议类型和年份
- **export_markdown.py**: 根据关键词筛选论文并导出为Markdown格式的工具
- **check_db.py**: 详细检查数据库内容的工具
- **check_db_simple.py**: 简单检查数据库内容的工具
- **clear_db.py**: 清空指定数据库内容的工具

### 爬虫模块
- **lib/spider_base.py**: 定义爬虫基类，实现通用爬虫功能
- **lib/spider_cvpr.py**: 针对CVPR会议的专用爬虫实现
- **lib/spider_iccv.py**: 针对ICCV会议的专用爬虫实现
- **lib/spider_eccv.py**: 针对ECCV会议的专用爬虫实现
- **lib/spider_ijcai.py**: 针对IJCAI会议的专用爬虫实现

### 测试工具
- **test_spiders.py**: 测试各种爬虫功能的脚本
- **test_*.py**: 其他专用测试脚本

## 使用指南

### 1. 爬取论文数据

使用`spider_run_all.py`脚本可以爬取指定会议和年份的论文数据。基本命令格式为：

```bash
python spider_run_all.py --conference [会议名称] --year [年份] --interval [爬取间隔]
```

#### 参数说明：
- `--conference` (必需): 指定会议名称，支持 cvpr、iccv、eccv、ijcai、miccai
- `--year` (必需): 指定会议年份，例如 2024
- `--interval` (可选): 爬取每篇论文之间的时间间隔（秒），默认为2秒，可根据实际网络情况调整

#### 使用示例：

```bash
# 爬取IJCAI 2024年论文
python spider_run_all.py --conference ijcai --year 2024

# 爬取CVPR 2025年论文，设置爬取间隔为2秒
python spider_run_all.py --conference cvpr --year 2025 --interval 2

# 爬取ICCV 2023年论文
python spider_run_all.py --conference iccv --year 2023 --interval 2

# 爬取ECCV 2024年论文
python spider_run_all.py --conference eccv --year 2024 --interval 2
```

### 2. 检查数据库

爬取完成后，可以使用以下工具检查数据库内容：

```bash
# 简单检查数据库内容
python check_db_simple.py

# 详细检查数据库内容
python check_db.py
```

### 3. 导出查询结果

使用`export_markdown.py`脚本可以根据关键词筛选论文并导出为Markdown格式：

```bash
python export_markdown.py --keyword [关键词] --output [输出文件名]
```

#### 参数说明：
- `--keyword`: 搜索关键词，可以使用多个关键词用空格分隔
- `--output`: 输出的Markdown文件名

#### 使用示例：

```bash
# 搜索包含"3D reconstruction"关键词的论文
python export_markdown.py --keyword "3D reconstruction" --output "3D_reconstruction.md"

# 搜索包含多个关键词的论文
python export_markdown.py --keyword "deep learning computer vision" --output "dl_cv_papers.md"
```

### 4. 清空数据库

如需清空特定会议的数据库内容，可以使用`clear_db.py`脚本：

```bash
python clear_db.py
```

## 数据库说明

本项目使用SQLite数据库存储论文信息，每个会议年份对应一个独立的数据库文件，例如：
- `IJCAI2024Paper.db`: 存储IJCAI 2024年会议论文
- `CVPR2025Paper.db`: 存储CVPR 2025年会议论文
- `ICCV2023Paper.db`: 存储ICCV 2023年会议论文
- `ECCV2024Paper.db`: 存储ECCV 2024年会议论文

数据库表结构包含以下字段：
- `paper_name`: 论文标题
- `link`: 论文链接
- `abstract`: 论文摘要
- `conference`: 会议名称
- `year`: 会议年份

## 常见问题解决

1. **爬取速度过慢**：可以通过调整`--interval`参数减少爬取间隔，但请注意不要设置得过小，以免对会议网站服务器造成过大压力。

2. **爬取过程中断**：爬虫支持断点续爬，重新运行相同命令即可从上次中断的地方继续爬取。

3. **搜索结果不准确**：确保使用的关键词准确反映您的搜索意图，可以尝试调整关键词或使用多个关键词组合。

## 注意事项

1. 本工具仅供学术研究使用，请遵守相关网站的使用条款。
2. 请合理设置爬取间隔，避免对会议网站造成不必要的负担。
3. 论文数据仅用于个人研究，不得用于商业用途。
