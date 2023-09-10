#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：ShopTools 
@File    ：PriceUtil.py
@Author  ：Ddd
@Date    ：2023/9/10 23:55 
'''
from ShopBackData.Common.GlobleData import *

def CalSize(sizeDescription):
    productSize = 0
    for i in range(len(sizeDescription)):
        if sizeDescription[i] >= '0' and sizeDescription[i] <= '9':
            productSize = productSize * 10 + int(sizeDescription[i])
        else:
            break
    return productSize

def CalPriceLocation(productSize):
    if productSize[0] in EnglishCode:
        return CalPriceLocationENCode(productSize)
    # print(CalSize(_size))
    theta = (CalSize(productSize) - 90)/5
    _col = 5 + theta
    # print(_col)
    return _col

def CalPriceLocationENCode(productSize):
    if productSize == "":
        return -1

    if productSize[0] == 'S' or productSize[0] == 's':
        return 24

    if productSize[0] == 'M' or productSize[0] == 'm':
        return 25

    if productSize[0] == 'L' or productSize[0] == 'l':
        return 26

    if productSize[0] == 'x' or productSize[0] == 'X':
        if productSize[1] == 'L' or productSize[1] == 'l':
            return 27
        elif productSize[1] == 'x' or productSize[1] == 'X':
            if productSize[2] == 'L' or productSize[2] == 'l':
                return 28
            elif productSize[2] == 'x' or productSize[2] == 'X':
                return 29