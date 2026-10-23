# ShopBackData

多电商平台的 **API 汇总库（SDK）**，用于被不同形态的宿主工程复用（现有 PySide2 备货单客户端、未来的 Web 网站），沉淀平台接入、订单拉取、价格查询、备货数据聚合等能力。

当前已完成 **1688 平台** 接入，并在平台层之下抽象了 **品类（Category）** 层，以隔离同一平台内不同品类的数据结构差异。

## 目录结构

```
ShopBackData/
├── Common/                  # 平台无关的公共工具与统一数据模型
│   ├── GlobleData.py        # 全局常量（EnglishCode / AlbbBaseUrl / request_type）
│   ├── Model.py             # 统一数据模型（Shop/Order/ProductItem/BeihuoItem/ShopSummary 等）
│   ├── ImageHandler.py      # 图片缓存/下载/读取（与宿主回调解耦）
│   └── Utils/
│       ├── ConfigUtil.py    # 配置读取（JSON / YAML）
│       ├── ExcelUtil.py     # 价格表/工厂表读取（getSheet）
│       └── PriceUtil.py     # 尺寸→价格列定位、货号标准化、显示格式化
├── Platform/
│   └── Base.py              # 平台适配器抽象基类（PlatformAdapter）
├── Ali/                     # 1688 平台实现
│   ├── Config.py            # 店铺鉴权凭据加载（字典 / JSON / YAML）
│   ├── Client.py            # 1688 OpenAPI 客户端（HMAC-SHA1 签名 + 四接口）
│   └── Category/
│       ├── Base.py          # 品类适配器抽象基类（CategoryAdapter）
│       ├── Cloth.py         # 童装/服装品类（多尺码）
│       └── Accessory.py     # 饰品类（单品/无尺码）
└── tests/
    └── verify_sdk.py        # 最小自检脚本（不依赖 Qt）
```

## 快速开始

```python
from ShopBackData.Ali import Alibaba1688Client, CredentialStore
from ShopBackData.Common.Model import CATEGORY_CLOTH

# 1. 配置店铺凭据（不硬编码在 SDK 内）
credentials = CredentialStore.from_mapping({
    '联球制衣厂': {
        'app_key': '你的AppKey',
        'app_secret': '你的AppSecret',
        'access_token': '你的access_token',
    },
})

# 2. 创建 1688 客户端
client = Alibaba1688Client(credentials=credentials)

# 3. 拉取订单（分页）
orders = client.fetch_orders(
    '联球制衣厂',
    start_time='2026-10-20 00:00:00',
    end_time='2026-10-23 00:00:00',
    order_status='waitsellersend',
)

# 4. 按品类聚合为备货数据
cloth = client.get_category_adapter(CATEGORY_CLOTH, 'price.xlsx')
items = cloth.aggregate(orders)  # -> List[BeihuoItem]
```

## 平台接入方式

新平台（如淘宝/抖音/拼多多）只需：

1. 继承 `Platform.Base.PlatformAdapter`，实现 `get_order_list`、`get_order_detail`、`get_logistics`、`get_logistics_trace`、`fetch_orders`、`get_category_adapter`。
2. 在该平台包下按品类继承 `Category.Base.CategoryAdapter`，实现 `get_price` 与 `aggregate`，把品类差异内聚到各自适配器。

## 宿主集成（无 Qt 依赖）

SDK 不 `import` PySide2/Qt，三类宿主行为均通过注入实现：

- **日志**：构造时传入 `logger`（`logging.Logger`），否则使用标准 `logging`。
- **任务取消**：构造时传入 `check_cancel` 回调（取消失抛 `TaskInterrupted`），否则为空操作。
- **图片手动下载兜底**：`Common.ImageHandler.download_image(..., on_manual_download=url_callback)`，由宿主决定如何打开浏览器。

## 自检

```bash
python tests/verify_sdk.py
```

覆盖：签名一致性、货号标准化、价格列定位、童装/饰品聚合、品类工厂、无 Qt 依赖。