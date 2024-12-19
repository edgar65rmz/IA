import pygame
from queue import PriorityQueue
import tkinter as tk
from threading import Thread
import string

# Configuraciones iniciales
ANCHO_VENTANA = 800

# Colores (RGB)
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
GRIS = (128, 128, 128)
VERDE = (0, 255, 0)
ROJO = (255, 0, 0)
NARANJA = (255, 165, 0)
PURPURA = (128, 0, 128)
AZUL = (0, 0, 255)

pygame.font.init()
FUENTE = pygame.font.SysFont("comicsans", 50)


class Nodo:
    def __init__(self, fila, col, ancho, total_filas, etiqueta):
        self.fila = fila
        self.col = col
        self.x = fila * ancho
        self.y = col * ancho
        self.color = BLANCO
        self.ancho = ancho
        self.total_filas = total_filas
        self.vecinos = []
        self.g = float("inf")
        self.h = 0
        self.f = float("inf")
        self.padre = None
        self.etiqueta = etiqueta

    def get_pos(self):
        return self.fila, self.col

    def es_pared(self):
        return self.color == NEGRO

    def es_inicio(self):
        return self.color == NARANJA

    def es_fin(self):
        return self.color == PURPURA

    def restablecer(self):
        self.color = BLANCO

    def hacer_inicio(self):
        self.color = NARANJA

    def hacer_pared(self):
        self.color = NEGRO

    def hacer_fin(self):
        self.color = PURPURA

    def dibujar(self, ventana):
        pygame.draw.rect(ventana, self.color, (self.x, self.y, self.ancho, self.ancho))

    def actualizar_vecinos(self, grid):
        self.vecinos = []
        direcciones = [
            (1, 0), (-1, 0), (0, 1), (0, -1),  # Cardinales
            (1, 1), (1, -1), (-1, 1), (-1, -1)  # Diagonales
        ]
        for dx, dy in direcciones:
            nuevo_fila = self.fila + dx
            nuevo_col = self.col + dy
            if 0 <= nuevo_fila < self.total_filas and 0 <= nuevo_col < self.total_filas:
                vecino = grid[nuevo_fila][nuevo_col]
                if not vecino.es_pared():
                    self.vecinos.append(vecino)

    def __lt__(self, other):
        return self.f < other.f


def heuristica(nodo1, nodo2):
    x1, y1 = nodo1.get_pos()
    x2, y2 = nodo2.get_pos()
    return abs(x1 - x2) + abs(y1 - y2)


def reconstruir_camino(came_from, actual, dibujar):
    while actual in came_from:
        actual = came_from[actual]
        actual.color = VERDE
        dibujar()
        pygame.time.delay(50)


class ListaVentana:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Listas Abierta y Cerrada")
        self.root.geometry("500x600")

        # Lista abierta
        self.label_abierta = tk.Label(self.root, text="Lista Abierta:", font=("Arial", 14, "bold"))
        self.label_abierta.pack()
        self.text_abierta = tk.Text(self.root, height=10, width=60)
        self.text_abierta.pack()

        # Lista cerrada
        self.label_cerrada = tk.Label(self.root, text="Lista Cerrada:", font=("Arial", 14, "bold"))
        self.label_cerrada.pack()
        self.text_cerrada = tk.Text(self.root, height=10, width=60)
        self.text_cerrada.pack()

        # Valores del camino final
        self.label_camino = tk.Label(self.root, text="Camino Final (g, h, f):", font=("Arial", 14, "bold"))
        self.label_camino.pack()
        self.text_camino = tk.Text(self.root, height=10, width=60)
        self.text_camino.pack()

    def actualizar_abierta(self, abierta):
        self.text_abierta.delete(1.0, tk.END)
        # Concatenar etiquetas en una sola línea separada por comas
        etiquetas = [nodo.etiqueta for nodo in abierta]
        self.text_abierta.insert(tk.END, ", ".join(etiquetas))
        self.text_abierta.update_idletasks()

    def actualizar_cerrada(self, cerrada):
        self.text_cerrada.delete(1.0, tk.END)
        # Mostrar etiquetas en la lista cerrada
        etiquetas = [nodo.etiqueta for nodo in cerrada]
        self.text_cerrada.insert(tk.END, ", ".join(etiquetas))
        self.text_cerrada.update_idletasks()

    def actualizar_camino_final(self, camino):
        self.text_camino.delete(1.0, tk.END)
        # Mostrar los valores de g, h, f junto con las etiquetas
        for nodo in camino:
            self.text_camino.insert(tk.END, f"Nodo: {nodo.etiqueta}, g: {nodo.g:.2f}, h: {nodo.h:.2f}, f: {nodo.f:.2f}\n")
        self.text_camino.update_idletasks()

    def iniciar(self):
        self.root.mainloop()



