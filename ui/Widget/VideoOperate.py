from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from ui.ComponentLib.MyWidget import MyWidget
from SystemInfo import SystemInfo

class VideoOperate(MyWidget):
    def __init__(self):
        self.GroupBox = QGroupBox("视频控制")
        self.videoOperateGrid = QGridLayout()
        self.GroupBox.setLayout(self.videoOperateGrid)

        back = QPushButton("Back")

        self.opStart = QPushButton("开始")
        self.opPause = QPushButton("暂停")

        forward = QPushButton("forward")

        self.nowTime = QLabel("")

        self.totalTime = QLabel("")

        self.timeSlide = QSlider(Qt.Horizontal)

        self.videoOperateGrid.addWidget(self.timeSlide, 0, 0, 1, 9)
        self.videoOperateGrid.addWidget(self.nowTime, 1, 2, 1, 1)
        self.videoOperateGrid.addWidget(back, 1, 3, 1, 1)
        self.videoOperateGrid.addWidget(self.opStart, 1, 4, 1, 1)
        self.videoOperateGrid.addWidget(self.opPause, 1, 5, 1, 1)
        self.videoOperateGrid.addWidget(forward, 1, 6, 1, 1)
        self.videoOperateGrid.addWidget(self.totalTime, 1, 7, 1, 1)

    def updateUI(self):
        self.timeSlide.setMinimum(0)
        self.timeSlide.setMaximum(SystemInfo.video_total_fps)
        self.totalTime.setText("{}:{}".format(str(int(SystemInfo.video_time / 60)).zfill(2),
                                              str(SystemInfo.video_time % 60).zfill(2)))
