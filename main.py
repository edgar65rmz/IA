import pygame
import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.utils import resample
from sklearn.utils.validation import check_is_fitted
import random
import os

pygame.init()

menu_font = pygame.font.Font(None, 36) 

# Configurar música de fondo
pygame.mixer.music.load("assets/music/background_music.mp3")  
pygame.mixer.music.set_volume(0.5)  
pygame.mixer.music.play(-1)  


# Cargar efecto de sonido para el salto
jump_sound = pygame.mixer.Sound("assets/sounds/jump.mp3")  
jump_sound.set_volume(0.7)  


# Dimensiones de la ventana
WIDTH, HEIGHT = 800, 400
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Juego: Modo Manual y Automático")

# Colores
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# Recursos del juego
player_image = pygame.image.load("assets/player.png")
player_image = pygame.transform.scale(player_image, (50, 70))
ball_image = pygame.image.load("assets/ball.png")
background_image = pygame.image.load("assets/background.png")
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
plant_image = pygame.image.load("assets/frames/frame13.png")  
plant_image = pygame.transform.scale(plant_image, (80, 100))  



plant_frames = []
for i in range(1, 14):  
    frame = pygame.image.load(f"assets/frames/frame{i}.png")
    frame = pygame.transform.scale(frame, (70, 100))  
    plant_frames.append(frame)



plant_x = WIDTH - 100
plant_y = HEIGHT - 90  



# Inicialización del jugador y la bala
player = pygame.Rect(50, HEIGHT - 70, 50, 70)  # Jugador
bala = pygame.Rect(plant_x + 20, plant_y + 40, 30, 30)  

# Velocidades
player_speed_y = 0
gravity = 1
jump_strength = -15
is_jumping = False
velocidad_bala = -random.randint(10, 20)  # Incrementamos la velocidad mínima y máxima

# Dataset para entrenamiento
data = []

def reiniciar_datos():
    global data
    data = []  # Vaciar los datos almacenados


def reiniciar_modelos():
    global arbol_model, nn_model
    arbol_model = DecisionTreeClassifier()  
    nn_model = None  
    print("Modelos reiniciados.")


# Variables del modo
modo_manual = True
usar_arbol = True
paused = False
juego_activo = False  # Controla si el juego está activo

current_frame = 0  # Frame inicial
frame_delay = 3  # Velocidad de la animación (más bajo = más rápido)
frame_counter = 0  # Contador para manejar los ticks

# Modelos
arbol_model = DecisionTreeClassifier()
nn_model = None

# Fuente
font = pygame.font.Font(None, 36)

# Función para inicializar la red neuronal
def inicializar_red_neuronal():
    global nn_model
    nn_model = Sequential([
        Dense(16, input_dim=2, activation='relu'),  # Aumentamos las neuronas
        Dense(8, activation='relu'),               # Añadimos una capa más profunda
        Dense(1, activation='sigmoid')
    ])
    nn_model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Rebalanceo de datos
def rebalancear_datos(data):
    df = pd.DataFrame(data, columns=["Desplazamiento", "Velocidad", "Salto"])
    clase_mayoritaria = df[df["Salto"] == 0]
    clase_minoritaria = df[df["Salto"] == 1]

    # Validar que ambas clases tengan al menos un dato
    if len(clase_mayoritaria) == 0 or len(clase_minoritaria) == 0:
        print("Error: No hay suficientes datos de ambas clases para entrenar.")
        return None

    # Sobremuestrear la clase minoritaria
    clase_minoritaria_oversampled = resample(
        clase_minoritaria,
        replace=True,  # Muestreo con reemplazo
        n_samples=len(clase_mayoritaria),  # Igualar al tamaño de la clase mayoritaria
        random_state=42
    )

    # Combinar ambas clases
    data_balanceada = pd.concat([clase_mayoritaria, clase_minoritaria_oversampled])
    print(f"Datos rebalanceados. Total registros: {len(data_balanceada)}")
    return data_balanceada.values.tolist()

from sklearn.tree import export_graphviz
import graphviz

