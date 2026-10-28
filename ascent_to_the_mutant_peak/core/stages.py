"""
Stages Module.
Models the altitude zones, environmental riddles, and linked progression of Mutant Peak.
"""
import random
from core.data_structures import StageLinkedList
from core.entities import generate_procedural_enemy, generate_boss
from core.combat import Combat


class Stage:
    """Represents an altitude zone with narrative lore, environmental hazards, and enemies."""
    def __init__(self, number: int, name: str, altitude: str, lore: str, riddle_data: dict):
        self.number = number
        self.name = name
        self.altitude = altitude
        self.lore = lore
        self.riddle_data = riddle_data

    def run_stage_event(self, heroes: list, input_func=input) -> bool:
        """Executes the stage lore, riddle challenge, the mutant ambush and the stage boss."""
        print(f"\n{'='*55}")
        print(f"📍 ENTERING STAGE {self.number}: {self.name.upper()} ({self.altitude})")
        print(f"{'='*55}")
        print(f"📖 Lore: {self.lore}\n")

        passed_riddle = self._ask_riddle(input_func)
        if passed_riddle:
            print("\n💡 Correct assessment! The squad traverses safely and secures high ground.")
            reward_xp = self.riddle_data.get("reward_xp", 0)
            if reward_xp > 0:
                print(f"🎓 The squad learns from the challenge (+{reward_xp} XP each).")
                for hero in heroes:
                    if hero.is_alive():
                        hero.gain_xp(reward_xp)
        else:
            print("\n⚠️ Dangerous mistake! Exposure to mutagenic radiation damages the squad.")
            for hero in heroes:
                if hero.is_alive():
                    damage_taken = hero.take_damage(8, ignore_defense=True)
                    print(f"   - {hero.name} suffers {damage_taken} environmental damage.")

        enemy_count = random.randint(1, 2)
        enemies = [generate_procedural_enemy(self.number) for _ in range(enemy_count)]
        print(f"\n🚨 AMBUSH! {len(enemies)} mutant threats emerge from the fog:")
        for enemy in enemies:
            print(f"   - {enemy.name} (HP: {enemy.max_hp}, ATK: {enemy.attack}, DEF: {enemy.defense})")

        combat_encounter = Combat(heroes, enemies, input_func=input_func)
        if not combat_encounter.start_combat():
            return False

        boss = generate_boss(self.number)
        print(f"\n👹 STAGE BOSS: {boss.name} blocks the path!")
        print(f"   - HP: {boss.max_hp}, ATK: {boss.attack}, DEF: {boss.defense}")
        boss_encounter = Combat(heroes, [boss], input_func=input_func)
        return boss_encounter.start_combat()

    def _ask_riddle(self, input_func) -> bool:
        """Prompts the environmental choice or tactical puzzle."""
        q = self.riddle_data
        print(f"🧩 Tactical Challenge: {q['question']}")
        for idx, option in enumerate(q["options"], start=1):
            print(f"   {idx}. {option}")

        while True:
            choice = input_func("Select your action (number): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(q["options"]):
                return int(choice) == q["correct"]
            print(f"Please select a number between 1 and {len(q['options'])}.")

    def __str__(self):
        return f"Stage {self.number}: {self.name} [{self.altitude}]"


def build_mountain_ascent() -> StageLinkedList:
    """Creates and links the 3 stages of Mutant Peak using StageLinkedList."""
    mountain = StageLinkedList()

    stage_1 = Stage(
        number=1,
        name="The Muddy Foothills",
        altitude="1,500m",
        lore="The mountain base is choked with runoff from failed Primis experiment drains. Thick sludge conceals mutated vermin.",
        riddle_data={
            "question": "A river of corrosive bio-sludge blocks the trail. How does the squad proceed?",
            "options": [
                "Sprint directly through the center before the boots melt.",
                "Scout the banks for petrified tree trunks to construct a temporary bridge.",
                "Wait for nightfall expecting the acidic current to freeze."
            ],
            "correct": 2,
            "reward_xp": 40
        }
    )

    stage_2 = Stage(
        number=2,
        name="The Frozen Ridge",
        altitude="3,800m",
        lore="Violent sub-zero blizzards howl along razor-sharp cliffs. Abandoned weather pods shelter dormant abominations.",
        riddle_data={
            "question": "A sudden drop in barometric pressure freezes air filters. How do you maintain respirators?",
            "options": [
                "Ignite surplus rocket fuel inside a sealed ice cave.",
                "Anchor inside a leeward crevasse and apply thermal heat pads to intake valves.",
                "Strip off insulated armor to decrease ascent weight and move faster."
            ],
            "correct": 2,
            "reward_xp": 60
        }
    )

    stage_3 = Stage(
        number=3,
        name="The Mutant Peak Summit",
        altitude="5,600m",
        lore="The summit crater hosts the central Primis lab. Pulsing violet atmospheric spires illuminate apex biological specimens.",
        riddle_data={
            "question": "The blast doors into the central laboratory require calibrating the resonance array:",
            "options": [
                "Standard 440 Hz acoustic wave.",
                "Zero oscillation (absolute vacuum seal).",
                "High harmonic resonance attuned to mutagenic crystal vibration frequencies."
            ],
            "correct": 3,
            "reward_xp": 80
        }
    )

    mountain.append(stage_1)
    mountain.append(stage_2)
    mountain.append(stage_3)

    return mountain