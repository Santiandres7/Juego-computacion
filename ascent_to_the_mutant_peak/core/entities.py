"""
Entities Module.
Defines the abstract base class Entity, Hero classes, Skills, Enemy classes and Bosses.
"""
from abc import ABC, abstractmethod
import random
from core.items import get_random_loot
from core.data_structures import InventoryStack

ENERGY_ON_ATTACK = 5


class Entity(ABC):
    """Abstract base class for all living creatures in the game."""
    def __init__(self, name: str, max_hp: int, attack: int, defense: int, speed: int):
        self.name = name
        self.max_hp = max_hp
        self.current_hp = max_hp
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.statuses = {}

    def is_alive(self) -> bool:
        """Returns True if current HP is greater than 0."""
        return self.current_hp > 0

    @property
    def effective_defense(self) -> int:
        bonus = self.get_status_value("defense_up") + self.get_status_value("guard")
        penalty = self.get_status_value("defense_down")
        return max(0, self.defense + bonus - penalty)

    def take_damage(self, amount: int, ignore_defense: bool = False) -> int:
        if ignore_defense:
            real_damage = max(1, amount)
        else:
            real_damage = max(1, int(amount * 100 / (100 + self.effective_defense)))
        self.current_hp = max(0, self.current_hp - real_damage)
        return real_damage

    def heal(self, amount: int):
        """Restores HP without exceeding max HP."""
        self.current_hp = min(self.max_hp, self.current_hp + amount)

    def add_status(self, name: str, turns: int, value: int = 0):
        self.statuses[name] = {"turns": turns, "value": value}

    def has_status(self, name: str) -> bool:
        return name in self.statuses

    def get_status_value(self, name: str) -> int:
        return self.statuses[name]["value"] if name in self.statuses else 0

    def clear_statuses(self):
        self.statuses.clear()

    def tick_statuses(self) -> list:
        """Applies damage over time and lowers every status duration by 1. Returns messages."""
        messages = []
        if "dot" in self.statuses:
            damage = self.take_damage(self.get_status_value("dot"), ignore_defense=True)
            messages.append(f"☣️ {self.name} sufre {damage} de daño por ácido.")
        for name in list(self.statuses):
            self.statuses[name]["turns"] -= 1
            if self.statuses[name]["turns"] <= 0:
                del self.statuses[name]
        return messages

    def start_turn(self) -> tuple:
        """Call at the start of this entity's turn. Returns (messages, can_act)."""
        stunned = self.has_status("stun")
        messages = self.tick_statuses()
        if stunned and self.is_alive():
            messages.append(f"❄️ {self.name} está inmovilizado y pierde su turno.")
        return messages, (self.is_alive() and not stunned)

    @abstractmethod
    def attack_target(self, target):
        """Abstract method that must be implemented by subclasses."""
        pass


class Skill:
    """A hero ability. target_type: 'enemy', 'allies' or 'self'."""
    def __init__(self, name: str, energy_cost: int, power: int, effect: str,
                target_type: str, unlock_level: int = 1, description: str = "",
                is_passive: bool = False):
        self.name = name
        self.energy_cost = energy_cost
        self.power = power
        self.effect = effect
        self.target_type = target_type
        self.unlock_level = unlock_level
        self.description = description
        self.is_passive = is_passive

    def apply(self, user, target, allies: list) -> list:
        """Applies the skill and returns a list of messages to display."""
        if self.effect == "heal_all":
            for ally in allies:
                if ally.is_alive():
                    ally.heal(self.power)
            return [f"💚 {user.name} usa {self.name}: el escuadrón recupera {self.power} HP."]

        if self.effect == "acid":
            damage = target.take_damage(user.attack + self.power)
            target.add_status("defense_down", 3, 10)
            target.add_status("dot", 3, 6)
            return [f"🧪 {user.name} lanza {self.name} sobre {target.name}: {damage} daño, "
                    f"DEF reducida y ácido persistente."]

        if self.effect == "bulwark":
            user.add_status("defense_up", 3, 40)
            user.add_status("taunt", 3)
            return [f"🧊 {user.name} usa {self.name}: DEF muy aumentada y atrae los ataques enemigos."]

        if self.effect == "stun":
            damage = target.take_damage(user.attack + self.power)
            target.add_status("stun", 1)
            if target.has_status("stun"):
                return [f"🪓 {user.name} usa {self.name} sobre {target.name}: {damage} daño e inmoviliza 1 turno."]
            return [f"🪓 {user.name} usa {self.name} sobre {target.name}: {damage} daño, pero es inmune a la inmovilización."]

        if self.effect == "pierce":
            damage = target.take_damage(user.attack + self.power, ignore_defense=True)
            return [f"🎯 {user.name} usa {self.name} sobre {target.name}: {damage} daño ignorando la armadura."]

        return [f"{self.name} no tuvo efecto."]


