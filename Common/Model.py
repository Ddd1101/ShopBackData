"""统一数据模型与常量：SDK 对外稳定契约，与平台/品类解耦。"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# 平台标识
PLATFORM_ALI_1688 = 'alibaba_1688'

# 品类标识（SDK 品类 key）
CATEGORY_CLOTH = 'cloth'          # 童装/服装（多尺码）
CATEGORY_ACCESSORY = 'accessory'  # 饰品（单品/无尺码）

# 品类标识（对齐 ShopTools SHOPTYPE）
SHOPTYPE_ALI_CHILD_CLOTH = 1
SHOPTYPE_ALI_ACCESSOR = 2


class TaskInterrupted(Exception):
    """任务被取消时抛出，用于跳出工作循环。"""


@dataclass
class Shop:
    """店铺鉴权凭据（app_secret 为 HMAC 签名密钥字节）。"""

    shop_name: str
    app_key: str
    app_secret: bytes
    access_token: str


@dataclass
class ProductItem:
    """订单中的商品条目（规格化）。"""

    cargo_number: str = ''
    quantity: int = 0
    sku_infos: List[str] = field(default_factory=list)  # 颜色/尺码等 sku 值
    product_img_url: str = ''
    refund: int = 0
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Order:
    """规格化订单。"""

    order_id: Any = None
    base_info: Dict[str, Any] = field(default_factory=dict)
    product_items: List[ProductItem] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SizeItem:
    """童装多尺码明细。"""

    size: str
    quantity: int
    price: float
    cost: float


@dataclass
class BeihuoItem:
    """备货聚合结果项（统一产出契约）。

    - 童装：sizes 含各尺码明细，quantity/cost 为汇总值，price 置 0。
    - 饰品：无 sizes，price/cost 为单品单价与总成本。
    """

    cargo_number: str
    color: str
    product_img_url: str = ''
    quantity: int = 0
    price: float = 0.0
    cost: float = 0.0
    sizes: List[SizeItem] = field(default_factory=list)


@dataclass
class ShopSummary:
    """店铺拿货汇总。"""

    shop_name: str
    total_count: int
    total_cost: float


def normalize_product_item(raw: Dict[str, Any]) -> ProductItem:
    """将 1688 原始商品条目结构化为 ProductItem。"""

    cargo_tag = 'cargoNumber' if 'cargoNumber' in raw else 'productCargoNumber'
    img_url = ''
    img_list = raw.get('productImgUrl') or []
    if len(img_list) > 1:
        img_url = img_list[1]
    sku_infos = [sku.get('value', '') for sku in raw.get('skuInfos', [])]
    return ProductItem(
        cargo_number=raw.get(cargo_tag, ''),
        quantity=raw.get('quantity', 0),
        sku_infos=sku_infos,
        product_img_url=img_url,
        refund=raw.get('refund', 0),
        raw=raw,
    )


def normalize_order(raw: Dict[str, Any]) -> Order:
    """将 1688 原始订单结构化为 Order。"""

    return Order(
        order_id=raw.get('id'),
        base_info=raw.get('baseInfo', {}),
        product_items=[normalize_product_item(p) for p in raw.get('productItems', [])],
        raw=raw,
    )