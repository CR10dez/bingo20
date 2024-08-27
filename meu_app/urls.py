# meu_app/urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('gerar-rodada/', gerar_rodada, name='gerar_rodada'),
    path('gerar-concurso/', gerar_concurso, name='gerar-concurso'),
    path('gerar-cartela/', gerar_cartelas, name='gerar_cartela'),
    path('quantidade-cartelas/', obter_quantidade_cartelas, name='obter_quantidade_cartelas'),
    path('ultimo-concurso/', obter_ultimo_concurso, name='obter_ultimo_concurso'),
    path('cartelas/', Obter_Cartelas, name='todas-cartelas'),
    path('download-Pdf/', download_Pdf, name='download_Pdf'),
    path('vendedor-login/', vendedor_login, name='vendedor_login'),
    path('verificar-telefone/<str:telefone>/', verificar_telefone, name='verificar_telefone'),
    path('salvar-comprador/', salvar_comprador, name='salvar_comprador'),
    path('salvar-cartela-concurso/', salvar_cartela_concurso, name='salvar_cartela_concurso'),
    path('verificar-cartelas-associadas/', verificar_cartelas_associadas, name='verificar_cartelas_associadas'),
    path('iniciar-concurso/', iniciar_concurso, name='iniciar_concurso'),
    path('ultima-rodada/<int:numero_concurso>/', obter_ultima_rodada, name='obter_ultima_rodada'),
    path('adicionar-numero-marcado/', adicionar_numero_marcado, name='adicionar_numero_marcado'),
    
]
