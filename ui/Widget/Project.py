from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from ui.ComponentLib.MyWidget import MyWidget
from SystemInfo import SystemInfo

class Project(MyWidget):
    def __init__(self):
        self.GroupBox = QGroupBox("视频选项")
        self.selectComboBox = QComboBox()
        self.startDetect = QPushButton("开始检测")
        self.modeComboBox = QComboBox()
        self.modeComboBox.addItem("视频")
        self.modeComboBox.addItem("检测结果")
        self.modeComboBox.currentIndexChanged.connect(self.modeChange)
        # self.result = QPushButton("查看结果")

        self.GroupBox.setLayout(
            self.set2FullHBoxLayout([self.selectComboBox, self.startDetect, self.modeComboBox]))

    def modeChange(self):
        SystemInfo.video_mode = self.modeComboBox.currentIndex()
