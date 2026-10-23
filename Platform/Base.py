"""平台适配器抽象基类。"""

import logging
from abc import ABC, abstractmethod


class PlatformAdapter(ABC):
    """所有电商平台接入须实现此接口，使上层宿主无需感知平台差异。"""

    platform_key = ''

    def __init__(self, logger=None, check_cancel=None):
        self.logger = logger if logger is not None else logging.getLogger(self.__class__.__name__)
        self.check_cancel = check_cancel if check_cancel is not None else (lambda: None)

    @abstractmethod
    def get_order_list(self, shop_name, **kwargs):
        """获取订单列表（单页）。"""

    @abstractmethod
    def get_order_detail(self, shop_name, **kwargs):
        """获取单笔订单详情。"""

    @abstractmethod
    def get_logistics(self, shop_name, **kwargs):
        """获取物流信息。"""

    @abstractmethod
    def get_logistics_trace(self, shop_name, **kwargs):
        """获取物流轨迹信息。"""

    @abstractmethod
    def fetch_orders(self, shop_name, start_time, end_time, order_status, **kwargs):
        """按时间范围与订单状态分页拉取全量订单。"""

    @abstractmethod
    def get_category_adapter(self, category_key, price_path, **kwargs):
        """按品类类型返回对应品类适配器。"""