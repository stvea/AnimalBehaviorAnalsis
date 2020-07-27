from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from ui.ComponentLib.MyWidget import MyWidget
from SystemInfo import SystemInfo

class Set(MyWidget):
    def __init__(self):
        super(Set, self)
        self.stackWidget = QStackedWidget()

        self.videoInfo = QWidget()
        self.paintStrict = QWidget()
        self.detectSet = QWidget()

        self.videoInfoUI()
        self.detectSetUI()

        self.stackWidget.addWidget(self.videoInfo)
        self.stackWidget.addWidget(self.detectSet)

        self.GroupBox = QGroupBox("视屏信息")
        self.GroupBox.setLayout(self.set2FullVBoxLayout([self.stackWidget]))

    def videoInfoUI(self):
        layout = QFormLayout()
        self.videoAddress = QLineEdit()
        self.videoLength = QLineEdit()
        self.videoType = QLineEdit()
        self.videoFps = QLineEdit()
        self.videoAddress.setEnabled(False)
        self.videoLength.setEnabled(False)
        self.videoFps.setEnabled(False)
        self.videoType.setEnabled(False)
        layout.addRow(QLabel("视频地址"), self.videoAddress)
        layout.addRow(QLabel("时长"), self.videoLength)
        layout.addRow(QLabel("格式"), self.videoType)
        layout.addRow(QLabel("FPS"), self.videoFps)
        self.videoInfo.setLayout(layout)

    def updateVideoInfoUI(self):
        self.videoAddress.setText(SystemInfo.video_opened_url)
        self.videoLength.setText(str(SystemInfo.video_total_fps / SystemInfo.video_fps))
        self.videoFps.setText(str(SystemInfo.video_fps))
        self.startTimeEdit.setMaximumTime(
            QtCore.QTime(int(SystemInfo.video_time / 60), SystemInfo.video_time % 60, 0))
        self.endTimeEdit.setMaximumTime(QtCore.QTime(int(SystemInfo.video_time / 60), SystemInfo.video_time % 60, 0))
        self.endTimeEdit.setTime(QtCore.QTime(int(SystemInfo.video_time / 60), SystemInfo.video_time % 60, 0))

    def detectSetUI(self):
        layout = QFormLayout()
        self.chooseAreaBTN = QPushButton()
        self.chooseAreaBTN.setText("绘制检测区域")
        self.startTimeEdit = QTimeEdit()
        self.startTimeEdit.setDisplayFormat("HH:mm:ss")
        self.startTimeEdit.setTime(QtCore.QTime(0, 0, 0))
        self.startTimeEdit.setMinimumTime(QtCore.QTime(0, 0, 0))

        self.endTimeEdit = QTimeEdit()
        self.endTimeEdit.setDisplayFormat("HH:mm:ss")
        self.endTimeEdit.setTime(QtCore.QTime(0, 0, 0))
        self.endTimeEdit.setMinimumTime(QtCore.QTime(0, 0, 0))

        self.step = QSpinBox()
        self.step.setMinimum(1)
        layout.addRow(QLabel("绘制检测区域"),self.chooseAreaBTN)
        layout.addRow(QLabel("开始时间"), self.startTimeEdit)
        layout.addRow(QLabel("结束时间"), self.endTimeEdit)
        layout.addRow(QLabel("步长"), self.step)

        self.detectSet.setLayout(layout)
