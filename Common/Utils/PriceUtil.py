"""价格列定位 / 货号标准化 / 显示格式化等纯函数（无副作用、无 Qt 依赖）。"""

import re

from ..GlobleData import EnglishCode


def CalSize(sizeDescription):
    """从尺码描述中提取开头的连续数字。"""

    _size = 0
    for ch in sizeDescription:
        if '0' <= ch <= '9':
            _size = _size * 10 + int(ch)
        else:
            break
    return _size


def CalPriceLocationENCode(_size):
    """英文码（S/M/L/XL/XXL/XXXL）→ 价格列下标。"""

    if _size == '':
        return -1
    if _size[0] in ('S', 's'):
        return 24
    if _size[0] in ('M', 'm'):
        return 25
    if _size[0] in ('L', 'l'):
        return 26
    if _size[0] in ('x', 'X'):
        if _size[1] in ('L', 'l'):
            return 27
        elif _size[1] in ('x', 'X'):
            if _size[2] in ('L', 'l'):
                return 28
            elif _size[2] in ('x', 'X'):
                return 29
    return -1


def CalENCode(_size):
    """归一化英文尺码为 S/M/L/XL/XXL 标识。"""

    if _size[0] in ('S', 's'):
        return 'S'
    if _size[0] in ('M', 'm'):
        return 'M'
    if _size[0] in ('L', 'l'):
        return 'L'
    if _size[0] in ('x', 'X'):
        if _size[1] in ('L', 'l'):
            return 'XL'
        elif _size[1] in ('x', 'X'):
            if _size[2] in ('L', 'l'):
                return 'XXL'
            elif _size[2] in ('x', 'X'):
                return 'XXL'
    return -1


def CalPriceLocation(_size):
    """按尺码计算价格列（数字码按 90 起每 5 一档）。"""

    if _size[0] in EnglishCode:
        return CalPriceLocationENCode(_size)
    theta = (CalSize(_size) - 90) / 5
    return 5 + theta


def CalPriceColByName(_size, worksheet):
    """按表头名称定位价格列。"""

    _size = _size.upper()
    if _size == '2XL':
        _size = 'XXL'
    elif _size == '3XL':
        _size = 'XXXL'
    if _size and _size[0] in EnglishCode:
        _size = CalENCode(_size)
        for col in range(worksheet.ncols):
            if worksheet.cell_value(0, col) == _size:
                return col
    for col in range(worksheet.ncols):
        if worksheet.cell_value(0, col) == CalSize(_size):
            return col
    return -1


def NumFormate4Print(numStr):
    """尺寸显示格式化。"""

    res = ''
    if numStr[0] in EnglishCode:
        for item in numStr:
            if item in EnglishCode:
                res += item
            else:
                break
        fomateSpaceNum = 5 - len(res)
        for _ in range(fomateSpaceNum):
            res = ' ' + res
    else:
        for item in numStr:
            if '0' <= item <= '9':
                res += item
            else:
                if len(res) and res[0] == '9':
                    res += ' '
                break
        res += 'cm'
    return res


def CalCargoNum4ERP(cargoNumber):
    """货号标准化：剥离末尾「-」+ 1~4 位数字的变体后缀。

    例：TZ-240312-17 → TZ-240312；230573-75 → 230573。
    """

    return re.sub(r'-\d{1,4}$', '', cargoNumber)


def pad_shop_name(name, width):
    """按显示宽度补齐空格：中文/全角按 2 列、英文数字按 1 列。"""

    visual = sum(2 if ord(c) > 127 else 1 for c in name)
    return name + ' ' * max(0, width - visual)