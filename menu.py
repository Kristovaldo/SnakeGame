import pygame
import sys
import mysql.connector
import re
import tkinter as tk
from tkinter import messagebox
import paramiko
from client import inicializa_client, game_loop
from game_offline import rodar_jogo
import config
pygame.init()

# Inicializar Pygame
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Snake Game")

# Cores
white = config.branco
black = config.preto
gray = (200, 200, 200)
active_color = pygame.Color('dodgerblue2')
inactive_color = pygame.Color('lightskyblue3')
bg = pygame.image.load("BG.jpg")
# Fonte
font = pygame.font.Font("Unlock-Regular.ttf", 32)
fontPlay = pygame.font.Font("Unlock-Regular.ttf", 50)

# Variável Global para Armazenar Nickname do Usuário Logado
logged_in_user = None

# Número de entradas por página
entries_per_page = 10

def draw_text(surface, text, pos, color=black):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, pos)

def draw_text2(surface, text, pos, color=black):
    text_surface = fontPlay.render(text, True, color)
    surface.blit(text_surface, pos)

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
        sys.exit(1)

def update_score(new_score):
    global pont
    if new_score > pont:
        try:
            pont = new_score
            connection = connect_to_db()
            cursor = connection.cursor()

            query = "UPDATE PLAYER SET nmaior_pontc = %s WHERE cd_player = %s"
            cursor.execute(query,(new_score, cd_player))
            connection.commit()
            cursor.close()
            connection.close()
        except mysql.connector.Error as err:
            show_popup_error("Erro", f"Falha ao buscar dados: {translate_error(err)}")

def fetch_leaderboards_data():
    try:
        connection = connect_to_db()
        cursor = connection.cursor()

        query = "SELECT nickname, nmaior_pontc FROM PLAYER ORDER BY nmaior_pontc DESC LIMIT 100"
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        connection.close()

        return result
    except mysql.connector.Error as err:
        show_popup_error("Erro", f"Falha ao buscar dados: {translate_error(err)}")
        return []

def main_menu():
    # Dimensões dos botões
    button_width = 150
    button_height = 50

    # Criar botões
    play_button = pygame.Rect(300, 200, button_width +50, button_height+ 50)
    login_button = pygame.Rect(0, 0, button_width, button_height)
    register_button = pygame.Rect(650, 0, button_width, button_height)
    credits_button = pygame.Rect(350, 550, button_width, button_height)
    leaderboards_button = pygame.Rect(0, 550, button_width+90, button_height)
    quit_button = pygame.Rect(650, 550, button_width, button_height)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.collidepoint(event.pos):
                    play_game()
                if login_button.collidepoint(event.pos) and not logged_in_user:
                    login_screen()
                if register_button.collidepoint(event.pos)and not logged_in_user:
                    register_screen()
                #if credits_button.collidepoint(event.pos):
                #    credits_screen()
                if leaderboards_button.collidepoint(event.pos):
                    leaderboards_screen()
                if quit_button.collidepoint(event.pos):
                    running = False
                    pygame.quit()
                    sys.exit()

        screen.fill(white)
        screen.blit(bg, (0 ,0))

        pygame.draw.rect(screen, black, play_button, 2)
        if logged_in_user is None:
            pygame.draw.rect(screen, black, login_button, 2)
            pygame.draw.rect(screen, black, register_button, 2)
        #pygame.draw.rect(screen, black, credits_button, 2)
        pygame.draw.rect(screen, black, leaderboards_button, 2)
        pygame.draw.rect(screen, black, quit_button, 2)

        draw_text2(screen, "Play", (play_button.x + 40, play_button.y + 20))
        if logged_in_user is None:
            draw_text(screen, "Login", (login_button.x + 15, login_button.y + 10))
            draw_text(screen, "Register", (register_button.x + 5, register_button.y + 10))
        #draw_text(screen, "Credits", (credits_button.x + 15, credits_button.y + 10))
        draw_text(screen, "Leaderboards", (leaderboards_button.x + 5, leaderboards_button.y + 10))
        draw_text(screen, "Quit", (quit_button.x + 40, quit_button.y + 10))

        # Exibir nickname do usuário logado
        if logged_in_user:
            draw_text(screen, f"{logged_in_user}", (10, 10))
            draw_text(screen, f"{pont}", (650, 10))

        pygame.display.flip()


