# {{ project_name_title }}

{{ project_description }}

## 项目信息

- **项目类型**: Graph项目 (工作流图)
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
│   ├── graph.py         # 图执行引擎
│   ├── nodes/           # 节点实现
│   │   ├── __init__.py
│   │   ├── base.py      # 基础节点类
│   │   └── custom.py    # 自定义节点
│   └── models.py        # 数据模型
├── tests/
│   └── test_graph.py    # 测试文件
├── workflow.json        # 工作流定义
├── pyproject.toml       # 项目配置
├── sdw.json            # SDW平台配置
└── README.md           # 项目说明
```

## 工作流定义

在 `workflow.json` 中定义你的工作流图：

```json
{
  "name": "{{ project_name }}",
  "version": "{{ project_version }}",
  "nodes": [
    {
      "id": "input",
      "type": "InputNode",
      "config": {}
    },
    {
      "id": "process",
      "type": "CustomProcessNode",
      "config": {
        "param1": "value1"
      }
    },
    {
      "id": "output",
      "type": "OutputNode",
      "config": {}
    }
  ],
  "edges": [
    {"from": "input", "to": "process"},
    {"from": "process", "to": "output"}
  ]
}
```

## 自定义节点

在 `src/nodes/custom.py` 中实现你的自定义节点：

```python
from .base import BaseNode
from ..models import NodeData

class CustomProcessNode(BaseNode):
    async def execute(self, input_data: NodeData) -> NodeData:
        # 实现你的节点逻辑
        pass
```

## 测试

运行测试：

```bash
pytest
```

## 代码格式化

```bash
black src/ tests/
```

## 部署

使用 `sdwk publish` 命令将项目发布到SDW平台。

## Graph项目特性

- **并行执行**: 支持节点的并行执行
- **条件分支**: 支持基于条件的流程控制
- **错误处理**: 内置错误处理和重试机制
- **状态管理**: 跟踪工作流执行状态
- **可视化**: 支持工作流图的可视化展示