from core import create_squad, build_mountain_ascent, save_game_state, load_game_state

STORY_INTRO = """
En la cordillera septentrional se alza el Monte Colmillo. En su cima, la estación
'Apex' liberó por accidente el compuesto mutágeno Primis. Una niebla bioluminiscente
desciende hacia los valles y la fauna evoluciona en abominaciones hiperagresivas.

Si el reactor no es purificado en la cumbre antes de 72 horas, toda la vida humana
de la región desaparecerá. Tres supervivientes son la última esperanza.
"""


def show_main_menu() -> int:
    print("\n==================================")
    print("   ASCENSO AL PICO MUTANTE")
    print("==================================")
    print("1. Nueva partida")
    print("2. Cargar partida")
    print("3. Salir")
    while True:
        choice = input("> ").strip()
        if choice in ("1", "2", "3"):
            return int(choice)
        print("Por favor, ingrese 1, 2 o 3.")


def show_squad(squad: list) -> None:
    print("\nTu escuadrón:")
    for hero in squad:
        print(f"  - {hero.name} ({hero.role}) | HP {hero.max_hp} | ATK {hero.attack} "
              f"| DEF {hero.defense} | VEL {hero.speed} | ENERGÍA {hero.max_energy}")
        for skill in hero.skills:
            print(f"      · {skill.name} (nivel {skill.unlock_level}): {skill.description}")


def rest_squad(squad: list) -> None:
    print("\n🏕️ El escuadrón acampa y recupera fuerzas...")
    for hero in squad:
        was_dead = not hero.is_alive()
        hero.rest()
        if was_dead:
            print(f"   - {hero.name} vuelve a levantarse con {hero.current_hp} HP.")
        else:
            print(f"   - {hero.name} recupera fuerzas ({hero.current_hp}/{hero.max_hp} HP).")


def play_game(load_save: bool = False) -> str:
    mountain = build_mountain_ascent()

    if load_save:
        save_data = load_game_state()
        if not save_data:
            print("\n⚠️ No se encontró ninguna partida guardada. Iniciando nueva expedición...")
            squad = create_squad()
        else:
            print("\n📂 Cargando escuadrón y progreso...")
            squad = create_squad()
            # Restaurar vida de los héroes según el archivo guardado
            saved_heroes = {h["name"]: h for h in save_data.get("squad", [])}
            for hero in squad:
                if hero.name in saved_heroes:
                    hero.current_hp = saved_heroes[hero.name].get("current_hp", hero.max_hp)

            # Avanzar la montaña hasta la etapa guardada
            target_stage = save_data.get("current_stage_number", 1)
            while mountain.get_current_stage() and mountain.get_current_stage().number < target_stage:
                if not mountain.advance():
                    break
    else:
        print(STORY_INTRO)
        squad = create_squad()
        show_squad(squad)
        input("\nPresiona ENTER para comenzar el ascenso...")

    while True:
        stage = mountain.get_current_stage()
        survived = stage.run_stage_event(squad)

        if not survived:
            return "defeat"

        print(f"\n✅ Tramo {stage.number} superado: {stage.name}")

        if not mountain.advance():
            return "victory"

        rest_squad(squad)

        # Menú interactivo en el campamento
        camp_exit = False
        while True:
            print("\n--- CAMPAMENTO BASE ---")
            print("1. Continuar el ascenso")
            print("2. Guardar partida")
            print("3. Guardar y volver al menú principal")

            choice = input("> ").strip()

            if choice == "1":
                break
            elif choice == "2":
                save_game_state(mountain, squad)
                print("✔ Partida guardada con éxito.")
            elif choice == "3":
                save_game_state(mountain, squad)
                print("✔ Partida guardada. Regresando al menú principal...")
                camp_exit = True
                break
            else:
                print("Por favor, selecciona 1, 2 o 3.")

        if camp_exit:
            return "menu"


def main() -> None:
    try:
        while True:
            choice = show_main_menu()
            if choice == 3:
                print("¡Hasta la próxima, superviviente!")
                break

            # Si eligió 2 pasa load_save=True, si eligió 1 pasa False
            result = play_game(load_save=(choice == 2))

            if result == "victory":
                print("\n🏔️ ¡El reactor fue purificado! La niebla se disipa y los valles se salvan.")
            elif result == "defeat":
                print("\n💀 La expedición ha fallado... La niebla mutante consume la montaña.")
                print("☠️ GAME OVER")
            elif result == "menu":
                continue

            again = input("\n¿Volver al menú principal? (s/n): ").strip().lower()
            if again != "s":
                print("¡Gracias por jugar!")
                break
    except (KeyboardInterrupt, EOFError):
        print("\n\nJuego interrumpido. ¡Hasta luego!")


if __name__ == "__main__":
    main()

