from django.shortcuts import render, redirect, get_object_or_404
from .models import Slide, Noticia, Comentario, SiteConfig, DownloadList, VIPType, VIPAdvantage, descriptionVip, Info
from django.contrib import messages
import base64
from PIL import Image, ImageDraw
from django.db import connections
from .forms import CadastroForm, LoginForm, MudarSenhaForm, MudarIDForm, MudarClasseForm, AlterarNomeForm
from django.contrib.auth.models import User
from datetime import datetime
from django.contrib.auth import login, logout
from django.db import connection, transaction
from .config import *



# Funções para gerar a logo da guilda em base64 e retornar a imagem
def get_color(hex_value):
    HEX_TO_COLOR = {
        "0": (255, 255, 255),
        "1": (0, 0, 0),
        "2": (128, 128, 128),
        "3": (255, 255, 255),
        "4": (254, 0, 0),
        "5": (255, 127, 0),
        "6": (255, 255, 0),
        "7": (128, 255, 0),
        "8": (0, 255, 1),
        "9": (0, 254, 129),
        "a": (0, 255, 255),
        "b": (0, 128, 255),
        "c": (0, 0, 254),
        "d": (127, 0, 255),
        "e": (255, 0, 254),
        "f": (255, 0, 128)
    }
    return HEX_TO_COLOR.get(hex_value.lower(), (255, 255, 255))


