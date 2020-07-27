# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QApplication, QWidget, QDialog, QLabel, QLineEdit, QProgressBar, \
    QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, QDialogButtonBox
from PyQt5.QtCore import Qt, QBasicTimer, QThread
import sys

from qtconsole.qtconsoleapp import QtCore
# from qtconsole.qt import QtCore


class ProgressBar(QDialog):
    def __init__(self, fileIndex, filenum, max=100,parent=None):
        super(ProgressBar, self).__init__(parent)

        self.resize(350, 100)
        self.setWindowTitle(self.tr("检测中"))
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.TipLabel = QLabel(self.tr("Processing:" + "   " + str(fileIndex) + "/" + str(filenum)))
        self.FeatLabel = QLabel(self.tr("Extract feature:"))

        self.FeatProgressBar = QProgressBar(self)
        self.FeatProgressBar.setMinimum(0)
        self.FeatProgressBar.setMaximum(max)  # 总进程换算为100
        self.FeatProgressBar.setValue(0)  # 进度条初始值为0

        TipLayout = QHBoxLayout()
        TipLayout.addWidget(self.TipLabel)

        FeatLayout = QHBoxLayout()
        FeatLayout.addWidget(self.FeatLabel)
        FeatLayout.addWidget(self.FeatProgressBar)

        # self.startButton = QPushButton('start',self)
        # self.cancelButton = QPushButton('cancel', self)
        # self.cancelButton.setFocusPolicy(Qt.NoFocus)

        buttonlayout = QHBoxLayout()
        buttonlayout.addStretch(1)
        # buttonlayout.addWidget(self.cancelButton)
        # buttonlayout.addStretch(1)
        # buttonlayout.addWidget(self.startButton)

        layout = QVBoxLayout()
        # layout = QGridLayout()
        layout.addLayout(FeatLayout)
        layout.addLayout(TipLayout)
        layout.addLayout(buttonlayout)
        self.setLayout(layout)
        self.show()

        # self.startButton.clicked.connect(self.setValue)

        # self.cancelButton.clicked.connect(self.onCancel)
        # self.startButton.clicked.connect(self.onStart)
        # self.timer = QBasicTimer()
        # self.step = 0
    def setTipLable(self,label):
        self.TipLabel.setText(label)

    def setValue(self, value):
        self.FeatProgressBar.setValue(value)

    def onCancel(self, event):
        self.close()
