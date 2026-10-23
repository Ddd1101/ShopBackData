"""1688 OpenAPI 客户端：HMAC-SHA1 签名 + 鉴权 + 各接口调用。"""

import hmac
import math
import time

import requests

from ..Common import AlbbBaseUrl, request_type
from ..Platform import PlatformAdapter
from .Config import CredentialStore
from .Category import get_category_adapter


def _cal_page_num(total_record, page_size=20):
    return math.ceil(total_record / page_size)


class Alibaba1688Client(PlatformAdapter):
    platform_key = 'alibaba_1688'

    def __init__(self, credentials=None, logger=None, check_cancel=None, request_sleep=0.2):
        super().__init__(logger=logger, check_cancel=check_cancel)
        self.credentials = credentials if credentials is not None else CredentialStore()
        self.request_sleep = request_sleep

    # ---- 内部 ----
    def _cred(self, shop_name):
        return self.credentials.get(shop_name)

    def _sign(self, url_path, data, secret):
        """HMAC-SHA1 签名，与 1688 OpenAPI 规范一致。"""

        params = [key + str(data[key]) for key in data.keys()]
        params.sort()
        merged = (url_path + ''.join(params)).encode('utf-8')
        return hmac.new(secret, merged, digestmod='sha1').hexdigest().upper()

    def _post(self, rtype, api_name, shop_name, data):
        cred = self._cred(shop_name)
        payload = dict(data)
        payload['access_token'] = cred.access_token
        url_path = request_type[rtype] + api_name + '/' + cred.app_key
        payload['_aop_signature'] = self._sign(url_path, payload, cred.app_secret)
        url = AlbbBaseUrl + url_path
        if self.request_sleep:
            time.sleep(self.request_sleep)
        try:
            response = requests.post(url, data=payload)
        except Exception as e:  # noqa: BLE001
            self.logger.debug('post error %s', e)
            raise
        return response.json()

    # ---- 平台统一接口 ----
    def get_order_list(self, shop_name, **kwargs):
        """订单列表。"""

        return self._post('trade', 'alibaba.trade.getSellerOrderList', shop_name, kwargs)

    def get_order_detail(self, shop_name, **kwargs):
        """单笔订单详情。"""

        return self._post('trade', 'alibaba.trade.ec.getOrder.sellerView', shop_name, kwargs)

    def get_logistics(self, shop_name, **kwargs):
        """物流信息。"""

        return self._post('delivery', 'alibaba.trade.getLogisticsInfos.sellerView', shop_name, kwargs)

    def get_logistics_trace(self, shop_name, **kwargs):
        """物流轨迹信息。"""

        return self._post('delivery', 'alibaba.trade.getLogisticsTraceInfo.sellerView', shop_name, kwargs)

    def fetch_orders(self, shop_name, start_time, end_time, order_status, **kwargs):
        """按时间范围与订单状态分页拉取全量订单（原始结果列表）。"""

        first = self.get_order_list(
            shop_name,
            createStartTime=start_time.strip(),
            createEndTime=end_time.strip(),
            orderStatus=order_status.strip(),
            needMemoInfo='true',
        )
        page_num = _cal_page_num(first.get('totalRecord', 0))
        orders = []
        for page_id in range(page_num):
            self.check_cancel()
            resp = self.get_order_list(
                shop_name,
                page=str(page_id + 1),
                createStartTime=start_time,
                createEndTime=end_time,
                orderStatus=order_status.strip(),
                needMemoInfo='true',
            )
            orders += resp.get('result', [])
        return orders

    def get_category_adapter(self, category_key, price_path, **kwargs):
        """按品类类型返回品类适配器（复用当前 logger 与取消回调）。"""

        kw = {'logger': self.logger, 'check_cancel': self.check_cancel}
        kw.update(kwargs)
        return get_category_adapter(category_key, price_path, **kw)