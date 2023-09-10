#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：ShopTools 
@File    ：Config.py
@Author  ：Ddd
@Date    ：2023/9/10 23:51 
'''

import yaml

# 读取yaml
def ReadYaml(path):
    with open(path, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    return config