def translate_error(err):
    if err.errno == mysql.connector.errorcode.ER_DUP_ENTRY:
        return "E-mail já cadastrado."
    elif err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
        return "O banco de dados especificado não existe."
    elif err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
        return "Credenciais de acesso ao banco de dados inválidas."
    else:
        return "Ocorreu um erro desconhecido."


def show_popup(title, message):
    root = tk.Tk()
    root.withdraw()  # Esconder a janela principal
    root.attributes('-topmost', True)
    messagebox.showinfo(title, message)


def show_popup_error(title, message):
    root = tk.Tk()
    root.withdraw()  # Esconder a janela principal
    root.attributes('-topmost', True)
    messagebox.showerror(title, message)

def check_server_running(ssh):
    stdin, stdout, stderr = ssh.exec_command('pgrep -f server.py')
    #stdin, stdout, stderr = ssh.exec_command('ls')
    print(stdout.read().decode())
    if not stdout.read().decode():
        return False
    return True

def winner_screen(winner):
    back_button = pygame.Rect(650, 550, 120, 50)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    return

        screen.fill(white)
        screen.blit(bg, (0, 0))
        if winner == "":
            draw_text(screen, "Empate!", (400, 300))
        else:
            draw_text(screen, f"{winner} Venceu!", (200, 300))
        pygame.draw.rect(screen, black, back_button, 2)
        draw_text(screen, "Back", (back_button.x + 20, back_button.y + 10))

        # Exibir nickname do usuário logado
        if logged_in_user:
            draw_text(screen, f"{logged_in_user}", (10, 10))
            draw_text(screen, f"{pont}", (650, 10))

        pygame.display.flip()
def connect_vm_ssh():
    # Definindo as informações da conexão
    ip_address = '35.212.236.121'
    username = 'chuaum141'
    private_key_path = 'keyVM-open'  # Substitua pelo caminho correto da sua chave privada

    # Cria um cliente SSH
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Aceita automaticamente a chave do servidor

    try:
        # Carrega a chave privada
        private_key = paramiko.RSAKey.from_private_key_file(private_key_path)
        ssh.connect(ip_address, username=username, pkey=private_key)
        if not check_server_running(ssh):
            ssh.exec_command('nohup python3 ./server.py > server.log 2>&1 &')
        try:
            # Conectar ao banco de dados
            connection = connect_to_db()
            cursor = connection.cursor()

            # Buscar o código da última partida
            query = "SELECT MAX(cd_partida) FROM PARTIDAS"
            cursor.execute(query)
            result = cursor.fetchone()

            cd_partida = 0
            if result[0]:
                cd_partida = result[0]
            cd_partida += 1

            # Inserir nova partida na tabela PARTIDAS
            query = "INSERT INTO PARTIDAS (cd_partida, dt_inic, dt_fim, ctpo_sit, cd_vencedor) VALUES (%s, CURRENT_TIMESTAMP, NULL, 3, NULL)"
            cursor.execute(query, (cd_partida,))

            # Confirmar as alterações no banco de dados
            connection.commit()

            # Fechar o cursor e a conexão
            cursor.close()
            connection.close()

            return cd_partida

        except mysql.connector.Error as err:
            # Tratar mensagens de erro
            error_message = translate_error(err)
            # Exibir popup de erro
            show_popup_error("Erro", f"Falha ao registrar: {error_message}")
    except paramiko.AuthenticationException:
        print("Falha na autenticação, verifique suas credenciais")
    except paramiko.SSHException as sshException:
        print(f"Erro ao se conectar ao servidor SSH: {sshException}")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
    finally:
        # Fecha a conexão SSH
        ssh.close()

