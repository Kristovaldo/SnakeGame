import socket
import threading
import random
from config import width, height, snake_block  # Importa as configurações do arquivo config.py

# Configurações do jogo
players_connected = [False, False]  # Lista para rastrear o status dos jogadores conectados
player_connections = {}  # Dicionário para armazenar os sockets dos jogadores
server_running = True  # Variável para verificar se o servidor está em execução

# Inicializa a comida
food_pos = [random.randrange(1, (width // snake_block)) * snake_block,
            random.randrange(1, (height // snake_block)) * snake_block]

# Armazena as direções, posições e scores das cobras
players = {
    "player1": {"snake": [[100, 100]], "direction": "STOP", "score": 0},
    "player2": {"snake": [[200, 200]], "direction": "STOP", "score": 0}
}


def handle_client(client_socket, player):
    global food_pos, server_running
    while server_running:
        try:
            # Aguarda ambos os jogadores estarem conectados
            if not all(players_connected):
                continue

            data = client_socket.recv(2048).decode('utf-8')
            if not data:
                break

            print(f"Recebido do {player}: {data}")
            players[player]["direction"] = data
            update_snake(players[player]["snake"], players[player]["direction"])

            # Verifica colisões com a comida
            if abs(players[player]["snake"][0][0] - food_pos[0]) < snake_block and abs(
                    players[player]["snake"][0][1] - food_pos[1]) < snake_block:
                food_pos = [random.randrange(1, (width // snake_block)) * snake_block,
                            random.randrange(1, (height // snake_block)) * snake_block]
                players[player]["snake"].append(players[player]["snake"][-1][:])
                players[player]["score"] += 10  # Incrementa o score do jogador

            # Envia a atualização para os clientes
            game_state = {"player1": players["player1"], "player2": players["player2"], "food_pos": food_pos}
            game_state_str = str(game_state)
            client_socket.sendall(game_state_str.encode('utf-8'))
            print(f"Enviando estado do jogo para {player}: {game_state}")
        except Exception as e:
            print(f"Erro ao comunicar com o cliente {player}: {e}")
            break

    client_socket.close()
    players[player]["direction"] = "STOP"
    players_connected[int(player[-1]) - 1] = False
    server_running = False
    print(f"{player} desconectou. Servidor encerrado")
    if player_connections:
        list(player_connections.values())[0].close()
        if len(player_connections) > 1:
            list(player_connections.values())[1].close()


def update_snake(snake, direction):
    if direction == "UP":
        new_head = [snake[0][0], snake[0][1] - snake_block]
    elif direction == "DOWN":
        new_head = [snake[0][0], snake[0][1] + snake_block]
    elif direction == "LEFT":
        new_head = [snake[0][0] - snake_block, snake[0][1]]
    elif direction == "RIGHT":
        new_head = [snake[0][0] + snake_block, snake[0][1]]

    if direction != "STOP":
        snake.insert(0, new_head)
        snake.pop()


def main():
    global players_connected, player_connections, server_running
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 9999))
    server.listen(2)
    # Obtendo o IP do servidor
    server_ip, server_port = server.getsockname()
    print(f"Servidor iniciado no IP {server_ip} na porta {server_port}, aguardando conexões...")

    player_count = 0
    threads = []
    while server_running and player_count < 2:
        client_socket, addr = server.accept()
        player_count += 1
        player = f"player{player_count}"
        print(f"Conexão aceita de {addr}. Atribuído a {player}.")

        players_connected[player_count - 1] = True
        player_connections[player] = client_socket

        client_handler = threading.Thread(target=handle_client, args=(client_socket, player))
        threads.append(client_handler)
        client_handler.start()

    # Aguardar todas as threads concluírem antes de encerrar o servidor
    for t in threads:
        t.join()

    server.close()


if __name__ == "__main__":
    main()
