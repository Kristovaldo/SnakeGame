---
title: Servidor(Server.py)
---
# Introduction

This document will walk you through the implementation of the server logic for a multiplayer snake game.

The feature involves:

1. Initializing server and player states.
2. Handling player connections.
3. Managing game state and player interactions.
4. Updating the database with game results.

# Initializing server and player states

<SwmSnippet path="/server.py" line="9">

---

We start by defining the initial state of the server and players. This includes tracking connected players, player connections, and the initial position of the food.

```

players_connected = [False, False]
player_connections = {}
server_running = True

food_pos = [random.randrange(1, (width // snake_block)) * snake_block,
            random.randrange(1, (height // snake_block)) * snake_block]
```

---

</SwmSnippet>

<SwmSnippet path="/server.py" line="16">

---

Next, we define the initial state for each player, including their snake's position, direction, score, and other relevant attributes.

```

players = {
    "player1": {"snake": [[100, 100]], "direction": "STOP", "score": 0, "name": "","id_jogador": 0, "venceu": False},
    "player2": {"snake": [[200, 200]], "direction": "STOP", "score": 0, "name": "", "id_jogador": 0, "venceu": False}
}
vencedor = False
```

---

</SwmSnippet>

# Handling player connections

<SwmSnippet path="/server.py" line="228">

---

The <SwmToken path="/server.py" pos="228:2:2" line-data="def main():">`main`</SwmToken> function sets up the server to listen for incoming connections. It binds the server to an IP and port and starts listening for up to 2 connections.

```
def main():
    global players_connected, player_connections, server_running
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 9999))
    server.listen(2)
    server_ip, server_port = server.getsockname()
    print(f"[Main] Servidor iniciado no IP {server_ip} na porta {server_port}, aguardando conexões...", flush=True)
```

---

</SwmSnippet>

<SwmSnippet path="/server.py" line="235">

---

We then check for player connections. If fewer than 2 players connect within a minute, the server shuts down.

```

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
```

---

</SwmSnippet>

<SwmSnippet path="/server.py" line="247">

---

When a player connects, we assign them a player slot and start a new thread to handle their connection.

```

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
```

---

</SwmSnippet>

<SwmSnippet path="/server.py" line="259">

---

We update the list of connected players and start a thread to handle communication with the client.

```

                players_connected[player_count - 1] = True
                player_connections[player] = client_socket

                client_handler = threading.Thread(target=handle_client, args=(client_socket, player))
                threads.append(client_handler)
                client_handler.start()
```

---

</SwmSnippet>

<SwmSnippet path="/server.py" line="266">

---

Once both players are connected, the game loop continues to run while the server is active.

```

                if player_count == 2:
                    break

            except socket.timeout:
                continue

        while server_running and all(players_connected):
            time.sleep(1)
```

---

</SwmSnippet>

# Managing game state and player interactions

<SwmSnippet path="/server.py" line="185">

---

We handle snake movement and check for collisions between players. If a collision is detected, we determine the winner based on their scores and stop the server.

```

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
```

---

</SwmSnippet>

<SwmSnippet path="/server.py" line="213">

---

We also check if a player has moved out of bounds. If so, the other player is declared the winner, and the server stops.

```

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
```

---

</SwmSnippet>

# Updating the database with game results

<SwmSnippet path="/server.py" line="36">

---

When the game ends, we update the database with the results. We insert a new game record and update the scores for each player.

```
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
```

---

</SwmSnippet>

<SwmSnippet path="/server.py" line="65">

---

We also update the game status and the winner in the database.

```
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
```

---

</SwmSnippet>

# Finalizing and closing the server

<SwmSnippet path="/server.py" line="275">

---

Finally, we handle the server shutdown process. If a winner is determined, we update the database accordingly. We then close all threads and the server socket.

```

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
```

---

</SwmSnippet>

<SwmSnippet path="/server.py" line="302">

---

The server is closed gracefully, and the program exits.

```
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        server_running = False
        print("\n[Main] Servidor interrompido pelo usuário.", flush=True)
        for sock in player_connections.values():
            sock.close()

```

---

</SwmSnippet>

This concludes the walkthrough of the server implementation for the multiplayer snake game.

<SwmMeta version="3.0.0" repo-id="Z2l0aHViJTNBJTNBU25ha2VHYW1lJTNBJTNBS3Jpc3RvdmFsZG8=" repo-name="SnakeGame"><sup>Powered by [Swimm](https://app.swimm.io/)</sup></SwmMeta>
