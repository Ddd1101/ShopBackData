"""品类适配器抽象基类。"""

import logging
from abc import ABC, abstractmethod

from ...Common.Utils.ExcelUtil import load_price_grid


class CategoryAdapter(ABC):
    """同平台内不同品类的数据结构差异在此内聚。"""

    category_key = ''

    def __init__(self, price_path, logger=None, check_cancel=None):
        self.price_path = price_path
        self.logger = logger if logger is not None else logging.getLogger(self.__class__.__name__)
        self.check_cancel = check_cancel if check_cancel is not None else (lambda: None)
        self._worksheet = None
        self.missing_price_records = []

    def _load_grid(self):
        if self._worksheet is None:
            self._worksheet = load_price_grid(self.price_path)
        return self._worksheet

    @abstractmethod
    def get_price(self, cargo_number, sku_value, col_num=0):
        """按货号与规格查询价格。"""

    @abstractmethod
    def aggregate(self, orders, mode=0):
        """将订单聚合为备货数据（BeihuoItem 列表）。"""