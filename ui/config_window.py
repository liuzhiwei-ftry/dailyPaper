from PySide6.QtGui import QScreen
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QMessageBox,
                               QWidget, QApplication)
from PySide6.QtCore import Qt
from config.app_config import global_config
from config.style_config import (
    GLOBAL_FONT, BOLD_FONT, TITLE_FONT,
    MAIN_WINDOW_STYLE, CONTAINER_STYLE,
    INPUT_STYLE, BTN_MAIN_STYLE, LABEL_STYLE
)

class ConfigWindow(QDialog):
    """系统配置窗口（ARK_API_KEY+模型文本输入，支持自定义模型名）"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
        # 核心：定义默认模型（原下拉框的目标模型，作为文本框默认值）
        self.default_model = "doubao-seed-1-6-lite-251015"
        self.init_ui()
        self.load_config()  # 加载已保存的配置

    def init_ui(self):
        self.setWindowTitle("系统配置 - 火山方舟鉴权")
        self.setGeometry(400, 300, 500, 280)
        self.setMinimumSize(450, 250)
        self.setFont(GLOBAL_FONT)
        self.setStyleSheet(MAIN_WINDOW_STYLE + LABEL_STYLE + INPUT_STYLE)

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setAlignment(Qt.AlignTop)

        # 标题
        title_label = QLabel("🔥 火山方舟AI配置（仅需ARK_API_KEY）")
        title_label.setFont(TITLE_FONT)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # 配置容器
        config_container = QWidget()
        config_container.setObjectName("container")
        config_container.setStyleSheet(CONTAINER_STYLE)
        config_layout = QVBoxLayout(config_container)
        config_layout.setSpacing(12)
        config_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.addWidget(config_container, stretch=1)

        # 1. ARK API Key 输入框（唯一鉴权字段，核心）
        self.ak_label = QLabel("ARK API Key：")
        self.ak_label.setFont(BOLD_FONT)
        self.ak_edit = QLineEdit()
        self.ak_edit.setPlaceholderText("输入火山方舟平台获取的ARK_API_KEY（唯一鉴权，无前后空格）")
        self.ak_edit.setEchoMode(QLineEdit.PasswordEchoOnEdit)  # 输入时隐藏，选中显示
        config_layout.addWidget(self.ak_label)
        config_layout.addWidget(self.ak_edit)

        # 2. AI模型名 文本输入框（核心修改：替换下拉框，支持自定义模型）
        self.model_label = QLabel("AI模型名：")
        self.model_label.setFont(BOLD_FONT)
        self.model_edit = QLineEdit()  # 替换QComboBox为QLineEdit
        # 占位符提示：告知默认模型+输入规则，降低用户使用成本
        self.model_edit.setPlaceholderText(
            f"输入火山方舟模型名（默认推荐：{self.default_model}，需先在平台开通模型权限）"
        )
        config_layout.addWidget(self.model_label)
        config_layout.addWidget(self.model_edit)

        # 底部按钮布局
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)
        btn_layout.setAlignment(Qt.AlignCenter)

        self.save_btn = QPushButton("💾 保存配置")
        self.save_btn.setStyleSheet(BTN_MAIN_STYLE)
        self.save_btn.clicked.connect(self.save_config)

        self.reset_btn = QPushButton("🔄 重置默认")
        self.reset_btn.setStyleSheet(BTN_MAIN_STYLE)
        self.reset_btn.clicked.connect(self.reset_config)

        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.reset_btn)
        main_layout.addLayout(btn_layout)

        # 窗口居中
        self.center_window()

    def center_window(self):
        """窗口屏幕垂直+水平居中"""
        screen_geometry = QScreen.availableGeometry(QApplication.primaryScreen())
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_geometry.center())
        self.move(window_geometry.topLeft())

    def load_config(self):
        """加载全局配置到界面控件：有历史模型则加载，无则填充默认模型"""
        # 加载已保存的ARK_API_KEY
        self.ak_edit.setText(global_config.ark_api_key)
        # 加载模型名：有历史配置则用历史，无则填充默认模型（核心优化）
        if global_config.model_name and global_config.model_name.strip():
            self.model_edit.setText(global_config.model_name.strip())
        else:
            self.model_edit.setText(self.default_model)

    def save_config(self):
        """保存配置到全局+本地文件，仅校验ARK_API_KEY，模型名由用户自行保证有效性"""
        # 获取界面输入值并去空格（关键：去空格避免模型名/密钥带无效字符）
        ark_api_key = self.ak_edit.text().strip()
        model_name = self.model_edit.text().strip()

        # 唯一必填项校验：ARK API Key不能为空
        if not ark_api_key:
            QMessageBox.warning(self, "配置错误", "ARK API Key为唯一必填项，不能为空！", QMessageBox.Ok)
            self.ak_edit.setFocus()
            return
        # 模型名非空兜底：若用户清空，自动填充默认模型
        if not model_name:
            model_name = self.default_model
            self.model_edit.setText(model_name)

        # 更新全局配置（实时生效，无需重启程序）
        global_config.ark_api_key = ark_api_key
        global_config.model_name = model_name

        # 保存到本地config.ini文件，持久化存储
        global_config.save_config()

        # 保存成功提示（提示模型名，提醒用户开通权限）
        QMessageBox.information(
            self,
            "配置成功",
            f"火山方舟配置已保存并实时生效！\n✅ ARK API Key：{ark_api_key[:10]}****（已脱敏）\n✅ 选中模型：{model_name}\n⚠️  请确保已在火山方舟平台开通该模型的使用权限！",
            QMessageBox.Ok
        )
        self.close()

    def reset_config(self):
        """重置配置为默认值：清空ARK_API_KEY，模型名恢复默认"""
        # 二次确认，防止用户误操作
        if QMessageBox.question(
            self, "确认重置",
            "是否确定重置所有配置为默认值？\n已保存的ARK_API_KEY将被清空，模型名恢复为默认！",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        ) == QMessageBox.No:
            return
        # 重置控件值：清空密钥，恢复默认模型
        self.ak_edit.clear()
        self.model_edit.setText(self.default_model)
        QMessageBox.information(self, "重置成功", "配置已重置为默认值！", QMessageBox.Ok)

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    window = ConfigWindow()
    window.show()
    sys.exit(app.exec())