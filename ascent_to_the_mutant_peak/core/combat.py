"""
Combat Module.
Implements the Combat system using TurnQueue (FIFO) and handling
actions for heroes and procedural enemies.
"""
from core.data_structures import TurnQueue


class Combat:
    """Manages the turn-based combat loop between heroes and enemies."""
    def __init__(self, heroes: list, enemies: list, input_func=input):
        self.heroes = heroes
        self.enemies = enemies
        self.turn_queue = TurnQueue()
        self.round_number = 0
        self.input_func = input_func
        self.extra_defense = {}

    def start_combat(self) -> bool:
        """Runs the combat loop. Returns True if heroes win, False if defeated."""
        print("\n==================================")
        print("       COMIENZA EL COMBATE!")
        print("==================================")

        result = "continue"
        while result == "continue":
            self.execute_round()
            result = self.check_combat_status()

        self._clear_all_defenses()

        if result == "victory":
            self._distribute_rewards()
            return True

        print("\n💀 La expedición ha fallado... La niebla mutante consume la montaña.")
        return False

    def execute_round(self):
        """Executes a round: alive entities act in order of speed."""
        self.round_number += 1
        print(f"\n########### RONDA {self.round_number} ###########")
        self._display_status()

        active_units = [u for u in self.heroes + self.enemies if u.is_alive()]
        self.turn_queue.sort_by_speed(active_units)

        while not self.turn_queue.is_empty():
            if self.check_combat_status() != "continue":
                break

            entity = self.turn_queue.dequeue()
            if not entity or not entity.is_alive():
                continue

            if entity in self.heroes:
                self.process_hero_turn(entity)
            else:
                self.process_enemy_turn(entity)

    def check_combat_status(self) -> str:
        """Determines if the encounter is still active, won, or lost."""
        if not self._get_alive(self.enemies):
            return "victory"
        if not self._get_alive(self.heroes):
            return "defeat"
        return "continue"

    def process_hero_turn(self, hero):
        """Allows the player to select actions for a hero."""
        self._remove_defense_bonus(hero)

        while True:
            print(f"\n--- Giro of {hero.name} (HP: {hero.current_hp}/{hero.max_hp}) ---")
            print("1. Ataque   2. Usar Item (Mochila)   3. Defender")
            choice = self._prompt_number("Choose action: ", 1, 3)

            if choice == 1:
                target = self._select_target(self._get_alive(self.enemies))
                damage = hero.attack_target(target)
                print(f"⚔️ {hero.name} ataques {target.name} por {damage} daño.")
                self._notify_if_slain(target)
                return

            elif choice == 2:
                if hero.backpack.is_empty():
                    print("🎒 La mochila está vacía.")
                    continue

                top_item = hero.backpack.pop()
                result_msg = top_item.apply(hero)
                print(f"✨ {hero.name} used {top_item.name}: {result_msg}")
                if not top_item.is_consumable:
                    hero.backpack.push(top_item)
                return

            elif choice == 3:
                bonus = max(2, hero.defense // 2)
                hero.defense += bonus
                self.extra_defense[hero] = bonus
                print(f"🛡️ {hero.name} toma una postura defensiva (+{bonus} DEF hasta el último turno).")
                return

    def process_enemy_turn(self, enemy):
        """Processes the AI attack on a living hero."""
        self._remove_defense_bonus(enemy)
        target, damage = enemy.auto_attack(self.heroes)
        if target:
            print(f"💥 {enemy.name} golpea a {target.name} causando {damage} daño.")
            self._notify_if_slain(target)

    def _distribute_rewards(self):
        """Grants experience points and drops loot for surviving heroes."""
        print("\n🏆 *** VICTORIA! ***")
        survivors = self._get_alive(self.heroes)
        total_xp = sum(e.xp_reward for e in self.enemies)
        print(f"Todos los héroes sobrevivientes ganan {total_xp} XP.")

        for hero in survivors:
            hero.gain_xp(total_xp)

        for enemy in self.enemies:
            item_drop = enemy.drop_loot()
            if item_drop and survivors:
                receiver = survivors[0]
                receiver.backpack.push(item_drop)
                print(f"🎁 {receiver.name} ha obtenido: {item_drop.name} (Añadido a la mochila).")

    @staticmethod
    def _get_alive(entity_list: list) -> list:
        return [e for e in entity_list if e.is_alive()]

    def _notify_if_slain(self, target):
        if not target.is_alive():
            print(f"💀 >> {target.name} ha caído!")

    def _remove_defense_bonus(self, entity):
        bonus = self.extra_defense.pop(entity, 0)
        if bonus > 0:
            entity.defense -= bonus

    def _clear_all_defenses(self):
        for entity, bonus in list(self.extra_defense.items()):
            entity.defense -= bonus
        self.extra_defense.clear()

    def _display_status(self):
        print("\nHÉROES:")
        for h in self.heroes:
            print(f"  {self._health_bar(h)}")
        print("ENEMIGOS:")
        for e in self.enemies:
            print(f"  {self._health_bar(e)}")

    @staticmethod
    def _health_bar(entity) -> str:
        ratio = max(0.0, min(1.0, entity.current_hp / entity.max_hp))
        filled = int(10 * ratio)
        empty = 10 - filled
        bar = "█" * filled + "░" * empty
        return f"{entity.name:<25} [{bar}] {entity.current_hp}/{entity.max_hp} HP"

    def _prompt_number(self, prompt: str, min_val: int, max_val: int) -> int:
        while True:
            raw = self.input_func(prompt).strip()
            if raw.isdigit():
                val = int(raw)
                if min_val <= val <= max_val:
                    return val
            print(f"Por favor, ingrese un número entre {min_val} y {max_val}.")

    def _select_target(self, targets: list):
        if len(targets) == 1:
            return targets[0]
        print("Seleccionar objetivo:")
        for idx, target in enumerate(targets, start=1):
            print(f"{idx}. {target.name} ({target.current_hp}/{target.max_hp} HP)")
        choice = self._prompt_number("> ", 1, len(targets))
        return targets[choice - 1]

