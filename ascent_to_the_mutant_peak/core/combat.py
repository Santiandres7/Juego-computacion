"""
Combat Module.
Implements the Combat system using TurnQueue (FIFO) and handling
actions for heroes and procedural enemies.
"""
from core.data_structures import TurnQueue

DEFEND_BONUS = 50


class Combat:
    """Manages the turn-based combat loop between heroes and enemies."""
    def __init__(self, heroes: list, enemies: list, input_func=input):
        self.heroes = heroes
        self.enemies = enemies
        self.turn_queue = TurnQueue()
        self.round_number = 0
        self.input_func = input_func

    def start_combat(self) -> bool:
        """Runs the combat loop. Returns True if heroes win, False if defeated."""
        print("\n==================================")
        print("       COMIENZA EL COMBATE!")
        print("==================================")

        result = "continue"
        while result == "continue":
            self.execute_round()
            result = self.check_combat_status()

        self._clear_all_statuses()

        if result == "victory":
            self._distribute_rewards()
            return True

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
        messages, can_act = hero.start_turn()
        self._print_all(messages)
        if not can_act:
            return

        while True:
            print(f"\n--- Turno de {hero.name} (HP: {hero.current_hp}/{hero.max_hp} | "
                f"Energía: {hero.current_energy}/{hero.max_energy}) ---")
            print("1. Ataque (+energía)   2. Habilidad   3. Usar Item (Mochila)   4. Defender")
            choice = self._prompt_number("Elige una acción: ", 1, 4)

            if choice == 1:
                target = self._select_target(self._get_alive(self.enemies))
                damage = hero.attack_target(target)
                crit_tag = " ¡CRÍTICO!" if hero.last_attack_was_crit else ""
                print(f"⚔️ {hero.name} ataca a {target.name} por {damage} daño.{crit_tag}")
                self._notify_if_slain(target)
                return

            elif choice == 2:
                if self._hero_use_skill(hero):
                    return
                continue

            elif choice == 3:
                result = hero.use_backpack_item()
                if result is None:
                    print("🎒 La mochila está vacía.")
                    continue
                item, result_msg = result
                print(f"✨ {hero.name} usó {item.name}: {result_msg}")
                if not item.is_consumable:
                    print(f"🔧 {item.name} queda equipado de forma permanente.")
                return

            elif choice == 4:
                hero.add_status("guard", 1, DEFEND_BONUS)
                print(f"🛡️ {hero.name} toma una postura defensiva (+{DEFEND_BONUS} DEF hasta su próximo turno).")
                return

    def _hero_use_skill(self, hero) -> bool:
        available = [s for s in hero.skills if s.unlock_level <= hero.level and not s.is_passive]
        if not available:
            print("No tienes habilidades desbloqueadas.")
            return False

        print("\nHabilidades:")
        for idx, skill in enumerate(available, start=1):
            print(f"{idx}. {skill.name} (Energía: {skill.energy_cost}) - {skill.description}")
        print("0. Volver")
        choice = self._prompt_number("> ", 0, len(available))
        if choice == 0:
            return False

        skill = available[choice - 1]
        if hero.current_energy < skill.energy_cost:
            print("⚡ No tienes suficiente energía.")
            return False

        target = None
        if skill.target_type == "enemy":
            target = self._select_target(self._get_alive(self.enemies))

        hero.spend_energy(skill.energy_cost)
        self._print_all(skill.apply(hero, target, self.heroes))
        if target:
            self._notify_if_slain(target)
        return True

    def process_enemy_turn(self, enemy):
        """Processes the AI action of an enemy (normal attack or boss special)."""
        messages, can_act = enemy.start_turn()
        self._print_all(messages)
        if not enemy.is_alive():
            print(f"💀 >> {enemy.name} ha caído!")
            return
        if not can_act:
            return

        alive_before = self._get_alive(self.heroes)
        self._print_all(enemy.take_turn(self.heroes))
        for hero in alive_before:
            self._notify_if_slain(hero)

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

    def _clear_all_statuses(self):
        for entity in self.heroes + self.enemies:
            entity.clear_statuses()

    @staticmethod
    def _print_all(messages: list):
        for message in messages:
            print(message)

    @staticmethod
    def _status_tags(entity) -> str:
        names = {"stun": "Inmovilizado", "dot": "Ácido", "guard": "Defendiendo",
                "defense_up": "DEF+", "defense_down": "DEF-", "taunt": "Provocación"}
        tags = [names[s] for s in entity.statuses if s in names]
        return f" [{', '.join(tags)}]" if tags else ""

    def _display_status(self):
        print("\nHÉROES:")
        for h in self.heroes:
            print(f"  {self._health_bar(h)}  ⚡{h.current_energy}/{h.max_energy}{self._status_tags(h)}")
        print("ENEMIGOS:")
        for e in self.enemies:
            print(f"  {self._health_bar(e)}{self._status_tags(e)}")

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