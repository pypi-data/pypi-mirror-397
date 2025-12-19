# {{ project_name_title }}

{{ project_description }}

## 项目信息

- **项目类型**: Node项目
- **版本**: {{ project_version }}
- **平台地址**: {{ platform_url }}

## 快速开始

### 安装依赖

```bash
uv sync
```

### 开发模式运行

```bash
sdwk dev
```

### 检查代码质量

```bash
sdwk check
```

### 发布到平台

```bash
sdwk publish
```

## 项目结构

```
{{ project_name_kebab }}/
├── src/
│   ├── main.py          # 主入口文件
│   ├── node.py          # 节点处理逻辑
│   └── models.py        # 数据模型
├── tests/
│   └── test_node.py     # 测试文件
├── pyproject.toml       # 项目配置
├── sdw.json            # SDW平台配置
└── README.md           # 项目说明
```

## 开发指南

### 节点处理逻辑

在 `src/node.py` 中实现你的节点处理逻辑：

```python
from .models import InputData, OutputData

async def process(input_data: InputData) -> OutputData:
    # 在这里实现你的处理逻辑
    pass
```

### 测试

运行测试：

```bash
pytest
```

### 代码格式化

```bash
black src/ tests/
```

## 部署

使用 `sdwk publish` 命令将项目发布到SDW平台。