from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt

# ===================== 全局字体配置（PySide6标准，确保文字渲染正常，无透明/渐变）=====================
GLOBAL_FONT = QFont("微软雅黑", 9)
BOLD_FONT = QFont("微软雅黑", 10, 75)
ITALIC_FONT = QFont("微软雅黑", 8, 50, 2)
SMALL_FONT = QFont("微软雅黑", 8)
TITLE_FONT = QFont("微软雅黑", 11, QFont.Weight.Bold)  # 标题专用，纯色高对比

# ===================== 高对比清爽配色（修复背景黑/字体不可见，核心：浅灰背景+深灰/黑色文字）=====================
# 主色：科技蓝（按钮/选中态/标题，高饱和高对比）
COLOR_MAIN = "#2E86AB"
COLOR_MAIN_LIGHT = "#4A90E2"
COLOR_MAIN_LIGHTER = "#6BB6FF"
# 辅助色：成功/危险/警告（按钮专用，保留渐变）
COLOR_SUCCESS = "#28A745"
COLOR_SUCCESS_LIGHT = "#51CF66"
COLOR_DANGER = "#DC3545"
COLOR_DANGER_LIGHT = "#FF6B6B"
COLOR_WARNING = "#FFC107"
COLOR_WARNING_LIGHT = "#FFD43B"
# 中性色：核心修复！浅灰背景+深灰文字，确保所有内容可见，无黑色
COLOR_BG_MAIN = "#F5F7FA"       # 全局主背景（浅灰，清爽不刺眼）
COLOR_BG_CONTAINER = "#FFFFFF"  # 容器/卡片背景（纯白，分层清晰）
COLOR_TEXT_PRIMARY = "#1A1A1A"  # 主文本（近黑，高对比100%可见）
COLOR_TEXT_SECONDARY = "#666666"# 次文本（中灰，提示/占位）
COLOR_TEXT_HINT = "#999999"     # 提示文本（浅灰，禁用/占位）
COLOR_BORDER = "#E5E7EB"        # 基础边框（浅灰，柔和不突兀）
COLOR_SHADOW = "rgba(0,0,0,0.08)"# 轻阴影（轻量化，卡片分层）
COLOR_FROSTED = "#FFFFFF"       # 磨砂兜底为纯白，修复渲染异常

# ------------------- 新增：菜单栏/子菜单样式（核心）-------------------
MENU_BAR_STYLE = """
/* 主菜单栏样式：独立显示，不融合系统标题栏 */
QMenuBar {
    background-color: #F5F5F5;
    color: #2C3E50;
    height: 35px;
    font-size: 10pt;
    border-bottom: 1px solid #EAECEE;
}
/* 菜单项基础样式 */
QMenuBar::item {
    padding: 6px 20px;
    margin: 0 2px;
    border-radius: 4px;
}
/* 菜单项悬停/选中样式 */
QMenuBar::item:selected {
    background-color: #3498DB;
    color: white;
}
/* 子菜单容器样式 */
QMenu {
    background-color: white;
    color: #2C3E50;
    border: 1px solid #BDC3C7;
    border-radius: 6px;
    padding: 5px 0;
    font-size: 10pt;
}
/* 子菜单项样式 */
QMenu::item {
    padding: 6px 30px;
    border-radius: 4px;
}
/* 子菜单项悬停/选中样式 */
QMenu::item:selected {
    background-color: #3498DB;
    color: white;
}
"""

# ===================== 全局基础样式（核心修复：移除模糊/渐变文字，确保背景/字体正常）=====================
# 主窗口/弹窗基础样式：修复背景黑，文字纯色高对比，抗锯齿
MAIN_WINDOW_STYLE = f"""
QMainWindow, QDialog {{
    background-color: {COLOR_BG_MAIN}; /* 浅灰主背景，修复黑色问题 */
    color: {COLOR_TEXT_PRIMARY};      /* 纯色深灰文字，修复不可见 */
    font-family: "微软雅黑";
    qproperty-antialiasing: true;
}}
/* 弹窗模态遮罩：移除模糊层（解决配置窗口报错），纯色半透实现层级 */
QDialog {{
    background-color: rgba(245,247,250,0.95);
}}
"""

