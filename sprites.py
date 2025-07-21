import pygame
from settings import *
import os

# --- Directorio de Assets ---
# Creamos la ruta completa a la carpeta de assets.
# os.path.dirname(__file__) obtiene el directorio del archivo actual (sprites.py)
# y os.path.join() une las partes de la ruta de forma segura.
directorio_juego = os.path.dirname(__file__)
directorio_assets = os.path.join(directorio_juego, CARPETA_ASSETS)

# --- Clase Jugador ---
# Heredamos de pygame.sprite.Sprite para poder usar las funciones de sprites de Pygame.
class Jugador(pygame.sprite.Sprite):
    def __init__(self, juego):
        """
        Constructor de la clase Jugador.
        """
        # Es obligatorio llamar al constructor de la clase padre (Sprite).
        super().__init__()
        
        # Guardamos una referencia al juego principal.
        self.juego = juego

        # --- Imagen y Rectángulo ---
        # Cargamos la imagen del jugador desde la carpeta de assets.
        # .convert_alpha() optimiza la imagen para un dibujado rápido con transparencias.
        self.image = pygame.image.load(os.path.join(directorio_assets, IMAGEN_JUGADOR)).convert_alpha()
        
        # Obtenemos el rectángulo de la imagen. Pygame lo hace por nosotros.
        self.rect = self.image.get_rect()

        # --- Posición Inicial ---
        # Centramos al jugador en la pantalla.
        self.rect.center = (ANCHO_PANTALLA / 2, ALTO_PANTALLA / 2)

        # --- Velocidad ---
        # Guardaremos la velocidad del jugador en los ejes x e y.
        self.vx = 0
        self.vy = 0

    def get_teclas_presionadas(self):
        """
        Comprueba las teclas que están siendo presionadas y ajusta la velocidad del jugador.
        """
        # Reseteamos la velocidad en cada fotograma para que el personaje se pare si no se pulsa nada.
        self.vx, self.vy = 0, 0
        
        # Obtenemos un diccionario con el estado de todas las teclas.
        teclas = pygame.key.get_pressed()

        # Comprobamos las teclas de movimiento horizontal.
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            self.vx = -VELOCIDAD_JUGADOR
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            self.vx = VELOCIDAD_JUGADOR

        # Comprobamos las teclas de movimiento vertical.
        if teclas[pygame.K_UP] or teclas[pygame.K_w]:
            self.vy = -VELOCIDAD_JUGADOR
        if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
            self.vy = VELOCIDAD_JUGADOR
            
        # Para evitar que el movimiento diagonal sea más rápido, normalizamos el vector velocidad.
        # Si el jugador se está moviendo en ambas direcciones (vx y vy no son cero)...
        if self.vx != 0 and self.vy != 0:
            # ... ajustamos la velocidad para que la velocidad total sea la misma que en horizontal/vertical.
            # Esto es un poco de matemáticas (teorema de Pitágoras), pero hace que el movimiento se sienta mejor.
            self.vx *= 0.7071
            self.vy *= 0.7071


    def update(self):
        """
        Actualiza la posición del jugador en cada fotograma.
        Este método es llamado automáticamente por el grupo de sprites en el bucle principal.
        """
        # Primero, obtenemos las teclas presionadas para saber en qué dirección movernos.
        self.get_teclas_presionadas()
        
        # --- Actualización de Posición y Colisiones ---
        # Movemos el rectángulo en el eje X.
        self.rect.x += self.vx
        # Comprobamos si ha habido colisión en el eje X.
        self.comprobar_colisiones('x')

        # Movemos el rectángulo en el eje Y.
        self.rect.y += self.vy
        # Comprobamos si ha habido colisión en el eje Y.
        self.comprobar_colisiones('y')


        # --- Comprobación de Límites de Pantalla (opcional si el nivel es cerrado) ---
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > ANCHO_PANTALLA:
            self.rect.right = ANCHO_PANTALLA
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > ALTO_PANTALLA:
            self.rect.bottom = ALTO_PANTALLA

    def comprobar_colisiones(self, direccion):
        """
        Comprueba y resuelve las colisiones del jugador con las paredes.
        :param direccion: 'x' o 'y', para saber en qué eje estamos comprobando.
        """
        # La función spritecollide devuelve una lista con todos los sprites del grupo
        # con los que hemos chocado. El False indica que el sprite no debe ser destruido.
        colisiones = pygame.sprite.spritecollide(self, self.juego.paredes, False)

        if colisiones:
            if direccion == 'x':
                # Si nos movemos a la derecha...
                if self.vx > 0:
                    # ...nuestro borde derecho se alinea con el borde izquierdo del objeto chocado.
                    self.rect.right = colisiones[0].rect.left
                # Si nos movemos a la izquierda...
                if self.vx < 0:
                    # ...nuestro borde izquierdo se alinea con el borde derecho del objeto chocado.
                    self.rect.left = colisiones[0].rect.right
            
            if direccion == 'y':
                # Si nos movemos hacia abajo...
                if self.vy > 0:
                    self.rect.bottom = colisiones[0].rect.top
                # Si nos movemos hacia arriba...
                if self.vy < 0:
                    self.rect.top = colisiones[0].rect.bottom


