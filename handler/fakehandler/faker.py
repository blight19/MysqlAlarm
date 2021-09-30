#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:yanshushuang
# datetime:2021/9/30
def fake_handler(host, parameter, current, threshold, th_type, tag="",logger=None):
    print(f"Ding!!!Alarm!!!{tag} {host},{parameter}:current{current},threshold:{threshold} th_type:{th_type}")