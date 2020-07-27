import sys
import threading
import numpy as np

import time
from collections import defaultdict

import cv2
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QMutex, QMutexLocker
from PyQt5.QtGui import QFont, QImage, QPixmap
from PyQt5.QtWidgets import *
from PyQt5 import QtGui
# from PyQt5.uic.properties import QtGui

from Entity.OperateMenu import OperateMenu
from locateCode import locate_code
from ui.ProgressBar import ProgressBar


class SystemInfos:

    video_name = []
    # video's cache list index is the frame
    video_cache = []
    video_is_cached = False
    video_cache_fps = 0

    video_opened_url = None
    video_is_opened = False
    video_isPlay = False
    video_fps = 12
    video_time = 0
    video_now_fps = 0
    video_now_time = 0
    video_total_fps = 0

    # 0:show video 1:detect result
    video_mode = 0

    detect_set_start_time = 0
    detect_set_end_time = 0
    detect_set_step = 20
    detect_step = 1
    detect_info = defaultdict(list)
    detect_all_number = []

    video = None
    video_thread = None


class Widget:
    def set2FullVBoxLayout(self, widgets):
        vbl = QVBoxLayout()
        vbl.setContentsMargins(0, 0, 0, 0)
        for widget in widgets:
            vbl.addWidget(widget)
        return vbl

    def set2FullHBoxLayout(self, widgets):
        hbl = QHBoxLayout()
        hbl.setContentsMargins(0, 0, 0, 0)
        for widget in widgets:
            hbl.addWidget(widget)
        return hbl


class SetWidget(Widget):
    def __init__(self):
        super(SetWidget, self)
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
        self.videoAddress.setText(SystemInfos.video_opened_url)
        self.videoLength.setText(str(SystemInfos.video_total_fps / SystemInfos.video_fps))
        self.videoFps.setText(str(SystemInfos.video_fps))
        self.startTimeEdit.setMaximumTime(
            QtCore.QTime(int(SystemInfos.video_time / 60), SystemInfos.video_time % 60, 0))
        self.endTimeEdit.setMaximumTime(QtCore.QTime(int(SystemInfos.video_time / 60), SystemInfos.video_time % 60, 0))
        self.endTimeEdit.setTime(QtCore.QTime(int(SystemInfos.video_time / 60), SystemInfos.video_time % 60, 0))

    def detectSetUI(self):
        layout = QFormLayout()
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

        layout.addRow(QLabel("开始时间"), self.startTimeEdit)
        layout.addRow(QLabel("结束时间"), self.endTimeEdit)
        layout.addRow(QLabel("步长"), self.step)

        self.detectSet.setLayout(layout)


class MenuWidget(Widget):
    def __init__(self):
        super(MenuWidget, self)
        self.GroupBox = QGroupBox("实验步骤")
        self.experimentExploer = QTreeWidget()
        self.experimentExploer.setColumnCount(1)
        self.experimentExploer.setHeaderHidden(True)
        operateMenus = [['视频操作', '查看视频信息'], ['检测设置', '标注区域', '视频范围'], ['结果分析', '结果预览', '数据导出', '数据预览']]
        for menusIndex in range(len(operateMenus)):
            for menuIndex in range(len(operateMenus[menusIndex])):
                if menuIndex == 0:
                    operateMenus[menusIndex][menuIndex] = OperateMenu(operateMenus[menusIndex][menuIndex],
                                                                      self.experimentExploer)
                else:
                    operateMenus[menusIndex][menuIndex] = OperateMenu(operateMenus[menusIndex][menuIndex],
                                                                      operateMenus[menusIndex][0].getQTreeWidgetItem())
        self.experimentExploer.expandAll()
        self.GroupBox.setLayout(self.set2FullVBoxLayout([self.experimentExploer]))

    def setUnable(self):
        self.GroupBox.setEnabled(False)


class ProjectWidget(Widget):
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
        SystemInfos.video_mode = self.modeComboBox.currentIndex()


class VideoOperateWidget(Widget):
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
        self.timeSlide.setMaximum(SystemInfos.video_total_fps)
        self.totalTime.setText("{}:{}".format(str(int(SystemInfos.video_time / 60)).zfill(2),
                                              str(SystemInfos.video_time % 60).zfill(2)))