def generate_guild_mark(decoded_hex, size=130):
    expected_length = 64
    if len(decoded_hex) != expected_length:
        print(f"Alerta: O código hexadecimal tem {len(decoded_hex)} caracteres, mas espera-se {expected_length}.")
    
    image = Image.new("RGB", (size, size), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    block_size = size // 8

    for i in range(min(len(decoded_hex), expected_length)):
        x = (i % 8) * block_size
        y = (i // 8) * block_size
        color = get_color(decoded_hex[i])
        draw.rectangle([x, y, x + block_size, y + block_size], fill=color)

    return image


def decode_bytes(byte_sequence):
    return ''.join(format(byte, 'x') for byte in byte_sequence)


def get_top_ranking():
    queries = {
        "Top Reset": f"SELECT TOP 1 Name, {columnsCharacter['reset']}, cLevel, Class FROM Character ORDER BY {columnsCharacter['reset']} DESC",
        "Top Master Reset": f"SELECT TOP 1 Name, {columnsCharacter['master_reset']}, cLevel, Class FROM Character ORDER BY {columnsCharacter['master_reset']} DESC",
        "Top PK": f"SELECT TOP 1 Name, {columnsCharacter['pk']}, cLevel, Class FROM Character ORDER BY {columnsCharacter['pk']} DESC",
        "Top Herói": f"SELECT TOP 1 Name, {columnsCharacter['hero']}, cLevel, Class FROM Character ORDER BY {columnsCharacter['hero']} ASC",
        "Top Guild": f"SELECT TOP 1 G_Name, {columnsCharacter['guild_score']}, G_mark FROM Guild ORDER BY {columnsCharacter['guild_score']} DESC",
    }
    results = {}

    conn = conexao_mssql()  # Conectar ao banco SQL Server
    if conn:
        try:
            cursor = conn.cursor()  # Criando o cursor

            for category, query in queries.items():
                cursor.execute(query)
                row = cursor.fetchone()
                if row:
                    columns = [col[0] for col in cursor.description]
                    results[category] = dict(zip(columns, row))
                else:
                    results[category] = None

        except pyodbc.Error as e:
            print(f"Ocorreu um erro ao executar as consultas: {e}")
            return None
        finally:
            conn.close()  # Fechar a conexão

    return results


def get_top_guild_logo():
    top_ranking = get_top_ranking()
    if top_ranking and isinstance(top_ranking, dict):
        top_guild = top_ranking.get("Top Guild", None)
    else:
        top_guild = None

    
    if top_guild and top_guild.get("G_mark"):
        img_data = top_guild["G_mark"]
        
        if isinstance(img_data, bytes):
            decoded_hex = decode_bytes(img_data)
            image = generate_guild_mark(decoded_hex, size=129)

            # Converte a imagem para base64
            from io import BytesIO
            buffer = BytesIO()
            image.save(buffer, format="PNG")
            img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return img_base64
    return None


# Função para buscar informações sobre o Castle Siege
def get_castle_siege_info():
    conn = conexao_mssql()  # Obter a conexão global
    if not conn:
        return None  # Retorna None se a conexão não for bem-sucedida

    try:
        cursor = conn.cursor()  # Criar o cursor para executar a consulta

        # Consulta para verificar se a tabela MuCastle_DATA existe
        cursor.execute("""
            SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = 'MuCastle_DATA'
        """)
        table_exists = cursor.fetchone()[0]

        if not table_exists:
            return None  # Retorna None se a tabela não existir

        # Se a tabela existir, busca os dados do Castle Siege
        cursor.execute("""
            SELECT OWNER_GUILD, SIEGE_START_DATE, SIEGE_END_DATE 
            FROM MuCastle_DATA
        """)
        
        row = cursor.fetchone()
        if row:
            return {
                "OWNER_GUILD": row[0], 
                "SIEGE_START_DATE": row[1], 
                "SIEGE_END_DATE": row[2]
            }
        
        return None  # Retorna None se não encontrar nenhum dado

    except pyodbc.Error as e:
        print(f"Ocorreu um erro ao executar a consulta: {e}")
        return None

    finally:
        if conn:
            conn.close()  # Fechar a conexão


def home(request):
    slides = Slide.objects.all()
    top_players = get_top_ranking()
    config = SiteConfig.objects.first()
    noticias = Noticia.objects.order_by("-criado_em")
    show_castle_siege = config.castle_siege_exists if config else True

    castle_siege_info = None
    guild_master = "Sem Dono"
    event_message = ""

    if show_castle_siege:
        # Chama a função para obter as informações do Castle Siege
        castle_siege_info = get_castle_siege_info()

        if castle_siege_info:
            # Se encontrou o Castle Siege, busca a guilda relacionada
            conn = conexao_mssql()  # Obtendo a conexão global
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT G_Master FROM Guild WHERE G_Name = ?
                    """, [castle_siege_info["OWNER_GUILD"]])
                    
                    guild = cursor.fetchone()
                    if guild:
                        guild_master = guild[0]
                    else:
                        guild_master = "Guilda não encontrada"
                except pyodbc.Error as e:
                    print(f"Ocorreu um erro ao obter dados da Guilda: {e}")
                    guild_master = "Erro ao consultar a guilda"
                finally:
                    conn.close()  # Fechar a conexão após o uso
        else:
            event_message = "O evento Castle Siege não existe nesta versão."

    logo_base64 = get_top_guild_logo()

    return render(request, f"{request.current_theme}/home.html", {
        'guild_master': guild_master,
        'slides': slides,
        'top_players': top_players,
        'logo_base64': logo_base64,
        'castle_siege': castle_siege_info,
        'show_castle_siege': show_castle_siege,
        "event_message": event_message,
        "noticias": noticias
    })


def noticia_detalhe(request, noticia_id):
    noticia = get_object_or_404(Noticia, id=noticia_id)
    comentarios = noticia.comentarios.all()

    if request.method == "POST":
        if not request.user.is_authenticated:  # Verifica se o usuário não está logado
            messages.error(request, "Você precisa estar logado para comentar.")
            return redirect("noticia_detalhe", noticia_id=noticia.id)

        nome = request.user.username
        texto = request.POST.get("texto")
        if nome and texto:
            Comentario.objects.create(noticia=noticia, nome=nome, texto=texto)
            return redirect("noticia_detalhe", noticia_id=noticia.id)  # Evita reenvio do formulário ao recarregar

    return render(request, f"{request.current_theme}/detalhe_noticia.html", {
        "noticia": noticia,
        "comentarios": comentarios, 

        })


def notice_all(request):
    noticias = Noticia.objects.order_by("-criado_em")

    return render(request, f"{request.current_theme}/notice_all.html", {"noticias": noticias})


def get_character_details(character_name):
    conn = conexao_mssql()  # Conectar ao banco SQL Server
    if conn:
        try:
            cursor = conn.cursor()  # Criando o cursor
            cursor.execute(f"""
                SELECT Name, {columnsCharacter['reset']}, cLevel, Class, Strength, Dexterity, Vitality, Energy
                FROM Character
                WHERE Name = %s
            """, [character_name])
            
            row = cursor.fetchone()
            if row:
                columns = [col[0] for col in cursor.description]
                return dict(zip(columns, row))
            return None

        except pyodbc.Error as e:
            print(f"Ocorreu um erro ao executar a consulta: {e}")
            return None
        finally:
            conn.close()  # Fechar a conexão
    return None


def character_detail(request, character_name):
    character = get_character_details(character_name)
    if not character:
        return render(request, "character_not_found.html", {"character_name": character_name})

    return render(request, f"{request.current_theme}/character_detail.html", {"character": character})


def get_ranking(limit=10, search_name=None):
    conn = conexao_mssql()  # Conectar ao banco SQL Server
    if conn:
        try:
            query = f"""
                SELECT TOP {limit} Name, {columnsCharacter['reset']}, cLevel, Class
                FROM Character
                WHERE 1=1
            """
            
            params = []
            
            if search_name:  # Se um nome foi passado, adiciona a cláusula de busca
                query += " AND Name LIKE %s"
                params.append(f"%{search_name}%")

            query += " ORDER BY ResetCount DESC"
            
            cursor = conn.cursor()  # Criando o cursor
            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            return results

        except pyodbc.Error as e:
            print(f"Ocorreu um erro ao executar a consulta: {e}")
            return None
        finally:
            conn.close()  # Fechar a conexão
    return None


def ranking_view(request):
    limit = request.GET.get('limit', 10)
    search_name = request.GET.get('search', None)
    ranking = get_ranking(limit, search_name)

    return render(request, f"{request.current_theme}/ranking.html", {'ranking': ranking})


def cadastro_view(request):
    config = SiteConfig.objects.first()
    # Verifique se o site_config existe antes de passá-lo para o template
    if not config:
        config = None

    if request.method == "POST":
        form = CadastroForm(request.POST)

        if form.is_valid():
            # Pega os dados validados
            nome = form.cleaned_data["nome"]
            nick = form.cleaned_data["nick"]
            senha = form.cleaned_data["senha"]
            email = form.cleaned_data["email"]
            personal_id = form.cleaned_data["personal_id"]
            telefone = form.cleaned_data["telefone"]

            # ✅ Cadastrar no banco MuOnline via Query com conexão global
            try:
                conn = conexao_mssql()  # Usar a conexão global
                if conn:
                    with conn.cursor() as cursor:
                        cursor.execute(f"""
                            INSERT INTO MEMB_INFO ({columnsMEMB_INFO['name']}, {columnsMEMB_INFO['nick']}, {columnsMEMB_INFO['password']}, {columnsMEMB_INFO['email']}, {columnsMEMB_INFO['p_id']}, {columnsMEMB_INFO['tel']}, bloc_code, ctl1_code)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """, [nome, nick, senha, email, personal_id, telefone, '0', '0'])
                        conn.commit()  # Comitar as mudanças
            except Exception as e:
                messages.error(request, f"Erro ao cadastrar no banco do jogo: {str(e)}")
                return render(request, f"{request.current_theme}/cadastro.html", {"form": form, 'config': config})

            # ✅ Cadastrar no banco padrão do Django
            try:
                user = User.objects.create_user(username=nick, email=email, password=senha)
                user.first_name = nome
                user.save()
            except Exception as e:
                messages.error(request, f"Erro ao cadastrar no site: {str(e)}")
                return render(request, f"{request.current_theme}/cadastro.html", {"form": form, 'config': config})

            messages.success(request, "Cadastro realizado com sucesso!")
            return redirect("/")

        else:
            messages.error(request, "Corrija os erros no formulário.")

    else:
        form = CadastroForm()

    return render(request, f"{request.current_theme}/cadastro.html", {"form": form, 'config': config})


# Configuraçõs da views da pagina informações
def info_view(request):
    vips = VIPType.objects.all()
    #descricao = descriptionVip.objects.all()
    vantagens = VIPAdvantage.objects.all()
    descricoes = descriptionVip.objects.all()
    comandos = Info.objects.all()
    config = SiteConfig.objects.first()

    # Preparar o dicionário 'vantagens_por_descricao' na view
    vantagens_por_descricao = {}
    for descricao in descricoes:
        # Caso description_id seja o campo correto
        vantagens_por_descricao = {descricao.id: vantagens.filter(description_id=descricao.id) for descricao in descricoes}

    return render(request, f"{request.current_theme}/info.html", {
        'comandos': comandos,
        'config': config,
        'vips': vips,
        'vantagens': vantagens,
        'descricoes': descricoes,
        'vantagens_por_descricao': vantagens_por_descricao,
    })


# Configuraçõs da views da pagina download
def download_view(request):
    items = DownloadList.objects.all().order_by('-id')

    # Criar uma lista com os dados e converter 'created' para datetime
    items_list = [
        {
            'title': item.title,
            'link': item.link,
            'created': datetime.combine(item.created, datetime.min.time()) if item.created else None
        }
        for item in items
    ]

    return render(request, f"{request.current_theme}/download.html", {
        'itens': items_list, 
    })


def realizar_logout(request):
    # Verifica se o parâmetro 'logout' está presente na URL
    if 'logout' in request.GET:
        current_theme = request.session.get('theme', 'kingrox')  # Pega o tema atual da sessão
        logout(request)  # Realiza o logout
        request.session['theme'] = current_theme  # Garante que o tema seja mantido na próxima sessão
        messages.info(request, 'Você foi desconectado com sucesso, volte sempre!')  # Mensagem de logout
        return redirect('login')  # Redireciona para a página de login (ou outra página desejada)
    return None  # Caso contrário, não faz nada

def login_view(request):
    logout_redirect = realizar_logout(request)  # Chama a função de logout
    if logout_redirect:
        return logout_redirect  # Redireciona caso o logout tenha sido executado

    # Inicializa user_data com valores padrão
    user_data = {"nome": "Usuário não encontrado", "email": "N/A", "telefone": "N/A"}
    personagens = []

    if request.user.is_authenticated:
        try:
            conn = conexao_mssql()  # Usar a conexão global
            if conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"""
                        SELECT {columnsMEMB_INFO['name']}, {columnsMEMB_INFO['email']}, {columnsMEMB_INFO['tel']}
                        FROM MEMB_INFO
                        WHERE memb___id = %s
                    """, [request.user.username])
                    result = cursor.fetchone()

                    if result:
                        user_data = {
                            "nome": result[0],
                            "email": result[1],
                            "telefone": result[2],
                        }

                # Buscando personagens associados a esse usuário
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT Name
                        FROM Character
                        WHERE AccountID = %s
                    """, [request.user.username])
                    personagens = cursor.fetchall()

        except Exception as e:
            messages.error(request, f"Erro ao buscar dados no banco: {str(e)}")

    if request.method == 'POST':  # Processo de login via POST
        form = LoginForm(request.POST)

        if form.is_valid():
            memb___id = form.cleaned_data['memb___id']
            memb__pwd = form.cleaned_data['memb__pwd']

            try:
                conn = conexao_mssql()  # Usar a conexão global
                if conn:
                    with conn.cursor() as cursor:
                        cursor.execute("""
                            SELECT memb__pwd
                            FROM MEMB_INFO
                            WHERE memb___id = %s
                        """, [memb___id])
                        result = cursor.fetchone()

                    if result:
                        if result[0] == memb__pwd:
                            django_user, created = User.objects.get_or_create(username=memb___id)
                            django_user.set_password(memb__pwd)
                            django_user.save()

                            login(request, django_user)
                            messages.success(request, 'Usuário logado com sucesso!')
                            return redirect('login')  # Redirecionar após sucesso
                        else:
                            messages.error(request, 'Senha incorreta')
                    else:
                        messages.error(request, 'Usuário não encontrado')

            except Exception as e:
                messages.error(request, f"Erro ao buscar dados do usuário: {str(e)}")

    else:
        form = LoginForm()

    return render(request, f"{request.current_theme}/panelUser.html", {
        'form': form,
        **user_data,
        'personagens': [personagem[0] for personagem in personagens]
    })

def mudar_senha(request):
    logout_redirect = realizar_logout(request)  # Chama a função de logout
    if logout_redirect:
        return logout_redirect  # Redireciona caso o logout tenha sido executado

    if request.method == 'POST':
        form = MudarSenhaForm(request.POST)

        if form.is_valid():
            senha_atual = form.cleaned_data['senha_atual']
            nova_senha = form.cleaned_data['nova_senha']

            try:
                django_user = User.objects.get(username=request.user.username)

                if django_user.check_password(senha_atual):
                    django_user.set_password(nova_senha)
                    django_user.save()

                    # Atualiza a senha no banco MuOnline
                    conn = conexao_mssql()  # Usar a conexão global
                    if conn:
                        with conn.cursor() as cursor:
                            cursor.execute(f"""
                                UPDATE MEMB_INFO SET {columnsMEMB_INFO['password']} = %s 
                                WHERE {columnsMEMB_INFO['nick']} = %s
                            """, [nova_senha, request.user.username])

                    # Reautenticar o usuário após a alteração da senha
                    login(request, django_user)

                    messages.success(request, 'Senha alterada com sucesso!')
                    return redirect('mudar_senha')
                else:
                    messages.error(request, 'Senha atual incorreta.')
            except User.DoesNotExist:
                messages.error(request, 'Usuário não encontrado.')
            except Exception as e:
                messages.error(request, f'Ocorreu um erro: {str(e)}')
        else:
            messages.error(request, 'O formulário contém erros.')

    else:
        form = MudarSenhaForm()

    return render(request, f"{request.current_theme}/mudar_senha.html", {'form': form})

def mudar_id(request):
    logout_redirect = realizar_logout(request)  # Chama a função de logout
    if logout_redirect:
        return logout_redirect  # Redireciona caso o logout tenha sido executado

    if request.method == 'POST':
        form = MudarIDForm(request.POST, initial={'username': request.user.username})

        if form.is_valid():
            novo_id = form.cleaned_data['novo_id']

            # Usando a conexão 'muonline' para atualizar o ID no banco de dados
            conn = conexao_mssql()  # Usar a conexão global
            if conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"""
                        UPDATE MEMB_INFO SET {columnsMEMB_INFO['p_id']} = %s 
                        WHERE {columnsMEMB_INFO['nick']} = %s
                    """, [novo_id, request.user.username])

            messages.success(request, 'ID alterado com sucesso!')
            return redirect('mudar_id')
        else:
            messages.error(request, 'Ocorreu um erro. Verifique a senha.')

    else:
        form = MudarIDForm()

    return render(request, f"{request.current_theme}/mudar_id.html", {'form': form})


