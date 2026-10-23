"""Excel / xls 读取工具。"""

import xlrd


def get_sheet(path, sheet_index=0):
    workbook = xlrd.open_workbook(path)
    sheets = workbook.sheet_names()
    return workbook.sheet_by_name(sheets[sheet_index])


def load_price_grid(price_path):
    """读取价格表第一个 sheet。"""

    return get_sheet(price_path)


def load_factory_grid(factory_path):
    """读取工厂表，返回以工厂名为 key 的空字典容器。"""

    worksheet = get_sheet(factory_path)
    factory_map = {}
    for t in range(1, worksheet.nrows):
        factory_map[worksheet.cell(t, 0).value] = {}
    return factory_map