def play_game():
    back_button = pygame.Rect(650, 550, 120, 50)
    play_off_button = pygame.Rect(300, 250, 220, 50)
    play_on_button = pygame.Rect(300, 350, 220, 50)
    player1_name = logged_in_user
    player2_name = ""
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    return
                if play_off_button.collidepoint(event.pos):
                    rodar_jogo()
                if play_on_button.collidepoint(event.pos) and logged_in_user:
                    partida = connect_vm_ssh()
                    data = inicializa_client(player1_name, player2_name, partida, cd_player)
                    if data is not None:
                        winner, players = data
                        if players is not None and "player1" in players and "id_jogador" in players["player1"]:
                            if int(players["player1"]["id_jogador"]) == cd_player:
                                update_score(int(players["player1"]["score"]))
                            else:
                                update_score(int(players["player2"]["score"]))
                            winner_screen(winner)
                        else:
                            show_popup("Server", "Servidor Encerrado!")

        screen.fill(white)
        screen.blit(bg, (0, 0))

        pygame.draw.rect(screen, black, play_off_button, 2)
        draw_text(screen, "Play Offline", (play_off_button.x + 20, play_off_button.y + 10))

        if logged_in_user:
            pygame.draw.rect(screen, black, play_on_button, 2)
            draw_text(screen, "Play Online", (play_on_button.x + 20, play_on_button.y + 10))

        pygame.draw.rect(screen, black, back_button, 2)
        draw_text(screen, "Back", (back_button.x + 20, back_button.y + 10))

        # Exibir nickname do usuário logado
        if logged_in_user:
            draw_text(screen, f"{logged_in_user}", (10, 10))
            draw_text(screen, f"{pont}", (650, 10))

        pygame.display.flip()


def leaderboards_screen():
    leaderboards_data = fetch_leaderboards_data()
    back_button = pygame.Rect(650, 550, 120, 50)
    next_button = pygame.Rect(680, 500, 80, 40)
    prev_button = pygame.Rect(20, 500, 80, 40)

    page = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    return

                if next_button.collidepoint(event.pos):
                    if (page + 1) * entries_per_page < len(leaderboards_data):
                        page += 1

                if prev_button.collidepoint(event.pos):
                    if page > 0:
                        page -= 1

        screen.fill(white)
        screen.blit(bg, (0, 0))

        # Desenhar botões
        pygame.draw.rect(screen, black, back_button, 2)
        draw_text(screen, "Back", (back_button.x + 20, back_button.y + 10))

        pygame.draw.rect(screen, black, next_button, 2)
        draw_text(screen, "Next", (next_button.x + 10, next_button.y + 5))

        pygame.draw.rect(screen, black, prev_button, 2)
        draw_text(screen, "Prev", (prev_button.x + 10, prev_button.y + 5))

        # Desenhar cabeçalhos da tabela
        draw_text(screen, "Nickname", (150, 50))
        draw_text(screen, "Maior Pontuação", (500, 50))

        # Desenhar dados da tabela
        start_index = page * entries_per_page
        end_index = start_index + entries_per_page

        for i, (nickname, score) in enumerate(leaderboards_data[start_index:end_index]):
            y_pos = 100 + i * 40
            order_number = start_index + i + 1
            draw_text(screen, str(order_number), (50, y_pos))  # Exibir ordem do registro
            draw_text(screen, nickname, (150, y_pos))
            draw_text(screen, str(score), (500, y_pos))

        # Exibir nickname do usuário logado
        if logged_in_user:
            draw_text(screen, f"{logged_in_user}", (10, 10))
            draw_text(screen, f"{pont}", (650, 10))

        pygame.display.flip()


