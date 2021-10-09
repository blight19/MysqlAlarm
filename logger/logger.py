#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:yanshushuang
# datetime:2021/9/26
import logging
import time


class Logger:
    def __init__(self, stream=False, file=False):
        self.logger = logging.getLogger("Alarm Logger")
        self.formatter = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
        self.logger.setLevel(logging.INFO)
        if stream:
            self.__add_stream()
        if file:
            self.__add_file()

    def __add_stream(self):
        sh = logging.StreamHandler()
        sh.setFormatter(self.formatter)
        self.logger.addHandler(sh)

    def __add_file(self):
        filename = time.strftime("%Y-%m-%d")
        fh = logging.FileHandler(filename=f"{filename}.log")
        fh.setFormatter(self.formatter)
        self.logger.addHandler(fh)

    def get_logger(self):
        return self.logger


