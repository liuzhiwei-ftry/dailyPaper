from db.history_dao import TemplateDAO

class TemplateManager:
    """模板管理核心逻辑（新增：编辑、删除、设为默认、加载到主窗口）"""
    def __init__(self):
        self.template_dao = TemplateDAO()

    def get_default_template(self) -> str:
        """获取当前数据库标记的默认模板内容（替代原固定名称逻辑）"""
        default_template = self.template_dao.get_default_template()
        return default_template["content"] if default_template else ""

    def get_default_template_name(self) -> str:
        """获取当前默认模板名称"""
        default_template = self.template_dao.get_default_template()
        return default_template["template_name"] if default_template else "默认日报模板"

    def add_template(self, template_name: str, template_type: str, content: str) -> bool:
        """新增模板"""
        return self.template_dao.add_template(template_name, template_type, content)

    def update_template(self, template_name: str, template_type: str, content: str) -> bool:
        """编辑保存模板（修改后覆盖）"""
        return self.template_dao.update_template(template_name, template_type, content)

    def save_template(self, template_name: str, template_type: str, content: str) -> bool:
        """统一保存入口：新增（名称不存在）或编辑（名称存在）"""
        if self.template_dao.get_template_by_name(template_name):
            return self.update_template(template_name, template_type, content)
        else:
            return self.add_template(template_name, template_type, content)

    def load_template(self, template_name: str) -> str:
        """按名称加载模板内容"""
        template = self.template_dao.get_template_by_name(template_name)
        return template["content"] if template else ""

    def get_all_template_names(self, template_type: str = None) -> list:
        """获取所有模板名称（默认模板排首位）"""
        templates = self.template_dao.get_all_templates(template_type)
        return [t["template_name"] for t in templates]

    def set_default_template(self, template_name: str) -> bool:
        """将指定模板设为默认"""
        return self.template_dao.set_default_template(template_name)

    def delete_template(self, template_name: str) -> bool:
        """删除模板（系统默认日报模板不可删）"""
        return self.template_dao.delete_template(template_name)

    def get_template_info(self, template_name: str) -> dict:
        """获取模板完整信息（名称/类型/内容/是否默认）"""
        return self.template_dao.get_template_by_name(template_name)