import pygame
import socket
import ast
import tkinter as tk
from tkinter import messagebox
import config  # Importa as configurações do arquivo config.py

pygame.init()

# Configurações da tela
screen = pygame.display.set_mode((config.width, config.height))
pygame.display.set_caption("Snake Game Online")

# Direções
UP = "UP"
DOWN = "DOWN"
LEFT = "LEFT"
RIGHT = "RIGHT"
STOP = "STOP"

# Configurações do jogo
clock = pygame.time.Clock()

# Inicializa as cobras e comida (será atualizado do servidor)
player_snake = []
other_snake = []
food_pos = [0, 0]

# Função para mostrar a pontuação (opcional)
font_style = pygame.font.Font(None, 20)
waiting_font = pygame.font.Font(None, 50)
def show_popup_error(title, message):
    root = tk.Tk()
    root.withdraw()  # Esconder a janela principal
    root.attributes('-topmost', True)
    messagebox.showerror(title, message)

def show_popup(title, message):
    root = tk.Tk()
    root.withdraw()  # Esconder a janela principal
    root.attributes('-topmost', True)
    messagebox.showinfo(title, message)

def inicializa_client(player1_name, player2_name, partida, cd_player):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("35.212.236.121", 9999))
        #client.connect(("192.168.15.2", 9999))
        client.sendall(f"{player1_name},{player2_name},{partida},{cd_player}".encode('utf-8'))
        data = client.recv(2048).decode('utf-8')
        if data:
            received_player1_name, received_player2_name = data.split(',')
            print(f"[Client] Recebido do servidor: {received_player1_name}, {received_player2_name}")
        waiting_message = waiting_font.render("Aguardando conexão Player 2", True, config.branco)
        screen.fill(config.preto)
        screen.blit(waiting_message, (
            (config.width - waiting_message.get_width()) // 2,
            (config.height - waiting_message.get_height()) // 2
        ))
        pygame.display.update()
        winner = game_loop(client)
        if winner is not None:
            return winner
    except Exception as e:
        show_popup_error('Error',f"Erro ao conectar ao servidor: {e}")


def show_score(player_name, score, x, y):
    value = font_style.render(f"{player_name}: {score}", True, config.branco)
    screen.blit(value, [x, y])

def game_loop(client):
    global player_snake, other_snake, food_pos
    winner = None
    game_state = None
    running = True
    direction = STOP

    player1_score = 0
    player2_score = 0
    player1_name = ''
    player2_name = ''

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    direction = UP
                elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    direction = DOWN
                elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    direction = LEFT
                elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    direction = RIGHT
                elif event.key == pygame.K_ESCAPE:
                    running = False
                    return

        try:
            # Envia a direção para o servidor
            client.sendall(direction.encode('utf-8'))

            # Recebe o estado do jogo do servidor
            data = client.recv(2048).decode('utf-8')

            if len(data) == 0:
                print("Nenhum dado recebido do servidor")
                break

            try:
                game_state = ast.literal_eval(data)
                print("Estado do jogo recebido do servidor:", game_state)
            except SyntaxError as e:
                print("Erro ao decodificar o estado do jogo:", e)
                break

            if game_state:
                player_snake = game_state["player1"]["snake"]
                player1_score = game_state["player1"]["score"]
                other_snake = game_state["player2"]["snake"]
                player2_score = game_state["player2"]["score"]
                food_pos = game_state["food_pos"]
                player1_name = game_state["player1"]["name"]
                player2_name = game_state["player2"]["name"]
                if game_state["player2"]["venceu"]:
                   winner = game_state["player2"]["name"]
                elif game_state["player1"]["venceu"]:
                    winner = game_state["player1"]["name"]
                else:
                    winner = ""

        except Exception as e:
            print(f"Erro ao comunicar com o servidor: {e}")
            break

        # Desenha tudo na tela
        screen.fill(config.preto)

        for block in player_snake:
            pygame.draw.rect(screen, config.verde, pygame.Rect(block[0], block[1], config.snake_block, config.snake_block))
        for block in other_snake:
            pygame.draw.rect(screen, config.azul, pygame.Rect(block[0], block[1], config.snake_block, config.snake_block))
        pygame.draw.rect(screen, config.vermelho, pygame.Rect(food_pos[0], food_pos[1], config.snake_block, config.snake_block))

        # Mostrar as pontuações
        show_score(player1_name, player1_score, 10, 10)
        show_score(player2_name, player2_score, config.width - 150, 10)  # Ajuste a posição conforme necessário

        # Atualiza a tela
        pygame.display.update()
        clock.tick(config.snake_speed)

    client.close()  # Fecha a conexão com o servidor
    print("Cliente desconectado")
    return winner, game_state


if __name__ == "__main__":
    game_loop()
