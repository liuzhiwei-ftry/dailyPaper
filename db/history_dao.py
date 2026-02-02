import sqlite3
from datetime import datetime
from config.app_config import DB_PATH

class HistoryDAO:
    """历史记录数据访问对象（新增template_content字段支持+条件查询+健壮性优化）"""
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row  # 支持按列名访问

    def __del__(self):
        if self.conn:
            self.conn.close()

    def add_history(self, template_content: str, work_content: str, report_content: str) -> int:
        """新增历史记录（新增template_content参数）"""
        try:
            cursor = self.conn.cursor()
            create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
            INSERT INTO history (create_time, template_content, work_content, report_content)
            VALUES (?, ?, ?, ?)
            """, (create_time, template_content, work_content, report_content))
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            self.conn.rollback()
            print(f"新增历史记录失败：{e}")
            return -1

    def get_all_template_types(self):
        """查询所有唯一的模板类型（从templates表查询，适配筛选）"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT DISTINCT template_type FROM templates WHERE template_type IS NOT NULL")
            template_types = [row["template_type"] for row in cursor.fetchall()]
            return template_types
        except sqlite3.Error as e:
            print(f"查询模板类型失败: {e}")
            return []

    # ========== 新增核心方法：条件查询历史记录 ==========
    def get_history_by_conditions(self, keyword: str = "", template_type: str = "") -> list:
        """
        按条件查询历史记录（适配搜索关键词+模板类型筛选）
        :param keyword: 搜索关键词（匹配时间/模板内容/工作内容/生成结果）
        :param template_type: 模板类型（先查对应模板内容，再匹配历史记录的template_content）
        :return: 符合条件的历史记录列表
        """
        try:
            cursor = self.conn.cursor()
            # 基础SQL和参数列表
            sql = "SELECT * FROM history WHERE 1=1"
            params = []

            # 1. 模板类型筛选：先查templates表中该类型的所有模板内容，再模糊匹配历史记录的template_content
            if template_type:
                # 子查询：获取指定模板类型的所有模板内容
                sql += " AND template_content IN (SELECT content FROM templates WHERE template_type = ?)"
                params.append(template_type)

            # 2. 关键词搜索：匹配生成时间/模板内容/工作内容/生成结果
            if keyword:
                sql += """ AND (create_time LIKE ? 
                              OR template_content LIKE ? 
                              OR work_content LIKE ? 
                              OR report_content LIKE ?)"""
                like_key = f"%{keyword}%"
                params.extend([like_key, like_key, like_key, like_key])

            # 按生成时间倒序
            sql += " ORDER BY create_time DESC"
            cursor.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"条件查询历史记录失败：{e}")
            self.conn.rollback()
            return []
    # ========== 新增方法结束 ==========

    def get_all_history(self) -> list:
        """获取所有历史记录（含template_content）"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM history ORDER BY create_time DESC")
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"查询全量历史记录失败：{e}")
            return []

    def delete_history(self, history_id: int) -> bool:
        """删除指定历史记录"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM history WHERE id = ?", (history_id,))
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            self.conn.rollback()
            print(f"删除历史记录失败：{e}")
            return False

    def get_history_by_id(self, history_id: int) -> dict:
        """根据ID获取单条记录（含template_content）"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM history WHERE id = ?", (history_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            print(f"查询单条历史记录失败：{e}")
            return None

class TemplateDAO:
    """模板数据访问对象（无修改，保持原有功能）"""
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row

    def __del__(self):
        if self.conn:
            self.conn.close()

    def add_template(self, template_name: str, template_type: str, content: str) -> bool:
        """新增模板（名称唯一，默认is_default=0）"""
        try:
            cursor = self.conn.cursor()
            create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
            INSERT INTO templates (template_name, template_type, content, create_time, is_default)
            VALUES (?, ?, ?, ?, 0)
            """, (template_name, template_type, content, create_time))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        except Exception as e:
            print(f"新增模板失败：{e}")
            self.conn.rollback()
            return False

    def update_template(self, template_name: str, template_type: str, content: str) -> bool:
        """编辑保存模板（根据名称覆盖内容/类型）"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
            UPDATE templates
            SET template_type = ?, content = ?
            WHERE template_name = ?
            """, (template_type, content, template_name))
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"编辑模板失败：{e}")
            self.conn.rollback()
            return False

    def get_all_templates(self, template_type: str = None) -> list:
        """获取模板列表（可选按类型筛选，包含is_default）"""
        cursor = self.conn.cursor()
        if template_type:
            cursor.execute("SELECT * FROM templates WHERE template_type = ? ORDER BY is_default DESC, create_time DESC", (template_type,))
        else:
            cursor.execute("SELECT * FROM templates ORDER BY is_default DESC, create_time DESC")
        return [dict(row) for row in cursor.fetchall()]

    def get_template_by_name(self, template_name: str) -> dict:
        """按名称获取模板"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM templates WHERE template_name = ?", (template_name,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_default_template(self) -> dict:
        """获取当前默认模板（is_default=1）"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM templates WHERE is_default = 1")
        row = cursor.fetchone()
        return dict(row) if row else self.get_template_by_name("默认日报模板")

    def set_default_template(self, template_name: str) -> bool:
        """设为默认模板：先置空所有，再标记当前（修复rowcount判断+强制提交+无回滚）"""
        try:
            cursor = self.conn.cursor()
            # 步骤1：将所有模板的默认标记置0（必执行，不影响结果判断）
            cursor.execute("UPDATE templates SET is_default = 0")
            # 步骤2：将指定模板标记为默认（核心更新）
            cursor.execute("UPDATE templates SET is_default = 1 WHERE template_name = ?", (template_name,))
            # 关键修复：直接提交，不根据rowcount判断（避免前置更新影响）
            self.conn.commit()
            # 二次校验：查询数据库确认是否设置成功（保证结果准确）
            cursor.execute("SELECT is_default FROM templates WHERE template_name = ?", (template_name,))
            row = cursor.fetchone()
            return row and row["is_default"] == 1
        except Exception as e:
            print(f"设为默认模板失败：{e}")
            self.conn.rollback()
            return False

    def delete_template(self, template_name: str) -> bool:
        """删除模板（默认日报模板不可删）"""
        try:
            cursor = self.conn.cursor()
            if template_name == "默认日报模板":
                return False
            template = self.get_template_by_name(template_name)
            if not template:
                return False
            is_current_default = template["is_default"] == 1
            cursor.execute("DELETE FROM templates WHERE template_name = ?", (template_name,))
            if is_current_default:
                cursor.execute("UPDATE templates SET is_default = 1 WHERE template_name = '默认日报模板'")
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"删除模板失败：{e}")
            self.conn.rollback()
            return False