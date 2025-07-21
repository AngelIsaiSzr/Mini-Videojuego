# Este archivo contiene la configuración global y las constantes del juego.
# La idea es tener un solo lugar para modificar valores como el tamaño de la pantalla,
# los colores, la velocidad del jugador, etc.

# --- Título de la Ventana ---
TITULO = "Mi Aventura Épica"

# --- Dimensiones de la pantalla ---
ANCHO_PANTALLA = 768 # 24 tiles * 32 pixeles
ALTO_PANTALLA = 448 # 14 tiles * 32 pixeles

# --- Fotogramas Por Segundo (FPS) ---
# Controla la "velocidad" a la que se actualiza el juego.
FPS = 60

# --- Ajustes del Nivel ---
TILE_SIZE = 32
# Creamos una lista con todos los mapas de niveles que vaya teniendo el juego.
LEVEL_MAPS = [
    "level1.txt",
    "level2.txt",
    "level3.txt"
]

# --- Ajustes del Jugador ---
VELOCIDAD_JUGADOR = 5
VIDAS_JUGADOR = 3

# --- Ajustes de Enemigos ---
VELOCIDAD_ENEMIGO = 3

# --- Archivos de Assets ---
CARPETA_ASSETS = "assets"

# --- Imágenes ---
IMAGEN_JUGADOR = "images/player.png"
IMAGEN_PARED = "images/wall.png"
IMAGEN_ENEMIGO = "images/enemy.png"
IMAGEN_ENEMIGO_VERTICAL = "images/enemy_vertical.png"
IMAGEN_ENEMIGO_PERSEGUIDOR = "images/enemy.png"
IMAGEN_ITEM = "images/item.png"

# --- Música ---
MUSICA_FONDO = "music/musica.mp3"  # Puedes ser .mp3 o .ogg
MUSICA_GAME_OVER = "music/game_over.mp3"  # Música para cuando pierdes
MUSICA_VICTORIA = "music/victoria.mp3"  # Música para cuando ganas

# --- Colores (en formato RGB) ---
# Puedes encontrar más colores buscando "RGB color picker" en internet.
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
ROJO = (255, 0, 0)
VERDE = (0, 255, 0)
AZUL = (0, 0, 255) 