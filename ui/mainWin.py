import sys
import os
import pickle
import numpy as np

import time

import cv2
import configparser
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QMutex, QMutexLocker, QSize
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import *
from PyQt5 import QtGui

from SystemInfo import SystemInfo
from locateCode import locate_code
from ui.ComponentLib.ProgressBar import ProgressBar
from ui.Widget.Menu import Menu
from ui.Widget.Project import Project
from ui.Widget.Set import Set
from ui.Widget.Video import Video
from ui.Widget.VideoOperate import VideoOperate
from sort import Sort, get_detect_info


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("动物行为分析系统")
        mainWidget = QWidget()
        grid = QGridLayout()
        mainWidget.setLayout(grid)

        self.setCentralWidget(mainWidget)

        self.status = self.statusBar()

        self.setWidget = Set()

        self.menuWidget = Menu()

        self.projectWidget = Project()
        self.projectWidget.startDetect.clicked.connect(self.detectStart)

        self.videoWidget = Video()

        self.videoOperateWidget = VideoOperate()
        self.videoOperateWidget.start.clicked.connect(self.videoOp)
        self.videoOperateWidget.pause.clicked.connect(self.videoOp)
        self.videoOperateWidget.timeSlide.sliderMoved.connect(self.changeTime)

        self.setSystemMenus()

        grid.addWidget(self.menuWidget.GroupBox, 0, 0, 10, 5)
        grid.addWidget(self.projectWidget.GroupBox, 0, 5, 1, 15)
        grid.addWidget(self.videoWidget.GroupBox, 1, 5, 6, 15)
        grid.addWidget(self.videoOperateWidget.GroupBox, 7, 5, 1, 15)
        grid.addWidget(self.setWidget.GroupBox, 8, 5, 2, 15)
        self.resize(1920, 1080)
        self.setContentsMargins(0, 0, 0, 0)
        system_config_file = os.path.abspath('../system.ini')
        print(os.path.exists(system_config_file))
        SystemInfo.get(system_config_file)
        self.setWidgetsStatus(False)

    def updateVideoArea(self):
        QSize(1,2)
        x_len = abs((SystemInfo.video_label_size[0]-SystemInfo.video_label_hint_size[0])/2)
        y_len = abs((SystemInfo.video_label_size[1]-SystemInfo.video_label_hint_size[1])/2)
        hint = [x_len,y_len,SystemInfo.video_label_hint_size[0]+x_len,SystemInfo.video_label_hint_size[1]+y_len]
        if not (hint[0] <= SystemInfo.detect_area[0] <= SystemInfo.detect_area[2] <= hint[2] and hint[1] <= SystemInfo.detect_area[1] <= SystemInfo.detect_area[3] <= hint[3]):
            self.echo("选择区域超出视屏区域，请重新选择！")
            return False
        ratio = SystemInfo.video_size[0]/SystemInfo.video_label_hint_size[0]
        SystemInfo.detect_area = [ratio*(SystemInfo.detect_area[0]-x_len),ratio*(SystemInfo.detect_area[1]-y_len),ratio*(SystemInfo.detect_area[2]-x_len),ratio*(SystemInfo.detect_area[3]-y_len)]
        print(SystemInfo.detect_area)

    def setWidgetsStatus(self, status):
        self.menuWidget.GroupBox.setEnabled(status)
        self.projectWidget.GroupBox.setEnabled(status)
        self.setWidget.GroupBox.setEnabled(status)
        self.videoOperateWidget.setEnabled(status)

    def setSystemMenus(self):
        # 菜单栏
        bar = self.menuBar()
        file = bar.addMenu("文件")
        open = QAction("打开视频", self)
        open.triggered.connect(self.openVideo)
        file.addAction(open)

    def getDetectSet(self):
        try:
            if SystemInfo.detect_area_flag:
                self.updateVideoArea()
        except:
            SystemInfo.log("System",'获取坐标失败！')
        # try:
        #     if SystemInfo.detect_area_flag:
        #         self.getVideoArea()
        #         print(SystemInfo.detect_area)
        # except:
        #     print("[System]Get Area Fail")
        SystemInfo.detect_set_step = int(self.setWidget.step.text())

    def detectStart(self):
        if SystemInfo.video_opened_url is None:
            self.showMessage("提示", "还没选择视频")
            return
        dir_name, file_name = os.path.split(SystemInfo.video_opened_url)
        info_dir = os.path.join(dir_name, os.path.splitext(file_name)[0])
        if not os.path.exists(info_dir):
            os.makedirs(info_dir)
        self.getDetectSet()
        SystemInfo.detect_step = SystemInfo.detect_set_step
        config_file = os.path.join(info_dir, 'detect_config.ini')
        config = configparser.ConfigParser()
        if not os.path.exists(config_file):
            open(config_file, 'w').close()
            # os.mknod(config_file)
        config.read(config_file)
        section = str(SystemInfo.detect_set_start_time) + '-' + str(SystemInfo.detect_set_end_time) + '__' + \
                  str(SystemInfo.detect_step)
        if section in config.sections():
            self.showMessage('提示', '相同的设置已经检测')
            return
        info_file = os.path.join(info_dir, section + '.pkl')
        total_step = (SystemInfo.detect_set_end_time * SystemInfo.video_fps -
                      SystemInfo.detect_set_start_time * SystemInfo.video_fps) / SystemInfo.detect_set_step
        self.ProgressBar = ProgressBar("self.FileIndex", "self.VideoNum", SystemInfo.video_total_fps)
        mul_trackers = Sort(step=SystemInfo.detect_step)
        for i in range(int(SystemInfo.detect_set_start_time * SystemInfo.video_fps),
                       int(SystemInfo.detect_set_end_time * SystemInfo.video_fps) + 1, int(SystemInfo.detect_set_step)):
            SystemInfo.detect_info['detect_frame'].append(i)
            SystemInfo.video.set(cv2.CAP_PROP_POS_FRAMES, i)
            success, frame = SystemInfo.video.read()
            # tag_list = []
            # number, orientation, _, tag_center, _ = locate_code(frame, threshMode=0, bradleyFilterSize=15,
            #                                                     bradleyThresh=3, tagList=tag_list)
            # SystemInfo.detect_info['tag_label'].append(number)
            # SystemInfo.detect_all_number.extend(number)
            # SystemInfo.detect_info['orientation'].append(orientation)
            # SystemInfo.detect_info['tag_center'].append(tag_center)
            if success:
                mul_trackers.update(frame)
            self.ProgressBar.setTipLable(
                "总帧数：{}帧,当前帧数：{},步长：{}".format(int(SystemInfo.video_total_fps), i, SystemInfo.detect_set_step))
            self.ProgressBar.setValue(i)  # 更新进度条的值
            QApplication.processEvents()  # 实时显示
        with open(info_file, 'wb') as f:
            pickle.dump(mul_trackers, f)
        get_detect_info(info_file, SystemInfo)
        SystemInfo.write(config, section, config_file)
        self.ProgressBar.close()  # 记得关闭进度条
        self.showMessage("提示", "检测完成！")
        SystemInfo.video_is_detect = True
        self.projectWidget.addDetect()

    def videoOp(self):
        if SystemInfo.video_is_play:
            SystemInfo.video_thread.videoStop()
            SystemInfo.video_is_play = False
        else:
            # play to the end and replay
            if SystemInfo.video_now_fps == SystemInfo.video_total_fps:
                SystemInfo.video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                SystemInfo.video_now_fps = 0
                SystemInfo.video_now_time = 0
                self.videoOperateWidget.timeSlide.setValue(SystemInfo.video_now_fps)

            SystemInfo.video_is_play = True
            try:
                SystemInfo.video_thread.resume()
            except:
                SystemInfo.video_thread = Thread()
                SystemInfo.video_thread.init()
                SystemInfo.video_thread.timeSignal.connect(self.updateVideoUI)
                SystemInfo.video_thread.videoImage.connect(self.setImage)
                SystemInfo.video_thread._buttonSignal.connect(self.setButton)
                SystemInfo.video_thread.warnSignal.connect(self.showMessage)
                SystemInfo.video_thread.start()

    def showMessage(self, label, text):
        QMessageBox.about(self, label, text)

    def setButton(self, flag):
        if flag:
            self.videoOperateWidget.start.setEnabled(True)
            self.videoOperateWidget.pause.setEnabled(False)
        else:
            self.videoOperateWidget.start.setEnabled(False)
            self.videoOperateWidget.pause.setEnabled(True)

    def setImage(self, image):
        self.videoWidget.videoLabel.setPixmap(QPixmap.fromImage(image))

    def openVideo(self):
        if not os.path.exists(SystemInfo.default_dir):
            SystemInfo.default_dir = ''
        videoName, videoType = QFileDialog.getOpenFileName(self,
                                                           "打开视频",
                                                           SystemInfo.default_dir,
                                                           # " *.jpg;;*.png;;*.jpeg;;*.bmp")
                                                           " *.mp4;;*.avi;;All Files (*)")
        if videoName == "" or not videoName:
            SystemInfo.log("System","未打开视屏！")
            return

        self.setWidgetsStatus(True)
        if SystemInfo.video_is_opened:
            try:
                SystemInfo.video.release()
                self.clearTime()
            except:
                print("Do not played")
            print("Open New Video")
        else:
            SystemInfo.log('user',"First open video")
        self.projectWidget.selectComboBox.addItem(videoName)
        SystemInfo.video_name.append([videoName, videoType])

        self.getVideoInfo(videoName)
        self.videoOperateWidget.updateUI()
        self.setWidget.updateVideoInfoUI()
        self.setImage(self.readVideo(SystemInfo.video))

    def getVideoInfo(self, videoName):
        SystemInfo.video_opened_url = videoName
        SystemInfo.video = cv2.VideoCapture(videoName)
        SystemInfo.video_is_opened = True
        SystemInfo.video_fps = SystemInfo.video.get(5)
        SystemInfo.video_total_fps = SystemInfo.video.get(7)
        SystemInfo.video_time = int(SystemInfo.video_total_fps / SystemInfo.video_fps)
        SystemInfo.detect_area = [0,0,SystemInfo.video.get(3),SystemInfo.video.get(4)]
        SystemInfo.detect_set_start_time = 0
        SystemInfo.detect_set_end_time = SystemInfo.video_time

        SystemInfo.video_size = SystemInfo.detect_area[2:4]
        SystemInfo.video_label_size = [self.videoWidget.videoLabel.size().width(),self.videoWidget.videoLabel.size().height()]

        # 自适应窗口大小
        if SystemInfo.video_size[0] > SystemInfo.video_label_size[0] or SystemInfo.video_size[1] > SystemInfo.video_label_size[1]:
            ratio_width = SystemInfo.video_label_size[0]/SystemInfo.video_size[0]
            ratio_height = SystemInfo.video_label_size[1]/SystemInfo.video_size[1]
            if ratio_width <= ratio_height:
                SystemInfo.video_label_hint_size = [i * ratio_width for i in SystemInfo.video_size]
            else:
                SystemInfo.video_label_hint_size = [i * ratio_height for i in SystemInfo.video_size]

    def changeTime(self, value):
        SystemInfo.video_now_fps = value
        if SystemInfo.video_now_fps >= SystemInfo.video_total_fps:
            SystemInfo.video_now_fps = SystemInfo.video_total_fps-1
        SystemInfo.video_now_time = int(SystemInfo.video_now_fps / SystemInfo.video_fps)
        SystemInfo.video_is_play = False
        SystemInfo.video.set(cv2.CAP_PROP_POS_FRAMES, SystemInfo.video_now_fps)
        self.setImage(self.readVideo(SystemInfo.video))
        self.updateVideoUI()

    def clearTime(self):
        SystemInfo.video_now_fps = SystemInfo.video_now_time = 0
        SystemInfo.video_is_play = False
        self.videoOperateWidget.timeSlide.setValue(0)

    def updateVideoUI(self):
        self.videoOperateWidget.nowTime.setText("{}:{}".format(str(int(SystemInfo.video_now_time / 60)).zfill(2),
                                                               str(SystemInfo.video_now_time % 60).zfill(2)))
        self.videoOperateWidget.timeSlide.setValue(SystemInfo.video_now_fps)

    # def setTime(self, time):
    #     print("now time:{}".format(time))
    #     # self.videoOperateBtns[3].setText(str(time))

    def readVideo(self, cap):
        ret, frame = cap.read()
        if ret:
            rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            convertToQtFormat = QtGui.QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0],
                                             QImage.Format_RGB888)  # 在这里可以对每帧图像进行处理，
            p = convertToQtFormat.scaled(SystemInfo.video_label_hint_size[0], SystemInfo.video_label_hint_size[1],
                                         Qt.KeepAspectRatio)
        return p

    def echo(self, msg):
        QMessageBox.information(self, "提示", msg, QMessageBox.Ok)

    def getScaleReal(self):
        i, okPressed = QInputDialog.getInt(self, "实际长度", "请输入实际长度，单位CM:", 10, 0, 1000, 1)
        if okPressed:
            SystemInfo.detect_scale_real = i



