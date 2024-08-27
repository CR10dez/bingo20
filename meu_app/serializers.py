# meu_app/serializers.py
from rest_framework import serializers
from .models import *
import json

class NumerosSorteadosSerializer(serializers.ModelSerializer):
    class Meta:
        model = NumerosSorteados
        fields = ['id', 'numero_concurso', 'drawn_numbers', 'created_at', 'updated_at']

class ConcursoGeradoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConcursoGerado
        fields = ['id', 'data_criacao', 'descricao', 'numero_concurso', 'concurso_finalizado']

class CompradorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comprador
        fields = ['id', 'nome', 'cpf', 'telefone', 'bairro', 'cidade', 'whatsapp', 'created_at', 'updated_at']

class CartelasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cartelas
        fields = ['id_cartela', 'qr_code', 'data_criacao', 'numeros', 'numero_concurso']


class CartelaConcursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartelaConcurso
        fields = ['id_cartela', 'numero_concurso', 'nome', 'telefone', 'bairro', 'vendedor']