def visualizar_arbol(modelo, feature_names):
    # Exportar el árbol en formato DOT
    dot_data = export_graphviz(
        modelo,
        out_file=None,
        feature_names=feature_names,
        class_names=["No Saltar", "Saltar"],
        filled=True,
        rounded=True,
        special_characters=True
    )
    # Renderizar el gráfico usando graphviz
    graph = graphviz.Source(dot_data)
    graph.render("decision_tree")  # Genera un archivo 'decision_tree.pdf'
   


def entrenar_modelos():
    global data, arbol_model, nn_model

    if len(data) < 10:
        print("Necesitas más datos para entrenar los modelos.")
        return

    # Rebalancear los datos
    datos_balanceados = rebalancear_datos(data)
    if datos_balanceados is None:
        print("Entrenamiento cancelado: Datos insuficientes.")
        return

    data_np = np.array(datos_balanceados)
    X = data_np[:, :2]  # Entrada: [desplazamiento, velocidad]
    y = data_np[:, 2]   # Salida: [1=saltar, 0=no saltar]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    if usar_arbol:
        # Entrenar Árbol de Decisión
        print("Entrenando Árbol de Decisión...")
        arbol_model.fit(X_train, y_train)
        print("Árbol entrenado con precisión en datos de prueba:", arbol_model.score(X_test, y_test))
        
        # Visualizar el Árbol de Decisión
        visualizar_arbol(arbol_model, ["Desplazamiento", "Velocidad"])
    else:
        # Entrenar Red Neuronal
        print("Entrenando Red Neuronal...")
        class_weights = {0: 1, 1: len(y) / sum(y)}
        inicializar_red_neuronal()
        nn_model.fit(X_train, y_train, epochs=10, batch_size=32, verbose=1, class_weight=class_weights)
        print("Red neuronal entrenada.")
        # Evaluar Red Neuronal
        loss, accuracy = nn_model.evaluate(X_test, y_test, verbose=0)
        print(f"Precisión de la Red Neuronal en datos de prueba: {accuracy:.2f}")



    
def prediccion_modelo(desplazamiento, velocidad):
    entrada = np.array([[desplazamiento, velocidad]])
    if usar_arbol:  # Si se seleccionó el Árbol de Decisión
        try:
            check_is_fitted(arbol_model)  # Verifica si el modelo está entrenado
            return arbol_model.predict(entrada)[0] == 1
        except Exception as e:
            
            return False
    else:  # Si se seleccionó la Red Neuronal
        if nn_model is None:
            print("La Red Neuronal no está entrenada.")
            return False
        prediccion = nn_model.predict(entrada)
        return prediccion[0][0] > 0.4


# Definir colores para el menú
highlight_color = (29, 131, 72)  # Verde para resaltar opciones seleccionadas
text_color = (0, 0, 0)  # Negro para texto normal

