from math import sqrt

from PyQt5 import QtGui
from PyQt5.QtCore import QRect, Qt, QLine
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtWidgets import QLabel

from SystemInfo import SystemInfo


class MyLabel(QLabel):
    scale = [0,0,0,0]
    scale_flag = False
    scale_start_paint = False

    area =[0,0,0,0]
    area_flag = False
    area_start_paint = False
    area_show = True

    def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
        if self.area_start_paint:
            self.area_flag = True
            self.area[0] = ev.x()
            self.area[1] = ev.y()
        elif self.scale_start_paint:
            self.scale_flag = True
            self.scale[0] = ev.x()
            self.scale[1] = ev.y()


    def mouseReleaseEvent(self, ev: QtGui.QMouseEvent) -> None:
        if self.area_start_paint:
            self.area_flag = False
            self.area_start_paint = False
            SystemInfo.detect_area = self.area
            SystemInfo.main_view.status.showMessage('绘制结束，若重新绘制请再次点击', 2000)

        elif self.scale_start_paint:
            self.scale_flag = False
            self.scale_start_paint = False
            SystemInfo.detect_scale = self.scale
            SystemInfo.detect_scale_label = sqrt((self.scale[0]-self.scale[2])**2+(self.scale[1]-self.scale[3])**2)
            SystemInfo.main_view.getScaleReal()
            SystemInfo.main_view.status.showMessage('绘制结束，若重新绘制请再次点击', 2000)


    def mouseMoveEvent(self, ev: QtGui.QMouseEvent) -> None:
        if self.area_start_paint:
            if self.area_flag:
                self.area[2] = ev.x()
                self.area[3] = ev.y()
                self.update()
        elif self.scale_start_paint:
            if self.scale_flag:
                self.scale[2] = ev.x()
                self.scale[3] = ev.y()
                self.update()

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        super().paintEvent(a0)
        painter = QPainter(self)
        if self.area_start_paint or SystemInfo.detect_area_show :
            painter.setPen(QPen(Qt.blue, 2, Qt.SolidLine))
            rect = QRect(self.area[0], self.area[1], abs(self.area[2] - self.area[0]), abs(self.area[3] - self.area[1]))
            painter.drawRect(rect)

        if self.scale_start_paint:
            painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))
            painter.drawLine(self.scale[0], self.scale[1],self.scale[2],self.scale[3])

    def startAreaPaint(self):
        self.area_start_paint = True
        SystemInfo.main_view.status.showMessage('开始绘制区域',0)

    def startScalePaint(self):
        self.scale_start_paint = True
        SystemInfo.main_view.status.showMessage('开始绘制比例尺',0)
