import sqlite3
import os

DB_FILENAME = "IJCAI2024Paper.db"

# 检查文件是否存在
if not os.path.exists(DB_FILENAME):
    print(f"数据库文件 {DB_FILENAME} 不存在")
    exit(1)

# 连接到数据库
conn = sqlite3.connect(DB_FILENAME)
cursor = conn.cursor()

# 删除paper表中的所有记录
try:
    cursor.execute("DELETE FROM paper")
    conn.commit()
    print("已成功删除数据库中的所有论文记录")

except sqlite3.Error as e:
    print(f"删除记录时出错: {e}")
    conn.rollback()

# 关闭连接
conn.close()