import pygame
import sys
# Importamos todo desde nuestro archivo de settings.
from settings import *
# Importamos las clases Jugador, Pared y Enemigo desde el archivo sprites.
from sprites import Jugador, Pared, Enemigo, EnemigoVertical, Item
import os

# Las constantes como ANCHO_PANTALLA, FPS, NEGRO, etc., ahora se importan
# desde el archivo settings.py

# --- Clase Juego ---
# Usaremos una clase para organizar todo el código de nuestro juego.
# Esto nos permite agrupar las variables y funciones relacionadas en un solo lugar.
class Juego:
    def __init__(self):
        """
        Constructor de la clase Juego.
        Aquí es donde inicializamos Pygame y configuramos la ventana del juego.
        """
        # Inicializa todos los módulos de Pygame. Es necesario hacerlo siempre al principio.
        pygame.init()
        # Inicializamos el módulo de sonido para la música.
        pygame.mixer.init()

        # Creamos la pantalla del juego con las dimensiones que definimos en settings.py
        self.pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))

        # Establecemos el título que aparecerá en la barra de la ventana.
        pygame.display.set_caption(TITULO)

        # Creamos un reloj para controlar los FPS.
        self.reloj = pygame.time.Clock()

        # --- Fuentes de Texto ---
        # Guardamos el nombre de una fuente para usarla más tarde.
        self.nombre_fuente = pygame.font.match_font('arial')
        # Estado actual del juego para manejar las diferentes pantallas.
        self.estado = 'inicio'
        # Índice del nivel actual.
        self.nivel_actual_idx = 0
        # Vidas restantes del jugador.
        self.vidas_jugador = VIDAS_JUGADOR
        self.tiempo_nivel = 90  # segundos
        self.tiempo_restante = self.tiempo_nivel
        self.mostrar_mensaje_nivel = False
        self.mensaje_nivel_timer = 0
        self.musica_cargada = False
        self.musica_actual = None
        
        # --- Sistema de Pausa ---
        self.pausado = False

    def reproducir_musica(self, tipo_musica=MUSICA_FONDO, tiempo_inicio=0):
        """
        Intenta cargar y reproducir la música especificada.
        """
        # Si ya hay música reproduciéndose, la paramos.
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        
        # Construimos la ruta completa al archivo de música.
        ruta_musica = os.path.join(os.path.dirname(__file__), CARPETA_ASSETS, tipo_musica)
        
        # Comprobamos si el archivo existe antes de intentar cargarlo.
        if os.path.exists(ruta_musica):
            try:
                pygame.mixer.music.load(ruta_musica)
                pygame.mixer.music.play(-1, start=tiempo_inicio)  # -1 significa que se repite infinitamente
                self.musica_actual = tipo_musica
                print(f"Música cargada exitosamente: {ruta_musica}")
            except Exception as e:
                print(f"Error al cargar la música {tipo_musica}: {e}")
        else:
            print(f"Archivo de música no encontrado: {ruta_musica}")
            print(f"Asegúrate de tener un archivo '{tipo_musica}' en la carpeta 'assets'")

    def reproducir_musica_fondo(self):
        """
        Reproduce la música de fondo original.
        """
        self.reproducir_musica(MUSICA_FONDO)

    def reproducir_musica_game_over(self):
        """
        Reproduce la música de Game Over iniciando desde el segundo 1.
        """
        self.reproducir_musica(MUSICA_GAME_OVER, tiempo_inicio=0.5)

    def reproducir_musica_victoria(self):
        """
        Reproduce la música de Victoria.
        """
        self.reproducir_musica(MUSICA_VICTORIA)

    def dibujar_texto(self, texto, tamaño, color, x, y):
        """
        Función de ayuda para dibujar texto en la pantalla.
        """
        # Creamos un objeto de fuente.
        fuente = pygame.font.Font(self.nombre_fuente, tamaño)
        # Creamos una superficie de texto (el texto real). El True es para el antialiasing.
        superficie_texto = fuente.render(texto, True, color)
        # Obtenemos el rectángulo de la superficie del texto.
        rect_texto = superficie_texto.get_rect()
        # Centramos el rectángulo en la posición dada.
        rect_texto.center = (x, y)
        # Dibujamos el texto en la pantalla principal.
        self.pantalla.blit(superficie_texto, rect_texto)

    def dibujar_hud(self):
        """
        Dibuja el Head-Up Display (vidas, tiempo, etc.)
        """
        # Muestra las vidas en la esquina superior izquierda.
        self.dibujar_texto(f'Vidas: {self.vidas_jugador}', 22, BLANCO, 60, 15)
        
        # Muestra el tiempo restante en la esquina superior derecha.
        # Convertimos el tiempo a entero para evitar decimales.
        tiempo_entero = int(self.tiempo_restante)
        self.dibujar_texto(f'Tiempo: {tiempo_entero}', 22, BLANCO, ANCHO_PANTALLA - 100, 15)
        
        # Mostramos instrucciones de pausa en la esquina inferior.
        self.dibujar_texto('ESC = Pausa', 16, BLANCO, 100, ALTO_PANTALLA - 15)

    def cargar_mapa(self):
        """
        Carga el mapa actual desde la lista de niveles.
        """
        directorio_juego = os.path.dirname(__file__)
        mapa_actual_path = LEVEL_MAPS[self.nivel_actual_idx]
        self.mapa = []
        with open(os.path.join(directorio_juego, mapa_actual_path), 'rt') as f:
            for linea in f:
                self.mapa.append(linea.strip())

    def run(self):
        """
        El bucle principal que gestiona los estados del juego.
        """
        # Intentamos reproducir la música al inicio.
        self.reproducir_musica()
        
        self.jugando = True
        while self.jugando:
            if self.estado == 'inicio':
                self.mostrar_pantalla_inicio()
            elif self.estado == 'jugando':
                self.nuevo_juego()
            elif self.estado == 'game_over':
                self.mostrar_pantalla_game_over()
            elif self.estado == 'victoria':
                self.mostrar_pantalla_victoria()
        
        self.salir()

    def nuevo_juego(self):
        """
        Configura e inicia un nuevo nivel.
        """
        # --- Carga del Mapa ---
        self.cargar_mapa()

        # --- Grupos de Sprites ---
        # Creamos un grupo que contendrá todos los sprites del juego.
        self.todos_los_sprites = pygame.sprite.Group()
        # Creamos un grupo específico para las paredes para gestionar colisiones.
        self.paredes = pygame.sprite.Group()
        # Creamos un grupo específico para los enemigos.
        self.enemigos = pygame.sprite.Group()
        # Creamos un grupo específico para los items.
        self.items = pygame.sprite.Group()

        # --- Creación del Nivel desde el Mapa ---
        for y, linea in enumerate(self.mapa):
            for x, caracter in enumerate(linea):
                if caracter == '#':
                    # Creamos una pared en esta posición.
                    pared = Pared(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    self.todos_los_sprites.add(pared)
                    self.paredes.add(pared)
                if caracter == 'E':
                    # Creamos un enemigo horizontal en esta posición.
                    enemigo = Enemigo(self, x * TILE_SIZE, y * TILE_SIZE)
                    self.todos_los_sprites.add(enemigo)
                    self.enemigos.add(enemigo)
                if caracter == 'V':
                    # Creamos un enemigo vertical en esta posición.
                    enemigo_v = EnemigoVertical(self, x * TILE_SIZE, y * TILE_SIZE)
                    self.todos_los_sprites.add(enemigo_v)
                    self.enemigos.add(enemigo_v)
                if caracter == 'C':
                    from sprites import EnemigoPerseguidor
                    enemigo_c = EnemigoPerseguidor(self, x * TILE_SIZE, y * TILE_SIZE)
                    self.todos_los_sprites.add(enemigo_c)
                    self.enemigos.add(enemigo_c)
                if caracter == 'G':
                    # Creamos el objetivo (item) en esta posición.
                    item = Item(self, x * TILE_SIZE, y * TILE_SIZE)
                    self.todos_los_sprites.add(item)
                    self.items.add(item)
                if caracter == 'P':
                    # Creamos al jugador en la posición 'P'
                    self.jugador = Jugador(self)
                    self.jugador.rect.x = x * TILE_SIZE
                    self.jugador.rect.y = y * TILE_SIZE

        # Añadimos al jugador al grupo de todos los sprites.
        self.todos_los_sprites.add(self.jugador)
        
        # --- Inicialización del Temporizador ---
        # Reseteamos el tiempo para el nuevo nivel.
        self.tiempo_restante = self.tiempo_nivel
        
        # --- Configuración del Mensaje de Nivel ---
        # Activamos la muestra del mensaje de nivel.
        self.mostrar_mensaje_nivel = True
        # Guardamos el momento en que empezó el mensaje.
        self.mensaje_nivel_timer = pygame.time.get_ticks()
        
        # --- Reinicio del Estado de Pausa ---
        self.pausado = False
        
        # Ejecutamos el bucle del nivel.
        self.ejecutar_nivel()

    def ejecutar_nivel(self):
        """
        Bucle del juego mientras se está en un nivel.
        """
        self.en_nivel = True
        # Dibujamos el nivel una vez al inicio para que se vea durante el mensaje.
        self.dibujar()
        
        while self.en_nivel:
            # Forzamos el bucle a correr a la velocidad que definimos en FPS.
            self.reloj.tick(FPS)
            
            # Procesamos los eventos (teclado, ratón, etc.).
            self.eventos()
            
            # --- Manejo del Mensaje de Nivel ---
            if self.mostrar_mensaje_nivel:
                # Solo dibujamos el mensaje de nivel sin redibujar el fondo.
                # Esto evita el parpadeo.
                self.dibujar_texto(f"Nivel {self.nivel_actual_idx+1}", 48, BLANCO, ANCHO_PANTALLA/2, ALTO_PANTALLA/2)
                pygame.display.flip()
                
                # Comprobamos si han pasado 2 segundos (2000 milisegundos).
                if pygame.time.get_ticks() - self.mensaje_nivel_timer > 2000:
                    self.mostrar_mensaje_nivel = False
                continue
            
            # --- Manejo de Pausa ---
            if self.pausado:
                # Si está pausado, solo dibujamos el mensaje de pausa sin redibujar el fondo.
                # Esto evita el parpadeo.
                self.dibujar_texto("PAUSA", 48, BLANCO, ANCHO_PANTALLA/2, ALTO_PANTALLA/2)
                self.dibujar_texto("Presiona ESC para continuar", 22, BLANCO, ANCHO_PANTALLA/2, ALTO_PANTALLA/2 + 50)
                pygame.display.flip()
                continue
            
            # Actualizamos el estado de los objetos del juego.
            self.actualizar()
            # Dibujamos todo en la pantalla.
            self.dibujar()

    def ejecutar(self):
        """Este método queda obsoleto por el nuevo sistema de estados. Lo mantenemos por si acaso."""
        pass

    def eventos(self):
        """
        Gestiona todos los eventos del juego.
        Un evento es cualquier acción que ocurre: una tecla presionada,
        el movimiento del ratón, cerrar la ventana, etc.
        """
        for evento in pygame.event.get():
            # Si el evento es que el usuario ha cerrado la ventana...
            if evento.type == pygame.QUIT:
                # ...detenemos el bucle del nivel y el juego principal.
                self.en_nivel = False
                self.jugando = False
            
            # --- Manejo de Teclas ---
            if evento.type == pygame.KEYDOWN:
                # Tecla de pausa (ESC)
                if evento.key == pygame.K_ESCAPE:
                    # Solo permitimos pausar si no estamos mostrando el mensaje de nivel.
                    if not self.mostrar_mensaje_nivel:
                        self.pausado = not self.pausado  # Alternamos entre pausado y no pausado
                        
                        # --- Control de Música ---
                        if self.pausado:
                            # Pausamos la música cuando el juego está pausado.
                            pygame.mixer.music.pause()
                        else:
                            # Reanudamos la música cuando el juego se reanuda.
                            pygame.mixer.music.unpause()

    def actualizar(self):
        """
        Actualiza la lógica del juego.
        Aquí irán los cálculos de movimiento, colisiones, etc.
        """
        # Solo actualizamos si no estamos mostrando el mensaje de nivel y no está pausado.
        if not self.mostrar_mensaje_nivel and not self.pausado:
            # Pygame se encarga de llamar al método update() de cada sprite en el grupo.
            self.todos_los_sprites.update()

            # --- Sistema de Temporizador ---
            # Decrementamos el tiempo restante.
            if self.tiempo_restante > 0:
                self.tiempo_restante -= 1 / FPS
                # Nos aseguramos de que no baje de 0.
                if self.tiempo_restante < 0:
                    self.tiempo_restante = 0
            
            # --- Comprobación de Tiempo Agotado ---
            # Si el tiempo se acaba, el jugador pierde una vida.
            if self.tiempo_restante == 0:
                self.vidas_jugador -= 1
                self.en_nivel = False
                if self.vidas_jugador <= 0:
                    # Si no quedan vidas, es Game Over.
                    self.estado = 'game_over'
                else:
                    # Si quedan vidas, se reinicia el mismo nivel.
                    self.estado = 'jugando'
                return

            # --- Comprobación de Colisión Jugador-Item (Victoria de Nivel) ---
            # El True hace que el item desaparezca al ser recogido.
            colisiones_items = pygame.sprite.spritecollide(self.jugador, self.items, True)
            if colisiones_items:
                # Si recogemos el item, ganamos el nivel.
                self.en_nivel = False
                self.nivel_actual_idx += 1
                # Comprobamos si ha completado todos los niveles.
                if self.nivel_actual_idx >= len(LEVEL_MAPS):
                    self.estado = 'victoria'
                else:
                    self.estado = 'jugando' # Prepara el siguiente nivel
                return

            # --- Comprobación de Colisión Jugador-Enemigo (Derrota) ---
            # El False indica que el enemigo no debe desaparecer al chocar.
            colisiones_enemigos = pygame.sprite.spritecollide(self.jugador, self.enemigos, False)
            if colisiones_enemigos:
                # Si hay colisión, el jugador pierde una vida.
                self.vidas_jugador -= 1
                self.en_nivel = False # Salimos del bucle del nivel para reiniciarlo.

                if self.vidas_jugador <= 0:
                    # Si no quedan vidas, es Game Over.
                    self.estado = 'game_over'
                else:
                    # Si quedan vidas, se reinicia el mismo nivel.
                    self.estado = 'jugando'

    def dibujar(self):
        """
        Dibuja todos los elementos en la pantalla.
        Es importante el orden: lo que se dibuja primero queda "debajo".
        """
        # Rellenamos la pantalla de un color. Esto "limpia" la pantalla en cada fotograma.
        self.pantalla.fill(NEGRO)

        # Pygame se encarga de dibujar cada sprite en el grupo en su respectiva posición (rect).
        self.todos_los_sprites.draw(self.pantalla)

        # Dibujamos el HUD por encima de todo.
        self.dibujar_hud()

        # ¡Importante! Después de dibujar todo, actualizamos la pantalla para que se muestren los cambios.
        pygame.display.flip()

    def mostrar_pantalla_inicio(self):
        """
        Muestra la pantalla de inicio del juego.
        """
        # Al ir a la pantalla de inicio, reseteamos el progreso.
        self.nivel_actual_idx = 0
        self.vidas_jugador = VIDAS_JUGADOR
        
        # --- Restauración de Música de Fondo ---
        # Si no estamos reproduciendo la música de fondo, la restauramos.
        if self.musica_actual != MUSICA_FONDO:
            self.reproducir_musica_fondo()
        
        self.pantalla.fill(NEGRO)
        self.dibujar_texto(TITULO, 48, BLANCO, ANCHO_PANTALLA / 2, ALTO_PANTALLA / 4)
        self.dibujar_texto("Usa W A S D o las flechas para moverte", 22, BLANCO, ANCHO_PANTALLA / 2, ALTO_PANTALLA / 2)
        self.dibujar_texto("Pulsa ENTER para empezar", 22, BLANCO, ANCHO_PANTALLA / 2, ALTO_PANTALLA * 3 / 4)
        pygame.display.flip()
        
        # Esperamos a que el jugador pulse una tecla.
        self.esperar_tecla()
        # Cambiamos de estado para empezar a jugar.
        self.estado = 'jugando'

    def mostrar_pantalla_game_over(self):
        """
        Muestra la pantalla de Game Over.
        """
        # --- Reproducción de Música de Game Over ---
        self.reproducir_musica_game_over()
        
        self.pantalla.fill(NEGRO)
        self.dibujar_texto("GAME OVER", 48, ROJO, ANCHO_PANTALLA / 2, ALTO_PANTALLA / 4)
        self.dibujar_texto("Te has quedado sin vidas.", 22, BLANCO, ANCHO_PANTALLA/2, ALTO_PANTALLA/2)
        self.dibujar_texto("Pulsa ENTER para volver a empezar", 22, BLANCO, ANCHO_PANTALLA / 2, ALTO_PANTALLA * 3 / 4)
        pygame.display.flip()
        self.esperar_tecla()
        # Cambiamos el estado para volver a la pantalla de inicio.
        self.estado = 'inicio'

    def mostrar_pantalla_victoria(self):
        """
        Muestra la pantalla de Victoria final.
        """
        # --- Reproducción de Música de Victoria ---
        self.reproducir_musica_victoria()
        
        self.pantalla.fill(NEGRO)
        self.dibujar_texto("¡FELICIDADES!", 48, VERDE, ANCHO_PANTALLA / 2, ALTO_PANTALLA / 4)
        self.dibujar_texto("Has completado todos los niveles.", 22, BLANCO, ANCHO_PANTALLA / 2, ALTO_PANTALLA / 2)
        self.dibujar_texto("Pulsa ENTER para volver al menú.", 22, BLANCO, ANCHO_PANTALLA / 2, ALTO_PANTALLA * 3 / 4)
        pygame.display.flip()
        self.esperar_tecla()
        self.estado = 'inicio'

    def esperar_tecla(self):
        """
        Bucle de espera para una pulsación de tecla específica (ENTER).
        """
        esperando = True
        while esperando:
            self.reloj.tick(FPS)
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    esperando = False
                    self.salir()
                if evento.type == pygame.KEYUP:
                    if evento.key == pygame.K_RETURN or evento.key == pygame.K_KP_ENTER:
                        esperando = False

    def salir(self):
        """
        Cierra Pygame y termina el programa.
        """
        pygame.quit()
        sys.exit()


# --- Punto de entrada del programa ---
# Este es el código que se ejecuta cuando corremos el archivo directamente.
if __name__ == "__main__":
    # Creamos una instancia de nuestra clase Juego.
    juego = Juego()
    # Ejecutamos el bucle principal del juego.
    juego.run() 