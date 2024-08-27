# meu_app/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from django.db.models import Max
from django.http import JsonResponse
import random
from rest_framework import generics, status
from .models import *
from .serializers import *
from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import black, gray, white
from reportlab.pdfgen import canvas
from django.middleware.csrf import get_token
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from django.views.decorators.csrf import csrf_exempt


@api_view(['POST'])
def gerar_concurso(request):
    # Verifica se há algum concurso não finalizado
    concurso_nao_finalizado = ConcursoGerado.objects.filter(concurso_finalizado=False).last()
    
    if concurso_nao_finalizado:
        # Retorna uma mensagem personalizada informando que há um concurso em andamento
        return Response({
            "message": f"Concurso {concurso_nao_finalizado.numero_concurso} em andamento. Finalize-o antes de criar outro concurso."
        }, status=400)
    
    # Se não há concurso não finalizado, calcula o próximo número de concurso
    max_numero_concurso = ConcursoGerado.objects.aggregate(Max('numero_concurso'))['numero_concurso__max']
    proximo_numero_concurso = (max_numero_concurso or 0) + 1
    
    # Cria o novo concurso com o próximo número disponível
    novo_concurso = ConcursoGerado.objects.create(
        numero_concurso=proximo_numero_concurso,
        data_criacao=timezone.now(),
        descricao='Descrição do concurso',
        concurso_finalizado=False  # Marca o novo concurso como não finalizado
    )
    
    # Serializa e retorna o novo concurso
    serializer = ConcursoGeradoSerializer(novo_concurso)
    return Response(serializer.data, status=201)

@api_view(['GET'])
def obter_ultimo_concurso(request):
    ultimo_concurso = ConcursoGerado.objects.latest('data_criacao')  # Assume que 'data_criacao' é o campo que você quer ordenar
    return Response({
        "numero_concurso": ultimo_concurso.numero_concurso,
        "data_criacao": ultimo_concurso.data_criacao
    })

@api_view(['POST'])
def gerar_cartelas(request):
    quantidade = request.query_params.get('quantidade', 1)  # Use query_params para capturar parâmetros GET
    
    try:
        quantidade = int(quantidade)
    except ValueError:
        return JsonResponse({'error': 'Quantidade deve ser um número inteiro'}, status=400)
    
    def gerar_numeros_bingo():
        b = random.sample(range(1, 16), 5)
        i = random.sample(range(16, 31), 5)
        n = random.sample(range(31, 46), 4)
        g = random.sample(range(46, 61), 5)
        o = random.sample(range(61, 76), 5)

        n.insert(2, ' ')
        
        numeros = {
            'B': b,
            'I': i,
            'N': n,
            'G': g,
            'O': o
        }
        
        return numeros

    cartelas = []
    
    for _ in range(quantidade):
        numeros = gerar_numeros_bingo()
        print(f"Gerando cartela com números: {numeros}")  # Debugging output
        
        cartela = Cartelas.objects.create(
            numeros=json.dumps(numeros)  # Use json.dumps to format the dictionary
        )
        
        print(f"Cartela criada com id: {cartela.id_cartela}")  # Debugging output
        serializer = CartelasSerializer(cartela)
        cartelas.append(serializer.data)
    
    return JsonResponse(cartelas, safe=False)

@api_view(['GET'])
def obter_quantidade_cartelas(request):
    quantidade = Cartelas.objects.count()
    return Response({'quantidade': quantidade})

