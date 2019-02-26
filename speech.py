#!/usr/bin/env python3
# encoding: utf-8
"""
@author: souno.io
@license: (C) Copyright 2013-2017, Node Supply Chain Manager Corporation Limited.
@contact: souno@qq.com
@file: mysql.py
@time: 18-11-7 下午4:49
@desc:
"""
import os
from aip import AipSpeech
import pygame
import time

class lpr_speech:
    def __init__(self, sentense):
        try:
            os.mkdir("audio")
        except FileExistsError:
            pass
        self.sentense = sentense
        self.APP_ID = "14778828"
        self.APP_KEY = "37gyWVK9sGL1lW3whsugZ9Mu"
        self.SCECRET_KEY = "y5GqYAbrf0OqRgb0ZhxV5GGwO0VgYbZz"
        self.client = AipSpeech(self.APP_ID, self.APP_KEY, self.SCECRET_KEY)

    def speech(self):
        result = self.client.synthesis(self.sentense, 'zh', 1, {'vol': 5, 'per': 4, 'aue': 6})
        if not isinstance(result, dict):
            with open('audio/license_'+self.sentense + '.wav', 'wb') as f:
                f.write(result)
            f.close()
        file = 'audio/license_'+self.sentense + '.wav'
        pygame.mixer.init(frequency=15500, size=-16, channels=4)
        pygame.mixer.Sound(file).play()


if __name__ == '__main__':
    speech = lpr_speech("你好")
    speech.speech()
