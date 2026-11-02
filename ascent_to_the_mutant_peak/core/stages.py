"""
Stages Module.
Models the altitude zones, environmental riddles, and linked progression of Mutant Peak.
"""
import random
from core.data_structures import StageLinkedList
from core.entities import generate_procedural_enemy, generate_boss
from core.combat import Combat


class Stage:
    """Representa una zona de altitud que incluye trasfondo narrativo, peligros ambientales y enemigos."""
    def __init__(self, number: int, name: str, altitude: str, lore: str, riddle_data: dict):
        self.number = number
        self.name = name
        self.altitude = altitude
        self.lore = lore
        self.riddle_data = riddle_data

    def run_stage_event(self, heroes: list, input_func=input) -> bool:
        """Ejecuta la narrativa del escenario, el desafío de acertijos, la emboscada de mutantes y el jefe de fase."""
        print(f"\n{'='*55}")
        print(f"📍 ENTRANDO EN LA ETAPA {self.number}: {self.name.upper()} ({self.altitude})")
        print(f"{'='*55}")
        print(f"📖 Lore: {self.lore}\n")

        passed_riddle = self._ask_riddle(input_func)
        if passed_riddle:
            print("\n💡 ¡Evaluación correcta! El escuadrón avanza sin contratiempos y toma una posición elevada.")
            reward_xp = self.riddle_data.get("reward_xp", 0)
            if reward_xp > 0:
                print(f"🎓 El equipo aprende del desafío (+{reward_xp} PE cada uno).")
                for hero in heroes:
                    if hero.is_alive():
                        hero.gain_xp(reward_xp)
        else:
            print("\n⚠️ ¡Error peligroso! La exposición a la radiación mutagénica daña al escuadrón.")
            for hero in heroes:
                if hero.is_alive():
                    damage_taken = hero.take_damage(8, ignore_defense=True)
                    print(f"   - {hero.name} sufre {damage_taken} daño ambiental.")

        enemy_count = random.randint(1, 2)
        enemies = [generate_procedural_enemy(self.number) for _ in range(enemy_count)]
        print(f"\n🚨 ¡EMBOSCADA!  {len(enemies)} amenazas mutantes surgen de la niebla:")
        for enemy in enemies:
            print(f"   - {enemy.name} (HP: {enemy.max_hp}, ATK: {enemy.attack}, DEF: {enemy.defense})")

        combat_encounter = Combat(heroes, enemies, input_func=input_func)
        if not combat_encounter.start_combat():
            return False

        boss = generate_boss(self.number)
        print(f"\n👹 JEFE DE NIVEL: {boss.name} bloquea el camino!")
        print(f"   - HP: {boss.max_hp}, ATK: {boss.attack}, DEF: {boss.defense}")
        boss_encounter = Combat(heroes, [boss], input_func=input_func)
        return boss_encounter.start_combat()

    def _ask_riddle(self, input_func) -> bool:
        """Da pie a una elección basada en el entorno o a un rompecabezas táctico."""
        q = self.riddle_data
        print(f"🧩 Desafío Táctico: {q['question']}")
        for idx, option in enumerate(q["options"], start=1):
            print(f"   {idx}. {option}")

        while True:
            choice = input_func("Select your action (number): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(q["options"]):
                return int(choice) == q["correct"]
            print(f"Por favor, selecciona un número entre 1 y {len(q['options'])}.")

    def __str__(self):
        return f"Stage {self.number}: {self.name} [{self.altitude}]"


def build_mountain_ascent() -> StageLinkedList:
    """Crea y vincula las 3 etapas de Mutant Peak usando StageLinkedList."""
    mountain = StageLinkedList()

    stage_1 = Stage(
        number=1,
        name="La Falda del Bosque Cenizo",
        altitude="1,500m",
        lore="La base de la montaña está anegada por el drenaje de experimentos fallidos de Primis. Un lodo espeso...",
        riddle_data={
            "question": "Un río de bio-residuos corrosivos bloquea el camino. ¿Cómo procede el escuadrón?",
            "options": [
                "Corre directamente a través del centro antes de que los botines se derritan.",
                "Explora las orillas en busca de troncos de árboles petrificados para construir un puente temporal.",
                "Espera a que caiga la noche, esperando que la corriente ácida se congele."
            ],
            "correct": 2,
            "reward_xp": 40
        }
    )

    stage_2 = Stage(
        number=2,
        name="La Cresta Helada",
        altitude="3,800m",
        lore="Violentas ventiscas a temperaturas bajo cero aúllan a lo largo de acantilados afilados como cuchillas. Módulos meteorológicos abandonados albergan abominaciones en estado latente.",
        riddle_data={
            "question": "Un descenso súbito en la presión barométrica congela los filtros de aire. ¿Cómo mantienes los respiradores?",
            "options": [
                "Enciende el combustible de cohete sobrante dentro de una cueva de hielo sellada.",
                "Ancla dentro de una grieta protegida del viento y aplica almohadillas térmicas a las válvulas de intake.",
                "Quita la armadura aislante para disminuir el peso de ascensión y moverse más rápido."
            ],
            "correct": 2,
            "reward_xp": 60
        }
    )

    stage_3 = Stage(
        number=3,
        name="La Cumbre del Pico Mutante",
        altitude="5,600m",
        lore="El cráter de la cima alberga el laboratorio central Primis. Unas agujas atmosféricas que emiten pulsos de color violeta iluminan especímenes biológicos de primer orden.",
        riddle_data={
            "question": "Las puertas blindadas que dan al laboratorio central requieren la calibración de la matriz de resonancia:",
            "options": [
                "Onda acústica estándar de 440 Hz.",
                "Cero oscilación (sellado al vacío absoluto).",
                "Resonancia armónica de alto orden, sintonizada con las frecuencias vibratorias de cristales mutagénicos."
            ],
            "correct": 3,
            "reward_xp": 80
        }
    )

    mountain.append(stage_1)
    mountain.append(stage_2)
    mountain.append(stage_3)

    return mountain
