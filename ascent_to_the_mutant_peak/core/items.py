import copy
import random


class Item:
    def __init__(self, name: str, stat_affected: str, value: int, is_consumable: bool):
        self.name = name
        self.stat_affected = stat_affected
        self.value = value
        self.is_consumable = is_consumable

    def apply(self, target) -> str:
        """Applies item effect to the target entity and returns a feedback message."""
        if self.stat_affected == "hp":
            target.heal(self.value)
            return f"{target.name} recovered {self.value} HP."
        elif self.stat_affected == "energy":
            target.restore_energy(self.value)
            return f"{target.name} recovered {self.value} Energy."
        elif hasattr(target, self.stat_affected):
            current_val = getattr(target, self.stat_affected)
            setattr(target, self.stat_affected, current_val + self.value)
            return f"{target.name}'s {self.stat_affected} increased by +{self.value}."
        return f"{self.name} had no effect."

    def __str__(self):
        consumable_tag = "Consumable" if self.is_consumable else "Permanent"
        return f"[{self.name}] (+{self.value} {self.stat_affected.upper()}) - {consumable_tag}"

ITEM_CATALOG = [
    Item("Purified Primis Serum", "hp", 45, is_consumable=True),
    Item("Thermal Energy Ration", "energy", 40, is_consumable=True),
    Item("Reinforced Titanium Ice Axe", "attack", 5, is_consumable=False),
    Item("Chemical Injector", "attack", 4, is_consumable=False),
    Item("Insulated Nano-Armor Plate", "defense", 8, is_consumable=False)
]


def get_random_loot():
    """Returns a NEW copy of a random catalog item (so enemies don't share instances)."""
    return copy.copy(random.choice(ITEM_CATALOG))