def mudar_classe(request):
    personagens = []
    conta = request.user.username

    # Busca todos os personagens associados à conta
    conn = conexao_mssql()  # Usar a conexão global
    with conn.cursor() as cursor:
        cursor.execute("SELECT Name FROM Character WHERE AccountID = %s", [conta])
        personagens = [row[0] for row in cursor.fetchall()]

    logout_redirect = realizar_logout(request)  # Chama a função de logout
    if logout_redirect:
        return logout_redirect  # Redireciona caso o logout tenha sido executado

    if request.method == 'POST':
        form = MudarClasseForm(request.POST, usuario=request.user)  # Passa o usuário ao inicializar o formulário
        if form.is_valid():
            personagem_atual = form.cleaned_data['personagem_atual']  # Personagem selecionado
            nova_classe = form.cleaned_data['nova_classe']  # Nova classe
            senha = form.cleaned_data['senha']  # Senha fornecida pelo usuário

            try:
                # Verifica se o personagem está online
                with conn.cursor() as cursor:
                    cursor.execute("SELECT ConnectStat FROM MEMB_STAT WHERE memb___id = %s", [conta])
                    connect_stat = cursor.fetchone()
                    if connect_stat and connect_stat[0] == 1:
                        messages.error(request, "Não é possível alterar a classe enquanto o personagem estiver online.")
                        return render(request, f"{request.current_theme}/mudar_classe.html", {"form": form, "personagens": personagens})

                    # Verifica a senha do usuário
                    cursor.execute(f"SELECT memb__pwd FROM MEMB_INFO WHERE {columnsMEMB_INFO['nick']} = %s", [conta])
                    senha_bd = cursor.fetchone()

                if not senha_bd or senha_bd[0].strip() != senha:
                    messages.error(request, "Senha incorreta!")
                    return render(request, f"{request.current_theme}/mudar_classe.html", {"form": form, "personagens": personagens})

                # Verifica se o personagem atual existe
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1 FROM Character WHERE Name = %s AND AccountID = %s", [personagem_atual, conta])
                    if not cursor.fetchone():
                        messages.error(request, "Personagem não encontrado ou não pertence a você.")
                        return render(request, f"{request.current_theme}/mudar_classe.html", {"form": form, "personagens": personagens})

                # Número de F's desejados
                numF = 7552  
                # Concatena 'F' numF vezes
                hex_value = 'F' * numF  
                # Cria a string no formato esperado '0x' + F's
                inventory_condition = f"0x{hex_value}"  

                # Converte a string hexadecimal para o formato binário necessário para comparação
                inventory_condition = bytes.fromhex(hex_value)  # Converte 'F' repetido em hex para binário

                # Verifica se o inventário está vazio (Inventory = 0x) ou se contém apenas o valor esperado
                with transaction.atomic(), conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT COUNT(*) 
                        FROM dbo.Character
                        WHERE Name = %s AND (Inventory != 0x AND Inventory != %s);
                    """, [personagem_atual, inventory_condition])

                    # Obtém o resultado da consulta
                    result = cursor.fetchone()
                    if result[0] > 0:
                        # Se o inventário não estiver vazio, mostra a mensagem pedindo para remover os itens
                        messages.warning(request, 'Para mudar a classe, remova os itens do inventário.')
                        return render(request, f"{request.current_theme}/mudar_classe.html", {"form": form, "personagens": personagens})

                # Lógica para alterar a classe somente após a verificação do inventário
                with transaction.atomic(), conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE dbo.Character
                        SET Class = %s
                        WHERE Name = %s AND AccountID = %s;
                    """, [nova_classe, personagem_atual, conta])

                    # Atualiza o inventário, MagicList e Quest
                    cursor.execute("""
                        UPDATE dbo.Character
                        SET MagicList = 0x,
                            Quest = 0x
                        WHERE Name = %s AND Inventory = %s;
                    """, [personagem_atual, inventory_condition])

                # Caso a classe seja alterada com sucesso
                messages.success(request, 'Classe do personagem alterada com sucesso!')
                return redirect('mudar_classe')

            except Exception as e:
                # Se ocorrer algum erro, exibe a mensagem de erro
                messages.error(request, f"Erro ao alterar a classe: {str(e)}")
                return render(request, f"{request.current_theme}/mudar_classe.html", {"form": form, "personagens": personagens})

    else:
        form = MudarClasseForm(usuario=request.user)

    return render(request, f"{request.current_theme}/mudar_classe.html", {'form': form})


