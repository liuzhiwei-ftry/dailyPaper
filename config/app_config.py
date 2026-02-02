import os
import configparser
from pathlib import Path

# 数据库文件存储路径：项目根目录下的 daily_paper.db
DB_PATH = Path(__file__).parent.parent / "daily_paper.db"
# 配置文件存储路径（项目根目录下的config.ini）
CONFIG_FILE = Path(__file__).parent.parent / "config.ini"

class AppConfig:
    """全局应用配置类（仅保留ARK_API_KEY+模型名，对齐附件逻辑）"""
    def __init__(self):
        # 仅保留核心配置（附件仅需这两个）
        self.ark_api_key = ""          # 火山方舟ARK_API_KEY（唯一鉴权字段）
        self.model_name = "doubao-seed-1-6-lite-251015"  # 默认目标模型
        # 应用基础配置（保留原有）
        self.window_geometry = ""      # 窗口大小位置
        self.default_template = "默认日报模板"  # 默认模板名称

        # 初始化配置解析器，加载配置文件
        self.config = configparser.ConfigParser()
        self.load_config()

    def load_config(self):
        """加载配置文件，无文件则创建空配置"""
        if os.path.exists(CONFIG_FILE):
            self.config.read(CONFIG_FILE, encoding="utf-8")
            # 读取火山方舟配置（ARK_CONFIG节点）
            self.ark_api_key = self.config.get("ARK_CONFIG", "ark_api_key", fallback="")
            self.model_name = self.config.get("ARK_CONFIG", "model_name", fallback="doubao-seed-1-6-lite-251015")
            # 读取应用配置
            self.window_geometry = self.config.get("APP_CONFIG", "window_geometry", fallback="")
            self.default_template = self.config.get("APP_CONFIG", "default_template", fallback="默认日报模板")

    def save_config(self):
        """保存配置到文件，utf-8编码避免中文乱码"""
        # 确保ARK_CONFIG节点存在
        if not self.config.has_section("ARK_CONFIG"):
            self.config.add_section("ARK_CONFIG")
        # 仅保存ARK_API_KEY和模型名（核心修改）
        self.config.set("ARK_CONFIG", "ark_api_key", self.ark_api_key)
        self.config.set("ARK_CONFIG", "model_name", self.model_name)

        # 确保APP_CONFIG节点存在
        if not self.config.has_section("APP_CONFIG"):
            self.config.add_section("APP_CONFIG")
        self.config.set("APP_CONFIG", "window_geometry", self.window_geometry)
        self.config.set("APP_CONFIG", "default_template", self.default_template)

        # 写入配置文件
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            self.config.write(f)

# 创建全局配置实例，其他模块直接导入使用
global_config = AppConfig()