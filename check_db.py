import sqlite3

# 连接数据库
conn = sqlite3.connect('data.db')
cursor = conn.cursor()

# 查询前5篇论文数据
cursor.execute("SELECT paper_name, link, abstract, conference, year FROM paper LIMIT 5")
papers = cursor.fetchall()

# 打印查询结果
print("数据库中存储的论文数据:")
for paper in papers:
    print(f"论文名称: {paper[0]}")
    print(f"链接: {paper[1]}")
    print(f"摘要: {paper[2][:100]}...")
    print(f"会议: {paper[3]}")
    print(f"年份: {paper[4]}")  # 只打印摘要的前100个字符
    print("-"*50)

# 关闭数据库连接
conn.close()