# 核心容器样式：纯白卡片+轻阴影+圆角，修复渲染异常，分层清晰
CONTAINER_STYLE = f"""
QWidget#container {{
    background-color: {COLOR_BG_CONTAINER}; /* 纯白卡片，无透明/磨砂 */
    border: 1px solid {COLOR_BORDER};
    border-radius: 6px;
    padding: 8px;
    box-shadow: 0 2px 6px {COLOR_SHADOW}; /* 轻阴影分层，无厚重感 */
}}
QWidget#container:hover {{
    border-color: {COLOR_MAIN_LIGHTER};
    box-shadow: 0 3px 8px {COLOR_SHADOW};
    transition: all 0.2s ease;
}}
"""

# ===================== 按钮样式（保留渐变效果+核心优化：高度压缩至24px，紧凑不高）=====================
# 主按钮：科技蓝渐变+高度24px（核心压缩）+圆角4px
BTN_MAIN_STYLE = f"""
QPushButton {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {COLOR_MAIN_LIGHT}, stop:1 {COLOR_MAIN});
    color: white;
    border: none;
    border-radius: 4px;
    padding: 4px 12px; /* 内边距压缩，匹配高度 */
    font-family: "微软雅黑";
    font-size: 9pt;
    min-height: 24px; /* 核心优化：按钮高度压缩至24px */
    min-width: 80px;  /* 宽度微缩，更紧凑 */
    box-shadow: 0 1px 3px rgba(46,134,171,0.2);
}}
QPushButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {COLOR_MAIN}, stop:1 {COLOR_MAIN_LIGHTER});
    box-shadow: 0 2px 5px rgba(46,134,171,0.3);
    transform: translateY(-1px);
}}
QPushButton:pressed {{
    background: {COLOR_MAIN};
    box-shadow: 0 1px 2px rgba(46,134,171,0.3);
    transform: translateY(0);
}}
QPushButton:disabled {{
    background: #E9ECEF;
    color: {COLOR_TEXT_HINT};
    box-shadow: none;
    transform: none;
}}
"""

# 危险按钮：红色渐变+高度24px
BTN_DANGER_STYLE = f"""
QPushButton {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {COLOR_DANGER_LIGHT}, stop:1 {COLOR_DANGER});
    color: white;
    border: none;
    border-radius: 4px;
    padding: 4px 12px;
    font-family: "微软雅黑";
    font-size: 9pt;
    min-height: 24px; /* 高度24px统一 */
    min-width: 80px;
    box-shadow: 0 1px 3px rgba(220,53,69,0.2);
}}
QPushButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {COLOR_DANGER}, stop:1 {COLOR_DANGER_LIGHT});
    box-shadow: 0 2px 5px rgba(220,53,69,0.3);
    transform: translateY(-1px);
}}
QPushButton:pressed {{
    background: {COLOR_DANGER};
    box-shadow: 0 1px 2px rgba(220,53,69,0.3);
    transform: translateY(0);
}}
QPushButton:disabled {{
    background: #E9ECEF;
    color: {COLOR_TEXT_HINT};
    box-shadow: none;
    transform: none;
}}
"""

