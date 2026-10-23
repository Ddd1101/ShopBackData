"""配置读取：JSON / YAML。"""

import json


def read_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def read_yaml(path):
    try:
        import yaml
    except ImportError as e:  # pragma: no cover
        raise ImportError('需要安装 PyYAML 才能读取 YAML 配置') from e
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


# 别名，兼容既有命名习惯
ReadYaml = read_yaml