def login_screen():
    email_input = pygame.Rect(300, 200, 400, 32)
    password_input = pygame.Rect(300, 250, 400, 32)
    login_button = pygame.Rect(350, 300, 120, 50)  # Botão de Login
    back_button = pygame.Rect(650, 550, 120, 50)

    email_text = ''
    password_text = ''

    active_input = None
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if email_input.collidepoint(event.pos):
                    active_input = 'email'
                elif password_input.collidepoint(event.pos):
                    active_input = 'password'
                elif login_button.collidepoint(event.pos):
                    if email_text == '' or password_text == '':
                        show_popup_error("Erro", "Preencha todos os campos.")
                    else:
                        if login_user(email_text, password_text):
                            show_popup("Sucesso", "Login realizado com sucesso!")
                            return
                        else:
                            show_popup_error("Erro", "E-mail ou senha inválidos.")
                elif back_button.collidepoint(event.pos):
                    return
                else:
                    active_input = None
            if event.type == pygame.KEYDOWN and active_input:
                if event.key == pygame.K_BACKSPACE:
                    if active_input == 'email':
                        email_text = email_text[:-1]
                    elif active_input == 'password':
                        password_text = password_text[:-1]
                else:
                    if active_input == 'email':
                        email_text += event.unicode
                    elif active_input == 'password':
                        password_text += event.unicode

        screen.fill(white)
        screen.blit(bg, (0, 0))
        draw_text(screen, "Login Screen", (300, 150))

        # Desenha caixa de e-mail
        draw_text(screen, "Email:", (190, email_input.y + 5))
        pygame.draw.rect(screen, active_color if active_input == 'email' else inactive_color, email_input, 2)
        draw_text(screen, email_text, (email_input.x, email_input.y))

        # Desenha caixa de senha
        draw_text(screen, "Senha:", (180, password_input.y + 5))
        pygame.draw.rect(screen, active_color if active_input == 'password' else inactive_color, password_input, 2)
        draw_text(screen, "*" * len(password_text), (password_input.x + 5, password_input.y + 5), color=black)

        # Desenha botão de login
        pygame.draw.rect(screen, black, login_button, 2)
        draw_text(screen, "Login", (login_button.x + 15, login_button.y + 10))

        pygame.draw.rect(screen, black, back_button, 2)
        draw_text(screen, "Back", (back_button.x + 20, back_button.y + 10))

        pygame.display.flip()


def register_user(nickname, email, password):
    try:
        connection = connect_to_db()
        cursor = connection.cursor()

        # Inserir usuário na tabela Player
        query = "INSERT INTO PLAYER (email_player, nickname, password, dt_cadastro) VALUES (%s, %s, %s, CURRENT_DATE)"
        cursor.execute(query, (email, nickname, password))
        connection.commit()
        cursor.close()
        connection.close()

        # Exibir popup de sucesso
        show_popup("Sucesso", "Registrado com sucesso!")
        return True
    except mysql.connector.Error as err:
        # Tratar mensagens de erro
        error_message = translate_error(err)
        # Exibir popup de erro
        show_popup_error("Erro", f"Falha ao registrar: {error_message}")
        return False


