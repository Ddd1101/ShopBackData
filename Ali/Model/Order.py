#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：ShopTools 
@File    ：FactoryUtil.py
@Author  ：Ddd
@Date    ：2024/03/04 0:38 
'''
class Order:
    def __init__(self, shopName, appKey, appSecret, accessToken):
        self.shopName = shopName
        self.appKey = appKey
        self.appSecret = appSecret
        self.accessToken = accessToken