# 成功按钮：绿色渐变+高度24px
BTN_SUCCESS_STYLE = f"""
QPushButton {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {COLOR_SUCCESS_LIGHT}, stop:1 {COLOR_SUCCESS});
    color: white;
    border: none;
    border-radius: 4px;
    padding: 4px 12px;
    font-family: "微软雅黑";
    font-size: 9pt;
    min-height: 24px; /* 高度24px统一 */
    min-width: 80px;
    box-shadow: 0 1px 3px rgba(40,167,69,0.2);
}}
QPushButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {COLOR_SUCCESS}, stop:1 {COLOR_SUCCESS_LIGHT});
    box-shadow: 0 2px 5px rgba(40,167,69,0.3);
    transform: translateY(-1px);
}}
QPushButton:pressed {{
    background: {COLOR_SUCCESS};
    box-shadow: 0 1px 2px rgba(40,167,69,0.3);
    transform: translateY(0);
}}
"""

# 警告按钮：黄色渐变+高度24px+深色文字（高对比）
BTN_WARNING_STYLE = f"""
QPushButton {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {COLOR_WARNING_LIGHT}, stop:1 {COLOR_WARNING});
    color: #212529;
    border: none;
    border-radius: 4px;
    padding: 4px 12px;
    font-family: "微软雅黑";
    font-size: 9pt;
    font-weight: bold;
    min-height: 24px; /* 高度24px统一 */
    min-width: 80px;
    box-shadow: 0 1px 3px rgba(255,193,7,0.2);
}}
QPushButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {COLOR_WARNING}, stop:1 {COLOR_WARNING_LIGHT});
    box-shadow: 0 2px 5px rgba(255,193,7,0.3);
    transform: translateY(-1px);
}}
QPushButton:pressed {{
    background: {COLOR_WARNING};
    box-shadow: 0 1px 2px rgba(255,193,7,0.3);
    transform: translateY(0);
}}
QPushButton:disabled {{
    background: #E9ECEF;
    color: {COLOR_TEXT_HINT};
    box-shadow: none;
    transform: none;
}}
"""

# 表格小按钮：高度压缩至20px，适配表格紧凑布局
BTN_TABLE_STYLE = f"""
QPushButton#tableBtn {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {COLOR_MAIN_LIGHTER}, stop:1 {COLOR_MAIN});
    color: white;
    border: none;
    border-radius: 3px;
    padding: 2px 6px;
    font-family: "微软雅黑";
    font-size: 8pt;
    min-height: 20px; /* 小按钮高度20px */
    min-width: 40px;
}}
QPushButton#tableBtn:hover {{
    box-shadow: 0 1px 3px rgba(46,134,171,0.2);
}}
QPushButton#tableDangerBtn {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {COLOR_DANGER_LIGHT}, stop:1 {COLOR_DANGER});
    color: white;
    border: none;
    border-radius: 3px;
    padding: 2px 6px;
    font-family: "微软雅黑";
    font-size: 8pt;
    min-height: 20px; /* 小按钮高度20px */
    min-width: 40px;
}}
QPushButton#tableDangerBtn:hover {{
    box-shadow: 0 1px 3px rgba(220,53,69,0.2);
}}
"""

# ===================== 文本编辑器样式：适配整体布局，无透明，高度正常=====================
TEXT_EDIT_STYLE = f"""
QTextEdit {{
    background-color: {COLOR_BG_CONTAINER};
    border: 1px solid {COLOR_BORDER};
    border-radius: 4px;
    padding: 6px 8px; /* 内边距压缩 */
    font-family: "微软雅黑";
    font-size: 9pt;
    color: {COLOR_TEXT_PRIMARY}; /* 纯色文字，确保可见 */
    min-height: 180px;
}}
QTextEdit:focus {{
    border: 1px solid {COLOR_MAIN_LIGHTER};
    box-shadow: 0 0 4px rgba(107,182,255,0.2);
    outline: none;
}}
QTextEdit::placeholder {{
    color: {COLOR_TEXT_HINT};
}}
"""

