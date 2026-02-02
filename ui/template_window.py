from PySide6.QtGui import QScreen
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QTextEdit, QPushButton, QComboBox,
                               QMessageBox, QListWidget, QWidget, QApplication)
from PySide6.QtCore import Qt, Signal
from core.template_manager import TemplateManager
from config.style_config import (
    GLOBAL_FONT, BOLD_FONT, TITLE_FONT,
    MAIN_WINDOW_STYLE, CONTAINER_STYLE, LIST_WIDGET_STYLE,
    TEXT_EDIT_STYLE, INPUT_STYLE, BTN_MAIN_STYLE,
    BTN_SUCCESS_STYLE, BTN_WARNING_STYLE, BTN_DANGER_STYLE,
    LABEL_STYLE, MENU_STYLE
)

class TemplateWindow(QDialog):
    """模板管理窗口（核心优化：输入框/下拉框高度26px，按钮24px；样式适配，文字可见）"""
    load_to_main_signal = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.template_manager = TemplateManager()
        self.current_selected = None
        self.setModal(True)
        self.init_ui()
        self.load_template_list()

    def init_ui(self):
        self.setWindowTitle("模板管理（日报/周报）")
        self.setGeometry(300, 300, 900, 650)
        self.setMinimumSize(800, 600)
        self.setFont(GLOBAL_FONT)
        # 适配新样式，输入框/下拉框高度26px由INPUT_STYLE统一控制
        self.setStyleSheet(MAIN_WINDOW_STYLE + LABEL_STYLE + INPUT_STYLE + LIST_WIDGET_STYLE + MENU_STYLE)

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # 标题（纯色主色，可见）
        title_label = QLabel("📑 日报/周报模板管理（支持新增/编辑/设为默认）")
        title_label.setFont(TITLE_FONT)
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # ========== 1. 模板列表容器 ==========
        list_container = QWidget()
        list_container.setObjectName("container")
        list_container.setStyleSheet(CONTAINER_STYLE)
        list_layout = QVBoxLayout(list_container)
        list_layout.setSpacing(6)
        list_layout.setContentsMargins(6, 6, 6, 6)

        list_label = QLabel("模板列表（★ 标记为当前默认模板）")
        list_label.setFont(BOLD_FONT)
        self.template_list = QListWidget()
        self.template_list.setMinimumHeight(120)
        self.template_list.itemClicked.connect(self.on_template_click)

        list_layout.addWidget(list_label)
        list_layout.addWidget(self.template_list)
        main_layout.addWidget(list_container)

        # ========== 2. 模板信息容器（输入框/下拉框高度26px，由INPUT_STYLE控制） ==========
        info_container = QWidget()
        info_container.setObjectName("container")
        info_container.setStyleSheet(CONTAINER_STYLE)
        info_layout = QVBoxLayout(info_container)
        info_layout.setSpacing(8)
        info_layout.setContentsMargins(6, 6, 6, 6)

        # 名称+类型（输入框/下拉框高度26px，无冗余）
        name_type_layout = QHBoxLayout()
        name_type_layout.setSpacing(10)
        name_label = QLabel("模板名称：")
        name_label.setFont(BOLD_FONT)
        self.template_name_edit = QLineEdit()
        self.template_name_edit.setPlaceholderText("输入唯一模板名称（不可重复，必填）")

        type_label = QLabel("模板类型：")
        type_label.setFont(BOLD_FONT)
        self.template_type_combo = QComboBox()
        self.template_type_combo.addItems(["daily（日报）", "weekly（周报）"])

        name_type_layout.addWidget(name_label)
        name_type_layout.addWidget(self.template_name_edit)
        name_type_layout.addWidget(type_label)
        name_type_layout.addWidget(self.template_type_combo)
        name_type_layout.addStretch()

        # 内容编辑
        content_label = QLabel("模板内容（支持自由编辑，生成时自动读取）")
        content_label.setFont(BOLD_FONT)
        content_label.setObjectName("titleLabel")
        self.template_content_edit = QTextEdit()
        self.template_content_edit.setStyleSheet(TEXT_EDIT_STYLE)
        self.template_content_edit.setMinimumHeight(220)

        info_layout.addLayout(name_type_layout)
        info_layout.addWidget(content_label)
        info_layout.addWidget(self.template_content_edit)
        main_layout.addWidget(info_container)

        # ========== 3. 功能按钮容器（按钮高度24px，样式保留） ==========
        btn_container = QWidget()
        btn_container.setObjectName("container")
        btn_container.setStyleSheet(CONTAINER_STYLE)
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setSpacing(8)
        btn_layout.setContentsMargins(6, 6, 6, 6)
        btn_layout.setAlignment(Qt.AlignLeft)

        self.save_btn = QPushButton("💾 保存/编辑模板")
        self.save_btn.setStyleSheet(BTN_MAIN_STYLE)

        self.set_default_btn = QPushButton("⭐ 设为默认模板")
        self.set_default_btn.setStyleSheet(BTN_WARNING_STYLE)
        self.set_default_btn.setEnabled(False)

        self.load_to_main_btn = QPushButton("📤 加载到主窗口")
        self.load_to_main_btn.setStyleSheet(BTN_SUCCESS_STYLE)
        self.load_to_main_btn.setEnabled(False)

        self.delete_btn = QPushButton("🗑️ 删除模板")
        self.delete_btn.setStyleSheet(BTN_DANGER_STYLE)
        self.delete_btn.setEnabled(False)

        self.add_new_btn = QPushButton("➕ 新增模板")
        self.add_new_btn.setStyleSheet(BTN_MAIN_STYLE)

        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.set_default_btn)
        btn_layout.addWidget(self.load_to_main_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.add_new_btn)
        btn_layout.addStretch()
        main_layout.addWidget(btn_container)

        # 信号绑定（原有逻辑，确保按钮100%生效）
        self.save_btn.clicked.connect(self.save_or_update_template)
        self.set_default_btn.clicked.connect(self.set_default_template)
        self.load_to_main_btn.clicked.connect(self.load_to_main_window)
        self.delete_btn.clicked.connect(self.delete_template)
        self.add_new_btn.clicked.connect(self.add_new_template)

        # 新增：窗口居中（init_ui末尾调用）
        self.center_window()

    def center_window(self):
        screen_geometry = QScreen.availableGeometry(QApplication.primaryScreen())
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_geometry.center())
        self.move(window_geometry.topLeft())

    # 以下所有业务逻辑无修改，确保模板管理功能正常
    def load_template_list(self):
        self.template_list.clear()
        template_names = self.template_manager.get_all_template_names()
        default_name = self.template_manager.get_default_template_name()
        for name in template_names:
            item_text = f"★ {name}" if name == default_name else name
            self.template_list.addItem(item_text)
        self.current_selected = None
        self.reset_input()
        self.update_btn_status()

    def reset_input(self):
        self.template_name_edit.clear()
        self.template_type_combo.setCurrentIndex(0)
        self.template_content_edit.clear()
        self.template_name_edit.setReadOnly(False)

    def update_btn_status(self):
        default_name = self.template_manager.get_default_template_name()
        if not self.current_selected:
            self.save_btn.setEnabled(True)
            self.set_default_btn.setEnabled(False)
            self.load_to_main_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            self.template_name_edit.setReadOnly(False)
        else:
            self.save_btn.setEnabled(True)
            self.set_default_btn.setEnabled(True)
            self.load_to_main_btn.setEnabled(True)
            self.template_name_edit.setReadOnly(True)
            if self.current_selected == default_name:
                self.set_default_btn.setText("⭐ 已是默认模板")
                self.set_default_btn.setEnabled(False)
                self.delete_btn.setEnabled(False)
            else:
                self.set_default_btn.setText("⭐ 设为默认模板")
                self.set_default_btn.setEnabled(True)
                self.delete_btn.setEnabled(True)

    def on_template_click(self, item):
        item_text = item.text().strip()
        self.current_selected = item_text.replace("★ ", "") if "★ " in item_text else item_text
        template_info = self.template_manager.get_template_info(self.current_selected)
        if not template_info:
            QMessageBox.warning(self, "提示", "模板信息获取失败！", QMessageBox.Ok)
            return
        self.template_name_edit.setText(template_info["template_name"])
        self.template_type_combo.setCurrentText("daily（日报）" if template_info["template_type"] == "daily" else "weekly（周报）")
        self.template_content_edit.setPlainText(template_info["content"])
        self.update_btn_status()

    def add_new_template(self):
        self.current_selected = None
        self.reset_input()
        self.update_btn_status()
        QMessageBox.information(self, "提示", "请输入新模板名称→选择模板类型→编辑模板内容，点击【保存/编辑模板】完成新增！", QMessageBox.Ok)

    def save_or_update_template(self):
        template_name = self.template_name_edit.text().strip()
        template_type = "daily" if self.template_type_combo.currentText() == "daily（日报）" else "weekly"
        template_content = self.template_content_edit.toPlainText().strip()
        if not template_name:
            QMessageBox.warning(self, "提示", "模板名称不能为空！", QMessageBox.Ok)
            return
        if not template_content:
            QMessageBox.warning(self, "提示", "模板内容不能为空！", QMessageBox.Ok)
            return
        if self.template_manager.save_template(template_name, template_type, template_content):
            tip = "模板新增成功！" if not self.current_selected else "模板编辑保存成功！"
            QMessageBox.information(self, "成功", tip, QMessageBox.Ok)
            self.load_template_list()
            for i in range(self.template_list.count()):
                item = self.template_list.item(i)
                if template_name in item.text():
                    self.template_list.setCurrentItem(item)
                    self.on_template_click(item)
                    break
        else:
            QMessageBox.warning(self, "失败", "模板名称已存在！请修改唯一名称后重新保存。", QMessageBox.Ok)

    def set_default_template(self):
        if not self.current_selected:
            QMessageBox.warning(self, "提示", "请先选择要设为默认的模板！", QMessageBox.Ok)
            return
        if QMessageBox.question(self, "确认", f"是否将【{self.current_selected}】设为默认模板？\n原默认模板将取消默认标记！", QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
            return
        if self.template_manager.set_default_template(self.current_selected):
            QMessageBox.information(self, "成功", f"【{self.current_selected}】已设为默认模板！\n主窗口将自动加载该模板内容。", QMessageBox.Ok)
            self.load_template_list()
            self.load_to_main_signal.emit(self.template_manager.get_default_template())
        else:
            QMessageBox.warning(self, "失败", "设为默认模板失败！", QMessageBox.Ok)

    def delete_template(self):
        if not self.current_selected:
            QMessageBox.warning(self, "提示", "请先选择要删除的模板！", QMessageBox.Ok)
            return
        if QMessageBox.question(self, "危险操作", f"是否确定删除【{self.current_selected}】模板？\n删除后无法恢复，系统默认模板不可删除！", QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
            return
        if self.template_manager.delete_template(self.current_selected):
            QMessageBox.information(self, "成功", f"【{self.current_selected}】模板已删除！", QMessageBox.Ok)
            self.current_selected = None
            self.load_template_list()
        else:
            QMessageBox.warning(self, "失败", "模板删除失败！\n系统默认日报模板不可删除，或模板不存在。", QMessageBox.Ok)

    def load_to_main_window(self):
        if not self.current_selected:
            QMessageBox.warning(self, "提示", "请先选择要加载的模板！", QMessageBox.Ok)
            return
        template_content = self.template_manager.load_template(self.current_selected)
        if not template_content:
            QMessageBox.warning(self, "提示", "模板内容为空，无法加载到主窗口！", QMessageBox.Ok)
            return
        self.load_to_main_signal.emit(template_content)
        QMessageBox.information(self, "成功", f"【{self.current_selected}】模板已成功加载到主窗口！", QMessageBox.Ok)