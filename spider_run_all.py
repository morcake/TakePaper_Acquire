import os
import sqlite3
import argparse
import os

from lib import SpiderCVPR, SpiderICCV, SpiderECCV, SpiderIJCAI


def create_db(conference, year):
    # 根据会议和年份生成数据库文件名
    db_filename = f"{conference.upper()}{year}Paper.db"
    
    if os.path.exists(db_filename):
        return db_filename

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
    
    return db_filename


def main():
    parser = argparse.ArgumentParser(description='爬取会议论文信息')
    parser.add_argument('--conference', type=str, required=True, choices=['cvpr', 'iccv', 'eccv', 'ijcai'],
                        help='会议名称: cvpr, iccv, eccv 或 ijcai')
    parser.add_argument('--year', type=int, required=True,
                        help='会议年份, 例如: 2025')
    parser.add_argument('--interval', type=int, default=1,
                        help='爬取间隔时间(秒), 默认为1秒')

    args = parser.parse_args()

    # 创建数据库并获取数据库文件名
    db_filename = create_db(args.conference, args.year)

    # 根据会议类型创建对应的爬虫实例，并传入数据库文件名
    if args.conference == 'cvpr':
        spider = SpiderCVPR(args.conference, args.year, data_file=db_filename)
    elif args.conference == 'iccv':
        spider = SpiderICCV(args.conference, args.year, data_file=db_filename)
    elif args.conference == 'eccv':
        spider = SpiderECCV(args.conference, args.year, data_file=db_filename)
    elif args.conference == 'ijcai':
        spider = SpiderIJCAI(args.conference, args.year, data_file=db_filename)
    else:
        raise ValueError('不支持的会议类型')

    # 运行爬虫
    spider.run_spider(interval=args.interval)


if __name__ == '__main__':
    main()