# --- Clase Enemigo ---
class Enemigo(pygame.sprite.Sprite):
    def __init__(self, juego, x, y):
        super().__init__()
        self.juego = juego
        # Cargamos la imagen del enemigo.
        self.image = pygame.image.load(os.path.join(directorio_assets, IMAGEN_ENEMIGO)).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        # Velocidad inicial de patrulla.
        self.vx = VELOCIDAD_ENEMIGO

    def update(self):
        # Movemos al enemigo.
        self.rect.x += self.vx
        
        # Comprobamos si choca con una pared.
        colisiones_pared = pygame.sprite.spritecollide(self, self.juego.paredes, False)
        if colisiones_pared:
            # Comprobamos la dirección en la que se movía ANTES de invertirla.
            if self.vx > 0: # Se movía a la derecha
                # Lo colocamos justo a la izquierda de la pared con la que chocó.
                self.rect.right = colisiones_pared[0].rect.left
            elif self.vx < 0: # Se movía a la izquierda
                # Lo colocamos justo a la derecha de la pared con la que chocó.
                self.rect.left = colisiones_pared[0].rect.right
            
            # Ahora sí, invertimos la velocidad para que vaya en la otra dirección en el siguiente fotograma.
            self.vx *= -1


# --- Clase EnemigoVertical ---
class EnemigoVertical(pygame.sprite.Sprite):
    def __init__(self, juego, x, y):
        super().__init__()
        self.juego = juego
        self.image = pygame.image.load(os.path.join(directorio_assets, IMAGEN_ENEMIGO_VERTICAL)).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vy = VELOCIDAD_ENEMIGO

    def update(self):
        self.rect.y += self.vy
        colisiones_pared = pygame.sprite.spritecollide(self, self.juego.paredes, False)
        if colisiones_pared:
            if self.vy > 0: # Se movía hacia abajo
                self.rect.bottom = colisiones_pared[0].rect.top
            elif self.vy < 0: # Se movía hacia arriba
                self.rect.top = colisiones_pared[0].rect.bottom
            self.vy *= -1


# --- Clase Item ---
class Item(pygame.sprite.Sprite):
    def __init__(self, juego, x, y):
        super().__init__()
        self.juego = juego
        # Cargamos la imagen del item.
        self.image = pygame.image.load(os.path.join(directorio_assets, IMAGEN_ITEM)).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


# --- Clase Pared ---
# Un obstáculo estático en el juego.
class Pared(pygame.sprite.Sprite):
    def __init__(self, x, y, ancho, alto):
        """
        Constructor de la clase Pared.
        :param x: Posición en el eje x.
        :param y: Posición en el eje y.
        :param ancho: Ancho del bloque.
        :param alto: Alto del bloque.
        """
        super().__init__()
        # Cargamos la imagen base de la pared.
        # .convert() optimiza la imagen para un dibujado rápido sin transparencias.
        imagen_pared = pygame.image.load(os.path.join(directorio_assets, IMAGEN_PARED)).convert()
        
        # Escalamamos la imagen al tamaño especificado (ancho, alto).
        self.image = pygame.transform.scale(imagen_pared, (ancho, alto))

        # Obtenemos su rectángulo y lo posicionamos.
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y 

class EnemigoPerseguidor(pygame.sprite.Sprite):
    """
    Clase que representa un enemigo que persigue al jugador.
    """
    def __init__(self, juego, x, y):
        super().__init__()
        # Cargamos la imagen del enemigo perseguidor (usamos la misma que el enemigo normal por ahora).
        self.image = pygame.image.load(os.path.join(directorio_assets, IMAGEN_ENEMIGO)).convert_alpha()
        # Redimensionamos la imagen.
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        # Creamos el rectángulo de colisión.
        self.rect = self.image.get_rect()
        # Posicionamos el enemigo.
        self.rect.x = x
        self.rect.y = y
        # Velocidad del enemigo perseguidor (un poco más lento que el jugador).
        self.velocidad = VELOCIDAD_ENEMIGO * 0.8
        # Referencia al juego.
        self.juego = juego

    def update(self):
        """
        Actualiza la posición del enemigo persiguiendo al jugador.
        """
        # Obtenemos la posición del jugador.
        jugador = self.juego.jugador
        
        # Calculamos la dirección hacia el jugador.
        dx = jugador.rect.centerx - self.rect.centerx
        dy = jugador.rect.centery - self.rect.centery
        
        # Normalizamos la dirección para movimiento uniforme.
        distancia = max(abs(dx), abs(dy))
        if distancia > 0:
            dx = (dx / distancia) * self.velocidad
            dy = (dy / distancia) * self.velocidad
        
        # Aplicamos el movimiento horizontal.
        self.rect.x += dx
        # Comprobamos colisiones horizontales.
        colisiones_h = pygame.sprite.spritecollide(self, self.juego.paredes, False)
        if colisiones_h:
            # Si hay colisión, revertimos el movimiento.
            if dx > 0:
                self.rect.right = colisiones_h[0].rect.left
            else:
                self.rect.left = colisiones_h[0].rect.right
        
        # Aplicamos el movimiento vertical.
        self.rect.y += dy
        # Comprobamos colisiones verticales.
        colisiones_v = pygame.sprite.spritecollide(self, self.juego.paredes, False)
        if colisiones_v:
            # Si hay colisión, revertimos el movimiento.
            if dy > 0:
                self.rect.bottom = colisiones_v[0].rect.top
            else:
                self.rect.top = colisiones_v[0].rect.bottom 