class Hero(Entity):
    """Protagonist character with level progression, energy, skills and a LIFO backpack."""
    def __init__(self, name: str, role: str, max_hp: int, attack: int, defense: int, speed: int,
                max_energy: int = 100, crit_chance: float = 0.05, skills: list = None):
        super().__init__(name, max_hp, attack, defense, speed)
        self.role = role
        self.level = 1
        self.xp = 0
        self.xp_next_level = 100
        self.backpack = InventoryStack()
        self.equipped = []
        self.max_energy = max_energy
        self.current_energy = max_energy
        self.crit_chance = crit_chance
        self.skills = skills if skills else []
        self.last_attack_was_crit = False

    def attack_target(self, target) -> int:
        """Performs a direct attack against an enemy target."""
        self.last_attack_was_crit = random.random() < self.crit_chance
        base_damage = self.attack * 2 if self.last_attack_was_crit else self.attack
        self.restore_energy(ENERGY_ON_ATTACK)
        return target.take_damage(base_damage)

    def restore_energy(self, amount: int):
        self.current_energy = min(self.max_energy, self.current_energy + amount)

    def spend_energy(self, amount: int) -> bool:
        """Spends energy. Returns False (and spends nothing) if there isn't enough."""
        if self.current_energy < amount:
            return False
        self.current_energy -= amount
        return True

    def use_backpack_item(self):
        """Pops the top item and applies it. Returns (item, message) or None if empty."""
        item = self.backpack.pop()
        if item is None:
            return None
        message = item.apply(self)
        if not item.is_consumable:
            self.equipped.append(item)
        return item, message

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
        self.max_energy += 10
        self.current_energy = self.max_energy
        print(f"🆙 {self.name} reached Level {self.level}! Attributes increased.")
        for skill in self.skills:
            if skill.unlock_level == self.level:
                print(f"🔓 {self.name} desbloqueó: {skill.name}!")
                if skill.is_passive and skill.effect == "passive_crit":
                    self.crit_chance += skill.power / 100

    def rest(self, hp_fraction: float = 0.3, energy_fraction: float = 0.5):
        self.heal(max(1, int(self.max_hp * hp_fraction)))
        self.restore_energy(int(self.max_energy * energy_fraction))
        self.clear_statuses()


class Enemy(Entity):
    """Mutant creatures and stage bosses."""
    def __init__(self, name: str, max_hp: int, attack: int, defense: int, speed: int,
                xp_reward: int, drop_chance: float = 0.60):
        super().__init__(name, max_hp, attack, defense, speed)
        self.xp_reward = xp_reward
        self.loot = get_random_loot()
        self.drop_chance = drop_chance

    def attack_target(self, target) -> int:
        """Attacks a specific target."""
        return target.take_damage(self.attack)

    def drop_loot(self):
        """Chance (drop_chance) to drop an item upon defeat."""
        if random.random() < self.drop_chance:
            return self.loot
        return None

    def pick_target(self, heroes: list):
        alive_heroes = [h for h in heroes if h.is_alive()]
        if not alive_heroes:
            return None
        taunters = [h for h in alive_heroes if h.has_status("taunt")]
        return random.choice(taunters if taunters else alive_heroes)

    def auto_attack(self, heroes: list) -> tuple:
        """AI picks a living hero to attack (taunting heroes are prioritized)."""
        target = self.pick_target(heroes)
        if target is None:
            return None, 0
        damage = self.attack_target(target)
        return target, damage

    def take_turn(self, heroes: list) -> list:
        """Performs this enemy's action and returns messages to display."""
        target, damage = self.auto_attack(heroes)
        if target is None:
            return []
        return [f"💥 {self.name} golpea a {target.name} causando {damage} daño."]


