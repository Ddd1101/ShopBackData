"""店铺鉴权凭据配置：支持字典与 JSON/YAML 文件加载，避免硬编码在业务逻辑。"""

from dataclasses import dataclass

from ..Common.Utils.ConfigUtil import read_json, read_yaml


@dataclass
class ShopCredential:
    shop_name: str
    app_key: str
    app_secret: bytes
    access_token: str


class CredentialStore:
    """按店铺名管理鉴权凭据。"""

    def __init__(self):
        self._credentials = {}

    def add(self, credential: ShopCredential):
        self._credentials[credential.shop_name] = credential

    def get(self, shop_name) -> ShopCredential:
        if shop_name not in self._credentials:
            raise KeyError('未配置店铺凭据: ' + shop_name)
        return self._credentials[shop_name]

    @property
    def shop_names(self):
        return list(self._credentials.keys())

    @classmethod
    def from_mapping(cls, mapping):
        """mapping: {shop_name: {"app_key":..., "app_secret":..., "access_token":...}}"""

        store = cls()
        for shop_name, cred in mapping.items():
            secret = cred['app_secret']
            if isinstance(secret, str):
                secret = secret.encode('utf-8')
            store.add(ShopCredential(
                shop_name=shop_name,
                app_key=str(cred['app_key']),
                app_secret=secret,
                access_token=str(cred['access_token']),
            ))
        return store

    @classmethod
    def from_file(cls, path):
        """从 JSON 文件加载（顶层或 `shops` 字段均可）。"""

        data = read_json(path)
        return cls.from_mapping(data.get('shops', data))

    @classmethod
    def from_yaml(cls, path):
        """从 YAML 文件加载（需安装 PyYAML）。"""

        data = read_yaml(path)
        return cls.from_mapping(data.get('shops', data))