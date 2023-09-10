#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：ShopTools 
@File    ：ExcelUtil.py
@Author  ：Ddd
@Date    ：2023/9/11 0:00 
'''
import xlrd


class ExcelUtil:
    def __init__(self, filePath):
        self.filePath = filePath


    # 打开文件
    def openFile(self):
        pass

    # 关闭文件
    def closeFile(self):
        pass

    # 写入指定行
    def writeRow(self, rowIndex, data):
        pass

    # 删除指定行
    def delRow(self):
        pass

    def getSheet(self):
        workbook = xlrd.open_workbook(self.filePath)  # 打开工作簿
        sheets = workbook.sheet_names()  # 获取工作簿中的所有表格
        worksheet = workbook.sheet_by_name(sheets[0])  # 获取工作簿中所有表格中的的第一个表格
        return worksheet