from contextlib import nullcontext

import pygame
import sys
import mysql.connector
import re
import tkinter as tk
from tkinter import messagebox

pygame.init()

# Inicializar Pygame
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Snake Game")

# Cores
white = (255, 255, 255)
black = (0, 0, 0)
gray = (200, 200, 200)
active_color = pygame.Color('dodgerblue2')
inactive_color = pygame.Color('lightskyblue3')

# Fonte
font = pygame.font.Font(None, 32)

# Variável Global para Armazenar Nickname do Usuário Logado
logged_in_user = None


def draw_text(surface, text, pos, color=black):
    text_surface = font.render(text, True, color)
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
    except mysql.connector.Error as err:
        # Tratar mensagens de erro
        error_message = translate_error(err)
        # Exibir popup de erro
        show_popup_error("Erro", f"Falha ao registrar: {error_message}")


def login_user(email, password):
    try:
        connection = connect_to_db()
        cursor = connection.cursor()

        # Buscar usuário na tabela Player
        query = "SELECT nickname FROM PLAYER WHERE email_player = %s AND password = %s"
        cursor.execute(query, (email, password))
        result = cursor.fetchone()
        cursor.close()
        connection.close()

        if result:
            global logged_in_user
            logged_in_user = result[0]
            return True
        else:
            return False
    except mysql.connector.Error as err:
        # Tratar mensagens de erro
        error_message = translate_error(err)
        show_popup_error("Erro", f"Falha ao fazer login: {error_message}")
        return False


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
    messagebox.showinfo(title, message)


def show_popup_error(title, message):
    root = tk.Tk()
    root.withdraw()  # Esconder a janela principal
    messagebox.showerror(title, message)


def main_menu():
    # Dimensões dos botões
    button_width = 150
    button_height = 50

    # Criar botões
    play_button = pygame.Rect(250, 100, button_width, button_height)
    login_button = pygame.Rect(250, 200, button_width, button_height)
    register_button = pygame.Rect(250, 300, button_width, button_height)
    credits_button = pygame.Rect(250, 400, button_width, button_height)
    leaderboards_button = pygame.Rect(250, 500, button_width, button_height)
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
                if login_button.collidepoint(event.pos):
                    login_screen()
                if register_button.collidepoint(event.pos):
                    register_screen()
                if credits_button.collidepoint(event.pos):
                    credits_screen()
                if leaderboards_button.collidepoint(event.pos):
                    leaderboards_screen()
                if quit_button.collidepoint(event.pos):
                    running = False
                    pygame.quit()
                    sys.exit()

        screen.fill(white)

        pygame.draw.rect(screen, black, play_button, 2)
        if logged_in_user is None:
            pygame.draw.rect(screen, black, login_button, 2)
            pygame.draw.rect(screen, black, register_button, 2)
        pygame.draw.rect(screen, black, credits_button, 2)
        pygame.draw.rect(screen, black, leaderboards_button, 2)
        pygame.draw.rect(screen, black, quit_button, 2)

        draw_text(screen, "Play", (play_button.x + 25, play_button.y + 10))
        if logged_in_user is None:
            draw_text(screen, "Login", (login_button.x + 15, login_button.y + 10))
            draw_text(screen, "Register", (register_button.x + 5, register_button.y + 10))
        draw_text(screen, "Credits", (credits_button.x + 15, credits_button.y + 10))
        draw_text(screen, "Leaderboards", (leaderboards_button.x + 5, leaderboards_button.y + 10))
        draw_text(screen, "Quit", (quit_button.x + 40, quit_button.y + 10))

        # Exibir nickname do usuário logado
        if logged_in_user:
            draw_text(screen, f"Logged in as: {logged_in_user}", (10, 10))

        pygame.display.flip()


def play_game():
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
        draw_text(screen, "Play Game Screen", (300, 250))

        pygame.draw.rect(screen, black, back_button, 2)
        draw_text(screen, "Back", (back_button.x + 20, back_button.y + 10))

        # Exibir nickname do usuário logado
        if logged_in_user:
            draw_text(screen, f"Logged in as: {logged_in_user}", (10, 10))

        pygame.display.flip()


def login_screen():
    email_input = pygame.Rect(300, 200, 200, 32)
    password_input = pygame.Rect(300, 250, 200, 32)
    login_button = pygame.Rect(350, 300, 100, 50)  # Botão de Login
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
        draw_text(screen, "Login Screen", (300, 150))

        # Desenha caixa de e-mail
        pygame.draw.rect(screen, active_color if active_input == 'email' else inactive_color, email_input, 2)
        draw_text(screen, email_text, (email_input.x + 5, email_input.y + 5))

        # Desenha caixa de senha
        pygame.draw.rect(screen, active_color if active_input == 'password' else inactive_color, password_input, 2)
        draw_text(screen, "*" * len(password_text), (password_input.x + 5, password_input.y + 5), color=black)

        # Desenha botão de login
        pygame.draw.rect(screen, black, login_button, 2)
        draw_text(screen, "Login", (login_button.x + 15, login_button.y + 10))

        pygame.draw.rect(screen, black, back_button, 2)
        draw_text(screen, "Back", (back_button.x + 20, back_button.y + 10))

        pygame.display.flip()


def register_screen():
    label_offset_y = 5  # Distância vertical entre a label e o campo de entrada
    email_input = pygame.Rect(300, 150, 200, 32)
    nickname_input = pygame.Rect(300, 200, 200, 32)
    password_input = pygame.Rect(300, 250, 200, 32)
    confirm_password_input = pygame.Rect(300, 300, 200, 32)
    register_button = pygame.Rect(340, 350, 120, 50)  # Botão Registrar
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
                                        register_user(nickname_text, email_text, password_text)
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
        draw_text(screen, "Register Screen", (300, 100))

        # Desenha rótulos e caixas de entrada
        draw_text(screen, "Email:", (225, email_input.y + label_offset_y))
        pygame.draw.rect(screen, active_color if active_input == 'email' else inactive_color, email_input, 2)
        draw_text(screen, email_text, (email_input.x + 5, email_input.y + 5))

        draw_text(screen, "Nickname:", (179, nickname_input.y + label_offset_y))
        pygame.draw.rect(screen, active_color if active_input == 'nickname' else inactive_color, nickname_input, 2)
        draw_text(screen, nickname_text, (nickname_input.x + 5, nickname_input.y + 5))

        draw_text(screen, "Senha:", (220, password_input.y + label_offset_y))
        pygame.draw.rect(screen, active_color if active_input == 'password' else inactive_color, password_input, 2)
        draw_text(screen, "*" * len(password_text), (password_input.x + 5, password_input.y + 5), color=black)

        draw_text(screen, "Confirme a Senha:", (100, confirm_password_input.y + label_offset_y))
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
        draw_text(screen, "Credits Screen", (300, 250))

        pygame.draw.rect(screen, black, back_button, 2)
        draw_text(screen, "Back", (back_button.x + 20, back_button.y + 10))

        # Exibir nickname do usuário logado
        if logged_in_user:
            draw_text(screen, f"Logged in as: {logged_in_user}", (10, 10))

        pygame.display.flip()


def leaderboards_screen():
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
        draw_text(screen, "Leaderboards Screen", (300, 250))

        pygame.draw.rect(screen, black, back_button, 2)
        draw_text(screen, "Back", (back_button.x + 20, back_button.y + 10))

        # Exibir nickname do usuário logado
        if logged_in_user:
            draw_text(screen, f"Logged in as: {logged_in_user}", (10, 10))

        pygame.display.flip()


main_menu()
