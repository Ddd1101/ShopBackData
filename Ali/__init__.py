"""1688 平台适配器入口。"""

from .Config import CredentialStore, ShopCredential
from .Client import Alibaba1688Client
from .Category import get_category_adapter

__all__ = ['CredentialStore', 'ShopCredential', 'Alibaba1688Client', 'get_category_adapter']