def a_star(dibujar, grid, inicio, fin, lista_ventana):
    cont = 0
    open_set = PriorityQueue()
    open_set.put((0, cont, inicio))
    came_from = {}

    inicio.g = 0
    inicio.f = heuristica(inicio, fin)

    open_set_hash = {inicio}
    closed_set = set()

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        actual = open_set.get()[2]
        open_set_hash.remove(actual)
        closed_set.add(actual)

        if actual == fin:
            reconstruir_camino(came_from, fin, dibujar)
            fin.hacer_fin()
            return True

        for vecino in actual.vecinos:
            diagonal = abs(vecino.fila - actual.fila) == 1 and abs(vecino.col - actual.col) == 1
            temp_g_score = actual.g + (1.4 if diagonal else 1)

            if temp_g_score < vecino.g:
                vecino.padre = actual
                came_from[vecino] = actual
                vecino.g = temp_g_score
                vecino.h = heuristica(vecino, fin)
                vecino.f = vecino.g + vecino.h
                if vecino not in open_set_hash and vecino not in closed_set:
                    cont += 1
                    open_set.put((vecino.f, cont, vecino))
                    open_set_hash.add(vecino)
                    vecino.color = ROJO

        dibujar()
        actual.color = AZUL
        pygame.time.delay(30)

        lista_ventana.actualizar_abierta(open_set_hash)
        lista_ventana.actualizar_cerrada(closed_set)

    return False


def crear_grid(filas, ancho):
    grid = []
    ancho_nodo = ancho // filas

    etiquetas = list(string.ascii_uppercase) + [str(i) for i in range(1, 1000)]
    etiqueta_idx = 0

    for i in range(filas):
        grid.append([])
        for j in range(filas):
            nodo = Nodo(i, j, ancho_nodo, filas, etiquetas[etiqueta_idx])
            etiqueta_idx += 1
            grid[i].append(nodo)
    return grid


def dibujar_grid(ventana, filas, ancho):
    ancho_nodo = ancho // filas
    for i in range(filas):
        pygame.draw.line(ventana, GRIS, (0, i * ancho_nodo), (ancho, i * ancho_nodo))
        for j in range(filas):
            pygame.draw.line(ventana, GRIS, (j * ancho_nodo, 0), (j * ancho_nodo, ancho))


def dibujar(ventana, grid, filas, ancho):
    ventana.fill(BLANCO)
    for fila in grid:
        for nodo in fila:
            nodo.dibujar(ventana)

    dibujar_grid(ventana, filas, ancho)
    pygame.display.update()


def obtener_click_pos(pos, filas, ancho):
    ancho_nodo = ancho // filas
    y, x = pos
    fila = y // ancho_nodo
    col = x // ancho_nodo
    return fila, col


def ejecutar_pygame(lista_ventana):
    ventana = pygame.display.set_mode((ANCHO_VENTANA, ANCHO_VENTANA))
    filas = 9
    grid = crear_grid(filas, ANCHO_VENTANA)

    inicio = None
    fin = None
    corriendo = True

    while corriendo:
        dibujar(ventana, grid, filas, ANCHO_VENTANA)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                corriendo = False

            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                fila, col = obtener_click_pos(pos, filas, ANCHO_VENTANA)
                nodo = grid[fila][col]
                if not inicio and nodo != fin:
                    inicio = nodo
                    inicio.hacer_inicio()
                elif not fin and nodo != inicio:
                    fin = nodo
                    fin.hacer_fin()
                elif nodo != fin and nodo != inicio:
                    nodo.hacer_pared()

            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                fila, col = obtener_click_pos(pos, filas, ANCHO_VENTANA)
                nodo = grid[fila][col]
                nodo.restablecer()
                if nodo == inicio:
                    inicio = None
                elif nodo == fin:
                    fin = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and inicio and fin:
                    for fila in grid:
                        for nodo in fila:
                            nodo.actualizar_vecinos(grid)

                    a_star(lambda: dibujar(ventana, grid, filas, ANCHO_VENTANA), grid, inicio, fin, lista_ventana)

                if event.key == pygame.K_r:
                    grid = crear_grid(filas, ANCHO_VENTANA)
                    inicio = None
                    fin = None

                if event.key == pygame.K_q:
                    corriendo = False

    pygame.quit()


if __name__ == "__main__":
    lista_ventana = ListaVentana()
    pygame_thread = Thread(target=ejecutar_pygame, args=(lista_ventana,))
    pygame_thread.start()
    lista_ventana.iniciar()
