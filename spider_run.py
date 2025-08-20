import os
import sqlite3
from lib import SpiderCVPR

def create_db():
    # 规范的数据库文件名
    db_filename = 'data.db'
    
    if os.path.exists(db_filename):
        return

    conn = sqlite3.connect(db_filename)
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

if __name__ == '__main__':
    create_db()
    conference = 'CVPR'
    year = 2025
    spider = SpiderCVPR(conference, year)
    spider.run_spider(interval=1)
