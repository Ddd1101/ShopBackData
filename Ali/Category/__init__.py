"""1688 品类适配器。"""

from ...Common.Model import CATEGORY_CLOTH, CATEGORY_ACCESSORY
from .Base import CategoryAdapter
from .Cloth import ClothCategoryAdapter
from .Accessory import AccessoryCategoryAdapter

CATEGORY_ADAPTERS = {
    CATEGORY_CLOTH: ClothCategoryAdapter,
    CATEGORY_ACCESSORY: AccessoryCategoryAdapter,
}


def get_category_adapter(category_key, price_path, **kwargs):
    cls = CATEGORY_ADAPTERS.get(category_key)
    if cls is None:
        raise ValueError('未知品类: ' + str(category_key))
    return cls(price_path, **kwargs)


__all__ = [
    'CategoryAdapter',
    'ClothCategoryAdapter',
    'AccessoryCategoryAdapter',
    'CATEGORY_ADAPTERS',
    'get_category_adapter',
]