"""
Módulo principal de felicidad
"""

import random
import time
from datetime import datetime


class Happiness:
    def __init__(self):
        self.level = random.randint(60, 100)
        self.affirmations = [
            "¡Eres un desarrollador increíble!",
            "Tu código está funcionando mejor de lo que crees",
            "Cada bug que resuelves te hace más fuerte",
            "Mereces ese café extra ☕",
            "Tu pull request será aprobado pronto",
            "Los tests pasarán... eventualmente",
            "Stack Overflow cree en ti",
            "Compilaste sin errores en el primer intento (bueno, casi)",
            "Tu código legacy del año pasado no está tan mal",
            "¡Hoy es un gran día para programar!",
        ]

        self.tips = [
            "Toma un descanso cada hora",
            "Hidrata tu cuerpo (y tu mente)",
            "Celebra los pequeños logros",
            "Pide ayuda cuando la necesites",
            "Comenta tu código (tu yo del futuro te lo agradecerá)",
            "Haz ejercicio, aunque sea caminar 10 minutos",
            "Duerme bien, los bugs no se van a ningún lado",
            "Desconecta después del trabajo",
            "Aprende algo nuevo hoy",
            "Comparte tu conocimiento con otros",
        ]

        self.jokes = [
            "¿Por qué los programadores prefieren el modo oscuro? Porque la luz atrae bugs 🐛",
            "No hay lugar como 127.0.0.1 🏠",
            "Hay 10 tipos de personas: las que entienden binario y las que no",
            "¿Cuántos programadores necesitas para cambiar un foco? Ninguno, es un problema de hardware",
            "JAVA: Just Another Valuable Acronym ☕",
            "Funciona en mi máquina ¯\\_(ツ)_/¯",
            "99 bugs en el código, 99 bugs... Tomas uno, lo corriges... 127 bugs en el código",
        ]

        self.christmas_messages = [
            "🎄 Que tu código compile en el primer intento esta Navidad",
            "😎 Jesus está revisando tu código... ¡y le gusta!",
            "⭐ Que tus commits sean mergeados sin conflictos",
            "🎁 El mejor regalo: un proyecto sin bugs",
            "❄️ Que esta Navidad sea tan estable como tu producción",
            "🔔 Feliz Navidad, que tus deploys sean exitosos",
            "🎄 Que encuentres más features que bugs bajo el árbol",
            "✨ Esta Navidad, que tu código sea tan limpio como la nieve",
        ]

    def get_level(self):
        """Obtiene tu nivel actual de felicidad"""
        print(f"\n{'='*50}")
        print(f"💖 NIVEL DE FELICIDAD: {self.level}%")
        print(f"{'='*50}")

        if self.level >= 80:
            print("Estado: ¡RADIANTE! ✨")
            print("Emoji del día: 😄")
        elif self.level >= 60:
            print("Estado: Bastante bien 🙂")
            print("Emoji del día: 😊")
        elif self.level >= 40:
            print("Estado: Podría estar mejor 😐")
            print("Emoji del día: 😕")
        else:
            print("Estado: Necesitas un boost 😔")
            print("Emoji del día: 😢")

        self._draw_happiness_bar()

    def _draw_happiness_bar(self):
        """Dibuja una barra de progreso de felicidad"""
        bar_length = 30
        filled = int((self.level / 100) * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"\n[{bar}] {self.level}%\n")

    def boost(self, amount=10):
        """Aumenta tu nivel de felicidad"""
        self.level = min(100, self.level + amount)
        print(f"\n✨ ¡Felicidad aumentada! +{amount}%")
        self._draw_happiness_bar()

    def affirmation(self):
        """Muestra una afirmación positiva"""
        msg = random.choice(self.affirmations)
        print(f"\n💭 Afirmación del momento:")
        print(f"   '{msg}'")
        self.boost(5)

    def daily_tip(self):
        """Muestra un consejo del día"""
        tip = random.choice(self.tips)
        print(f"\n💡 Consejo del día:")
        print(f"   {tip}")
        self.boost(3)

    def joke(self):
        """Cuenta un chiste de programador"""
        joke = random.choice(self.jokes)
        print(f"\n😄 Chiste del día:")
        print(f"   {joke}")
        self.boost(8)

    def meditate(self):
        """Mini sesión de meditación"""
        print("\n🧘 Iniciando meditación de 10 segundos...")
        print("   Respira profundo...")
        for i in range(3):
            time.sleep(1)
            print("   " + "." * (i + 1))
        print("   Exhala lentamente...")
        for i in range(3):
            time.sleep(1)
            print("   " + "." * (i + 1))
        print("\n✨ ¡Meditación completada!")
        self.boost(15)

    def gratitude(self):
        """Ejercicio de gratitud"""
        things = [
            "el IDE que funciona",
            "mi internet rápido",
            "una comunidad de desarrolladores solidaria",
            "la documentación bien escrita",
            "ese mentor que me ayudó",
            "un café ☕ delicioso",
            "git (para deshacer errores)",
            "mi computadora que no se ha prendido fuego",
            "ese código que funcionó a la primera",
        ]
        print(f"\n🙏 Padre Celestial hoy te agradecemos por:")
        for i in range(3):
            print(f"   • {random.choice(things)}")
        self.boost(7)

    def ascii_art(self):
        """Muestra arte ASCII alegre"""
        arts = [
            """
    ╔═══════════════════╗
    ║   ¡ERES GENIAL!   ║
    ╚═══════════════════╝
            """,
            """
       ___
      /   \\
     | ^_^ |
      \\_V_/
       |||
      _|||_
            """,
            """
    ★ ･ﾟ･｡★･ﾟ･｡☆
      ¡Sigue así!
    ☆･ﾟ･｡★･ﾟ･｡★
            """,
        ]
        print(random.choice(arts))
        self.boost(5)

    def christmas(self):
        """Modo especial de Navidad 🎄"""
        print("\n" + "=" * 50)
        print("🎄✨ MODO NAVIDAD ACTIVADO ✨🎄")
        print("=" * 50)

        # Árbol de Navidad ASCII
        tree = """
            ⭐
           🎄🎄
          🎄🎄🎄
         🎄🎄🎄🎄
        🎄🎄🎄🎄🎄
       🎄🎄🎄🎄🎄🎄
            |||
            |||
        """
        print(tree)

        # Mensaje navideño
        msg = random.choice(self.christmas_messages)
        print(f"\n{msg}")

        # Regalitos de código
        print("\n🎁 Regalos bajo el árbol:")
        gifts = [
            "📦 Una función que funciona a la primera",
            "📦 Documentación clara y actualizada",
            "📦 Tests que pasan todos",
            "📦 Un refactor exitoso",
            "📦 Cero conflictos de merge",
        ]
        for gift in random.sample(gifts, 3):
            time.sleep(0.5)
            print(f"   {gift}")

        # Villancico en código
        print("\n🎵 Villancico del Programador:")
        print("   ♪ Noche de deploys, noche de paz ♪")
        print("   ♪ Todo funciona, sin bugs jamás ♪")
        print("   ♪ Brilla el server con estabilidad ♪")
        print("   ♪ Logs limpios sin error fatal ♪")
        print("   ♪ Duerme en paz, duerme en paz ♪")

        # Boost navideño extra
        print("\n😎 ¡Jesus te dio un boost navideño!")
        self.boost(25)

        print("\n🎄 ¡Felices fiestas y feliz código! 🎄\n")

    def full_checkup(self):
        """Checkup completo de felicidad"""
        print("\n" + "=" * 50)
        print("🏥 INICIANDO CHECKUP DE FELICIDAD")
        print("=" * 50)
        time.sleep(1)

        self.get_level()
        time.sleep(1)

        self.affirmation()
        time.sleep(1)

        self.daily_tip()
        time.sleep(1)

        self.joke()

        # Si es diciembre, añadir mensaje navideño
        if datetime.now().month == 12:
            time.sleep(1)
            print("\n🎄 ¡Es diciembre! Activando espíritu navideño...")
            time.sleep(1)
            msg = random.choice(self.christmas_messages)
            print(f"   {msg}")
            self.boost(5)

        print("\n" + "=" * 50)
        print("✅ CHECKUP COMPLETADO")
        print("=" * 50)