@api_view(['GET'])
def Obter_Cartelas(request):
    cartelas = Cartelas.objects.all()
    serializer = CartelasSerializer(cartelas, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def download_Pdf(request):
     # Cria um buffer em memória para o PDF
    buffer = BytesIO()

    # Cria um canvas para desenhar o PDF
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Define as dimensões e posição das cartelas
    cell_width = 50  # Largura de cada célula
    cell_height = 40  # Altura de cada célula
    grid_width = cell_width * 5  # Largura total da cartela
    grid_height = cell_height * 5  # Altura total da cartela
    cartela_spacing = 30  # Espaço entre as cartelas
    cartela_repetida_spacing = 50  # Espaço entre cartelas repetidas
    column_width = width / 2  # Largura de cada coluna
    y_offset = 60  # Margem superior para a primeira cartela

    # Centraliza as cartelas dentro de cada coluna
    x_position_left = (column_width - grid_width) / 2  # Centraliza na coluna esquerda
    x_position_right = column_width + (column_width - grid_width) / 2  # Centraliza na coluna direita

    # Cores para as cartelas repetidas
    colors = [(0.9, 0.95, 1.0),  # Azul mais claro
              (1.0, 0.9, 0.9),  # Vermelho mais claro
              (0.9, 1.0, 0.9)]  # Verde mais claro

    # Obtém todas as cartelas do banco de dados
    cartelas = Cartelas.objects.all()

    def format_id_cartela(id_cartela):
        return str(id_cartela).zfill(4)

    def draw_bingo_card(p, cartela, x, y, color):
        # Desenha o contorno da cartela
        p.setStrokeColor(black)
        p.setFillColor(color)
        p.rect(x, y, grid_width, grid_height, fill=1)

        # Desenha linhas da grade
        p.setStrokeColor(black)
        for i in range(1, 5):
            p.line(x, y + i * cell_height, x + grid_width, y + i * cell_height)
            p.line(x + i * cell_width, y, x + i * cell_width, y + grid_height)

        # Adiciona o fundo cinza para o cabeçalho
        p.setFillColor(gray)
        p.rect(x, y + grid_height, grid_width, cell_height, fill=1)  # Fundo cinza

        # Adiciona os títulos das colunas em branco e com fonte negrito
        columns = ['B', 'I', 'N', 'G', 'O']
        p.setFillColor(white)
        p.setFont("Helvetica-Bold", 20)  # Fonte negrito e tamanho maior

        for i, col in enumerate(columns):
            # Centraliza a letra no cabeçalho
            p.drawCentredString(x + (i + 0.5) * cell_width, y + grid_height + (cell_height / 2), col)

        # Adiciona os números na cartela
        cartela_dict = eval(cartela.numeros)  # Converte a string do banco de dados para um dicionário
        p.setFillColor(black)
        p.setFont("Helvetica-Bold", 18)  # Fonte padrão para números
        for i, col in enumerate(columns):
            numbers = cartela_dict.get(col, [])
            for j, number in enumerate(numbers):
                if number != " ":
                    p.drawCentredString(x + (i + 0.5) * cell_width, y + (4 - j) * cell_height + 10, str(number))

    # Define posições iniciais
    y_position = height - grid_height - y_offset

    for idx in range(0, len(cartelas), 2):
        # Desenha a primeira cartela (repetida 3 vezes) na coluna da esquerda
        if idx < len(cartelas):
            for i in range(3):
                draw_bingo_card(p, cartelas[idx], x_position_left, y_position, colors[i])
                y_position -= (grid_height + cartela_repetida_spacing)

            # Desenha o ID da cartela formatado abaixo da última repetição
            formatted_id = format_id_cartela(cartelas[idx].id_cartela)
            p.setFont("Helvetica-Bold", 14)
            p.drawString(x_position_left + 10, y_position + grid_height + cartela_repetida_spacing - 30, f"N°: {formatted_id}")

            y_position = height - grid_height - y_offset  # Reseta para a próxima coluna

        # Desenha a segunda cartela (repetida 3 vezes) na coluna da direita
        if idx + 1 < len(cartelas):
            for i in range(3):
                draw_bingo_card(p, cartelas[idx + 1], x_position_right, y_position, colors[i])
                y_position -= (grid_height + cartela_repetida_spacing)

            # Desenha o ID da cartela formatado abaixo da última repetição
            formatted_id = format_id_cartela(cartelas[idx + 1].id_cartela)
            p.setFont("Helvetica-Bold", 14)
            p.drawString(x_position_right + 3, y_position + grid_height + cartela_repetida_spacing - 30, f"N°: {formatted_id}")

            y_position = height - grid_height - y_offset  # Reseta para a próxima página

        # Adiciona uma nova página se houver mais cartelas
        if idx + 2 < len(cartelas):
            p.showPage()
            y_position = height - grid_height - y_offset

    # Finaliza o PDF
    p.showPage()
    p.save()

    # Move o buffer para o início
    buffer.seek(0)

    # Retorna o PDF como uma resposta HTTP para download
    # Certifique-se de que o tipo de conteúdo está correto
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="cartelas_bingo.pdf"'


    return response


@api_view(['POST'])
def vendedor_login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'status': 'error', 'message': 'Username and password are required'}, status=400)

    user = authenticate(request, username=username, password=password)

    if user is not None:
        if user.groups.filter(name='Vendedores').exists():
            refresh = RefreshToken.for_user(user)
            return Response({
                'status': 'success',
                'message': 'Login successful',
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            })
        else:
            return Response({'status': 'error', 'message': 'User is not a Vendedor'}, status=403)
    else:
        return Response({'status': 'error', 'message': 'Invalid credentials'}, status=401)


    
