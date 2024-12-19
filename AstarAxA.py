import pygame
import tkinter as tk
from queue import PriorityQueue
import math

# Configuraciones iniciales
ANCHO_VENTANA = 800
VENTANA = pygame.display.set_mode((ANCHO_VENTANA, ANCHO_VENTANA))
pygame.display.set_caption("Visualización de Nodos - Algoritmo A*")

# Colores (RGB)
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
GRIS = (128, 128, 128)
VERDE = (0, 255, 0)
ROJO = (255, 0, 0)
NARANJA = (255, 165, 0)
PURPURA = (128, 0, 128)
AZUL = (0, 0, 255)

# Inicializar fuente de Pygame para el texto
pygame.font.init()
FUENTE = pygame.font.SysFont("Arial", 15)

# Función para convertir un número a un identificador de letras como Excel (a, b, ..., z, aa, ab, ...)
def convertir_a_letras(n):
    resultado = ""
    while n >= 0:
        resultado = chr(n % 26 + 97) + resultado
        n = n // 26 - 1
    return resultado

class Nodo:
    def __init__(self, fila, col, ancho, total_filas, id):
        self.fila = fila
        self.col = col
        self.x = fila * ancho
        self.y = col * ancho
        self.color = BLANCO
        self.ancho = ancho
        self.total_filas = total_filas
        self.vecinos = []
        self.g = float("inf")  # Distancia desde el inicio
        self.h = 0  # Heurística (distancia hasta el fin)
        self.f = float("inf")  # f = g + h
        self.padre = None  # Nodo anterior para reconstruir el camino
        self.id = id  # Identificador único del nodo

    def get_id(self):
        return self.id

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

    def hacer_fin_encontrado(self):
        self.color = AZUL  # Cambia el color a azul cuando se encuentra el camino

    def dibujar(self, ventana):
        pygame.draw.rect(ventana, self.color, (self.x, self.y, self.ancho, self.ancho))

    def actualizar_vecinos(self, grid):
        # Limpiar vecinos anteriores
        self.vecinos = []
        # Direcciones de movimiento en 8 direcciones (arriba, abajo, izquierda, derecha y diagonales)
        direcciones = [
            (1, 0), (-1, 0), (0, 1), (0, -1),  # Movimiento en línea recta
            (1, 1), (1, -1), (-1, 1), (-1, -1)  # Movimiento diagonal
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

# Función heurística para A* (distancia de Chebyshev para movimiento diagonal)
def heuristica(nodo1, nodo2):
    x1, y1 = nodo1.fila, nodo1.col
    x2, y2 = nodo2.fila, nodo2.col
    return max(abs(x1 - x2), abs(y1 - y2))

# Función para reconstruir el camino y colorearlo
def reconstruir_camino(came_from, actual, dibujar, lista_camino_tk):
    while actual in came_from:
        actual = came_from[actual]
        actual.color = VERDE  # Color del camino óptimo en verde
        dibujar()
        
        # Mostrar los datos del camino óptimo en la lista de Tkinter
        texto = f"ID: {actual.get_id()} | g: {int(actual.g)}, h: {int(actual.h)}, f: {int(actual.f)}"
        lista_camino_tk.insert(tk.END, texto)
        lista_camino_tk.itemconfig(tk.END, {'fg': 'green'})  # Colorear el texto en verde
        lista_camino_tk.yview(tk.END)  # Desplazar hacia abajo para mostrar el último nodo

# Mostrar los valores g, h, f y el ID en una ventana independiente usando Tkinter en tiempo real
def mostrar_valores_en_tkinter(lista, nodo):
    texto = f"ID: {nodo.get_id()} | g: {int(nodo.g)}, h: {int(nodo.h)}, f: {int(nodo.f)}"
    lista.insert(tk.END, texto)
    lista.yview(tk.END)  # Desplazarse automáticamente hacia abajo para ver el último nodo agregado
    lista.update_idletasks()  # Actualizar la lista en tiempo real

# Algoritmo A*
def a_star(dibujar, grid, inicio, fin, lista_tk, lista_camino_tk):
    cont = 0
    open_set = PriorityQueue()
    open_set.put((0, cont, inicio))
    came_from = {}

    inicio.g = 0
    inicio.f = heuristica(inicio, fin)

    open_set_hash = {inicio}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        actual = open_set.get()[2]
        open_set_hash.remove(actual)

        # Mostrar en tiempo real los valores del nodo actual en la ventana de Tkinter
        mostrar_valores_en_tkinter(lista_tk, actual)

        if actual == fin:
            reconstruir_camino(came_from, fin, dibujar, lista_camino_tk)
            fin.hacer_fin_encontrado()  # Cambia el color del nodo de fin a azul
            return True

        for vecino in actual.vecinos:
            # Costo de movimiento diagonal o recto
            temp_g_score = actual.g + (1 if abs(vecino.fila - actual.fila) + abs(vecino.col - actual.col) == 1 else math.sqrt(2))

            if temp_g_score < vecino.g:
                came_from[vecino] = actual
                vecino.g = temp_g_score
                vecino.h = heuristica(vecino, fin)
                vecino.f = vecino.g + vecino.h
                if vecino not in open_set_hash:
                    cont += 1
                    open_set.put((vecino.f, cont, vecino))
                    open_set_hash.add(vecino)
                    # Solo cambiar a rojo si no es el nodo de fin
                    if vecino != fin:
                        vecino.color = ROJO

        dibujar()

        if actual != inicio and actual != fin:
            actual.color = GRIS

    return False

# Crear la cuadrícula y asignar identificadores en formato de letras
def crear_grid(filas, ancho):
    grid = []
    ancho_nodo = ancho // filas
    id = 0  # Inicializar el ID en 0 para usar convertir_a_letras
    for i in range(filas):
        grid.append([])
        for j in range(filas):
            nodo_id = convertir_a_letras(id)
            nodo = Nodo(i, j, ancho_nodo, filas, nodo_id)
            grid[i].append(nodo)
            id += 1  # Incrementar el ID para el siguiente nodo
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

def main(ventana, ancho):
    FILAS = 9
    grid = crear_grid(FILAS, ancho)

    inicio = None
    fin = None

    # Configuración de la ventana de Tkinter para mostrar el proceso en tiempo real
    ventana_tk = tk.Tk()
    ventana_tk.title("Valores del Camino Óptimo")
    ventana_tk.geometry("300x600")

    # Lista para nodos explorados
    scrollbar = tk.Scrollbar(ventana_tk)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    lista_tk = tk.Listbox(ventana_tk, yscrollcommand=scrollbar.set, font=("Arial", 10))
    lista_tk.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    scrollbar.config(command=lista_tk.yview)

    # Lista para el camino óptimo
    lista_camino_tk = tk.Listbox(ventana_tk, font=("Arial", 10), fg="green")
    lista_camino_tk.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    for fila in grid:
        for nodo in fila:
            nodo.actualizar_vecinos(grid)

    corriendo = True

    while corriendo:
        dibujar(ventana, grid, FILAS, ancho)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                corriendo = False

            if pygame.mouse.get_pressed()[0]:  # Click izquierdo
                pos = pygame.mouse.get_pos()
                fila, col = obtener_click_pos(pos, FILAS, ancho)
                nodo = grid[fila][col]
                if not inicio and nodo != fin:
                    inicio = nodo
                    inicio.hacer_inicio()

                elif not fin and nodo != inicio:
                    fin = nodo
                    fin.hacer_fin()

                elif nodo != fin and nodo != inicio:
                    nodo.hacer_pared()

            elif pygame.mouse.get_pressed()[2]:  # Click derecho
                pos = pygame.mouse.get_pos()
                fila, col = obtener_click_pos(pos, FILAS, ancho)
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

                    a_star(lambda: dibujar(ventana, grid, FILAS, ancho), grid, inicio, fin, lista_tk, lista_camino_tk)

        ventana_tk.update()  # Actualizar la ventana de Tkinter en el bucle principal

    pygame.quit()
    ventana_tk.destroy()

main(VENTANA, ANCHO_VENTANA)
