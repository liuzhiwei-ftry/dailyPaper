import sys
import os
import qdarkstyle  # 可选，若安装了可开启，增强科技风
# 统一导入需要的Qt类，按模块划分避免混乱
from PySide6.QtWidgets import QApplication, QMessageBox, QStyleFactory
from PySide6.QtGui import QFont
from ui.main_window import DailyReportGenerator
from config.app_config import global_config
from db.db_init import init_database
from config.style_config import GLOBAL_FONT  # 从正确的样式文件导入全局字体

if __name__ == "__main__":
    try:
        # 1. 先实例化QApplication（Qt GUI资源初始化，必须是第一个Qt相关操作）
        app = QApplication(sys.argv)
        # 2. 初始化全局字体（从style_config.py导入，而非错误的global_config）
        app.setFont(GLOBAL_FONT)
        # 3. 初始化数据库（非Qt操作，顺序可在QApplication后）
        init_database()

        # ========== 核心修改：兼容系统环境变量的ARK_API_KEY判断 ==========
        # 优先取本地配置文件的API_KEY，为空则取系统环境变量的
        ark_api_key = global_config.ark_api_key.strip() if (global_config.ark_api_key and global_config.ark_api_key.strip()) else os.getenv("ARK_API_KEY", "").strip()
        # 两者都为空时，才弹出提示并退出
        if not ark_api_key:
            QMessageBox.critical(
                None,
                "环境配置错误",
                "请先配置ARK_API_KEY！\n方式1：系统 → 配置（本地文件）\n方式2：设置系统环境变量ARK_API_KEY",
                QMessageBox.Ok
            )
            sys.exit(0)
        # 若环境变量有值、本地配置无值，临时赋值给全局配置（让AI客户端能正常调用）
        elif not global_config.ark_api_key.strip() and ark_api_key:
            global_config.ark_api_key = ark_api_key
            # 可选：自动保存环境变量的key到本地配置文件，避免下次启动再读取环境变量
            # global_config.save_config()

        # 可选：开启qdarkstyle深色样式，和科技风更搭（需先安装：pip install qdarkstyle）
        # app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyside6'))
        app.setStyle(QStyleFactory.create('Fusion'))

        # 5. 实例化主窗口并显示
        window = DailyReportGenerator()
        window.show()
        # 6. 启动应用循环
        sys.exit(app.exec())

    except Exception as e:
        # 捕获所有启动异常，弹窗显示错误信息（便于排查后续问题）
        QMessageBox.critical(
            None,
            "程序启动失败",
            f"启动出错，请检查日志：\n{str(e)}",
            QMessageBox.Ok
        )
        # 异常时正常退出程序
        sys.exit(1)