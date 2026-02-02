from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QTextEdit, QPushButton, QMessageBox, QLabel,
                               QProgressBar, QTabWidget, QMenuBar, QApplication)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QScreen

from core.generator import GenerateReportThread
from core.template_manager import TemplateManager
from db.history_dao import HistoryDAO
from utils.common_utils import CommonUtils
from config.style_config import (
    GLOBAL_FONT, BOLD_FONT, ITALIC_FONT, TITLE_FONT,
    MAIN_WINDOW_STYLE, CONTAINER_STYLE, TAB_STYLE,
    TEXT_EDIT_STYLE, PROGRESS_BAR_STYLE, LABEL_STYLE,
    BTN_MAIN_STYLE, BTN_DANGER_STYLE, MENU_STYLE
)


class DailyReportGenerator(QMainWindow):
    """主窗口（新增执行日志Tab，分离日志和生成结果）"""
    def __init__(self):
        super().__init__()
        self.template_manager = TemplateManager()
        self.history_dao = HistoryDAO()
        self.generate_thread = None
        self.loading_timer = QTimer()
        self.loading_texts = ["生成中", "生成中.", "生成中..", "生成中..."]
        self.loading_index = 0
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("AI日报生成工具 - 火山方舟")
        # 1. 设置主窗口大小+最小尺寸（避免被无限缩小导致遮挡）
        self.resize(950, 750)  # 主窗口基础尺寸，可根据屏幕调整
        self.setMinimumSize(900, 650)  # 最小尺寸，防止结果域被压缩

        self.setFont(GLOBAL_FONT)
        self.setStyleSheet(MAIN_WINDOW_STYLE + LABEL_STYLE + MENU_STYLE)

        # 菜单栏初始化
        self.init_menu()
        # 关键：Windows系统强制菜单栏独立显示，不融合到系统标题栏（修复隐藏问题）
        self.menuBar().setNativeMenuBar(False)

        # 中心部件+主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setAlignment(Qt.AlignTop)

        # ========== 1. 模板+工作内容Tab容器 ==========
        tab_container = QWidget()
        tab_container.setObjectName("container")
        tab_container.setStyleSheet(CONTAINER_STYLE)
        tab_layout = QVBoxLayout(tab_container)
        tab_layout.setSpacing(8)
        tab_layout.setContentsMargins(0, 0, 0, 0)

        self.tab_widget = QTabWidget()
        self.tab_widget.setMinimumHeight(200)
        self.tab_widget.setStyleSheet(TAB_STYLE)
        # Tab1：模板编辑
        self.template_tab = QWidget()
        template_layout = QVBoxLayout(self.template_tab)
        template_layout.setSpacing(6)
        template_label = QLabel("📋 日报生成模版（生成时自动读取）")
        template_label.setFont(TITLE_FONT)
        template_label.setObjectName("titleLabel")
        self.template_editor = QTextEdit()
        self.template_editor.setStyleSheet(TEXT_EDIT_STYLE)
        self.template_editor.setPlainText(self.template_manager.get_default_template())
        template_layout.addWidget(template_label)
        template_layout.addWidget(self.template_editor)
        self.tab_widget.addTab(self.template_tab, "📝 模版编辑")

        # Tab2：工作内容
        self.work_tab = QWidget()
        work_layout = QVBoxLayout(self.work_tab)
        work_layout.setSpacing(6)
        work_label = QLabel("📌 当日工作内容（纯文本输入/粘贴，无需格式化）")
        work_label.setFont(TITLE_FONT)
        work_label.setObjectName("titleLabel")
        self.work_editor = QTextEdit()
        self.work_editor.setStyleSheet(TEXT_EDIT_STYLE)
        self.work_editor.setPlaceholderText("示例：开发安全管理模块，完成2个子功能开发，1个接口联调进行中...")
        work_layout.addWidget(work_label)
        work_layout.addWidget(self.work_editor)
        self.tab_widget.addTab(self.work_tab, "📖 工作内容")

        tab_layout.addWidget(self.tab_widget)
        main_layout.addWidget(tab_container)

        # ========== 2. 功能按钮容器 ==========
        btn_container = QWidget()
        btn_container.setObjectName("container")
        btn_container.setStyleSheet(CONTAINER_STYLE)
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setSpacing(10)
        btn_layout.setContentsMargins(6, 6, 6, 6)
        btn_layout.setAlignment(Qt.AlignLeft)

        self.gen_btn = QPushButton("📝 生成日报")
        self.gen_btn.setStyleSheet(BTN_MAIN_STYLE)

        self.cancel_btn = QPushButton("🛑 生成中断")
        self.cancel_btn.setStyleSheet(BTN_DANGER_STYLE)
        self.cancel_btn.setEnabled(False)

        self.clear_btn = QPushButton("🗑️ 清空所有")
        self.clear_btn.setStyleSheet(BTN_MAIN_STYLE)

        self.copy_btn = QPushButton("📋 复制结果")
        self.copy_btn.setStyleSheet(BTN_MAIN_STYLE)

        btn_layout.addWidget(self.gen_btn)
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addWidget(self.copy_btn)
        btn_layout.addStretch()
        main_layout.addWidget(btn_container)

        # ========== 3. 加载提示容器 ==========
        loading_container = QWidget()
        loading_container.setObjectName("container")
        loading_container.setStyleSheet(CONTAINER_STYLE)
        loading_layout = QHBoxLayout(loading_container)
        loading_layout.setSpacing(10)
        loading_layout.setContentsMargins(6, 6, 6, 6)

        self.loading_label = QLabel("")
        self.loading_label.setFont(ITALIC_FONT)
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet(PROGRESS_BAR_STYLE)

        loading_layout.addWidget(self.loading_label)
        loading_layout.addWidget(self.progress_bar)
        main_layout.addWidget(loading_container)

        # ========== 4. 结果+日志双Tab容器（核心新增：分离结果和日志） ==========
        result_log_tab_container = QWidget()
        result_log_tab_container.setObjectName("container")
        result_log_tab_container.setStyleSheet(CONTAINER_STYLE)
        result_log_tab_layout = QVBoxLayout(result_log_tab_container)
        result_log_tab_layout.setSpacing(8)
        result_log_tab_layout.setContentsMargins(0, 0, 0, 0)

        # 结果+日志Tab组件
        self.result_log_tab = QTabWidget()
        self.result_log_tab.setStyleSheet(TAB_STYLE)
        self.result_log_tab.setMinimumHeight(280)

        # Tab1：生成结果（原有，仅显示日报内容，无日志）
        self.result_tab = QWidget()
        result_layout = QVBoxLayout(self.result_tab)
        result_layout.setSpacing(6)
        result_label = QLabel("📊 AI生成日报结果（支持编辑，可直接复制到办公软件）")
        result_label.setFont(TITLE_FONT)
        result_label.setObjectName("titleLabel")
        self.output_editor = QTextEdit()  # 仅绑定日报内容信号
        self.output_editor.setStyleSheet(TEXT_EDIT_STYLE)
        self.output_editor.setMinimumHeight(250)
        result_layout.addWidget(result_label)
        result_layout.addWidget(self.output_editor)
        self.result_log_tab.addTab(self.result_tab, "📋 生成结果")

        # Tab2：执行日志（新增，仅显示执行步骤，无结果）
        self.log_tab = QWidget()
        log_layout = QVBoxLayout(self.log_tab)
        log_layout.setSpacing(6)
        log_label = QLabel("📝 执行过程日志（生成/中断/错误信息均在此显示）")
        log_label.setFont(TITLE_FONT)
        log_label.setObjectName("titleLabel")
        self.log_editor = QTextEdit()  # 仅绑定日志信号
        self.log_editor.setStyleSheet(TEXT_EDIT_STYLE)
        self.log_editor.setMinimumHeight(250)
        self.log_editor.setReadOnly(True)  # 日志设为只读，防止误编辑
        log_layout.addWidget(log_label)
        log_layout.addWidget(self.log_editor)
        self.result_log_tab.addTab(self.log_tab, "📄 执行日志")

        result_log_tab_layout.addWidget(self.result_log_tab)
        main_layout.addWidget(result_log_tab_container, stretch=1)

        # 信号绑定
        self.gen_btn.clicked.connect(self.start_generate)
        self.cancel_btn.clicked.connect(self.cancel_generate)
        self.clear_btn.clicked.connect(self.clear_all)
        self.copy_btn.clicked.connect(self.copy_result)
        self.loading_timer.timeout.connect(self.update_loading_text)

        self.center_window()

    def center_window(self):
        """窗口屏幕垂直+水平居中显示（所有窗口通用逻辑）"""
        # 获取屏幕可用几何区域（排除任务栏/状态栏）
        screen_geometry = QScreen.availableGeometry(QApplication.primaryScreen())
        # 获取窗口自身几何区域
        window_geometry = self.frameGeometry()
        # 计算屏幕中心点，将窗口移动到该点
        window_geometry.moveCenter(screen_geometry.center())
        self.move(window_geometry.topLeft())

    def init_menu(self):
        """菜单栏：新增帮助菜单，添加图标，应用统一样式"""
        menu_bar = QMenuBar()
        # 应用样式文件中的菜单栏样式
        menu_bar.setStyleSheet(MENU_STYLE)
        menu_bar.setFont(GLOBAL_FONT)

        # 系统菜单（加图标，原有功能）
        sys_menu = menu_bar.addMenu("🌀 系统")
        config_action = QAction("⚙️ 配置", self)
        config_action.triggered.connect(self.open_config)
        sys_menu.addAction(config_action)

        # 模板菜单（加图标，原有功能）
        template_menu = menu_bar.addMenu("📋 模板")
        template_manage_action = QAction("📝 模板管理", self)
        template_manage_action.triggered.connect(self.open_template_manage)
        template_menu.addAction(template_manage_action)

        # 历史菜单（加图标，原有功能）
        history_menu = menu_bar.addMenu("📜 历史")
        history_action = QAction("📃 历史记录", self)
        history_action.triggered.connect(self.open_history)
        history_menu.addAction(history_action)

        # 新增：帮助菜单（核心，加图标，绑定帮助手册）
        help_menu = menu_bar.addMenu("❓ 帮助")
        help_action = QAction("📖 用户操作手册", self)
        help_action.triggered.connect(self.open_help)
        help_menu.addAction(help_action)
        # 新增关于作者菜单项
        about_action = QAction("👤 关于作者", self)
        about_action.triggered.connect(self.open_about)
        help_menu.addAction(about_action)

        self.setMenuBar(menu_bar)

    def update_loading_text(self):
        self.loading_index = (self.loading_index + 1) % len(self.loading_texts)
        self.loading_label.setText(self.loading_texts[self.loading_index])

    def start_generate(self):
        """开始生成：清空日志+结果，绑定线程双信号"""
        self.gen_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.output_editor.clear()  # 清空生成结果
        self.log_editor.clear()     # 清空执行日志
        self.loading_label.setText("生成中")
        self.progress_bar.setVisible(True)
        self.loading_timer.start(300)

        template_content = self.template_editor.toPlainText()
        work_content = self.work_editor.toPlainText()

        self.generate_thread = GenerateReportThread(template_content, work_content)
        self.generate_thread.text_signal.connect(self.update_output)  # 结果信号→结果域
        self.generate_thread.log_signal.connect(self.update_log)      # 日志信号→日志域（新增）
        self.generate_thread.finish_signal.connect(self.generate_finish)
        self.generate_thread.error_signal.connect(self.show_error)
        self.generate_thread.start()

    def cancel_generate(self):
        """生成中断：仅更新日志，不清除结果"""
        if self.generate_thread and self.generate_thread.isRunning():
            self.generate_thread.cancel()
            self.cancel_btn.setEnabled(False)
            self.loading_timer.stop()
            self.loading_label.setText("❌ 正在中断生成")
            # 中断时自动切到日志Tab，方便用户查看中断状态
            self.result_log_tab.setCurrentIndex(1)
        else:
            # 强制复位状态
            self.cancel_btn.setEnabled(False)
            self.loading_timer.stop()
            self.loading_label.setText("❌ 生成已中断")
            self.progress_bar.setVisible(False)
            self.gen_btn.setEnabled(True)
            self.update_log("⚠️  无正在运行的生成任务，已强制复位状态！\n")

    def update_output(self, text_chunk):
        """更新生成结果：流式内容逐块拼接，保留原始格式，自动滚动到底部"""
        if text_chunk and text_chunk.strip():
            # 直接插入纯文本，保留模型生成的所有格式（换行/空格/分级）
            self.output_editor.insertPlainText(text_chunk + "\n")
            # 自动滚动到底部，实时查看最新生成内容
            scroll_bar = self.output_editor.verticalScrollBar()
            scroll_bar.setValue(scroll_bar.maximum())
            # 流式生成时自动切到【生成结果】Tab，方便查看
            self.result_log_tab.setCurrentIndex(0)

    def update_log(self, log_chunk):
        """新增：更新执行日志，仅在日志域显示，自动滚动到底部"""
        if log_chunk and log_chunk.strip():
            self.log_editor.insertPlainText(log_chunk + "\n")
            self.log_editor.verticalScrollBar().setValue(
                self.log_editor.verticalScrollBar().maximum()
            )

    def generate_finish(self):
        """生成完成：复位所有状态，切到结果Tab"""
        self.loading_timer.stop()
        self.loading_label.setText("✅ 生成完成！")
        self.progress_bar.setVisible(False)
        self.gen_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.result_log_tab.setCurrentIndex(0)  # 自动切到结果Tab

        # 保存历史记录（原有逻辑）
        template_content = self.template_editor.toPlainText().strip()
        work_content = self.work_editor.toPlainText().strip()
        report_content = self.output_editor.toPlainText().strip()
        if template_content and work_content and report_content:
            self.history_dao.add_history(template_content, work_content, report_content)
            self.update_log(f"📜 生成结果已保存到历史记录，可在【历史→历史记录】中查看！")

        if not report_content:
            QMessageBox.warning(self, "提示", "生成结果为空！", QMessageBox.Ok)
            self.update_log("⚠️  生成结果为空，未保存到历史记录！")

    def show_error(self, err_msg):
        """生成错误：复位状态，切到日志Tab"""
        self.loading_timer.stop()
        self.loading_label.setText("❌ 生成失败！")
        self.progress_bar.setVisible(False)
        self.gen_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.result_log_tab.setCurrentIndex(1)  # 错误时自动切到日志Tab
        QMessageBox.critical(self, "错误", err_msg, QMessageBox.Ok)

    def clear_all(self):
        """清空所有：模板恢复默认，结果+日志+提示均清空"""
        self.template_editor.setPlainText(self.template_manager.get_default_template())
        self.work_editor.clear()
        self.output_editor.clear()
        self.log_editor.clear()
        self.loading_label.setText("")
        QMessageBox.information(self, "提示", "已清空内容，模板恢复默认值！", QMessageBox.Ok)

    def copy_result(self):
        """复制结果：仅复制生成结果域的内容"""
        result = self.output_editor.toPlainText().strip()
        if not result:
            QMessageBox.warning(self, "警告", "暂无有效生成结果可复制！", QMessageBox.Ok)
            return
        if CommonUtils.copy_to_clipboard(result):
            QMessageBox.information(self, "成功", "生成结果已复制到剪贴板！", QMessageBox.Ok)
        else:
            QMessageBox.warning(self, "失败", "复制失败，请重试！", QMessageBox.Ok)

    def open_config(self):
        """打开配置窗口：局部导入，避免循环导入Bug"""
        from ui.config_window import ConfigWindow
        config_window = ConfigWindow(self)
        config_window.exec()

    def open_help(self):
        """打开帮助手册窗口：局部导入，避免循环导入Bug"""
        from ui.help_window import HelpWindow
        help_window = HelpWindow(self)
        help_window.exec()

    def open_about(self):
        """打开帮助手册窗口：局部导入，避免循环导入Bug"""
        from ui.about_window import AboutWindow
        about_window = AboutWindow(self)
        about_window.exec()

    def open_template_manage(self):
        """打开模板管理窗口：局部导入，避免循环导入Bug"""
        from ui.template_window import TemplateWindow
        template_window = TemplateWindow(self)
        template_window.load_to_main_signal.connect(self.load_template_to_editor)
        template_window.exec()

    def open_history(self):
        """打开历史记录窗口：局部导入，避免循环导入Bug"""
        from ui.history_window import HistoryWindow
        history_window = HistoryWindow(self)
        history_window.exec()

    def load_template_to_editor(self, template_content: str):
        if template_content:
            self.template_editor.setPlainText(template_content)
            self.tab_widget.setCurrentIndex(0)


# 程序入口（可选，若有单独的启动文件可删除）
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    app.setFont(GLOBAL_FONT)
    main_win = DailyReportGenerator()
    main_win.show()
    sys.exit(app.exec())