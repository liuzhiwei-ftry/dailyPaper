from PySide6.QtGui import QScreen
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget,
                               QTableWidgetItem, QPushButton, QMessageBox, QLabel,
                               QHeaderView, QFileDialog, QWidget, QApplication,
                               QLineEdit, QComboBox, QFrame)
from PySide6.QtCore import Qt
from db.history_dao import HistoryDAO
from utils.common_utils import CommonUtils
from config.style_config import (
    GLOBAL_FONT, BOLD_FONT, TITLE_FONT,
    MAIN_WINDOW_STYLE, CONTAINER_STYLE, TABLE_STYLE,
    BTN_TABLE_STYLE, BTN_MAIN_STYLE, LABEL_STYLE, MENU_STYLE
)
import pandas as pd
from datetime import datetime

class HistoryWindow(QDialog):
    """历史记录窗口（新增高级搜索/筛选、导出Excel功能【适配筛选结果导出】）"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.history_dao = HistoryDAO()
        self.setModal(True)
        # 新增属性：保存当前筛选后的结果集，供导出使用
        self.current_filtered_histories = []
        self.init_ui()
        # 初始化加载全量数据
        self.load_history_data()

    def init_ui(self):
        self.setWindowTitle("历史生成记录")
        self.setGeometry(300, 300, 1100, 650)
        self.setMinimumSize(900, 550)
        self.setFont(GLOBAL_FONT)
        self.setStyleSheet(MAIN_WINDOW_STYLE + LABEL_STYLE + TABLE_STYLE + BTN_TABLE_STYLE + MENU_STYLE)

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # 标题
        self.title_label = QLabel("📜 历史生成记录（共0条）")
        self.title_label.setFont(TITLE_FONT)
        self.title_label.setObjectName("titleLabel")
        main_layout.addWidget(self.title_label)

        # ========== 新增：高级搜索/筛选区域 ==========
        search_container = QWidget()
        search_container.setObjectName("container")
        search_container.setStyleSheet(CONTAINER_STYLE)
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(10, 8, 10, 8)
        search_layout.setSpacing(12)

        # 1. 搜索框（支持时间/关键词）
        search_label = QLabel("🔍 搜索：")
        search_label.setFont(BOLD_FONT)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("支持：生成时间（如2024-05）、模板/工作/结果关键词")
        self.search_input.setMinimumWidth(300)
        # 回车触发搜索
        self.search_input.returnPressed.connect(self.on_search)

        # 2. 模板类型筛选下拉框
        filter_label = QLabel("📋 模板筛选：")
        filter_label.setFont(BOLD_FONT)
        self.template_filter = QComboBox()
        self.template_filter.addItem("全部模板", "")  # 空值表示不筛选
        # 从DAO获取所有模板类型
        template_types = self.history_dao.get_all_template_types()
        for t_type in template_types:
            self.template_filter.addItem(t_type, t_type)
        self.template_filter.currentIndexChanged.connect(self.on_filter)  # 修正：移除多余的右括号

        # 3. 搜索按钮
        search_btn = QPushButton("搜索")
        search_btn.setStyleSheet(BTN_MAIN_STYLE)
        search_btn.clicked.connect(self.on_search)

        # 4. 重置按钮
        reset_btn = QPushButton("重置")
        reset_btn.setStyleSheet(BTN_MAIN_STYLE)
        reset_btn.clicked.connect(self.on_reset)

        # 添加到搜索布局
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(filter_label)
        search_layout.addWidget(self.template_filter)
        search_layout.addWidget(search_btn)
        search_layout.addWidget(reset_btn)
        search_layout.addStretch()

        # 分割线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        # 添加搜索区域到主布局
        main_layout.addWidget(search_container)
        main_layout.addWidget(line)
        # ========== 搜索区域结束 ==========

        # 表格容器
        table_container = QWidget()
        table_container.setObjectName("container")
        table_container.setStyleSheet(CONTAINER_STYLE)
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(6, 6, 6, 6)

        # 核心表格
        self.history_table = QTableWidget()
        self.columns = ["序号", "生成时间", "模板预览", "工作内容预览", "生成结果预览", "操作"]
        self.history_table.setColumnCount(len(self.columns))
        self.history_table.setHorizontalHeaderLabels(self.columns)
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.history_table.setSelectionMode(QTableWidget.SingleSelection)
        self.history_table.verticalHeader().setVisible(False)
        # 列宽自适应优化
        self.history_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.history_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.history_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.history_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.history_table.verticalHeader().setDefaultSectionSize(70)

        table_layout.addWidget(self.history_table)
        main_layout.addWidget(table_container, stretch=1)

        # 底部按钮布局（保留原有导出/刷新按钮）
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        # 刷新按钮（原有）
        refresh_btn = QPushButton("🔄 刷新记录")
        refresh_btn.setStyleSheet(BTN_MAIN_STYLE)
        refresh_btn.clicked.connect(self.load_history_data)
        # 导出Excel按钮（原有，功能已适配筛选结果）
        export_btn = QPushButton("📊 导出Excel")
        export_btn.setStyleSheet(BTN_MAIN_STYLE)
        export_btn.clicked.connect(self.export_to_excel)

        btn_layout.addWidget(refresh_btn)
        btn_layout.addWidget(export_btn)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        # 窗口居中
        self.center_window()

    def center_window(self):
        screen_geometry = QScreen.availableGeometry(QApplication.primaryScreen())
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_geometry.center())
        self.move(window_geometry.topLeft())

    def _truncate_text(self, text: str, max_len: int = 40) -> str:
        """界面预览文本截断（导出时不使用此方法，导出完整内容）"""
        if not text:
            return "无"
        clean_text = text.replace("\n\n", "\n").strip()
        if len(clean_text) <= max_len:
            return clean_text
        return clean_text[:max_len] + "..."

    def load_history_data(self, search_keyword="", template_type=""):
        """加载历史记录（新增搜索/筛选参数，核心：保存当前筛选结果到类属性）"""
        self.history_table.setRowCount(0)
        # 调用带条件的查询方法
        self.current_filtered_histories = self.history_dao.get_history_by_conditions(
            keyword=search_keyword,
            template_type=template_type
        )
        total = len(self.current_filtered_histories)
        self.title_label.setText(f"📜 历史生成记录（共{total}条）")

        for row_idx, history in enumerate(self.current_filtered_histories):
            self.history_table.insertRow(row_idx)
            history_id = history["id"]
            self.history_table.setItem(row_idx, 0, QTableWidgetItem(str(row_idx + 1)))
            self.history_table.setItem(row_idx, 1, QTableWidgetItem(history["create_time"]))
            self.history_table.setItem(row_idx, 2, QTableWidgetItem(self._truncate_text(history["template_content"], 35)))
            self.history_table.setItem(row_idx, 3, QTableWidgetItem(self._truncate_text(history["work_content"], 35)))
            self.history_table.setItem(row_idx, 4, QTableWidgetItem(self._truncate_text(history["report_content"], 50)))

            # 操作列小按钮
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setSpacing(6)
            btn_layout.setContentsMargins(4, 4, 4, 4)
            btn_layout.setAlignment(Qt.AlignCenter)

            copy_btn = QPushButton("复制")
            copy_btn.setObjectName("tableBtn")
            copy_btn.clicked.connect(lambda checked, hid=history_id: self.copy_history(hid))

            del_btn = QPushButton("删除")
            del_btn.setObjectName("tableDangerBtn")
            del_btn.clicked.connect(lambda checked, hid=history_id: self.delete_history(hid))

            btn_layout.addWidget(copy_btn)
            btn_layout.addWidget(del_btn)
            self.history_table.setCellWidget(row_idx, 5, btn_widget)

        # 内容对齐
        for row in range(total):
            for col in range(5):
                item = self.history_table.item(row, col)
                if item:
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignTop)

    # ========== 新增：搜索/筛选/重置逻辑 ==========
    def on_search(self):
        """执行搜索逻辑"""
        keyword = self.search_input.text().strip()
        template_type = self.template_filter.currentData()  # 获取筛选值
        self.load_history_data(search_keyword=keyword, template_type=template_type)

    def on_filter(self):
        """筛选下拉框变化时触发搜索"""
        self.on_search()

    def on_reset(self):
        """重置搜索条件"""
        self.search_input.clear()
        self.template_filter.setCurrentIndex(0)  # 重置为"全部模板"
        self.load_history_data()  # 加载全量数据
    # ========== 搜索逻辑结束 ==========

    def export_to_excel(self):
        """导出Excel【核心修改】：导出当前筛选后的结果集，保留原有格式特性"""
        try:
            # 核心修改：使用类属性中保存的当前筛选结果集，而非全量数据
            histories = self.current_filtered_histories
            if not histories:
                QMessageBox.information(self, "提示", "当前筛选结果集无记录，无需导出！", QMessageBox.Ok)
                return

            # 转换为DataFrame，处理数据格式（适配Excel）
            df = pd.DataFrame(histories)
            # 列重命名（更友好的Excel表头）
            df.rename(columns={
                "id": "记录ID",
                "create_time": "生成时间",
                "template_content": "完整模板内容",
                "work_content": "完整工作内容",
                "report_content": "完整生成结果"
            }, inplace=True)
            # 处理空值：替换为"无"
            df.fillna("无", inplace=True)
            # 按生成时间倒序排序（最新的在最前面）
            df.sort_values(by="生成时间", ascending=False, inplace=True)
            # 重置索引（从1开始，方便查看）
            df.reset_index(drop=True, inplace=True)
            df.index = df.index + 1
            df.rename_axis("序号", inplace=True)

            # 打开文件保存对话框，让用户选择保存路径和文件名
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"日报生成记录_筛选结果_{current_time}.xlsx"
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "导出当前筛选结果到Excel",
                default_filename,
                "Excel文件 (*.xlsx);;所有文件 (*.*)"
            )
            if not file_path:  # 用户取消保存
                return

            # 导出到Excel，设置单元格自动换行+列宽自适应（保留原有特性）
            with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name="日报筛选记录", index=True)
                # 获取工作表对象，设置单元格自动换行
                worksheet = writer.sheets["日报筛选记录"]
                for col in worksheet.columns:
                    # 所有单元格设为自动换行
                    for cell in col:
                        cell.alignment = cell.alignment.copy(wrap_text=True)
                    # 列宽自适应（根据内容长度调整，最大50）
                    max_length = max(len(str(cell.value)) for cell in col)
                    worksheet.column_dimensions[col[0].column_letter].width = min(max_length + 2, 50)

            # 导出成功反馈，提示筛选结果数量
            QMessageBox.information(
                self,
                "导出成功",
                f"当前{len(histories)}条筛选记录已成功导出！\n保存路径：\n{file_path}",
                QMessageBox.Ok
            )

        except Exception as e:
            # 导出失败反馈，打印详细错误信息
            QMessageBox.critical(
                self,
                "导出失败",
                f"Excel导出失败，请检查是否安装pandas/openpyxl！\n错误信息：{str(e)}",
                QMessageBox.Ok
            )

    def copy_history(self, history_id: int):
        history = self.history_dao.get_history_by_id(history_id)
        if not history or not history["report_content"]:
            QMessageBox.warning(self, "提示", "该记录内容为空，无法复制！", QMessageBox.Ok)
            return
        if CommonUtils.copy_to_clipboard(history["report_content"]):
            QMessageBox.information(self, "成功", "生成结果已复制到剪贴板！", QMessageBox.Ok)
        else:
            QMessageBox.warning(self, "失败", "复制失败，请重试！", QMessageBox.Ok)

    def delete_history(self, history_id: int):
        if QMessageBox.question(self, "确认删除", "是否确定删除该条历史记录？\n删除后无法恢复！",
                                QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.No:
            return
        if self.history_dao.delete_history(history_id):
            QMessageBox.information(self, "成功", "历史记录已删除！", QMessageBox.Ok)
            # 删除后重新加载当前筛选结果，保持筛选状态
            self.on_search()
        else:
            QMessageBox.warning(self, "失败", "历史记录删除失败！", QMessageBox.Ok)