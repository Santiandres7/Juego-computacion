"""
Items Module.
Defines consumable and equipment items found on Mutant Peak.
"""

class Item:
    def __init__(self, name: str, item_type: str, stat_affected: str, value: int, is_consumable: bool):
        self.name = name
        self.item_type = item_type              # 'consumable', 'equipment'
        self.stat_affected = stat_affected      # 'hp', 'attack', 'defense'
        self.value = value
        self.is_consumable = is_consumable

    def apply(self, target) -> str:
        """Applies item effect to the target entity and returns a feedback message."""
        if self.stat_affected == "hp":
            target.heal(self.value)
            return f"{target.name} recovered {self.value} HP."
        elif hasattr(target, self.stat_affected):
            current_val = getattr(target, self.stat_affected)
            setattr(target, self.stat_affected, current_val + self.value)
            return f"{target.name}'s {self.stat_affected} increased by +{self.value}."
        return f"{self.name} had no effect."

    def __str__(self):
        consumable_tag = "Consumable" if self.is_consumable else "Permanent"
        return f"[{self.name}] (+{self.value} {self.stat_affected.upper()}) - {consumable_tag}"


# Catalog of 5 lore-based items (healing consumables and gear boosts)
ITEM_CATALOG = [
    Item("Purified Primis Serum", "consumable", "hp", 45, is_consumable=True),
    Item("Thermal Energy Ration", "consumable", "hp", 30, is_consumable=True),
    Item("Reinforced Titanium Ice Axe", "equipment", "attack", 5, is_consumable=False),
    Item("Chemical Injector", "equipment", "attack", 4, is_consumable=False),
    Item("Insulated Nano-Armor Plate", "equipment", "defense", 4, is_consumable=False)
]

def get_random_loot():
    """Returns a random item instance from the catalog."""
    import random
    return random.choice(ITEM_CATALOG)
