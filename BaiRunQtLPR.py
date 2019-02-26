#!/usr/bin/env python3
# encoding: utf-8
"""
@author: souno.io
@license: (C) Copyright 2013-2017, Node Supply Chain Manager Corporation Limited.
@contact: souno@qq.com
@file: BaiRunQtLPR.py.py
@time: 18-11-8 下午2:28
@desc:
"""


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QDockWidget, QListWidget
from PyQt5.QtGui import *
from ui.BaiRun import Ui_MainWindow
from hyperlpr import *
import cv2
import sys
from PIL import Image
import os
from config import SOURCE
import datetime
from mysql import Pysql
from fake_to_chinese import put_chinese_text as putC
import configparser
from speech import lpr_speech
import _thread


class lpr_window(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(lpr_window, self).__init__()
        self.setupUi(self)
        self.timer_camera = QtCore.QTimer()
        self.cap = cv2.VideoCapture()
        self.config = configparser.ConfigParser()
        self.config.read("lpr.conf", encoding="utf-8-sig")
        self.CAM_NUM = int(self.config.get('LPR', 'camera_usb'))
        self.audio = int(self.config.get('LPR', 'audio'))
        if self.audio ==0:
            self.pushButton_cap.setText("开启播报")
        else:
            self.pushButton_cap.setText("关闭播报")
        self.__flag_work = 0
        self.__flag_vcr = int(self.config.get('LPR', 'vcr'))
        print(self.__flag_vcr)
        if self.__flag_vcr == 0:
            self.pushButton_vcr.setText("开启录像")
        else:
            self.pushButton_vcr.setText("关闭录像")
        self.x = 0
        self.data_old = ""
        self.plate_color = "蓝"
        self.sql = Pysql()
        self.car_cascade = cv2.CascadeClassifier('cars.xml')
        self.ft = putC('font/msyhl.ttc')
        fourcc = cv2.VideoWriter_fourcc(*'DIVX')
        self.outfile = cv2.VideoWriter('./video/' + datetime.datetime.now().strftime('%Y-%m-%d') + 'output_' + datetime.datetime.now().strftime('%H:%M:%S') + '.avi', fourcc, 20, (800, 500), True)
        # 子窗口的show_label()函数
        self.pushButton_2.clicked.connect(self.button_open_camera_click)
        self.pushButton_vcr.clicked.connect(self.button_vcr_click)
        self.timer_camera.timeout.connect(self.CatchVideo)
        self.pushButton.clicked.connect(self.close)
        self.actionRTSP.triggered.connect(self.changeRTSP)
        self.actionUSB.triggered.connect(self.changeUSB)
        self.actionClose.triggered.connect(self.close)
        self.actionAbout.triggered.connect(self.about)
        self.pushButton_cap.clicked.connect(self.button_audio_click)

    def about(self):
        msg = QtWidgets.QMessageBox.warning(self, u"关于", u"佰润汽车管理软件之车牌识别系统-作者：叶兴。", buttons=QtWidgets.QMessageBox.Ok,
                                            defaultButton=QtWidgets.QMessageBox.Ok)

    def changeRTSP(self):
        self.CAM_NUM = self.config['LPR']['camera_rtsp']
        self.infoLabel.setText('当前已连接摄像头：流协议摄像头 ')
        msg = QtWidgets.QMessageBox.warning(self, u"警告", u"切换摄像头后需要手动关闭相机，并再打开！", buttons=QtWidgets.QMessageBox.Ok,
                                            defaultButton=QtWidgets.QMessageBox.Ok)


    def changeUSB(self):
        self.CAM_NUM = int(self.config['LPR']['camera_usb'])
        self.infoLabel.setText('当前已连接摄像头：USB摄像头 ')
        msg = QtWidgets.QMessageBox.warning(self, u"警告", u"切换摄像头后需要手动关闭相机，并再打开！", buttons=QtWidgets.QMessageBox.Ok,
                                            defaultButton=QtWidgets.QMessageBox.Ok)
    def boBao(self, number):
        speech = lpr_speech("车牌号为：" + number)
        speech.speech()
        _thread.exit_thread()

    def sqlMake(self, data_sim):
        self.sql.get_conn()
        self.sql.add_one(data_sim, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        self.mysqlLabel.setText("数据库已写入：" + data_sim)
        self.sql.close_conn()

    def button_open_camera_click(self):
        if self.timer_camera.isActive() == False:
            flag = self.cap.open(self.CAM_NUM)
            print(self.CAM_NUM)
            if flag == False:
                msg = QtWidgets.QMessageBox.warning(self, u"Warning", u"请检测相机与电脑是否连接正确", buttons=QtWidgets.QMessageBox.Ok,
                                                defaultButton=QtWidgets.QMessageBox.Ok)
            # if msg==QtGui.QMessageBox.Cancel:
            #                     pass
            else:
                self.timer_camera.start(30)

                self.pushButton_2.setText(u'关闭相机')
        else:
            self.timer_camera.stop()
            self.cap.release()
            self.videoLabel.clear()
            self.pushButton_2.setText(u'打开相机')

    def button_vcr_click(self):
        if self.__flag_vcr == 0:
            # flag = self.cap.open(self.CAM_NUM)
            # if flag == False:
            #     msg = QtWidgets.QMessageBox.warning(self, u"Warning", u"请检测相机与电脑是否连接正确", buttons=QtWidgets.QMessageBox.Ok,
            #                                     defaultButton=QtWidgets.QMessageBox.Ok)
            # # if msg==QtGui.QMessageBox.Cancel:
            # #                     pass
            # else:
            #     self.timer_camera.start(30)
            if self.timer_camera.isActive() == False:
                msg = QtWidgets.QMessageBox.warning(self, u"Warning", u"使用录像功能请先打开摄像头！",
                                                    buttons=QtWidgets.QMessageBox.Ok,
                                                    defaultButton=QtWidgets.QMessageBox.Ok)
            else:
                self.__flag_vcr = 1
                self.pushButton_vcr.setText(u'关闭录像')
                self.config.set('LPR', 'vcr', '1')
                self.config.write(open("lpr.conf", "w"))
        else:
            # self.cap.release()
            # self.videoLabel.clear()
            self.__flag_vcr = 0
            self.pushButton_vcr.setText(u'开始录像')
            self.config.set('LPR', 'vcr', '0')
            self.config.write(open("lpr.conf", "w"))

    def button_audio_click(self):
        if self.audio == 0:
            self.pushButton_cap.setText("关闭播报")
            self.audio = 1
            self.config.set('LPR', 'audio', '1')
            self.config.write(open("lpr.conf", "w"))
        else:
            self.pushButton_cap.setText("开启播报")
            self.audio = 0
            self.config.set('LPR', 'audio', '0')
            self.config.write(open("lpr.conf", "w"))

    def CatchVideo(self):
        if not self.cap.isOpened():
            print("打开摄像头失败，请检查！")
        color = (0, 0, 255)
        ok, frame = self.cap.read()  # 读取一帧数据
        if not ok:
            print(ok)
        # 显示图像并等待10毫秒按键输入，输入‘q’退出程序
        data = HyperLPR_PlateRecogntion(frame)
        if len(data) > 0:  # 大于0则检测到车牌
            for data_sim in data:  # 单独框出每一张车牌
                # print(data_old)
                # print(data_sim[0])
                print(data)
                self.LPNLabel.setText(data_sim[0])
                self.proLabel.setText(str(data_sim[1]))
                self.timeLabel.setText(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                self.typeLabel.setStyleSheet("background-color: rgb(0, 0, 255);")
                print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                x, y, w, h = data_sim[2]
                cv2.rectangle(frame, (x, y), (w, h), color, 1)
                frame = self.ft.draw_text(frame, (x, y-18), str(data_sim[0]), 12, color)
                # cv2.putText(frame, str(data_sim[0]),
                #             (x, y - 10),  # 坐标
                #             cv2.FONT_HERSHEY_TRIPLEX,  # 字体
                #             0.5,  # 字号
                #             (255, 0, 255),  # 颜色
                #             2)  # 字的线宽
                # engine.say(str(data_sim[0]))
                # engine.runAndWait()
                if data_sim[1] > 0.97:
                    if (data_sim[0] != self.data_old):
                        print(self.data_old)
                        try:
                            if self.audio == 1:
                                _thread.start_new_thread(self.boBao, (data_sim[0],))
                            _thread.start_new_thread(self.sqlMake, (data_sim[0],))
                        except:
                            print("Error:无法启动线程", sys.exc_info())
                        self.stateLabel.setText("上一次的车牌取值为_" + data_sim[0] + "_" + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                        # _thread.start_new_thread(os.system('espeak -vzh ' + data_sim[0]), ("Thread-1", 2,))
                        self.data_old = data_sim[0]
        else:
            pass
        # cars = self.car_cascade.detectMultiScale(frame, 1.1, 1)
        # for (x, y, w, h) in cars:
        #     cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
        image_height, image_width, image_depth = frame.shape
        size = image_width/800
        frame = cv2.resize(frame, (800, int(image_height/size)))
        print(self.__flag_vcr)
        if self.__flag_vcr == 1:
            self.outfile.write(frame)
        else:
            pass
        Qframe = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # opencv读图片是BGR，qt显示要RGB，所以需要转换一下
        Qframe = QtGui.QImage(Qframe.data, 800, int(image_height/size),  # 创建QImage格式的图像，并读入图像信息
                                  800 * image_depth,
                                  QImage.Format_RGB888)
        self.videoLabel.setPixmap(QPixmap.fromImage(Qframe))

    def closeEvent(self, event):
        ok = QtWidgets.QPushButton()
        cacel = QtWidgets.QPushButton()

        msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, u"关闭", u"是否退出系统！")

        msg.addButton(ok,QtWidgets.QMessageBox.ActionRole)
        msg.addButton(cacel, QtWidgets.QMessageBox.RejectRole)
        ok.setText(u'确定')
        cacel.setText(u'取消')
        # msg.setDetailedText('sdfsdff')
        if msg.exec_() == QtWidgets.QMessageBox.RejectRole:
            event.ignore()
        else:
            #             self.socket_client.send_command(self.socket_client.current_user_command)
            if self.cap.isOpened():
                self.cap.release()
            if self.timer_camera.isActive():
                self.timer_camera.stop()
            event.accept()



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    window = lpr_window()
    window.show()
    sys.exit(app.exec_())


