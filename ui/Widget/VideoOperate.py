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

        self.back = QPushButton("Back")
        self.back.clicked.connect(self.videoBack)

        self.start = QPushButton("开始")

        self.pause = QPushButton("暂停")

        self.forward = QPushButton("forward")
        self.forward.clicked.connect(self.videoForward)

        self.nowTime = QLabel("")
        self.nowTime.setAlignment(Qt.AlignCenter)

        self.totalTime = QLabel("")
        self.totalTime.setAlignment(Qt.AlignCenter)

        self.timeSlide = QSlider(Qt.Horizontal)

        self.videoOperateGrid.addWidget(self.timeSlide, 0, 0, 1, 9)
        self.videoOperateGrid.addWidget(self.nowTime, 1, 2, 1, 1)
        self.videoOperateGrid.addWidget(self.back, 1, 3, 1, 1)
        self.videoOperateGrid.addWidget(self.start, 1, 4, 1, 1)
        self.videoOperateGrid.addWidget(self.pause, 1, 5, 1, 1)
        self.videoOperateGrid.addWidget(self.forward, 1, 6, 1, 1)
        self.videoOperateGrid.addWidget(self.totalTime, 1, 7, 1, 1)

    def videoForward(self):
        SystemInfo.main_view.changeTime(SystemInfo.video_now_fps+5)

    def videoBack(self):
        SystemInfo.main_view.changeTime(SystemInfo.video_now_fps-5)

    def updateUI(self):
        self.timeSlide.setMinimum(0)
        self.timeSlide.setMaximum(SystemInfo.video_total_fps)
        self.totalTime.setText("{}:{}".format(str(int(SystemInfo.video_time / 60)).zfill(2),
                                              str(SystemInfo.video_time % 60).zfill(2)))
    def setEnabled(self,status):
        self.timeSlide.setEnabled(status)
        self.back.setEnabled(status)
        self.forward.setEnabled(status)
        self.pause.setEnabled(status)
        self.start.setEnabled(status)

