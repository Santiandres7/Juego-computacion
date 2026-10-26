"""
Core Package Initialization.
Exposes core classes and structures for clean imports across the project.
"""
from core.data_structures import TurnQueue, InventoryStack, StageLinkedList
from core.items import Item, ITEM_CATALOG, get_random_loot
from core.entities import Hero, Enemy, generate_procedural_enemy
from core.combat import Combat

__all__ = [
    "TurnQueue",
    "InventoryStack",
    "StageLinkedList",
    "Item",
    "ITEM_CATALOG",
    "get_random_loot",
    "Hero",
    "Enemy",
    "generate_procedural_enemy",
    "Combat",
]