class Boss(Enemy):
    def __init__(self, name: str, max_hp: int, attack: int, defense: int, speed: int,
                xp_reward: int, special: str, special_interval: int = 3,
                has_second_phase: bool = False):
        super().__init__(name, max_hp, attack, defense, speed, xp_reward, drop_chance=1.0)
        self.special = special
        self.special_interval = special_interval
        self.has_second_phase = has_second_phase
        self.phase = 1
        self.turn_count = 0

    def add_status(self, name: str, turns: int, value: int = 0):
        if name == "stun":
            return
        super().add_status(name, turns, value)

    def _check_phase_change(self) -> list:
        if self.has_second_phase and self.phase == 1 and self.current_hp <= self.max_hp // 2:
            self.phase = 2
            self.attack = int(self.attack * 1.6)
            self.defense = int(self.defense * 0.25)
            self.speed += 4
            self.special_interval = 2
            return [f"🔥 ¡{self.name} entra en FRENESÍ BIOLÓGICO! Su armadura se resquebraja y su furia aumenta."]
        return []

    def _special_attack(self, heroes: list) -> list:
        messages = []
        if self.special == "poison_cloud":
            messages.append(f"☠️ {self.name} libera una ráfaga de veneno en área!")
            for hero in heroes:
                if hero.is_alive():
                    damage = hero.take_damage(int(self.attack * 0.7))
                    messages.append(f"   - {hero.name} recibe {damage} de daño.")
        elif self.special == "pulse":
            messages.append(f"⚡ {self.name} emite un pulso de energía mutagénica en área!")
            for hero in heroes:
                if hero.is_alive():
                    damage = hero.take_damage(int(self.attack * 0.8))
                    messages.append(f"   - {hero.name} recibe {damage} de daño.")
        elif self.special == "freeze":
            target = self.pick_target(heroes)
            if target:
                target.add_status("stun", 1)
                damage = self.attack_target(target)
                messages.append(f"🥶 {self.name} congela a {target.name} (pierde su próximo turno) y le causa {damage} daño.")
        return messages

    def take_turn(self, heroes: list) -> list:
        self.turn_count += 1
        messages = self._check_phase_change()
        if self.turn_count % self.special_interval == 0:
            messages += self._special_attack(heroes)
        else:
            messages += super().take_turn(heroes)
        return messages

def generate_procedural_enemy(stage: int) -> Enemy:
    """Procedurally scales mutant attributes depending on the current altitude/stage."""
    names_by_stage = {
        1: ["Armored Mud Rat", "Thorny Mutant Spider"],
        2: ["Blind Frost Bat", "Glacial Scaled Wolf"],
        3: ["Spore Chimera", "Primis Toxic Woven Golem"]
    }
    if stage not in names_by_stage:
        raise ValueError(f"Invalid stage {stage}. Valid stages: {list(names_by_stage)}")

    name = random.choice(names_by_stage[stage])
    multiplier = 1 + ((stage - 1) * 0.45)

    max_hp = int(random.randint(40, 60) * multiplier)
    attack = int(random.randint(14, 20) * multiplier)
    defense = int(random.randint(4, 8) * multiplier)
    speed = random.randint(9, 16)
    xp_reward = int(45 * multiplier)

    return Enemy(name, max_hp, attack, defense, speed, xp_reward)


def generate_boss(stage: int) -> Boss:
    """Creates the boss of the given stage."""
    if stage == 1:
        return Boss("Spore Colossus", 300, 26, 12, 7, 120, special="poison_cloud")
    if stage == 2:
        return Boss("Frost Winged Matriarch", 500, 36, 16, 13, 180, special="freeze")
    if stage == 3:
        return Boss("Aberrant Core (Subject Zero)", 800, 34, 70, 5, 300,
                    special="pulse", has_second_phase=True)
    raise ValueError(f"Invalid boss stage {stage}. Valid stages: 1, 2, 3")

def create_squad() -> list:
    """Creates the three heroes with the base stats of the design document."""
    camila = Hero(
        "Dra. Camila Brooks", "Chemist / Support", 80, 12, 8, 14, max_energy=120,
        skills=[
            Skill("Catalyst Dance", 30, 25, "heal_all", "allies", 1, "Cura grupal"),
            Skill("Solvent Bomb", 35, 15, "acid", "enemy", 2, "Daño, baja la DEF enemiga y ácido persistente"),
        ])
    julian = Hero(
        "Sgt. Julian Gunner", "Defensive Tank", 150, 15, 20, 8, max_energy=70,
        skills=[
            Skill("Glacial Bulwark", 25, 0, "bulwark", "self", 1, "Sube mucho su DEF y atrae los ataques"),
            Skill("Ice Axe Immobilizer", 30, 5, "stun", "enemy", 2, "Daño e inmoviliza 1 turno"),
        ])
    kael = Hero(
        "Kael", "Hunter / Assassin", 95, 25, 10, 18, max_energy=90, crit_chance=0.15,
        skills=[
            Skill("Surgical Strike", 30, 20, "pierce", "enemy", 1, "Gran daño que ignora la armadura"),
            Skill("Hunter's Eye", 0, 15, "passive_crit", "self", 2, "Pasiva: +15% de probabilidad de crítico",
                is_passive=True),
        ])
    return [camila, julian, kael]