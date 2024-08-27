# meu_app/models.py

from django.db import models
from django.contrib.auth.models import User

class ConcursoGerado(models.Model):
    data_criacao = models.DateTimeField(auto_now_add=True)
    descricao = models.TextField(null=True, blank=True)
    numero_concurso = models.IntegerField(unique=True)
    concurso_finalizado = models.BooleanField(default=False)  # Novo campo

    def __str__(self):
        return f"Concurso {self.numero_concurso}"


class NumerosSorteados(models.Model):
    numero_concurso = models.IntegerField(unique=True)
    drawn_numbers = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Concurso {self.numero_concurso}"


class Comprador(models.Model):
    nome = models.CharField(max_length=255)
    cpf = models.CharField(max_length=20, null=True, blank=True, unique=True)  # Permitir valores nulos e em branco
    telefone = models.CharField(max_length=20, unique=True)
    bairro = models.CharField(max_length=255, null=True, blank=True)
    cidade = models.CharField(max_length=255, null=True, blank=True)
    whatsapp = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome
    
class Cartelas(models.Model):
    id_cartela = models.AutoField(primary_key=True)  # Auto-incremento e chave primária
    qr_code = models.BinaryField(null=True, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)  # Data criada automaticamente
    numeros = models.TextField(null=True, blank=True)
    numero_concurso = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Cartela {self.id_cartela}"

class CartelaConcurso(models.Model):
    id_cartela = models.CharField(max_length=255, primary_key=True)  # Substituindo o OneToOneField por CharField
    numero_concurso = models.CharField(max_length=255)  # Substituindo o ForeignKey por CharField
    nome = models.CharField(max_length=255)
    telefone = models.CharField(max_length=20)
    bairro = models.CharField(max_length=255, null=True, blank=True)
    vencedor = models.BooleanField(default=False)
    rodadas_vencedoras = models.TextField(null=True, blank=True)
    vendedor = models.CharField(max_length=255)  # Campo de texto para o vendedor
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cartela_concurso'

    def __str__(self):
        return f"Cartela {self.id_cartela} - Concurso {self.numero_concurso}"

