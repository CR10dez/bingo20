import os
import django
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import gray, white, black, lightblue, lightpink, lightgreen
from io import BytesIO

# Configuração do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo.settings')  # Substitua 'bingo.settings' pelo nome do seu projeto Django
django.setup()

# Importa o modelo após configurar o Django
from meu_app.models import Cartelas

def gerar_pdf():
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

    # Salve o PDF em um arquivo no diretório especificado
    pdf_path = os.path.expanduser("~/Desktop/cartelas_bingo.pdf")  # Salva na área de trabalho do usuário
    with open(pdf_path, "wb") as f:
        f.write(buffer.getvalue())

    print(f"PDF gerado e salvo em {pdf_path}")

if __name__ == "__main__":
    gerar_pdf()