def register_screen():
    label_offset_y = 5  # Distância vertical entre a label e o campo de entrada
    email_input = pygame.Rect(300, 150, 400, 32)
    nickname_input = pygame.Rect(300, 200, 400, 32)
    password_input = pygame.Rect(300, 250, 400, 32)
    confirm_password_input = pygame.Rect(300, 300, 400, 32)
    register_button = pygame.Rect(340, 350, 160, 50)  # Botão Registrar
    back_button = pygame.Rect(650, 550, 120, 50)

    email_text = ''
    nickname_text = ''
    password_text = ''
    confirm_password_text = ''

    active_input = None
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if email_input.collidepoint(event.pos):
                    active_input = 'email'
                elif nickname_input.collidepoint(event.pos):
                    active_input = 'nickname'
                elif password_input.collidepoint(event.pos):
                    active_input = 'password'
                elif confirm_password_input.collidepoint(event.pos):
                    active_input = 'confirm_password'
                elif register_button.collidepoint(event.pos):
                    if email_text == '' or nickname_text == '' or password_text == '' or confirm_password_text == '':
                        show_popup_error("Erro", "Preencha todos os campos.")
                    else:
                        if validate_email(email_text):
                            if validate_field(nickname_text, 15):
                                if validate_field(password_text, 20):
                                    if password_text == confirm_password_text:
                                        if register_user(nickname_text, email_text, password_text):
                                           return
                                    else:
                                        show_popup_error("Erro", "As senhas não coincidem.")
                                else:
                                    show_popup_error("Erro", "Senha inválida. Máximo de 20 caracteres e sem acentos.")
                            else:
                                show_popup_error("Erro", "Nickname inválido. Máximo de 15 caracteres e sem acentos.")
                        else:
                            show_popup_error("Erro", "E-mail inválido.")
                elif back_button.collidepoint(event.pos):
                    return
                else:
                    active_input = None
            if event.type == pygame.KEYDOWN and event.key != pygame.K_RETURN and active_input:
                if event.key == pygame.K_BACKSPACE:
                    if active_input == 'email':
                        email_text = email_text[:-1]
                    elif active_input == 'nickname':
                        nickname_text = nickname_text[:-1]
                    elif active_input == 'password':
                        password_text = password_text[:-1]
                    elif active_input == 'confirm_password':
                        confirm_password_text = confirm_password_text[:-1]
                else:
                    if active_input == 'email':
                        email_text += event.unicode
                    elif active_input == 'nickname':
                        nickname_text += event.unicode
                    elif active_input == 'password':
                        password_text += event.unicode
                    elif active_input == 'confirm_password':
                        confirm_password_text += event.unicode


        screen.fill(white)
        screen.blit(bg, (0, 0))
        draw_text(screen, "Register Screen", (300, 100))

        # Desenha rótulos e caixas de entrada
        draw_text(screen, "Email:", (190, email_input.y + label_offset_y))
        pygame.draw.rect(screen, active_color if active_input == 'email' else inactive_color, email_input, 2)
        draw_text(screen, email_text, (email_input.x, email_input.y))

        draw_text(screen, "Nickname:", (115, nickname_input.y + label_offset_y))
        pygame.draw.rect(screen, active_color if active_input == 'nickname' else inactive_color, nickname_input, 2)
        draw_text(screen, nickname_text, (nickname_input.x, nickname_input.y))

        draw_text(screen, "Senha:", (180, password_input.y + label_offset_y))
        pygame.draw.rect(screen, active_color if active_input == 'password' else inactive_color, password_input, 2)
        draw_text(screen, "*" * len(password_text), (password_input.x + 5, password_input.y + 5), color=black)

        draw_text(screen, "Conf. a Senha:", (60, confirm_password_input.y + label_offset_y))
        pygame.draw.rect(screen, active_color if active_input == 'confirm_password' else inactive_color,
                         confirm_password_input, 2)
        draw_text(screen, "*" * len(confirm_password_text),
                  (confirm_password_input.x + 5, confirm_password_input.y + 5), color=black)

        # Desenha botão Registrar
        pygame.draw.rect(screen, black, register_button, 2)
        draw_text(screen, "Register", (register_button.x + 10, register_button.y + 10))

        pygame.draw.rect(screen, black, back_button, 2)
        draw_text(screen, "Back", (back_button.x + 20, back_button.y + 10))

        pygame.display.flip()


def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_field(field_text, max_length):
    pattern = fr'^[a-zA-Z0-9]{{1,{max_length}}}$'
    return re.match(pattern, field_text) is not None


def credits_screen():
    back_button = pygame.Rect(650, 550, 120, 50)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    return

        screen.fill(white)
        screen.blit(bg, (0, 0))
        draw_text(screen, "Credits Screen", (300, 250))

        pygame.draw.rect(screen, black, back_button, 2)
        draw_text(screen, "Back", (back_button.x + 20, back_button.y + 10))

        # Exibir nickname do usuário logado
        if logged_in_user:
            draw_text(screen, f"{logged_in_user}", (10, 10))
            draw_text(screen, f"{pont}", (650, 10))

        pygame.display.flip()


def login_user(email, password):
    try:
        connection = connect_to_db()
        cursor = connection.cursor()

        # Buscar usuário na tabela Player
        query = "SELECT cd_player, nickname, nmaior_pontc FROM PLAYER WHERE email_player = %s AND password = %s"
        cursor.execute(query, (email, password))
        result = cursor.fetchone()
        cursor.close()
        connection.close()

        if result:
            global logged_in_user, cd_player, pont
            logged_in_user = result[1]
            cd_player = result[0]
            pont = result[2]
            return True
        else:
            return False
    except mysql.connector.Error as err:
        # Tratar mensagens de erro
        error_message = translate_error(err)
        show_popup_error("Erro", f"Falha ao fazer login: {error_message}")
        return

if __name__ == "__main__":
    main_menu()
