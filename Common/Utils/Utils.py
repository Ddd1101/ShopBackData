#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：ShopTools 
@File    ：Utils.py
@Author  ：Ddd
@Date    ：2023/9/11 0:16 
'''
from ShopBackData.Common.GlobleData import *

def NumFormate4Print(numStr):
    res = ""
    if numStr[0] in EnglishCode:
        for item in numStr:
            if item in EnglishCode:
                res += item
            else:
                break
        fomateSpaceNum = 5 - len(res)
        for k in range(fomateSpaceNum):
            res = " " + res

    else:
        for item in numStr:
            if item >= '0' and item <= '9':
                res += item
            else:
                if res[0] == '9':
                    res += " "
                break
        res += "cm"
    return res