# 自定义圆形蒙版Label（可直接复用）
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPainter, QPixmap, QPainterPath, QColor
from PySide6.QtCore import Qt, QRectF

class CircleMaskLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setScaledContents(False)  # 必须关闭自动缩放，手动绘制

    def paintEvent(self, event):
        if not self.pixmap():
            super().paintEvent(event)
            return
        # 1. 创建画家，开启抗锯齿（避免边缘锯齿）
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        # 2. 创建圆形路径（蒙版形状）
        path = QPainterPath()
        path.addEllipse(QRectF(self.rect()))  # 以控件大小为圆形
        # 3. 设置蒙版：只绘制路径内的区域
        painter.setClipPath(path)
        # 4. 绘制图片（适配圆形）
        pixmap = self.pixmap().scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        x = (self.width() - pixmap.width()) / 2
        y = (self.height() - pixmap.height()) / 2
        painter.drawPixmap(x, y, pixmap)

# 使用：直接设置图片即可，自动变成圆形
# label = CircleMaskLabel()
# label.setPixmap(QPixmap("avatar.jpg"))
# label.setFixedSize(100, 100)