"""
节点模块 - 包含所有节点类型的实现
"""
from .base import BaseNode
from .custom import (
    InputNode,
    OutputNode,
    ValidationNode,
    CustomProcessNode,
    EnrichmentNode
)

# 节点注册表 - 用于动态创建节点实例
NODE_REGISTRY = {
    "BaseNode": BaseNode,
    "InputNode": InputNode,
    "OutputNode": OutputNode,
    "ValidationNode": ValidationNode,
    "CustomProcessNode": CustomProcessNode,
    "EnrichmentNode": EnrichmentNode,
}


def create_node(node_type: str, node_config: dict) -> BaseNode:
    """
    根据节点类型创建节点实例

    Args:
        node_type: 节点类型名称
        node_config: 节点配置

    Returns:
        BaseNode: 节点实例

    Raises:
        ValueError: 当节点类型不存在时
    """
    if node_type not in NODE_REGISTRY:
        raise ValueError(f"Unknown node type: {node_type}")

    node_class = NODE_REGISTRY[node_type]
    return node_class(node_config)


def get_available_node_types() -> list:
    """获取所有可用的节点类型"""
    return list(NODE_REGISTRY.keys())


__all__ = [
    "BaseNode",
    "InputNode",
    "OutputNode",
    "ValidationNode",
    "CustomProcessNode",
    "EnrichmentNode",
    "NODE_REGISTRY",
    "create_node",
    "get_available_node_types"
]