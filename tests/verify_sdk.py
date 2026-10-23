# -*- coding: utf-8 -*-
"""ShopBackData 最小自检脚本（不依赖 Qt）。

用法：python tests/verify_sdk.py
覆盖：签名一致性、货号标准化、价格列定位、品类聚合、无 Qt 依赖。
"""

import os
import sys

# 将 ShopTools 目录（ShopBackData 的父目录）加入 sys.path，使 `import ShopBackData` 可用
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from ShopBackData.Common.Utils.PriceUtil import CalCargoNum4ERP, CalPriceColByName
from ShopBackData.Common.Model import CATEGORY_CLOTH, CATEGORY_ACCESSORY
from ShopBackData.Ali import Alibaba1688Client, CredentialStore


class FakeCell:
    def __init__(self, value):
        self.value = value


class FakeSheet:
    """最小 xlrd sheet 替身。"""

    def __init__(self, header, rows):
        self._data = [header] + rows

    @property
    def ncols(self):
        return len(self._data[0])

    @property
    def nrows(self):
        return len(self._data)

    def cell(self, r, c):
        return FakeCell(self._data[r][c])

    def cell_value(self, r, c):
        return self._data[r][c]


def _sign_reference(url, data, secret):
    import hmac
    params = [k + str(data[k]) for k in data]
    params.sort()
    return hmac.new(secret, (url + ''.join(params)).encode('utf-8'), digestmod='sha1').hexdigest().upper()


def test_signature():
    cred = CredentialStore.from_mapping({
        '测试店': {'app_key': '3527689', 'app_secret': 'test-secret', 'access_token': 'dummy-token'},
    })
    client = Alibaba1688Client(credentials=cred)
    url = 'param2/1/com.alibaba.trade/alibaba.trade.getSellerOrderList/3527689'
    data = {
        'createStartTime': '2026-10-20',
        'createEndTime': '2026-10-23',
        'orderStatus': 'waitsellersend',
        'access_token': 'dummy-token',
    }
    got = client._sign(url, data, b'test-secret')
    assert got == _sign_reference(url, data, b'test-secret') == '9273BBD81DDB56C5C49A752A5D1F87D15597FF76', got
    print('[OK] 签名一致性:', got)


def test_cargo_normalize():
    assert CalCargoNum4ERP('TZ-240312-17') == 'TZ-240312'
    assert CalCargoNum4ERP('TZ-240312-21') == 'TZ-240312'
    assert CalCargoNum4ERP('230573-75') == '230573'
    assert CalCargoNum4ERP('230573-113') == '230573'
    assert CalCargoNum4ERP('TZ-240312') == 'TZ-240312'
    print('[OK] 货号标准化')


def test_price_col():
    sheet = FakeSheet(['货号', 'S', 'M', 'L', 'XL', 'XXL'], [['230573', 10, 11, 12, 13, 14]])
    assert CalPriceColByName('M', sheet) == 2
    assert CalPriceColByName('S', sheet) == 1
    assert CalPriceColByName('XL', sheet) == 4
    assert CalPriceColByName('2XL', sheet) == 5  # 2XL -> XXL 列(下标5)
    print('[OK] 价格列定位')


def test_cloth_aggregate():
    from ShopBackData.Ali.Category.Cloth import ClothCategoryAdapter
    adapter = ClothCategoryAdapter('dummy.xlsx')
    adapter._worksheet = FakeSheet(['货号', 'S', 'M', 'L'], [['230573', 10, 11, 12]])
    orders = [
        {
            'baseInfo': {'sellerRemarkIcon': '1'},
            'productItems': [
                {'cargoNumber': '测试品名【230573-75', 'skuInfos': [{'value': '红'}, {'value': 'M'}],
                 'quantity': 2, 'productImgUrl': ['', 'http://x/y.jpg'], 'refund': 0},
                {'cargoNumber': '测试品名【230573-75', 'skuInfos': [{'value': '红'}, {'value': 'L'}],
                 'quantity': 3, 'productImgUrl': ['', 'http://x/y.jpg'], 'refund': 0},
            ],
        }
    ]
    items = adapter.aggregate(orders)
    assert len(items) == 1, items
    it = items[0]
    assert it.cargo_number == '230573', it.cargo_number
    assert it.color == '红'
    assert it.quantity == 5
    assert len(it.sizes) == 2
    m = [s for s in it.sizes if s.size == 'M'][0]
    l = [s for s in it.sizes if s.size == 'L'][0]
    assert m.price == 11 and m.cost == 22, (m.price, m.cost)
    assert l.price == 12 and l.cost == 36, (l.price, l.cost)
    assert abs(it.cost - 58.0) < 1e-9, it.cost
    print('[OK] 童装聚合:', it.cargo_number, it.color, 'total', it.quantity, 'cost', it.cost)


def test_accessory_aggregate():
    from ShopBackData.Ali.Category.Accessory import AccessoryCategoryAdapter
    adapter = AccessoryCategoryAdapter('dummy.xlsx')
    adapter._worksheet = FakeSheet(['货号', '名称', '价格'], [['S-100', '手链', 3.5]])
    orders = [
        {
            'baseInfo': {'sellerRemarkIcon': '1'},
            'productItems': [
                {'cargoNumber': 'S-100', 'skuInfos': [{'value': '银色'}], 'quantity': 5,
                 'productImgUrl': ['', 'http://x/a.jpg'], 'refund': 0},
            ],
        }
    ]
    items = adapter.aggregate(orders)
    assert len(items) == 1
    it = items[0]
    assert it.cargo_number == 'S-100' and it.color == '银色'
    assert it.quantity == 5 and it.price == 3.5 and abs(it.cost - 17.5) < 1e-9
    print('[OK] 饰品聚合:', it.cargo_number, it.color, 'total', it.quantity, 'cost', it.cost)


def test_no_qt():
    assert 'PySide2' not in sys.modules, 'SDK 依赖链中不应引入 PySide2'
    print('[OK] 无 Qt 依赖')


def test_category_factory():
    from ShopBackData.Ali.Category import get_category_adapter
    cloth = get_category_adapter(CATEGORY_CLOTH, 'dummy.xlsx')
    acc = get_category_adapter(CATEGORY_ACCESSORY, 'dummy.xlsx')
    assert cloth.category_key == CATEGORY_CLOTH
    assert acc.category_key == CATEGORY_ACCESSORY
    print('[OK] 品类工厂')


if __name__ == '__main__':
    test_signature()
    test_cargo_normalize()
    test_price_col()
    test_cloth_aggregate()
    test_accessory_aggregate()
    test_category_factory()
    test_no_qt()
    print('\n全部校验通过。')