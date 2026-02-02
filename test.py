import os
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QTextEdit, QPushButton, QMessageBox,
                               QLabel, QProgressBar, QTabWidget)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QIcon
from volcenginesdkarkruntime import Ark

# ------------------- 火山方舟配置（无需修改） -------------------
client = Ark(
    base_url='https://ark.cn-beijing.volces.com/api/v3',
    api_key=os.getenv('ARK_API_KEY'),
)
MODEL_ID = "doubao-seed-1-6-lite-251015"  # 模型ID，可按需修改

# ------------------- 默认日报模版（抽离为常量，作为Tab默认值） -------------------
DEFAULT_REPORT_TEMPLATE = """请作为专业的项目助理，根据我提供的当日工作内容，按照【从整体到局部】的逻辑，结合以下模版结构生成日报。
    日报模版：
    【项目名称】：
    今天主要围绕【核心工作方向1】与【核心工作方向2】推进工作。
    1、【具体工作模块1】：聚焦【工作核心内容】，【具体操作/调整动作】，今日进展：【已完成/进行中/待推进】；同步推进【关联工作】，目前处于【当前阶段】。
    2、【具体工作模块2】：聚焦【工作核心内容】，涉及【相关子功能/子任务】的【规划/搭建/开发】，今日进展：【已完成XX项，包含具体内容】；【该模块整体进展】。
    """


# ------------------- 子线程：处理AI流式调用（兼容SDK解析+读取界面模版） -------------------
class GenerateReportThread(QThread):
    """后台子线程，执行流式调用，接收模版+工作内容，传递结果/异常"""
    text_signal = Signal(str)  # 传递流式返回的文本片段
    finish_signal = Signal()   # 传递生成完成信号
    error_signal = Signal(str) # 传递异常信息

    def __init__(self, template_content, work_content):
        super().__init__()
        self.template_content = template_content.strip()  # 日报模版内容
        self.work_content = work_content.strip()          # 当日工作内容

    def run(self):
        # 空值判断
        if not self.template_content:
            self.error_signal.emit("日报模版不能为空，请先填写模版内容！")
            return
        if not self.work_content:
            self.error_signal.emit("当日工作内容不能为空，请先粘贴/输入！")
            return

        # 拼接提示词（模版+工作内容）
        prompt = f"{self.template_content}\n\n我提供的当日工作内容：{self.work_content}"

        try:
            # 火山方舟流式调用核心：stream=True
            stream_resp = client.responses.create(
                model=MODEL_ID,
                input=prompt,
                temperature=0.3,  # 低温度保证输出结构化
                stream=True,       # 开启流式返回
                thinking={"type": "disabled"},  # 关闭思考过程，避免无关内容
            )

            # 兼容SDK新旧版本的流式解析逻辑
            for chunk in stream_resp:
                # 方案1：适配旧版本SDK（文本直接在chunk.text）
                if hasattr(chunk, 'text') and chunk.text and chunk.text.strip():
                    self.text_signal.emit(chunk.text.strip())
                # 方案2：适配新版本SDK（嵌套结构，兜底用）
                elif hasattr(chunk, 'output') and chunk.output:
                    for output in chunk.output:
                        if hasattr(output, 'content') and output.content:
                            for content in output.content:
                                if hasattr(content, 'text') and content.text.strip():
                                    self.text_signal.emit(content.text.strip())
            self.finish_signal.emit()  # 生成完成

        except Exception as e:
            err_msg = f"AI调用失败：{str(e)}"
            self.error_signal.emit(err_msg)

