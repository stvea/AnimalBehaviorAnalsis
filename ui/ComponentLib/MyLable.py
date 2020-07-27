from PyQt5 import QtGui
from PyQt5.QtCore import QRect, Qt
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtWidgets import QLabel

from SystemInfo import SystemInfo


class MyLabel(QLabel):
    area =[0,0,0,0]
    flag = False
    start_paint = False
    show_area = True

    def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:

        if self.start_paint:
            self.flag = True
            self.area[0] = ev.x()
            self.area[1] = ev.y()

    def mouseReleaseEvent(self, ev: QtGui.QMouseEvent) -> None:

        if self.start_paint:
            self.flag = False
            self.start_paint = False

    def mouseMoveEvent(self, ev: QtGui.QMouseEvent) -> None:

        if self.start_paint:
            if self.flag:
                self.area[2] = ev.x()
                self.area[3] = ev.y()
                self.update()

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        super().paintEvent(a0)
        if self.start_paint or self.show_area:
            rect = QRect(self.area[0], self.area[1], abs(self.area[2] - self.area[0]), abs(self.area[3] - self.area[1]))
            painter = QPainter(self)
            painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
            painter.drawRect(rect)
            SystemInfo.detect_area = self.area
    # def clearPaint(self):
    #     QPainter(self)

    def startPaint(self):
        self.start_paint = True