# ===================== Tab页签：重新设计（修复丑陋问题）现代化扁平样式，圆角+浅灰底色=====================
TAB_STYLE = f"""
QTabWidget {{
    background-color: transparent;
    qproperty-antialiasing: true;
}}
QTabWidget::pane {{
    background-color: {COLOR_BG_CONTAINER};
    border: 1px solid {COLOR_BORDER};
    border-radius: 0 6px 6px 6px; /* 与标签圆角衔接 */
    padding: 8px;
    box-shadow: 0 1px 3px {COLOR_SHADOW};
}}
QTabBar::tab {{
    background-color: #F1F3F5; /* 浅灰底色，无透明 */
    color: {COLOR_TEXT_SECONDARY};
    padding: 3px 16px; /* 内边距压缩，标签更紧凑 */
    margin-right: 2px;
    border-radius: 6px 6px 0 0;
    font-family: "微软雅黑";
    font-size: 9pt;
    min-height: 28px; /* 标签高度压缩，不突兀 */
}}
/* 选中态：科技蓝纯色+白色文字，简洁醒目，无复杂渐变 */
QTabBar::tab:selected {{
    background-color: {COLOR_MAIN};
    color: white;
    font-weight: bold;
}}
QTabBar::tab:hover:!selected {{
    background-color: #E9ECEF;
    color: {COLOR_TEXT_PRIMARY};
}}
"""

# ===================== 表格样式：清爽纯白，无透明，文字可见=====================
TABLE_STYLE = f"""
QTableWidget {{
    background-color: {COLOR_BG_CONTAINER};
    border: 1px solid {COLOR_BORDER};
    border-radius: 6px;
    gridline-color: #F1F3F5;
    font-family: "微软雅黑";
    font-size: 8pt;
    color: {COLOR_TEXT_PRIMARY}; /* 纯色文字 */
    qproperty-antialiasing: true;
}}
QTableWidget::header {{
    background-color: #F8F9FA;
    color: {COLOR_MAIN};
    font-weight: bold;
    font-size: 9pt;
}}
QTableWidget::horizontalHeader::section {{
    border: 1px solid {COLOR_BORDER};
    border-radius: 3px;
    padding: 3px;
    text-align: center;
    min-height: 26px;
}}
QTableWidget::verticalHeader::section {{
    border: 1px solid {COLOR_BORDER};
    padding: 0 4px;
    text-align: center;
}}
QTableWidget::item {{
    padding: 3px;
    border-bottom: 1px solid #F1F3F5;
}}
QTableWidget::item:selected {{
    background-color: rgba(107,182,255,0.15);
    color: {COLOR_MAIN};
}}
QTableWidget::item:hover {{
    background-color: #F8F9FA;
}}
"""

# ===================== 列表样式：适配整体，文字可见=====================
LIST_WIDGET_STYLE = f"""
QListWidget {{
    background-color: {COLOR_BG_CONTAINER};
    border: 1px solid {COLOR_BORDER};
    border-radius: 4px;
    padding: 4px;
    font-family: "微软雅黑";
    font-size: 9pt;
    color: {COLOR_TEXT_PRIMARY};
    min-height: 100px;
}}
QListWidget::item {{
    padding: 5px 6px;
    border-radius: 3px;
}}
QListWidget::item:hover {{
    background-color: rgba(107,182,255,0.1);
    border-left: 2px solid {COLOR_MAIN_LIGHTER};
}}
QListWidget::item:selected {{
    background-color: rgba(107,182,255,0.15);
    color: {COLOR_MAIN};
}}
"""

