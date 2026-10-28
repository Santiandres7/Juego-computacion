"""
Core Package Initialization.
Exposes core classes and structures for clean imports across the project.
"""
from core.data_structures import TurnQueue, InventoryStack, StageLinkedList
from core.items import Item, ITEM_CATALOG, get_random_loot
from core.entities import (Hero, Enemy, Boss, Skill, generate_procedural_enemy,generate_boss, create_squad)
from core.combat import Combat
from core.stages import Stage, build_mountain_ascent

__all__ = [
    "TurnQueue",
    "InventoryStack",
    "StageLinkedList",
    "Item",
    "ITEM_CATALOG",
    "get_random_loot",
    "Hero",
    "Enemy",
    "Boss",
    "Skill",
    "generate_procedural_enemy",
    "generate_boss",
    "create_squad",
    "Combat",
    "Stage",
    "build_mountain_ascent",
]