class Thread(QThread):  # 采用线程来播放视频
    timeSignal = pyqtSignal()
    videoImage = pyqtSignal(QtGui.QImage)
    _buttonSignal = pyqtSignal(bool)
    warnSignal = pyqtSignal(str, str)

    def init(self):
        self.mutex = QMutex()
        SystemInfo.video = cv2.VideoCapture(SystemInfo.video_opened_url)

    def run(self):
        with QMutexLocker(self.mutex):
            self.stopped = False
        while SystemInfo.video.isOpened() == True:
            # start time
            time_start = time.time()
            # check if play to end
            if SystemInfo.video_total_fps == SystemInfo.video_now_fps:
                self._buttonSignal.emit(True)
                return

            if SystemInfo.video_mode:
                max_detect_pos = max(SystemInfo.detect_info['detect_frame'])
                # when comes to error value emit a signal to show message
                # self.warnSignal.emit("123","890")
                # return

                # SystemInfos.video.set(cv2.CAP_PROP_POS_FRAMES, v)
                success, frame = SystemInfo.video.read()
                if success:
                    rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    detect_index = int(SystemInfo.video_now_fps / SystemInfo.detect_step) * SystemInfo.detect_step
                    if detect_index in SystemInfo.detect_info['detect_frame']:
                        index = SystemInfo.detect_info['detect_frame'].index(detect_index)
                        for i in range(0, len(SystemInfo.detect_info['tag_label'][index])):
                            center = np.round(SystemInfo.detect_info['tag_center'][index][i]).astype(int)
                            cv2.putText(rgbImage, str(SystemInfo.detect_info['tag_label'][index][i]),
                                        (center[0], center[1]), cv2.FONT_HERSHEY_COMPLEX, 2.0, (100, 200, 200), 5)
                    convertToQtFormat = QtGui.QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0],
                                                     QImage.Format_RGB888)  # 在这里可以对每帧图像进行处理，
                    self.videoImage.emit(convertToQtFormat.scaled(SystemInfo.video_label_hint_size[0], SystemInfo.video_label_hint_size[1], Qt.KeepAspectRatio))

            else:
                success, frame = SystemInfo.video.read()
                if success:
                    rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    convertToQtFormat = QtGui.QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0],
                                                     QImage.Format_RGB888)  # 在这里可以对每帧图像进行处理，
                    SystemInfo.log("System", "Play {} frame".format(SystemInfo.video_now_fps))
                    self.videoImage.emit(convertToQtFormat.scaled(SystemInfo.video_label_hint_size[0], SystemInfo.video_label_hint_size[1], Qt.KeepAspectRatio))

                    # [!]add into cache
                    # if SystemInfos.video_now_fps > SystemInfos.video_cache_fps:

            if SystemInfo.video_now_fps % SystemInfo.video_fps == 0:
                SystemInfo.video_now_time += 1
            SystemInfo.video_now_fps += 1
            time_end = time.time()
            self.timeSignal.emit()

            # deal operate button's status
            if SystemInfo.video_is_play == False:
                self._buttonSignal.emit(True)
                return
            else:
                self._buttonSignal.emit(False)

            if time_end - time_start < (1 / SystemInfo.video_fps):
                time.sleep(1 / SystemInfo.video_fps - (time_end - time_start))

    def videoStop(self):
        SystemInfo.video_is_play = False

    def resume(self):
        SystemInfo.video_is_play = True
        self.start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = MainWindow()
    SystemInfo.main_view = gui
    gui.showMaximized()
    # gui.showFullScreen()
    sys.exit(app.exec_())
    SystemInfo.log("System","Start")