# ===================== 输入框/下拉框样式（核心优化：高度压缩至26px，适配模板管理/配置窗口）=====================
# 单行输入框/下拉框高度统一26px，内边距压缩，无冗余高度
INPUT_STYLE = f"""
QLineEdit, QComboBox {{
    background-color: {COLOR_BG_CONTAINER};
    border: 1px solid {COLOR_BORDER};
    border-radius: 4px;
    padding: 3px 8px; /* 内边距核心压缩，匹配26px高度 */
    font-family: "微软雅黑";
    font-size: 9pt;
    color: {COLOR_TEXT_PRIMARY}; /* 纯色文字，确保可见 */
    min-height: 26px; /* 核心优化：输入框/下拉框高度压缩至26px */
}}
QLineEdit:focus, QComboBox:focus {{
    border: 1px solid {COLOR_MAIN_LIGHTER};
    box-shadow: 0 0 4px rgba(107,182,255,0.2);
    outline: none;
}}
QLineEdit::placeholder, QComboBox::placeholder {{
    color: {COLOR_TEXT_HINT};
}}
/* 下拉框箭头样式：匹配主色，无复杂渐变 */
QComboBox {{
    padding-right: 20px;
}}
QComboBox::drop-down {{
    border: none;
    border-radius: 0 4px 4px 0;
    background-color: {COLOR_MAIN};
}}
QComboBox::down-arrow {{
    image: none;
    color: white;
}}
/* 下拉菜单样式：高度匹配输入框，无冗余，文字可见 */
QComboBox QAbstractItemView {{
    background-color: {COLOR_BG_CONTAINER};
    border: 1px solid {COLOR_BORDER};
    border-radius: 4px;
    color: {COLOR_TEXT_PRIMARY};
    selection-background-color: rgba(107,182,255,0.15);
    selection-color: {COLOR_MAIN};
    font-size: 9pt;
}}
"""

# ===================== 进度条样式：清爽适配，无透明=====================
PROGRESS_BAR_STYLE = f"""
QProgressBar {{
    background-color: #F1F3F5;
    border: 1px solid {COLOR_BORDER};
    border-radius: 4px;
    text-align: center;
    font-family: "微软雅黑";
    font-size: 8pt;
    color: {COLOR_TEXT_PRIMARY};
    min-height: 20px;
}}
QProgressBar::chunk {{
    background-color: {COLOR_MAIN_LIGHTER};
    border-radius: 3px;
    box-shadow: 0 0 3px rgba(107,182,255,0.2);
}}
"""

# ===================== 标签/标题样式（修复渐变文字不可见：改用纯色高对比，标题加主色）=====================
# 移除渐变文字，改用**纯色主色标题+深灰普通标签**，确保100%可见
LABEL_STYLE = f"""
QLabel {{
    font-family: "微软雅黑";
    color: {COLOR_TEXT_PRIMARY}; /* 普通标签深灰，确保可见 */
}}
/* 标题标签：科技蓝纯色+粗体，无渐变，醒目且可见 */
QLabel#titleLabel {{
    font-family: "微软雅黑";
    font-size: 11pt;
    font-weight: bold;
    color: {COLOR_MAIN}; /* 纯色主色，修复不可见 */
}}
/* 提示标签：浅灰，辅助说明 */
QLabel#hintLabel {{
    color: {COLOR_TEXT_SECONDARY};
    font-size: 8pt;
}}
"""

# ===================== 菜单栏样式：清爽扁平，适配整体=====================
MENU_STYLE = f"""
QMenuBar {{
    background-color: {COLOR_BG_CONTAINER};
    border-bottom: 1px solid {COLOR_BORDER};
    font-family: "微软雅黑";
    font-size: 9pt;
    color: {COLOR_TEXT_PRIMARY};
}}
QMenuBar::item {{
    padding: 3px 14px;
    border-radius: 3px;
}}
QMenuBar::item:selected {{
    background-color: {COLOR_MAIN};
    color: white;
}}
QMenu {{
    background-color: {COLOR_BG_CONTAINER};
    border: 1px solid {COLOR_BORDER};
    border-radius: 4px;
    font-family: "微软雅黑";
    font-size: 9pt;
    color: {COLOR_TEXT_PRIMARY};
    box-shadow: 0 2px 6px {COLOR_SHADOW};
}}
QMenu::item:selected {{
    background-color: {COLOR_MAIN};
    color: white;
    border-radius: 3px;
}}
QMenu::separator {{
    background-color: {COLOR_BORDER};
    height: 1px;
}}
"""