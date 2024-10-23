import pygame
import random

pygame.init()
pygame.display.set_caption('Snake')
largura, altura = 600, 400
tela = pygame.display.set_mode((largura, altura))
relogio = pygame.time.Clock()

preto = (0, 0, 0)
branco = (255, 255, 255)
verde = (0, 255, 0)
vermelho = (255, 0, 0)

tamanho_quadrado = 10
velocidade_cobra = 10

def desenhar_cobra(tamanho_quadrado, lista_cobra):
    for parte in lista_cobra:
        pygame.draw.rect(tela, verde, [parte[0], parte[1], tamanho_quadrado, tamanho_quadrado])

def rodar_jogo():
    fim_jogo = False
    fim_de_jogo = False

    x_cobra = largura // 2
    y_cobra = altura // 2
    x_cobra_velocidade = 0
    y_cobra_velocidade = 0

    x_comida = round(random.randrange(0, largura - tamanho_quadrado) / 10.0) * 10.0
    y_comida = round(random.randrange(0, altura - tamanho_quadrado) / 10.0) * 10.0

    lista_cobra = []
    comprimento_cobra = 1

    while not fim_jogo:

        while fim_de_jogo:
            tela.fill(preto)
            fonte = pygame.font.SysFont(None, 50)
            mensagem = fonte.render("Fim de jogo - Pressione C", True, branco)
            tela.blit(mensagem, [largura // 6, altura // 3])
            pygame.display.update()

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    fim_jogo = True
                    fim_de_jogo = False
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_q:
                        fim_jogo = True
                        fim_de_jogo = False
                    if evento.key == pygame.K_c:
                        rodar_jogo()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                fim_jogo = True
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_LEFT:
                    x_cobra_velocidade = -tamanho_quadrado
                    y_cobra_velocidade = 0
                elif evento.key == pygame.K_RIGHT:
                    x_cobra_velocidade = tamanho_quadrado
                    y_cobra_velocidade = 0
                elif evento.key == pygame.K_UP:
                    y_cobra_velocidade = -tamanho_quadrado
                    x_cobra_velocidade = 0
                elif evento.key == pygame.K_DOWN:
                    y_cobra_velocidade = tamanho_quadrado
                    x_cobra_velocidade = 0

        x_cobra += x_cobra_velocidade
        y_cobra += y_cobra_velocidade

        if x_cobra >= largura or x_cobra < 0 or y_cobra >= altura or y_cobra < 0:
            fim_de_jogo = True

        tela.fill(preto)

        pygame.draw.rect(tela, vermelho, [x_comida, y_comida, tamanho_quadrado, tamanho_quadrado])

        cabeca_cobra = [x_cobra, y_cobra]
        lista_cobra.append(cabeca_cobra)

        if len(lista_cobra) > comprimento_cobra:
            del lista_cobra[0]

        for parte in lista_cobra[:-1]:
            if parte == cabeca_cobra:
                fim_de_jogo = True

        desenhar_cobra(tamanho_quadrado, lista_cobra)

        pygame.display.update()

        if x_cobra == x_comida and y_cobra == y_comida:
            x_comida = round(random.randrange(0, largura - tamanho_quadrado) / 10.0) * 10.0
            y_comida = round(random.randrange(0, altura - tamanho_quadrado) / 10.0) * 10.0
            comprimento_cobra += 1

        relogio.tick(velocidade_cobra)

    pygame.quit()

rodar_jogo()
