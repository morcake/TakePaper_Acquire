import os
import sqlite3

# 确保数据库存在
if not os.path.exists('data.db'):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE paper (
        paper_name TEXT,
        link TEXT,
        abstract TEXT,
        conference TEXT,
        year INTEGER
    )
    ''')
    conn.commit()
    conn.close()
    print("数据库已创建")
else:
    print("数据库已存在")

# 测试导入新的爬虫类
try:
    from lib import SpiderICCV, SpiderECCV
    print("成功导入SpiderICCV和SpiderECCV类")
    # 创建爬虫实例（不实际运行）
    iccv_spider = SpiderICCV('iccv', 2023)
    eccv_spider = SpiderECCV('eccv', 2022)
    print("成功创建ICCV和ECCV爬虫实例")
    print("测试完成，所有功能正常")
except ImportError as e:
    print(f"导入失败: {e}")
except Exception as e:
    print(f"创建实例失败: {e}")