@api_view(['GET'])
def verificar_telefone(request, telefone):
    try:
        comprador = Comprador.objects.get(telefone=telefone)
        serializer = CompradorSerializer(comprador)
        return Response({'existe': True, 'comprador': serializer.data})
    except Comprador.DoesNotExist:
        return Response({'existe': False})
    
@api_view(['POST'])
def verificar_cartelas_associadas(request):
    # Obtém a lista de IDs de cartelas do corpo da requisição
    id_cartelas = request.data.get('id_cartelas', [])
    
    # Verifica se id_cartelas é uma lista e contém apenas inteiros ou strings de inteiros
    if not isinstance(id_cartelas, list) or not all(isinstance(i, (int, str)) for i in id_cartelas):
        return Response({'status': 'error', 'message': 'ID das cartelas inválido'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Converte IDs de cartelas para inteiros, se necessário
    id_cartelas = [int(i) for i in id_cartelas]
    
    # Dicionário para armazenar os resultados
    resultado_verificacao = {}

    # Itera sobre cada ID de cartela
    for id_cartela in id_cartelas:
        # Verifica se a cartela existe
        cartela_existe = Cartelas.objects.filter(id_cartela=id_cartela).exists()
        
        if cartela_existe:
            # Se a cartela existe, verifica se está associada a um concurso
            concurso_associado = Cartelas.objects.filter(id_cartela=id_cartela, numero_concurso__isnull=False).exists()
            resultado_verificacao[id_cartela] = {
                'existe': True,
                'concurso_associado': concurso_associado
            }
        else:
            # Se a cartela não existe
            resultado_verificacao[id_cartela] = {
                'existe': False,
                'concurso_associado': False
            }

    # Retorna os resultados
    return Response({'resultado': resultado_verificacao}, status=status.HTTP_200_OK)

@api_view(['POST'])
def salvar_comprador(request):
    telefone = request.data.get('telefone')
    cpf = request.data.get('cpf')
    
    # Verificar se o telefone ou o CPF foi fornecido
    if not telefone and not cpf:
        return Response({'error': 'Telefone ou CPF é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Tenta recuperar o comprador pelo telefone (ou CPF, se for o caso)
        comprador = Comprador.objects.get(telefone=telefone)
        # Se o comprador existe, atualize-o
        serializer = CompradorSerializer(comprador, data=request.data, partial=True)  # partial=True para atualizações parciais
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Comprador atualizado com sucesso!'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Comprador.DoesNotExist:
        # Se o comprador não existe, crie um novo
        serializer = CompradorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Comprador criado com sucesso!'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def salvar_cartela_concurso(request):
    telefone = request.data.get('telefone')
    nome = request.data.get('nome')
    bairro = request.data.get('bairro', None)
    numero_concurso = request.data.get('numero_concurso')
    vendedor = request.user.username  # Usar o nome do usuário como vendedor
    id_cartelas = request.data.get('id_cartelas')  # Recebe uma lista com IDs das cartelas

    # Verificação básica dos campos
    if not id_cartelas:
        return Response({'status': 'error', 'message': 'IDs das Cartelas são obrigatórios'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not numero_concurso:
        return Response({'status': 'error', 'message': 'Número do Concurso é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)

    # Processa a string de IDs das cartelas, garantindo que é uma lista de strings
    if isinstance(id_cartelas, str):
        id_cartelas = id_cartelas.split(',')
    id_cartelas = [id_cartela.strip() for id_cartela in id_cartelas if id_cartela.strip()]

    if not id_cartelas:
        return Response({'status': 'error', 'message': 'Nenhum ID de Cartela válido encontrado'}, status=status.HTTP_400_BAD_REQUEST)

    # Salva cada cartela com o número do concurso e outros dados
    for id_cartela in id_cartelas:
        cartela_concurso_data = {
            'id_cartela': id_cartela,
            'numero_concurso': numero_concurso,  # Passa diretamente como string
            'nome': nome,
            'telefone': telefone,
            'bairro': bairro,
            'vendedor': vendedor  # Salva o nome do vendedor diretamente
        }

        serializer = CartelaConcursoSerializer(data=cartela_concurso_data)
        if serializer.is_valid():
            cartela_concurso = serializer.save()

            # Atualiza a tabela Cartelas com o número do concurso
            try:
                cartela = Cartelas.objects.get(id_cartela=id_cartela)
                cartela.numero_concurso = numero_concurso
                cartela.save()
            except Cartelas.DoesNotExist:
                # Lida com o caso onde a cartela não é encontrada
                print(f'Cartela com ID {id_cartela} não encontrada.')
                return Response({'status': 'error', 'message': f'Cartela com ID {id_cartela} não encontrada.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            print('Erro de Validação para ID de Cartela:', id_cartela, 'Erro:', serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({'status': 'success', 'message': 'Cartelas e Concurso salvos com sucesso'}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def iniciar_concurso(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            numero_concurso = data.get("numero_concurso")

            if numero_concurso:
                # Verifica se o concurso já existe
                concurso_existente = NumerosSorteados.objects.filter(numero_concurso=numero_concurso).first()

                if concurso_existente:
                    # Concurso já existe
                    return JsonResponse({"mensagem": "O concurso já foi iniciado."}, status=200)
                else:
                    # Concurso não existe, cria um novo
                    NumerosSorteados.objects.create(numero_concurso=numero_concurso)
                    return JsonResponse({"mensagem": "Concurso iniciado com sucesso!"}, status=201)
            else:
                return JsonResponse({"mensagem": "Número do concurso não fornecido"}, status=400)
        except Exception as e:
            return JsonResponse({"mensagem": f"Erro: {str(e)}"}, status=500)
    return JsonResponse({"mensagem": "Método não permitido"}, status=405)



@api_view(['POST'])
def gerar_rodada(request):
    numero_concurso = request.data.get('numero_concurso')

    try:
        concurso = NumerosSorteados.objects.get(numero_concurso=numero_concurso)
    except NumerosSorteados.DoesNotExist:
        return JsonResponse({'error': 'Concurso não encontrado'}, status=404)

    rodadas = concurso.drawn_numbers
    
    if rodadas:
        ultima_rodada = rodadas[-1]

        # Verifica se a última rodada está finalizada
        if not ultima_rodada.endswith("_finalizada"):
            return JsonResponse({'A última rodada ainda não foi finalizada'})

        try:
            numero_rodada = int(ultima_rodada.split(':')[1])
            nova_rodada = f"rodada:{numero_rodada + 1}:"
        except (IndexError, ValueError):
            nova_rodada = "rodada:1:"
    else:
        nova_rodada = "rodada:1:"

    rodadas.append(nova_rodada)
    concurso.drawn_numbers = rodadas
    concurso.save()

    return JsonResponse({'rodadas': rodadas})




@api_view(['GET'])
def obter_ultima_rodada(request, numero_concurso):
    try:
        concurso = NumerosSorteados.objects.get(numero_concurso=numero_concurso)
        rodadas = concurso.drawn_numbers
        if rodadas:
            ultima_rodada = rodadas[-1]
            partes = ultima_rodada.split(':')
            if len(partes) > 1:
                numero_rodada = partes[1]
                return Response({'ultima_rodada': numero_rodada})
            else:
                return Response({'error': 'Formato de rodada inválido'}, status=500)
        else:
            return Response({'ultima_rodada': 'Nenhuma rodada encontrada'}, status=404)
    except NumerosSorteados.DoesNotExist:
        return Response({'error': 'Concurso não encontrado'}, status=404)



@api_view(['POST'])
def adicionar_numero_marcado(request):
    numero_concurso = request.data.get('numero_concurso')
    numero = request.data.get('numero')

    if not numero_concurso or not numero:
        return JsonResponse({'error': 'Número do concurso e número são necessários'}, status=400)
    
    try:
        concurso = NumerosSorteados.objects.get(numero_concurso=numero_concurso)
    except NumerosSorteados.DoesNotExist:
        return JsonResponse({'error': 'Concurso não encontrado'}, status=404)

    rodadas = concurso.drawn_numbers

    if not rodadas:
        return JsonResponse({'error': 'Nenhuma rodada encontrada'}, status=404)
    
    # Obter a última rodada
    ultima_rodada = rodadas[-1]
    partes = ultima_rodada.split(':')
    numero_rodada = partes[1]
    numeros_sorteados = partes[2] if len(partes) > 2 else ''

    # Inicializar numeros_sorteados_set
    numeros_sorteados_set = set(numeros_sorteados.split(',')) if numeros_sorteados else set()
    print('oi',numeros_sorteados)

    if str(numero) not in numeros_sorteados_set:
        numeros_sorteados_set.add(str(numero))
        rodadas[-1] = f"rodada:{numero_rodada}:{','.join(numeros_sorteados_set)}"
    else:
        return JsonResponse({'error': 'Número já foi marcado nesta rodada'}, status=400)
    
    concurso.drawn_numbers = rodadas
    concurso.save()

    # Verificar se alguma cartela ganhou
    resultado_verificacao = verificar_cartelas(numero_concurso)
    print(resultado_verificacao)
    
    if 'ganhadores' in resultado_verificacao:
        # Adicionar os ganhadores ao final do JSON de drawn_numbers
        for ganhador in resultado_verificacao['ganhadores']:
            rodadas[-1] += f", {ganhador}"
        rodadas[-1] += f", rodada{numero_rodada}_finalizada"
        concurso.drawn_numbers = rodadas
        concurso.save()

    return JsonResponse(resultado_verificacao)


def verificar_cartelas(numero_concurso):
    try:
        concurso = NumerosSorteados.objects.get(numero_concurso=numero_concurso)
    except NumerosSorteados.DoesNotExist:
        return JsonResponse({'error': 'Concurso não encontrado'}, status=404)

    # Obter todos os números sorteados da rodada
    numeros_sorteados_por_rodada = {}
    for r in concurso.drawn_numbers:
        if r.startswith("rodada:"):
            partes = r.split(':')
            if len(partes) > 2:
                # Adicionar números da rodada específica
                rodada = partes[1]
                numeros = set(int(num) for num in partes[2].split(',') if num.isdigit())
                numeros_sorteados_por_rodada[rodada] = numeros

    ganhadores = []

    # Verificar cada cartela no CartelaConcurso
    cartelas = Cartelas.objects.filter(numero_concurso=numero_concurso)
    for cartela in cartelas:
        # Se 'numeros' é uma string JSON, converta-a para dicionário
        if isinstance(cartela.numeros, str):
            cartela_numeros = json.loads(cartela.numeros)
        else:
            cartela_numeros = cartela.numeros

        # Extrair números da cartela
        cartela_numeros_set = {num for col in cartela_numeros.values() for num in col if isinstance(num, int)}

        for rodada, numeros_sorteados in numeros_sorteados_por_rodada.items():
            if cartela_numeros_set <= numeros_sorteados:
                # Marcar a cartela como vencedora e salvar as rodadas vencedoras
                informacoes = CartelaConcurso.objects.get(numero_concurso=numero_concurso, id_cartela=cartela.id_cartela)
                informacoes.vencedor = True
                informacoes.rodadas_vencedoras = f"rodada{rodada}:{','.join(map(str, numeros_sorteados))}"
                informacoes.save()

                ganhador_info = f"cartela:{informacoes.id_cartela}, nome:{informacoes.nome}, telefone:{informacoes.telefone}, bairro:{informacoes.bairro}, vendedor:{informacoes.vendedor}"
                ganhadores.append(ganhador_info)
                break  # Pare ao encontrar a primeira rodada vencedora

    if ganhadores:
        return {'status': 'Uma ou mais cartelas ganharam!', 'ganhadores': ganhadores}
    else:
        return {'status': 'Nenhuma cartela ganhou'}
