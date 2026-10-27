from core import Hero
from core.stages import build_mountain_ascent

STORY_INTRO = """
En la cordillera septentrional se alza el Monte Colmillo. En su cima, la estación
'Apex' liberó por accidente el compuesto mutágeno Primis. Una niebla bioluminiscente
desciende hacia los valles y la fauna evoluciona en abominaciones hiperagresivas.

Si el reactor no es purificado en la cumbre antes de 72 horas, toda la vida humana
de la región desaparecerá. Tres supervivientes son la última esperanza.
"""


def create_squad() -> list:
    """Crea el escuadrón con las estadísticas base del documento de diseño."""
    return [
        Hero("Dra. Camila Brooks", "Chemist / Support", max_hp=80, attack=12, defense=8, speed=14),
        Hero("Sgt. Julian Gunner", "Defensive Tank", max_hp=150, attack=15, defense=20, speed=8),
        Hero("Kael", "Hunter / Assassin", max_hp=95, attack=25, defense=10, speed=18),
    ]


def show_main_menu() -> int:
    """Muestra el menú principal y devuelve la opción elegida (1 o 2)."""
    print("\n==================================")
    print("   ASCENSO AL PICO MUTANTE")
    print("==================================")
    print("1. Nueva partida")
    print("2. Salir")
    while True:
        choice = input("> ").strip()
        if choice in ("1", "2"):
            return int(choice)
        print("Por favor, ingrese 1 o 2.")


def show_squad(squad: list) -> None:
    print("\nTu escuadrón:")
    for hero in squad:
        print(f"  - {hero.name} ({hero.role}) | HP {hero.max_hp} | ATK {hero.attack} "
            f"| DEF {hero.defense} | VEL {hero.speed}")

def play_game() -> bool:
    """Recorre los tramos en orden. Devuelve True si el escuadrón llega a la cumbre."""
    print(STORY_INTRO)
    squad = create_squad()
    show_squad(squad)
    input("\nPresiona ENTER para comenzar el ascenso...")

    mountain = build_mountain_ascent()

    while True:
        stage = mountain.get_current_stage()
        survived = stage.run_stage_event(squad)

        if not survived:
            return False
        print(f"\n✅ Tramo {stage.number} superado: {stage.name}")

        if not mountain.advance():
            return True

        input("\nPresiona ENTER para continuar el ascenso...")


def main() -> None:
    try:
        while True:
            if show_main_menu() == 2:
                print("¡Hasta la próxima, superviviente!")
                break

            if play_game():
                print("\n🏔️ ¡El reactor fue purificado! La niebla se disipa y los valles se salvan.")
            else:
                print("\n☠️ GAME OVER")

            again = input("\n¿Volver al menú principal? (s/n): ").strip().lower()
            if again != "s":
                print("¡Gracias por jugar!")
                break
    except (KeyboardInterrupt, EOFError):
        print("\n\nJuego interrumpido. ¡Hasta luego!")


if __name__ == "__main__":
    main()