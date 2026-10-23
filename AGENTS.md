# AGENTS.md

本文件为 AI 编码助手（Agent）提供 ShopBackData 工程的背景、架构与强制约束。
开始任何任务前，请先阅读本文件与 [CHANGELOG.md](CHANGELOG.md)（如有）了解最近改动。

## 概述

ShopBackData 是一个 **多电商平台的 API 汇总库（SDK）**，用于被不同形态的宿主工程复用（现有 PySide2 备货单客户端 ShopTools、未来的 Web 网站），沉淀平台接入、订单拉取、价格查询、备货数据聚合等能力。

- 定位：SDK 子模块，独立 git 仓库（`github.com/Ddd1101/ShopBackData.git`）
- 首个平台：**1688**，并抽象了「品类（Category）」层以隔离同平台内不同品类的数据结构差异
- 主要依赖：requests、xlrd；**无 PySide2/Qt 依赖**

## 目录结构

```
ShopBackData/
├── Common/                  # 平台无关的公共工具与统一数据模型
│   ├── GlobleData.py        # 全局常量（EnglishCode / AlbbBaseUrl / request_type）
│   ├── Model.py             # 统一数据模型（Shop/Order/ProductItem/BeihuoItem/SizeItem/ShopSummary 等）
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

## 核心抽象

- **PlatformAdapter（`Platform/Base.py`）**：平台统一接口（拉单、单笔订单、物流、物流轨迹、品类分派）。新平台（淘宝/抖音/拼多多）只需继承实现。
- **CategoryAdapter（`Ali/Category/Base.py`）**：品类统一接口（`get_price`、`aggregate`），把同平台内不同品类的数据结构差异内聚到各自适配器（`Cloth` 多尺码 / `Accessory` 单品）。

## 强制约束（Hard Constraints）

1. **SDK 全程不得 `import` PySide2/Qt**，保证无 GUI 环境下可独立运行。
2. **宿主交互一律注入式**：日志（`logger`）、任务取消（`check_cancel`）、图片手动兜底（`on_manual_download`）均通过构造/调用注入，禁止在 SDK 内硬编码 UI 行为。
3. **鉴权凭据不硬编码**在业务逻辑中，统一由 `Ali/Config.py` 的 `CredentialStore` 从字典/配置文件加载。
4. **品类差异必须隔离**在各自品类适配器内，新增品类不得改动既有品类代码。

## 工程约定（Engineering Conventions）

- 从 ShopTools 迁移逻辑时采用「无副作用迁移」：保持行为与原实现一致，不擅自修复历史遗留行为。
- 统一数据模型集中在 `Common/Model.py`，作为 SDK 对外稳定契约。
- 纯函数工具集中在 `Common/Utils/`，不得依赖全局可变状态。

## 踩坑教训（Lessons Learned）

- 1688 签名前必须先把 `access_token` 加入参数字典再计算 HMAC-SHA1，且签名结果需转大写。
- 签名参数排序后拼接（`key + str(value)`），参数在字典中的顺序不影响结果。
- `Common/Utils/PriceUtil.CalENCode` 对 `XXXL` 返回 `XXL` 属历史遗留行为，迁移时保持原样，勿擅自"修复"。

## 提交约定（Commit Conventions）

commit message 采用「第一行摘要 + 空行 + 分点改造内容」格式：

- **第一行**：`类型: 一句话摘要`（`feat` / `fix` / `refactor` / `build` / `docs` / `style` 等）。
- **正文**：空一行后，每行 `- ` 开头，说明改了什么、涉及文件/模块。
- **bugfix**：正文用一条 `- 修复 …` 点明「问题」与「解决方案」。
- 涉及多个独立主题时，拆分多个聚焦单一主题的提交（分批提交）。

## 变更记录约定

- 每次重要改动完成后，在 [CHANGELOG.md](CHANGELOG.md) 顶部追加一条记录（日期 + 摘要）。
- 每次新对话处理任务前，先读 [CHANGELOG.md](CHANGELOG.md) 了解最近改动。