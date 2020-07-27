from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from ui.ComponentLib.MyLable import MyLabel
from ui.ComponentLib.MyWidget import MyWidget

# video 播放区域
class Video(MyWidget):
    def __init__(self):
        self.GroupBox = QGroupBox("视频预览")
        self.videoLabel = MyLabel()
        self.videoLabel.setText("未打开文件")
        self.videoLabel.setAlignment(Qt.AlignCenter)
        self.GroupBox.setLayout(self.set2FullVBoxLayout([self.videoLabel]))