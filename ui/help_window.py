from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton,
                               QWidget, QScrollArea, QApplication)
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QFont, QScreen

# 导入全局样式和字体（与项目原有样式统一）
from config.style_config import (
    GLOBAL_FONT, BOLD_FONT, TITLE_FONT,
    MAIN_WINDOW_STYLE, CONTAINER_STYLE,
    LABEL_STYLE, BTN_MAIN_STYLE
)

class HelpWindow(QDialog):
    """帮助窗口 - 用户操作手册（API配置+程序使用完整步骤）"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)  # 模态窗口，打开时无法操作主窗口
        self.init_ui()
        self.center_window()  # 窗口居中

    def init_ui(self):
        # 窗口基础设置
        self.setWindowTitle("📖 智能日报工具 - 用户操作手册")
        self.resize(700, 600)  # 手册窗口尺寸
        self.setMinimumSize(600, 500)  # 最小尺寸
        self.setFont(GLOBAL_FONT)
        self.setStyleSheet(MAIN_WINDOW_STYLE + LABEL_STYLE)

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setAlignment(Qt.AlignTop)

        # 标题
        title_label = QLabel("🔥 智能日报生成工具 - 完整操作手册")
        title_label.setFont(TITLE_FONT)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # 滚动区域（核心：支持长文本滚动查看）
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea {border: none;}")
        # 滚动区域内容容器
        content_widget = QWidget()
        content_widget.setStyleSheet(CONTAINER_STYLE)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(30, 30, 30, 30)
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area, stretch=1)  # 占满剩余高度

        # ------------------- 手册核心内容（按步骤编写）-------------------
        # 章节1：前置准备（API密钥获取+模型开通）
        step1_title = QLabel("一、前置准备：获取ARK_API_KEY并开通模型权限")
        step1_title.setFont(BOLD_FONT)
        step1_title.setStyleSheet("color: #2E86AB;")
        content_layout.addWidget(step1_title)

        step1_content = QLabel("""
1. 打开火山方舟官方平台：<a href="https://www.volcengine.com/">https://www.volcengine.com/</a><br>
2. 使用你的火山引擎账号登录平台（无账号请先注册）；<br>
3. 进入「个人中心」→「API密钥」，复制<strong>完整的ARK_API_KEY</strong>（务必删除前后空格，避免配置错误）；<br>
4. 进入平台「模型市场」，搜索模型名 <strong>doubao-seed-1-6-lite-251015</strong>；<br>
5. 找到目标模型后，点击「开通使用」（必须开通，否则调用模型会报403权限错误）；<br>
6. 确认模型开通成功后，返回程序进行配置。
""")
        step1_content.setTextFormat(Qt.RichText)  # 支持富文本（粗体、超链接）
        step1_content.setOpenExternalLinks(True)  # 超链接可直接打开浏览器
        step1_content.setWordWrap(True)  # 自动换行
        content_layout.addWidget(step1_content)

        # 章节2：程序配置（ARK_API_KEY填写+保存）
        step2_title = QLabel("二、程序配置：填写密钥并保存（实时生效）")
        step2_title.setFont(BOLD_FONT)
        step2_title.setStyleSheet("color: #2E86AB;")
        content_layout.addWidget(step2_title)

        step2_content = QLabel("""
1. 运行本智能日报生成工具，主窗口自动屏幕居中；<br>
2. 点击主窗口顶部「系统」→「配置」，打开配置窗口；<br>
3. 在「ARK API Key」输入框中，粘贴步骤一中复制的<strong>完整ARK_API_KEY</strong>；<br>
4. 模型文本框默认为<strong>doubao-seed-1-6-lite-251015</strong>（无需手动修改）；<br>
5. 点击「💾 保存配置」，弹窗提示「配置成功」即完成设置（<strong>无需重启程序</strong>，实时生效）；<br>
6. 配置窗口可点击「🔄 重置默认」清空密钥（谨慎操作）。
""")
        step2_content.setTextFormat(Qt.RichText)
        step2_content.setWordWrap(True)
        content_layout.addWidget(step2_content)

        # 章节3：生成日报（模板编辑+工作内容+一键生成）
        step3_title = QLabel("三、生成日报：模板编辑+内容填写+一键生成")
        step3_title.setFont(BOLD_FONT)
        step3_title.setStyleSheet("color: #2E86AB;")
        content_layout.addWidget(step3_title)

        step3_content = QLabel("""
1. 回到主窗口，点击「模版编辑」Tab，填写你的日报固定模板（保留格式和层级，支持编辑）；<br>
2. 点击「工作内容」Tab，粘贴你的当日实际工作内容（内容越详细，生成结果越精准）；<br>
3. 确认模板和工作内容非空后，点击「🚀 生成日报」按钮，开始调用AI模型；<br>
4. 生成过程中，「生成结果」Tab会<strong>实时流式显示</strong>日报内容，「执行日志」Tab可查看调用状态；<br>
5. 生成中可点击「🛑 生成中断」终止请求，生成完成后结果可直接编辑/复制；<br>
6. 生成的日报会自动保存到历史记录，可通过「历史」→「历史记录」查看/导出Excel。
""")
        step3_content.setTextFormat(Qt.RichText)
        step3_content.setWordWrap(True)
        content_layout.addWidget(step3_content)

        # 章节4：常见问题提示
        step4_title = QLabel("四、常见问题：核心报错解决方案")
        step4_title.setFont(BOLD_FONT)
        step4_title.setStyleSheet("color: #E74C3C;")
        content_layout.addWidget(step4_title)

        step4_content = QLabel("""
❌ 403权限错误：未开通doubao-seed-1-6-lite-251015模型权限，返回火山方舟平台重新开通；<br>
❌ 客户端初始化失败：ARK_API_KEY填写错误/有空格，重新粘贴纯密钥并保存；<br>
❌ Model not found：模型名拼写错误，直接在配置窗口选择下拉框模型，不要手动输入；<br>
❌ 流式生成无内容：网络被代理/防火墙拦截，关闭后重新生成；<br>
⚠️ 生成内容格式错乱：确保模板无特殊字符，工作内容描述清晰，重新编辑后生成。
""")
        step4_content.setTextFormat(Qt.RichText)
        step4_content.setWordWrap(True)
        content_layout.addWidget(step4_content)

        # 底部关闭按钮
        close_btn = QPushButton("❌ 关闭手册")
        close_btn.setStyleSheet(BTN_MAIN_STYLE)
        close_btn.clicked.connect(self.close)
        close_btn.setMinimumWidth(120)
        # 按钮居中布局
        btn_layout = QVBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.addWidget(close_btn)
        main_layout.addLayout(btn_layout)

    def center_window(self):
        """窗口垂直+水平居中（与其他窗口统一逻辑）"""
        screen_geometry = QScreen.availableGeometry(QApplication.primaryScreen())
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_geometry.center())
        self.move(window_geometry.topLeft())

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = HelpWindow()
    window.show()
    sys.exit(app.exec())