# ------------------- 主窗口：PySide6 GUI（双Tab布局+模版可编辑） -------------------
class DailyReportGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        # 先初始化加载动效属性（必须在init_ui之前）
        self.loading_timer = QTimer()
        self.loading_texts = ["生成中", "生成中.", "生成中..", "生成中..."]
        self.loading_index = 0
        # 初始化UI
        self.init_ui()
        self.generate_thread = None  # 子线程对象

    def init_ui(self):
        """初始化GUI：双Tab上半区 + 按钮 + 加载 + 输出区"""
        # 窗口基础设置
        self.setWindowTitle("AI日报生成工具 - 火山方舟（模版可编辑）")
        self.setGeometry(200, 200, 1100, 750)
        self.setMinimumSize(900, 650)

        # 中心部件和主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # ------------------- 核心：双Tab标签页（上半区） -------------------
        self.tab_widget = QTabWidget()
        self.tab_widget.setMinimumHeight(220)
        # 设置Tab字体和样式
        self.tab_widget.setFont(QFont("微软雅黑", 9))
        self.tab_widget.setTabPosition(QTabWidget.North)

        # Tab1：日报模版编辑页
        self.template_tab = QWidget()
        template_layout = QVBoxLayout(self.template_tab)
        template_label = QLabel("📋 日报生成模版（支持自由编辑，生成时自动读取）")
        template_label.setFont(QFont("微软雅黑", 10, QFont.Bold))
        self.template_editor = QTextEdit()
        self.template_editor.setPlainText(DEFAULT_REPORT_TEMPLATE)  # 加载默认模版
        self.template_editor.setPlaceholderText("请在此编辑日报生成的模版规则...")
        template_layout.addWidget(template_label)
        template_layout.addWidget(self.template_editor)
        self.tab_widget.addTab(self.template_tab, "📝 模版编辑")

        # Tab2：当日工作内容页
        self.work_tab = QWidget()
        work_layout = QVBoxLayout(self.work_tab)
        work_label = QLabel("📌 当日工作内容（纯文本粘贴/输入，无需格式化）")
        work_label.setFont(QFont("微软雅黑", 10, QFont.Bold))
        self.work_editor = QTextEdit()
        self.work_editor.setPlaceholderText("示例：今天开发安全管理模块，完成2个子功能，1个进行中...")
        work_layout.addWidget(work_label)
        work_layout.addWidget(self.work_editor)
        self.tab_widget.addTab(self.work_tab, "📖 工作内容")

        main_layout.addWidget(self.tab_widget)

        # ------------------- 功能按钮区 -------------------
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        self.gen_btn = QPushButton("📝 生成日报")
        self.clear_btn = QPushButton("🗑️ 清空所有")
        self.copy_btn = QPushButton("📋 复制结果")
        # 按钮样式
        for btn in [self.gen_btn, self.clear_btn, self.copy_btn]:
            btn.setMinimumHeight(40)
            btn.setMinimumWidth(120)
            btn.setFont(QFont("微软雅黑", 9))
        btn_layout.addWidget(self.gen_btn)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addWidget(self.copy_btn)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        # ------------------- 动态加载提示区 -------------------
        self.loading_layout = QHBoxLayout()
        self.loading_label = QLabel("")
        self.loading_label.setFont(QFont("微软雅黑", 9, italic=True))
        self.loading_label.setAlignment(Qt.AlignLeft)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # 无限滚动
        self.progress_bar.setVisible(False)
        self.loading_layout.addWidget(self.loading_label)
        self.loading_layout.addWidget(self.progress_bar)
        main_layout.addLayout(self.loading_layout)

        # ------------------- AI生成结果输出区 -------------------
        output_label = QLabel("📊 AI生成日报结果（支持编辑，可直接复制）")
        output_label.setFont(QFont("微软雅黑", 10, QFont.Bold))
        self.output_editor = QTextEdit()
        self.output_editor.setPlaceholderText("AI生成的日报将在此实时展示...")
        self.output_editor.setMinimumHeight(300)
        main_layout.addWidget(output_label)
        main_layout.addWidget(self.output_editor)

        # ------------------- 信号与槽绑定 -------------------
        self.gen_btn.clicked.connect(self.start_generate)
        self.clear_btn.clicked.connect(self.clear_all)
        self.copy_btn.clicked.connect(self.copy_result)
        self.loading_timer.timeout.connect(self.update_loading_text)

    def update_loading_text(self):
        """更新动态加载提示文字"""
        self.loading_index = (self.loading_index + 1) % len(self.loading_texts)
        self.loading_label.setText(self.loading_texts[self.loading_index])

    def start_generate(self):
        """开始生成：读取模版+工作内容，启动子线程"""
        # 初始化状态
        self.gen_btn.setEnabled(False)
        self.output_editor.clear()
        # 显示加载动效
        self.loading_label.setText("生成中")
        self.progress_bar.setVisible(True)
        self.loading_timer.start(300)

        # 读取界面上的模版和工作内容
        template_content = self.template_editor.toPlainText()
        work_content = self.work_editor.toPlainText()

        # 启动子线程（传递模版+工作内容）
        self.generate_thread = GenerateReportThread(template_content, work_content)
        self.generate_thread.text_signal.connect(self.update_output)
        self.generate_thread.finish_signal.connect(self.generate_finish)
        self.generate_thread.error_signal.connect(self.show_error)
        self.generate_thread.start()

    def update_output(self, text_chunk):
        """实时更新输出区内容"""
        self.output_editor.insertPlainText(text_chunk)
        # 自动滚动到最新内容
        self.output_editor.verticalScrollBar().setValue(
            self.output_editor.verticalScrollBar().maximum()
        )

    def generate_finish(self):
        """生成完成：恢复状态+提示"""
        self.loading_timer.stop()
        self.loading_label.setText("✅ 生成完成！")
        self.progress_bar.setVisible(False)
        self.gen_btn.setEnabled(True)
        # 空结果判断
        if not self.output_editor.toPlainText().strip():
            QMessageBox.warning(self, "提示", "生成结果为空，请检查模版/工作内容是否有效！", QMessageBox.Ok)
        else:
            QMessageBox.information(self, "成功", "日报生成完成！支持编辑后一键复制～", QMessageBox.Ok)

    def show_error(self, err_msg):
        """生成失败：恢复状态+报错"""
        self.loading_timer.stop()
        self.loading_label.setText("❌ 生成失败！")
        self.progress_bar.setVisible(False)
        self.gen_btn.setEnabled(True)
        QMessageBox.critical(self, "错误", err_msg, QMessageBox.Ok)

    def clear_all(self):
        """清空所有内容：模版+工作内容+输出+加载提示"""
        self.template_editor.setPlainText(DEFAULT_REPORT_TEMPLATE)  # 模版恢复默认值
        self.work_editor.clear()
        self.output_editor.clear()
        self.loading_label.setText("")
        QMessageBox.information(self, "提示", "已清空内容，模版恢复默认值！", QMessageBox.Ok)

    def copy_result(self):
        """一键复制输出结果"""
        result_text = self.output_editor.toPlainText().strip()
        if not result_text:
            QMessageBox.warning(self, "警告", "暂无有效生成结果可复制！", QMessageBox.Ok)
            return
        clipboard = QApplication.clipboard()
        clipboard.setText(result_text)
        QMessageBox.information(self, "成功", "日报结果已成功复制到剪贴板！", QMessageBox.Ok)

# ------------------- 程序入口 -------------------
if __name__ == "__main__":
    # 检查ARK_API_KEY
    if not os.getenv('ARK_API_KEY'):
        print("❌ 错误：未配置ARK_API_KEY环境变量！")
        app = QApplication(sys.argv)
        QMessageBox.critical(None, "环境配置错误", "请先配置系统环境变量【ARK_API_KEY】！", QMessageBox.Ok)
        sys.exit(1)

    # 启动应用
    app = QApplication(sys.argv)
    app.setFont(QFont("微软雅黑", 9))  # 全局中文字体
    window = DailyReportGenerator()
    window.show()
    sys.exit(app.exec())