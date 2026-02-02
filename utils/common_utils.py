import pyperclip
from PySide6.QtWidgets import QMessageBox

class CommonUtils:
    """通用工具类（适配科技风深色弹窗）"""
    @staticmethod
    def copy_to_clipboard(text: str) -> bool:
        """复制文本到剪贴板（适配深色）"""
        try:
            pyperclip.copy(text)
            return True
        except Exception as e:
            print(f"复制失败：{e}")
            # 深色弹窗样式
            msg = QMessageBox()
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #12192C;
                    color: #E8F3FF;
                    font-family: 微软雅黑;
                }
                QPushButton {
                    background: linear-gradient(135deg, #1E3A8A, #0078FF);
                    color: #E8F3FF;
                    border: 1px solid #0078FF;
                    border-radius: 4px;
                    padding: 4px 12px;
                }
                QPushButton:hover {
                    box-shadow: 0 0 6px #0078FF;
                }
            """)
            msg.setIcon(QMessageBox.Warning)
            msg.setText("复制失败！")
            msg.setInformativeText(f"错误信息：{str(e)[:50]}")
            msg.exec()
            return False