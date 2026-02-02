from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QWidget,
                               QApplication, QPushButton, QHBoxLayout)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QScreen, QTextOption
from config.style_config import (GLOBAL_FONT, BOLD_FONT, TITLE_FONT,
                                 MAIN_WINDOW_STYLE, CONTAINER_STYLE,
                                 BTN_MAIN_STYLE, LABEL_STYLE)


class AboutWindow(QDialog):
    """关于作者与工具窗口（最终版：火苗居中+按钮不压线+按钮带边框）"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.init_ui()
        self.center_window()

    def init_ui(self):
        # 窗口基础配置
        self.setWindowTitle("👤 关于 | 智能日报生成工具")
        self.resize(480, 490)
        self.setMinimumSize(480, 480)
        self.setFont(GLOBAL_FONT)
        # 主样式：保留原有所有样式
        self.setStyleSheet(MAIN_WINDOW_STYLE + LABEL_STYLE + """
            QLabel#descLabel {line-height: 1.6; font-size: 9.5pt; color: #34495E;}
            QWidget#infoCard {
                background-color: #F8F9FA;
                border: 1px solid #EAECEE;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                padding: 2px;
            }
            QPushButton {border-radius: 8px;}
            a {color:#2980B9; text-decoration:none;}
            a:hover {color:#1F618D;}
        """)

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(25)
        main_layout.setContentsMargins(30, 25, 30, 30)
        main_layout.setAlignment(Qt.AlignCenter)

        # ========== 1. 头部（火苗图标+标题+版本）==========
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setSpacing(8)
        header_layout.setAlignment(Qt.AlignCenter)
        header_layout.setContentsMargins(0, 0, 0, 0)

        # 🔥 火苗图标
        icon_container = QWidget()
        icon_container.setFixedSize(70, 70)
        icon_layout = QHBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setAlignment(Qt.AlignCenter)

        icon_label = QLabel("🔥")
        icon_label.setFont(QFont("微软雅黑", 36, QFont.Bold))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setContentsMargins(0, 0, 0, 0)
        icon_label.setStyleSheet("padding: 0px; margin: 0px;")
        icon_layout.addWidget(icon_label)
        header_layout.addWidget(icon_container, alignment=Qt.AlignCenter)

        # 工具标题
        title_label = QLabel("智能日报生成工具")
        title_label.setFont(TITLE_FONT)
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)

        # 版本号
        version_label = QLabel("Version 1.0.0 | 正式版")
        version_label.setFont(BOLD_FONT)
        version_label.setStyleSheet("color: #7F8C8D; font-size: 9pt;")
        version_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(version_label)

        main_layout.addWidget(header_widget, alignment=Qt.AlignCenter)

        # ========== 2. 核心信息卡片 ==========
        info_card = QWidget()
        info_card.setObjectName("infoCard")
        info_card.setFixedSize(380, 220)
        info_layout = QVBoxLayout(info_card)
        info_layout.setSpacing(12)
        info_layout.setContentsMargins(25, 25, 25, 25)
        info_layout.setAlignment(Qt.AlignTop)

        # 作者信息
        author_label = QLabel('<strong>开发作者：</strong>刘芝伟')
        author_label.setTextFormat(Qt.RichText)
        author_label.setFont(BOLD_FONT)
        author_label.setWordWrap(True)
        info_layout.addWidget(author_label)

        # 联系邮箱
        email_label = QLabel('<strong>联系邮箱：</strong>734867391@qq.com')
        email_label.setTextFormat(Qt.RichText)
        email_label.setFont(BOLD_FONT)
        email_label.setOpenExternalLinks(True)
        email_label.setWordWrap(True)
        info_layout.addWidget(email_label)

        # 工具简介
        desc_label = QLabel(
            '<strong>工具简介：</strong><br>基于火山方舟AI API开发的办公自动化工具，支持工作日报/周报快速生成、模板自定义管理、生成历史记录保存与多格式导出，高效提升办公效率。'
        )
        desc_label.setObjectName("descLabel")
        desc_label.setTextFormat(Qt.RichText)
        desc_label.setWordWrap(True)
        desc_label.setMinimumHeight(80)
        info_layout.addWidget(desc_label)

        # 核心依赖
        dep_label = QLabel('<strong>核心依赖：</strong>PySide6 · VolcEngine SDK · Pandas')
        dep_label.setTextFormat(Qt.RichText)
        dep_label.setStyleSheet("color: #6C7A89; font-size: 9pt;")
        dep_label.setWordWrap(True)
        info_layout.addWidget(dep_label)

        main_layout.addWidget(info_card, alignment=Qt.AlignCenter)

        # ========== 3. 关闭按钮（新增边框样式）==========
        close_btn = QPushButton("❌ 关闭窗口")
        # 核心修改：为按钮添加精致边框样式，兼容原有BTN_MAIN_STYLE
        close_btn.setStyleSheet(BTN_MAIN_STYLE + """
            QPushButton {
                border: 2px solid #2980B9; /* 主色边框 */
                background-color: #FFFFFF;  /* 白色底色 */
                color: #2980B9;            /* 文字颜色匹配边框 */
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #2980B9; /* hover时底色变主色 */
                color: #FFFFFF;            /* 文字变白 */
                border-color: #1F618D;     /* 边框加深 */
            }
            QPushButton:pressed {
                background-color: #1F618D; /* 按压时底色更深 */
                border-color: #1A5276;
            }
        """)
        close_btn.setFixedSize(160, 40)
        close_btn.clicked.connect(self.close)

        # 按钮布局
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.addWidget(close_btn)
        btn_layout.setContentsMargins(0, 20, 0, 10)
        main_layout.addLayout(btn_layout)

        # 底部拉伸
        main_layout.addStretch(1)

    def center_window(self):
        """窗口精准居中"""
        screen_geo = QScreen.availableGeometry(QApplication.primaryScreen())
        window_geo = self.frameGeometry()
        window_geo.moveCenter(screen_geo.center())
        self.move(window_geo.topLeft())


# 单独运行测试
if __name__ == "__main__":
    import sys
    # 模拟配置文件的字体和样式常量
    GLOBAL_FONT = QFont("微软雅黑", 10)
    BOLD_FONT = QFont("微软雅黑", 11, QFont.Bold)
    TITLE_FONT = QFont("微软雅黑", 18, QFont.Bold)
    MAIN_WINDOW_STYLE = CONTAINER_STYLE = BTN_MAIN_STYLE = LABEL_STYLE = ""

    app = QApplication(sys.argv)
    app.setFont(GLOBAL_FONT)
    window = AboutWindow()
    window.show()
    sys.exit(app.exec())