def mudar_nome(request):
    logout_redirect = realizar_logout(request)  # Chama a função de logout
    if logout_redirect:
        return logout_redirect  # Redireciona caso o logout tenha sido executado

    personagens = []
    conta = request.user.username

    # Busca todos os personagens associados à conta
    conn = conexao_mssql()  # Usar a conexão global
    with conn.cursor() as cursor:
        cursor.execute("SELECT Name FROM Character WHERE AccountID = %s", [conta])
        personagens = [row[0] for row in cursor.fetchall()]

    if request.method == 'POST':
        form = AlterarNomeForm(request.POST, personagens=personagens)  # Passa personagens para o formulário

        if form.is_valid():
            personagem_atual = form.cleaned_data['personagem_atual']
            novo_nome = form.cleaned_data['novo_nome']
            senha = form.cleaned_data['senha']

            try:
                # Verifica a senha do usuário
                with conn.cursor() as cursor:
                    cursor.execute(f"SELECT {columnsMEMB_INFO['password']} FROM MEMB_INFO WHERE {columnsMEMB_INFO['nick']} = %s", [conta])
                    senha_bd = cursor.fetchone()

                if not senha_bd or senha_bd[0].strip() != senha:
                    messages.error(request, "Senha incorreta!")
                    return render(request, f"{request.current_theme}/mudar_nome.html", {"form": form, "personagens": personagens})

                # Valida o novo nome
                if len(novo_nome) > 10:
                    messages.error(request, "O novo nome deve ter no máximo 10 caracteres.")
                    return render(request, f"{request.current_theme}/mudar_nome.html", {"form": form, "personagens": personagens})

                # Verifica se o personagem atual existe
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1 FROM Character WHERE Name = %s AND AccountID = %s", [personagem_atual, conta])
                    if not cursor.fetchone():
                        messages.error(request, "Personagem não encontrado ou não pertence a você.")
                        return render(request, f"{request.current_theme}/mudar_nome.html", {"form": form, "personagens": personagens})

                    # Verifica se o personagem está online
                    cursor.execute("SELECT ConnectStat FROM MEMB_STAT WHERE memb___id = %s", [conta])
                    connect_stat = cursor.fetchone()
                    if connect_stat and connect_stat[0] == 1:
                        messages.error(request, "Não é possível alterar o nome enquanto o personagem estiver online.")
                        return render(request, f"{request.current_theme}/mudar_nome.html", {"form": form, "personagens": personagens})

                # Atualiza o nome nos locais onde é referenciado
                with transaction.atomic(), conn.cursor() as cursor:
                    def safe_update(query, params):
                        try:
                            cursor.execute(query, params)
                        except Exception:
                            pass

                    # Atualiza o nome nas tabelas necessárias
                    safe_update("UPDATE Character SET Name = %s WHERE Name = %s", [novo_nome, personagem_atual])
                    safe_update("UPDATE GuildMember SET Name = %s WHERE Name = %s", [novo_nome, personagem_atual])
                    safe_update("UPDATE Guild SET G_Master = %s WHERE G_Master = %s", [novo_nome, personagem_atual])
                    for coluna in ["GameID1", "GameID2", "GameID3", "GameID4", "GameID5", "GameIDC"]:
                        safe_update(f"UPDATE AccountCharacter SET {coluna} = %s WHERE {coluna} = %s", [novo_nome, personagem_atual])
                    safe_update("UPDATE OptionData SET Name = %s WHERE Name = %s", [novo_nome, personagem_atual])
                    safe_update("UPDATE T_CGuid SET Name = %s WHERE Name = %s", [novo_nome, personagem_atual])

                    # Confirma a alteração e renderiza a página
                    messages.success(request, 'Nome do personagem alterado com sucesso!')
                    return redirect('mudar_nome')

            except Exception as e:
                # Se ocorrer algum erro, exibe a mensagem de erro
                messages.error(request, f"Erro ao alterar o nome: {str(e)}")
                return render(request, f"{request.current_theme}/mudar_nome.html", {"form": form, "personagens": personagens})
    else:
        form = AlterarNomeForm(personagens=personagens)  # Passa a lista de personagens

    return render(request, f"{request.current_theme}/mudar_nome.html", {"form": form, "personagens": personagens})
