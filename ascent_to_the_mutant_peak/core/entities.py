"""
Entities Module.
Defines the abstract base class Entity, Hero classes, and Enemy classes.
"""
from abc import ABC, abstractmethod
import random
from core.items import ITEM_CATALOG
from core.data_structures import InventoryStack


class Entity(ABC):
    """Abstract base class for all living creatures in the game."""
    def __init__(self, name: str, max_hp: int, attack: int, defense: int, speed: int):
        self.name = name
        self.max_hp = max_hp
        self.current_hp = max_hp
        self.attack = attack
        self.defense = defense
        self.speed = speed

    def is_alive(self) -> bool:
        """Returns True if current HP is greater than 0."""
        return self.current_hp > 0

    def take_damage(self, amount: int) -> int:
        """Calculates damage with a minimum of 1 and subtracts it from current HP."""
        real_damage = max(1, amount - self.defense)
        self.current_hp = max(0, self.current_hp - real_damage)
        return real_damage

    def heal(self, amount: int):
        """Restores HP without exceeding max HP."""
        self.current_hp = min(self.max_hp, self.current_hp + amount)

    @abstractmethod
    def attack_target(self, target):
        """Abstract method that must be implemented by subclasses."""
        pass


class Hero(Entity):
    """Protagonist character with level progression and a LIFO inventory backpack."""
    def __init__(self, name: str, role: str, max_hp: int, attack: int, defense: int, speed: int):
        super().__init__(name, max_hp, attack, defense, speed)
        self.role = role
        self.level = 1
        self.xp = 0
        self.xp_next_level = 100
        self.backpack = InventoryStack()

    def attack_target(self, target) -> int:
        """Performs a direct attack against an enemy target."""
        return target.take_damage(self.attack)

    def gain_xp(self, points: int):
        """Adds experience points and handles level ups."""
        self.xp += points
        print(f"✨ {self.name} gained {points} XP.")
        while self.xp >= self.xp_next_level:
            self.level_up()

    def level_up(self):
        """Increases base stats and completely restores health."""
        self.xp -= self.xp_next_level
        self.level += 1
        self.xp_next_level = int(self.xp_next_level * 1.5)
        self.max_hp += 15
        self.current_hp = self.max_hp
        self.attack += 4
        self.defense += 3
        print(f"🆙 {self.name} reached Level {self.level}! Attributes increased.")


class Enemy(Entity):
    """Mutant creatures and stage bosses."""
    def __init__(self, name: str, max_hp: int, attack: int, defense: int, speed: int, xp_reward: int):
        super().__init__(name, max_hp, attack, defense, speed)
        self.xp_reward = xp_reward
        self.loot = random.choice(ITEM_CATALOG)

    def attack_target(self, target) -> int:
        """Attacks a specific target."""
        return target.take_damage(self.attack)

    def drop_loot(self):
        """60% chance to drop an item upon defeat."""
        if random.random() < 0.60:
            return self.loot
        return None

    def auto_attack(self, heroes: list) -> tuple:
        """AI picks a random living hero to attack."""
        alive_heroes = [h for h in heroes if h.is_alive()]
        if not alive_heroes:
            return None, 0
        target = random.choice(alive_heroes)
        damage = self.attack_target(target)
        return target, damage


def generate_procedural_enemy(stage: int) -> Enemy:
    """Procedurally scales mutant attributes depending on the current altitude/stage."""
    names_by_stage = {
        1: ["Armored Mud Rat", "Thorny Mutant Spider"],
        2: ["Blind Frost Bat", "Glacial Scaled Wolf"],
        3: ["Spore Chimera", "Primis Toxic Woven Golem"]
    }
    name = random.choice(names_by_stage[stage])
    multiplier = 1 + ((stage - 1) * 0.45)
    
    max_hp = int(random.randint(40, 60) * multiplier)
    attack = int(random.randint(14, 20) * multiplier)
    defense = int(random.randint(4, 8) * multiplier)
    speed = random.randint(9, 16)
    xp_reward = int(45 * multiplier)

    return Enemy(name, max_hp, attack, defense, speed, xp_reward)