class VideoWidget(Widget):
    def __init__(self):
        self.GroupBox = QGroupBox("视频预览")
        self.videoLabel = QtWidgets.QLabel()
        self.videoLabel.setText("video label")
        self.GroupBox.setLayout(self.set2FullVBoxLayout([self.videoLabel]))


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("动物行为分析系统")
        mainWidget = QWidget()
        grid = QGridLayout()
        mainWidget.setLayout(grid)

        self.setCentralWidget(mainWidget)

        self.setWidget = SetWidget()
        self.menuWidget = MenuWidget()
        self.projectWidget = ProjectWidget()
        self.projectWidget.startDetect.clicked.connect(self.detectStart)
        self.videoWidget = VideoWidget()
        self.videoOperateWidget = VideoOperateWidget()

        self.videoOperateWidget.opStart.clicked.connect(self.videoOp)
        self.videoOperateWidget.opPause.clicked.connect(self.videoOp)
        self.videoOperateWidget.timeSlide.sliderMoved.connect(self.changeTime)
        # self.setWidgetsStatus(False)
        self.menuWidget.experimentExploer.clicked.connect(self.switchSet)

        self.setSystemMenus()
        # self.setWidgets()

        grid.addWidget(self.menuWidget.GroupBox, 0, 0, 10, 5)
        grid.addWidget(self.projectWidget.GroupBox, 0, 5, 1, 15)
        grid.addWidget(self.videoWidget.GroupBox, 1, 5, 6, 15)
        grid.addWidget(self.videoOperateWidget.GroupBox, 7, 5, 1, 15)
        grid.addWidget(self.setWidget.GroupBox, 8, 5, 2, 15)

        self.resize(1920, 1080)
        self.setContentsMargins(0, 0, 0, 0)

    def switchSet(self, index):
        item = self.menuWidget.experimentExploer.currentItem()
        # print(index.row())
        print(item.text(0))
        if item.text(0) == "查看视频信息":
            self.setWidget.stackWidget.setCurrentWidget(self.setWidget.videoInfo)
            self.setWidget.GroupBox.setTitle("查看视频信息")
        elif item.text(0) == "视频范围":
            self.setWidget.stackWidget.setCurrentWidget(self.setWidget.detectSet)
            self.setWidget.GroupBox.setTitle("视频范围")

    def setWidgetsStatus(self, status):
        self.menuWidget.GroupBox.setEnabled(status)
        self.projectWidget.GroupBox.setEnabled(status)
        self.setWidget.GroupBox.setEnabled(status)

    def setSystemMenus(self):
        # 菜单栏
        bar = self.menuBar()
        file = bar.addMenu("文件")
        open = QAction("打开视频", self)
        open.triggered.connect(self.openVideo)
        file.addAction(open)

    def setVideoOperateBtnsStatus(self, status):
        for btn in self.videoOperateBtns:
            btn.setEnabled(status)

    def videoBack(self):
        print("back")

    def getDetectSet(self):
        print(self.setWidget.step.text())
        SystemInfos.detect_set_step = int(self.setWidget.step.text())
        # SystemInfos.detect_set_start_time =

    def detectStart(self):
        # SystemInfos.
        self.getDetectSet()
        SystemInfos.detect_step = SystemInfos.detect_set_step
        total_step = (SystemInfos.detect_set_end_time * SystemInfos.video_fps - SystemInfos.detect_set_start_time * SystemInfos.video_fps) / SystemInfos.detect_set_step
        print('[sys]Start detect,total:{}'.format(total_step))
        self.ProgressBar = ProgressBar("self.FileIndex", "self.VideoNum", SystemInfos.video_total_fps)
        for i in range(int(SystemInfos.detect_set_start_time * SystemInfos.video_fps),
                       int(SystemInfos.detect_set_end_time * SystemInfos.video_fps), int(SystemInfos.detect_set_step)):
            SystemInfos.detect_info['detect_frame'].append(i)
            SystemInfos.video.set(cv2.CAP_PROP_POS_FRAMES, i)
            success, frame = SystemInfos.video.read()
            tag_list = []
            number, orientation, _, tag_center = locate_code(frame, threshMode=0, bradleyFilterSize=15,
                                                             bradleyThresh=3, tagList=tag_list)
            SystemInfos.detect_info['tag_label'].append(number)
            SystemInfos.detect_all_number.extend(number)
            SystemInfos.detect_info['orientation'].append(orientation)
            SystemInfos.detect_info['tag_center'].append(tag_center)
            print("total step:{} i:{}".format(total_step, i))
            self.ProgressBar.setTipLable(
                "总帧数：{}帧,当前帧数：{},步长：{}".format(int(SystemInfos.video_total_fps), i, SystemInfos.detect_set_step))
            self.ProgressBar.setValue(i)  # 更新进度条的值
            QApplication.processEvents()  # 实时显示
        self.ProgressBar.close()  # 记得关闭进度条
        self.showMessage("提示", "检测完成！")

    # def track_video(video, start_time, end_time, step, tag_list=[]):
    #     # det_info = defaultdict(list)
    #     # all_number = []
    #     # fps = video.get(cv2.CAP_PROP_FPS)
    #     # n_frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
    #     for i in range(int(start_time * fps), int(end_time * fps), int(step)):
    #         print(i)
    #         det_info['det_frame'].append(i)
    #         video.set(cv2.CAP_PROP_POS_FRAMES, i)
    #         success, frame = video.read()
    #         number, orientation, _, tag_center = locate_code(frame, threshMode=0, bradleyFilterSize=15,
    #                                                          bradleyThresh=3, tagList=tag_list)
    #         det_info['tag_label'].append(number)
    #         all_number.extend(number)
    #         det_info['orientation'].append(orientation)
    #         det_info['tag_center'].append(tag_center)
    #     if len(tag_list) == 0:
    #         tag_list = list(set(all_number))
    #     video.release()
    #     return det_info, tag_list

    def videoOp(self):
        if SystemInfos.video_isPlay:
            SystemInfos.video_thread.videoStop()
            SystemInfos.video_isPlay = False
        else:
            # play to the end and replay
            if SystemInfos.video_now_fps == SystemInfos.video_total_fps:
                SystemInfos.video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                SystemInfos.video_now_fps = 0
                SystemInfos.video_now_time = 0
                self.videoOperateWidget.timeSlide.setValue(SystemInfos.video_now_fps)

            SystemInfos.video_isPlay = True
            try:
                SystemInfos.video_thread.resume()
            except:
                SystemInfos.video_thread = Thread()
                SystemInfos.video_thread.init()
                SystemInfos.video_thread.timeSignal.connect(self.updateVideoUI)
                SystemInfos.video_thread.videoImage.connect(self.setImage)
                SystemInfos.video_thread._buttonSignal.connect(self.setButton)
                SystemInfos.video_thread.warnSignal.connect(self.showMessage)
                SystemInfos.video_thread.start()

    def showMessage(self, label, text):
        QMessageBox.about(self, label, text)

    def setButton(self, flag):
        if flag:
            self.videoOperateWidget.opStart.setEnabled(True)
            self.videoOperateWidget.opPause.setEnabled(False)
        else:
            self.videoOperateWidget.opStart.setEnabled(False)
            self.videoOperateWidget.opPause.setEnabled(True)

    def setImage(self, image):
        self.videoWidget.videoLabel.setPixmap(QPixmap.fromImage(image))

    def openVideo(self):
        videoName, videoType = QFileDialog.getOpenFileName(self,
                                                           "打开视频",
                                                           "",
                                                           # " *.jpg;;*.png;;*.jpeg;;*.bmp")
                                                           " *.mp4;;*.avi;;All Files (*)")
        self.setWidgetsStatus(True)
        if SystemInfos.video_is_opened:
            try:
                SystemInfos.video.release()
                self.clearTime()
            except:
                print("Do not played")
            print("Open New Video")
        else:
            print("[user]first open video")
        self.projectWidget.selectComboBox.addItem(videoName)
        SystemInfos.video_name.append([videoName, videoType])
        self.getVideoInfo(videoName)
        self.videoOperateWidget.updateUI()
        self.setWidget.updateVideoInfoUI()
        self.setImage(self.readVideo(SystemInfos.video))

    def getVideoInfo(self, videoName):
        SystemInfos.video_opened_url = videoName
        SystemInfos.video = cv2.VideoCapture(videoName)
        SystemInfos.video_is_opened = True
        SystemInfos.video_fps = SystemInfos.video.get(5)
        SystemInfos.video_total_fps = SystemInfos.video.get(7)
        SystemInfos.video_time = int(SystemInfos.video_total_fps / SystemInfos.video_fps)
        SystemInfos.detect_set_start_time = 0
        SystemInfos.detect_set_end_time = SystemInfos.video_time

    def changeTime(self, value):
        SystemInfos.video_now_fps = value
        SystemInfos.video_now_time = int(value / SystemInfos.video_fps)
        SystemInfos.video_isPlay = False
        SystemInfos.video.set(cv2.CAP_PROP_POS_FRAMES, value)
        self.setImage(self.readVideo(SystemInfos.video))
        self.updateTime()
        print("value change")

    def clearTime(self):
        SystemInfos.video_now_fps = SystemInfos.video_now_time = 0
        SystemInfos.video_isPlay = False
        self.videoOperateWidget.timeSlide.setValue(0)

    def updateVideoUI(self):
        self.updateTime()
        self.videoOperateWidget.timeSlide.setValue(SystemInfos.video_now_fps)

    def updateTime(self):
        self.videoOperateWidget.nowTime.setText("{}:{}".format(str(int(SystemInfos.video_now_time / 60)).zfill(2),
                                                               str(SystemInfos.video_now_time % 60).zfill(2)))

    def setTime(self, time):
        print("now time:{}".format(time))
        # self.videoOperateBtns[3].setText(str(time))

    def readVideo(self, cap):
        ret, frame = cap.read()
        if ret:
            rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            convertToQtFormat = QtGui.QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0],
                                             QImage.Format_RGB888)  # 在这里可以对每帧图像进行处理，
            p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
        return p


