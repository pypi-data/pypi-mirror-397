"""
Interfaz de línea de comandos para felicidad
"""

import time
from datetime import datetime
from .core import Happiness


def install_animation():
    """Simula la instalación del paquete"""
    print("\n🎉 Instalando felicidad...")
    time.sleep(1)
    steps = [
        "Descargando alegría del universo...",
        "Compilando sonrisas...",
        "Optimizando vibes positivos...",
        "Eliminando pensamientos negativos...",
        "¡Instalación completada! ✨",
    ]
    for step in steps:
        print(f"   {step}")
        time.sleep(0.5)
    print("\n💖 felicidad está listo para usar\n")


def main():
    """Función principal del CLI"""
    install_animation()
    h = Happiness()

    # Detectar si es época navideña
    is_christmas_season = datetime.now().month == 12

    while True:
        print("\n" + "=" * 50)
        print("🌟 MENÚ DE FELICIDAD")
        if is_christmas_season:
            print("🎄 ¡EDICIÓN NAVIDEÑA! 🎄")
        print("=" * 50)
        print("1. Ver nivel de felicidad")
        print("2. Recibir afirmación positiva")
        print("3. Consejo del día")
        print("4. Escuchar un chiste")
        print("5. Meditar (10 segundos)")
        print("6. Ejercicio de gratitud")
        print("7. Ver arte ASCII")
        print("8. Checkup completo")
        print("9. Boost manual (+10%)")
        if is_christmas_season:
            print("🎄. Modo Navidad especial")
        print("0. Salir")
        print("=" * 50)

        choice = input("\n👉 Elige una opción: ").strip()

        if choice == "1":
            h.get_level()
        elif choice == "2":
            h.affirmation()
        elif choice == "3":
            h.daily_tip()
        elif choice == "4":
            h.joke()
        elif choice == "5":
            h.meditate()
        elif choice == "6":
            h.gratitude()
        elif choice == "7":
            h.ascii_art()
        elif choice == "8":
            h.full_checkup()
        elif choice == "9":
            h.boost(10)
        elif choice.lower() in ["🎄", "navidad", "christmas"] and is_christmas_season:
            h.christmas()
        elif choice == "0":
            print("\n💖 ¡Que tengas un día feliz! Vuelve pronto.")
            if is_christmas_season:
                print("🎄 ¡Y felices fiestas! 🎄")
            print(f"Nivel final de felicidad: {h.level}%\n")
            break
        else:
            print("\n❌ Opción no válida. Intenta de nuevo.")

        input("\nPresiona Enter para continuar...")


if __name__ == "__main__":
    main()
