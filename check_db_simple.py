import sqlite3
import os

# 检查正确的数据库文件名 - spider_run_all.py会创建特定的数据库文件
DB_FILENAME = "IJCAI2024Paper.db"

# 检查文件是否存在
if os.path.exists(DB_FILENAME):
    print(f"数据文件{DB_FILENAME}存在，大小: {os.path.getsize(DB_FILENAME)} bytes")
else:
    print(f"数据文件{DB_FILENAME}不存在。")
    exit()

try:
    # 连接到数据库
    conn = sqlite3.connect(DB_FILENAME)
    cursor = conn.cursor()
    
    # 查询数据库中的所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    if tables:
        print("数据库中的表:")
        for table in tables:
            print(f"- {table[0]}")
            
            # 查看表的结构
            cursor.execute(f"PRAGMA table_info({table[0]})")
            columns = cursor.fetchall()
            print("  表结构:")
            for column in columns:
                print(f"  - {column[1]} ({column[2]})")
            
            # 查询表中的记录数
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"  记录数: {count}")
            
            # 如果有记录，显示第一条记录
            if count > 0:
                print("  第一条记录:")
                cursor.execute(f"SELECT * FROM {table[0]} LIMIT 1")
                record = cursor.fetchone()
                for i, col in enumerate(columns):
                    # 如果是长文本，只显示前100个字符
                    if col[2] == 'TEXT' and len(str(record[i])) > 100:
                        print(f"  - {col[1]}: {str(record[i])[:100]}...")
                    else:
                        print(f"  - {col[1]}: {record[i]}")
    else:
        print("数据库中没有表。")
except Exception as e:
    print(f"访问数据库时出错: {e}")
finally:
    if 'conn' in locals():
        conn.close()