class Thread(QThread):  # 采用线程来播放视频
    timeSignal = pyqtSignal()
    videoImage = pyqtSignal(QtGui.QImage)
    _buttonSignal = pyqtSignal(bool)
    warnSignal = pyqtSignal(str, str)

    def init(self):
        self.mutex = QMutex()
        SystemInfos.video = cv2.VideoCapture(SystemInfos.video_opened_url)

    def run(self):
        with QMutexLocker(self.mutex):
            self.stopped = False
        while SystemInfos.video.isOpened() == True:
            # start time
            time_start = time.time()
            # check if play to end
            if SystemInfos.video_total_fps == SystemInfos.video_now_fps:
                self._buttonSignal.emit(True)
                return

            if SystemInfos.video_mode:
                # when comes to error value emit a signal to show message
                # self.warnSignal.emit("123","890")
                # return

                # SystemInfos.video.set(cv2.CAP_PROP_POS_FRAMES, v)
                success, frame = SystemInfos.video.read()
                if success:
                    detect_index = int(SystemInfos.video_now_fps / SystemInfos.detect_step) * SystemInfos.detect_step
                    index = SystemInfos.detect_info['detect_frame'].index(detect_index)
                    rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    for i in range(0, len(SystemInfos.detect_info['tag_label'][index])):
                        center = np.round(SystemInfos.detect_info['tag_center'][index][i]).astype(int)
                        cv2.putText(rgbImage, str(SystemInfos.detect_info['tag_label'][index][i]),
                                    (center[1], center[0]), cv2.FONT_HERSHEY_COMPLEX, 2.0, (100, 200, 200), 5)
                    convertToQtFormat = QtGui.QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0],
                                                     QImage.Format_RGB888)  # 在这里可以对每帧图像进行处理，
                    self.videoImage.emit(convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio))

            else:
                success, frame = SystemInfos.video.read()
                if success:
                    rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    convertToQtFormat = QtGui.QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0],
                                                     QImage.Format_RGB888)  # 在这里可以对每帧图像进行处理，
                    print("[Sys]Play fps:{}".format(SystemInfos.video_now_fps))
                    self.videoImage.emit(convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio))

                    # [!]add into cache
                    # if SystemInfos.video_now_fps > SystemInfos.video_cache_fps:

            if SystemInfos.video_now_fps % SystemInfos.video_fps == 0:
                SystemInfos.video_now_time += 1
            SystemInfos.video_now_fps += 1
            time_end = time.time()
            self.timeSignal.emit()

            # deal operate button's status
            if SystemInfos.video_isPlay == False:
                self._buttonSignal.emit(True)
                return
            else:
                self._buttonSignal.emit(False)
            if time_end - time_start < (1 / SystemInfos.video_fps):
                time.sleep(1 / SystemInfos.video_fps - (time_end - time_start))

    def videoStop(self):
        SystemInfos.video_isPlay = False

    def resume(self):
        SystemInfos.video_isPlay = True
        self.start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = MainWindow()
    gui.show()
    sys.exit(app.exec_())