def mostrar_menu():
    window.fill(WHITE)  # Usa un color sólido

    titulo = menu_font.render("Selecciona una opción:", True, text_color)
    opcion1 = menu_font.render("1. Modo Manual ", True, highlight_color if modo_manual else text_color)
    opcion2_arbol = menu_font.render("2. Modo Árbol de Decisión", True, highlight_color if usar_arbol else text_color)
    opcion3_red = menu_font.render("3. Modo Red Neuronal", True, highlight_color if not usar_arbol else text_color)
    salir = menu_font.render("4. Salir", True, text_color)

    # Dibuja las opciones en la pantalla
    window.blit(titulo, (WIDTH // 2 - titulo.get_width() // 2, 50))
    window.blit(opcion1, (WIDTH // 2 - opcion1.get_width() // 2, 120))
    window.blit(opcion2_arbol, (WIDTH // 2 - opcion2_arbol.get_width() // 2, 160))
    window.blit(opcion3_red, (WIDTH // 2 - opcion3_red.get_width() // 2, 200))
    window.blit(salir, (WIDTH // 2 - salir.get_width() // 2, 240))

    pygame.display.flip()


def seleccionar_modo_automatico():
    global usar_arbol
    if len(data) < 10:
        print("Por favor, recoge más datos en Modo Manual antes de usar el Modo Automático.")
        return False
    entrenar_modelos()
    return True

# Reiniciar posiciones
def reiniciar_juego():
    global player, bala, velocidad_bala, juego_activo
    player = pygame.Rect(50, HEIGHT - 70, 50, 50)
    bala = pygame.Rect(plant_x + 25, plant_y + 35, 30, 30)
    velocidad_bala = -random.randint(10, 20)  # Velocidad incrementada
    juego_activo = True

# Loop principal del juego
clock = pygame.time.Clock()
running = True
en_menu = True

while running:
    if en_menu:
        mostrar_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:  # Modo Manual
                    modo_manual = True
                    reiniciar_datos()  # Reiniciar los datos
                    reiniciar_modelos()  # Reiniciar los modelos entrenados
                    reiniciar_juego()
                    en_menu = False
                elif event.key == pygame.K_2:  # Modo Automático (Árbol de Decisión)
                    usar_arbol = True
                    if seleccionar_modo_automatico():
                        modo_manual = False
                        reiniciar_juego()
                        en_menu = False
                elif event.key == pygame.K_3:  # Modo Automático (Red Neuronal)
                    usar_arbol = False
                    if seleccionar_modo_automatico():
                        modo_manual = False
                        reiniciar_juego()
                        en_menu = False
                elif event.key == pygame.K_4:  # Salir
                    running = False
    elif juego_activo:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:  # Pausar y reanudar
                    paused = not paused
                elif event.key == pygame.K_ESCAPE:  # Regresar al menú
                    en_menu = True
                    paused = False

        if paused:
            # Mostrar mensaje de pausa
            pause_text = font.render("Juego en Pausa. Presiona P para continuar.", True, (0, 0, 0))
            window.blit(pause_text, (WIDTH // 2 - 200, HEIGHT // 2))
            pygame.display.flip()
            clock.tick(10)
            continue  # Saltar el resto del bucle mientras está pausado

        # Movimiento del jugador
        keys = pygame.key.get_pressed()
        if modo_manual:
            if keys[pygame.K_SPACE] and not is_jumping:
                is_jumping = True
                player_speed_y = jump_strength
                jump_sound.play()
        else:  # Modo automático
            desplazamiento = bala.x - player.x
            if prediccion_modelo(desplazamiento, abs(velocidad_bala)) and not is_jumping:
                is_jumping = True
                player_speed_y = jump_strength
                jump_sound.play()

        # Aplicar gravedad
        player_speed_y += gravity
        player.y += player_speed_y
        if player.y >= HEIGHT - 70:
            player.y = HEIGHT - 70
            is_jumping = False

        # Movimiento de la bala
        bala.x += velocidad_bala
        if bala.x < 0:
            bala.x = plant_x + 25
            bala.y = plant_y + 35
            velocidad_bala = -random.randint(10, 20)

        # Actualizar la animación de la planta
        frame_counter += 1
        if frame_counter >= frame_delay:
            current_frame = (current_frame + 1) % len(plant_frames)
            frame_counter = 0

        # Recolectar datos en modo manual
        if modo_manual:
            desplazamiento = bala.x - player.x
            if keys[pygame.K_SPACE]:  # Si se presiona la barra espaciadora (salto)
                data.append([desplazamiento, abs(velocidad_bala), 1])  # Registramos "saltar"
            else:  # Si no se presiona la barra espaciadora
                data.append([desplazamiento, abs(velocidad_bala), 0])  # Registramos "no saltar"

        # Detección de colisión
        if bala.colliderect(player):
            print("¡Colisión detectada!")
            juego_activo = False
            en_menu = True

        # Dibujar en pantalla
        window.fill(WHITE)
        window.blit(background_image, (0, 0))
        window.blit(player_image, (player.x, player.y))
        window.blit(ball_image, (bala.x, bala.y))
        window.blit(plant_frames[current_frame], (plant_x, plant_y))

        pygame.display.flip()
        clock.tick(30)

pygame.quit()
