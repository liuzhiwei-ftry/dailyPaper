import sqlite3
from config.app_config import DB_PATH
import os

def init_database():
    """
    数据库初始化：仅创建不存在的表，仅在无默认模板时设置初始默认
    核心：不重复覆盖已有的is_default标记，保证持久化
    """
    # 确保数据库目录存在
    db_dir = os.path.dirname(DB_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. 创建历史记录表（history）- 保持原有结构
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        create_time TEXT NOT NULL,
        template_content TEXT NOT NULL,
        work_content TEXT NOT NULL,
        report_content TEXT NOT NULL
    )
    """)

    # 2. 创建模板表（templates）- 保持原有结构
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        template_name TEXT UNIQUE NOT NULL,
        template_type TEXT NOT NULL,
        content TEXT NOT NULL,
        create_time TEXT NOT NULL,
        is_default INTEGER DEFAULT 0
    )
    """)

    # 3. 初始化默认日报模板（仅当模板不存在时创建）
    cursor.execute("SELECT * FROM templates WHERE template_name = '默认日报模板'")
    if not cursor.fetchone():
        # 插入初始默认模板（仅首次创建）
        cursor.execute("""
        INSERT INTO templates (template_name, template_type, content, create_time, is_default)
        VALUES ('默认日报模板', '通用', '### 今日工作\\n{work_content}\\n### 工作总结\\n{summary}', datetime('now', 'localtime'), 1)
        """)
        print("初始化：创建默认日报模板并设为默认")
    else:
        # 仅当数据库中无任何默认模板时，才将默认日报模板设为默认（核心修复）
        cursor.execute("SELECT * FROM templates WHERE is_default = 1")
        if not cursor.fetchone():
            cursor.execute("UPDATE templates SET is_default = 1 WHERE template_name = '默认日报模板'")
            print("修复：无默认模板，将默认日报模板设为默认")

    # 提交并关闭连接
    conn.commit()
    conn.close()
    print(f"数据库初始化完成，路径：{DB_PATH}")

# 程序启动时执行一次初始化
if __name__ == "__main__":
    init_db()