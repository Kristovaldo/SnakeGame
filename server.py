import socket
import threading
import random
import time
import mysql.connector
from pygame.examples.midi import null_key

import config
from config import width, height, snake_block

players_connected = [False, False]
player_connections = {}
server_running = True

food_pos = [random.randrange(1, (width // snake_block)) * snake_block,
            random.randrange(1, (height // snake_block)) * snake_block]

players = {
    "player1": {"snake": [[100, 100]], "direction": "STOP", "score": 0, "name": "","id_jogador": 0, "venceu": False},
    "player2": {"snake": [[200, 200]], "direction": "STOP", "score": 0, "name": "", "id_jogador": 0, "venceu": False}
}
vencedor = False

def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host="snakegame-python-estacio.cfaemws4kovz.us-east-1.rds.amazonaws.com",
            port=3306,
            user="admin",
            password="Teste123",
            database="SnakePythonDB"
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")

def insere_partic_partida(partida, cd_player1, cd_player2):
    try:
        global cd_participa
        # Conectar ao banco de dados
        connection = connect_to_db()
        cursor = connection.cursor()

        # Buscar o código da última partida
        query = "SELECT MAX(cd_participa) FROM PARTIC_PARTIDA"
        cursor.execute(query)
        result = cursor.fetchone()
        cd_participa = 0
        if result[0]:
            cd_participa = result[0]
        cd_participa += 1

        # Inserir nova partida na tabela PARTIC_PARTIDA
        query = "INSERT INTO PARTIC_PARTIDA(cd_participa ,fk_PARTIDA_cd_partida, fk_cd_player1, fk_cd_player2) value (%s, %s, %s, %s)"
        cursor.execute(query, (cd_participa, partida, cd_player1, cd_player2))

        # Confirmar as alterações no banco de dados
        connection.commit()

        # Fechar o cursor e a conexão
        cursor.close()
        connection.close()
    except mysql.connector.Error as err:
        print(err)

def update_partic_partida(partida, sit_partida, id_player):
    try:
        # Conectar ao banco de dados
        connection = connect_to_db()
        cursor = connection.cursor()

        # Inserir nova partida na tabela PARTIC_PARTIDA
        query = ("UPDATE PARTIC_PARTIDA SET nponts_player1 = %s, nponts_player2 = %s "
                 "WHERE cd_participa = %s")
        cursor.execute(query, (int(players["player1"]["score"]), int(players["player2"]["score"]), cd_participa,))
        # Confirmar as alterações no banco de dados
        connection.commit()

        query = "UPDATE PARTIDAS SET dt_fim = CURRENT_TIMESTAMP, cd_vencedor = %s, ctpo_sit = %s WHERE cd_partida = %s"
        if id_player == 0:
            id_player = None
        cursor.execute(query, (id_player,sit_partida,partida,))

        # Confirmar as alterações no banco de dados
        connection.commit()

        # Fechar o cursor e a conexão
        cursor.close()
        connection.close()
    except mysql.connector.Error as err:
        print(err)

def handle_client(client_socket, player):
    global food_pos, server_running, cd_partida
    try:
        data = client_socket.recv(2048).decode('utf-8')
        if data:
            player1_name, player2_name, cd_partida, cd_player = data.split(',')
            players[player]["name"] = player1_name
            players[player]["id_jogador"] = cd_player

            #print(f"[Handle Client] Nomes dos jogadores recebidos: {player1_name}, {player2_name}.", flush=True)

            # Enviar os nomes dos jogadores de volta para o cliente
            client_socket.sendall(f"{player1_name},{player2_name}".encode('utf-8'))

        print(f"[Handle Client] Iniciando manipulação do cliente {player}", flush=True)
        if player == "player2":
            insere_partic_partida(cd_partida, players["player1"]["id_jogador"],players["player2"]["id_jogador"])

        while server_running:
            if not all(players_connected):
                continue
            try:
                client_socket.settimeout(1)
                data = client_socket.recv(2048).decode('utf-8')
            except socket.timeout:
                continue

            if not data:
                print(f"[Handle Client] Nenhum dado recebido de {player}. Desconectando...", flush=True)
                break
            print(f"[Handle Client] Recebido do {player}: {data}", flush=True)

            players[player]["direction"] = data
            update_snake(players[player], players)
            if abs(players[player]["snake"][0][0] - food_pos[0]) < snake_block and abs(
                    players[player]["snake"][0][1] - food_pos[1]) < snake_block:
                food_pos = [random.randrange(1, (width // snake_block)) * snake_block,
                            random.randrange(1, (height // snake_block)) * snake_block]
                players[player]["score"] += 10
                players[player]["snake"].append(players[player]["snake"][-1][:])
            game_state = {"player1": players["player1"], "player2": players["player2"], "food_pos": food_pos}
            game_state_str = str(game_state)
            client_socket.sendall(game_state_str.encode('utf-8'))
            print(f"[Handle Client] Enviando estado do jogo para {player}: {game_state}", flush=True)

    except Exception as e:
        print(f"Erro ao comunicar com o cliente {player}: {e}", flush=True)
    finally:
        client_socket.close()
        players[player]["direction"] = "STOP"
        players_connected[int(player[-1]) - 1] = False
        print(f"[Handle Client] {player} desconectou.", flush=True)


def is_out_of_bounds(snake):
    head = snake[0]
    if head[0] < 0 or head[0] >= config.width or head[1] < 0 or head[1] >= config.height:
        return True
    return False


def check_collision_players(player1, player2):
    for segment in player2:
        if player1[0] == segment:
            return True
    for segment in player1:
        if player2[0] == segment:
            return True
    return False


def check_collision_self(player):
    for segment in player[1:]:
        if player[0] == segment:
            return True
    return False


def update_snake(player, players):
    global server_running, vencedor
    snake = player["snake"]
    direction = player["direction"]

    if direction == "UP":
        new_head = [snake[0][0], snake[0][1] - snake_block]
    elif direction == "DOWN":
        new_head = [snake[0][0], snake[0][1] + snake_block]
    elif direction == "LEFT":
        new_head = [snake[0][0] - snake_block, snake[0][1]]
    elif direction == "RIGHT":
        new_head = [snake[0][0] + snake_block, snake[0][1]]
    else:
        return

    snake.insert(0, new_head)
    snake.pop()

    player1_snake = players["player1"]["snake"]
    player2_snake = players["player2"]["snake"]

    if check_collision_players(player1_snake, player2_snake):
        print("[Update Snake] Colisão detectada entre player1 e player2", flush=True)
        if players["player1"]["score"] > players["player2"]["score"]:
            players["player1"]["venceu"] = True
        elif players["player2"]["score"] > players["player1"]["score"]:
            players["player2"]["venceu"] = True
        vencedor = True
        server_running = False
        return

    #if check_collision_self(player1_snake):
    #    print("[Update Snake] Player 1 colidiu com ele mesmo", flush=True)
    #    vencedor, players["player2"]["venceu"]  = True
    #    server_running = False
    #    return

    #if check_collision_self(player2_snake):
    #    print("[Update Snake] Player 2 colidiu com ele mesmo", flush=True)
    #    vencedor, players["player1"]["venceu"]  = True
    #    server_running = False
    #    return

    if is_out_of_bounds(player1_snake):
        print("[Update Snake] Player1 saiu da tela", flush=True)
        vencedor = True
        players["player2"]["venceu"]  = True
        server_running = False
        return
    if is_out_of_bounds(player2_snake):
        print("[Update Snake] Player2 saiu da tela", flush=True)
        vencedor = True
        players["player1"]["venceu"]  = True
        server_running = False
        return


def main():
    global players_connected, player_connections, server_running
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 9999))
    server.listen(2)
    server_ip, server_port = server.getsockname()
    print(f"[Main] Servidor iniciado no IP {server_ip} na porta {server_port}, aguardando conexões...", flush=True)

    player_count = 0
    threads = []

    def check_connections():
        global server_running
        time.sleep(60)
        if sum(players_connected) < 2:
            print("[Main] Não há 2 conexões em 1 minuto. Encerrando o servidor...", flush=True)
            server_running = False
            for sock in player_connections.values():
                sock.close()

    connection_checker = threading.Thread(target=check_connections)
    connection_checker.start()

    try:
        while server_running:
            server.settimeout(1)
            try:
                client_socket, addr = server.accept()
                player_count += 1
                player = f"player{player_count}"
                print(f"[Main] Conexão aceita de {addr}. Atribuído a {player}.", flush=True)

                players_connected[player_count - 1] = True
                player_connections[player] = client_socket

                client_handler = threading.Thread(target=handle_client, args=(client_socket, player))
                threads.append(client_handler)
                client_handler.start()

                if player_count == 2:
                    break

            except socket.timeout:
                continue

        while server_running and all(players_connected):
            time.sleep(1)

    finally:
        if vencedor:
            if players["player1"]["venceu"]:
                id_vencedor = int(players["player1"]["id_jogador"])
            elif players["player2"]["venceu"]:
                id_vencedor = int(players["player2"]["id_jogador"])
            else:
                id_vencedor = 0

            if id_vencedor > 0:
                update_partic_partida(cd_partida,1,id_vencedor)
            else:
                update_partic_partida(cd_partida, 1, 0)
        else:
            update_partic_partida(cd_partida, 3, 0)

        print("[Main] Encerrando o servidor...", flush=True)
        server_running = False
        for t in threads:
            t.join(timeout=1)

        server.close()
        print("[Main] Servidor fechado.", flush=True)
        exit()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        server_running = False
        print("\n[Main] Servidor interrompido pelo usuário.", flush=True)
        for sock in player_connections.values():
            sock.close()
