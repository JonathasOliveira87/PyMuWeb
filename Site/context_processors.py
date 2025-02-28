from django.db import connection, connections
from .models import UserTheme
from django.shortcuts import render, redirect
from .config import *
from django.contrib import messages
from .models import SiteConfig

# Retorna o tema selecionado pelo usuário. Se o usuário estiver autenticado, o tema é recuperado do banco de dados. 
# Caso contrário, o tema é obtido da sessão do usuário ou define 'kingrox' como padrão.
def get_user_theme(request):
    # Quando o usuário está autenticado, tentamos obter o tema do banco de dados,
    # mas se houver um tema na sessão, usamos o tema da sessão.
    if request.user.is_authenticated:
        user_theme = UserTheme.objects.filter(user=request.user).first()
        if user_theme:
            theme = request.session.get('theme', user_theme.theme)
        else:
            theme = 'kingrox'  # Tema padrão se não houver tema salvo no banco
        request.session['theme'] = theme  # Atualiza a sessão com o tema
    else:
        theme = request.session.get('theme', 'kingrox')  # Tema padrão para não autenticados
    
    return theme


def change_theme(request, theme_name=None):
    # Se o tema for enviado via POST, capturamos o valor
    if request.method == 'POST':
        theme_name = request.POST.get('theme', theme_name)

    if theme_name:
        # Armazena o tema na sessão
        request.session['theme'] = theme_name
        messages.success(request, f"Tema alterado para {theme_name}!")

        # Se o usuário estiver autenticado, atualiza o tema no banco de dados
        if request.user.is_authenticated:
            user_theme, created = UserTheme.objects.get_or_create(user=request.user)
            user_theme.theme = theme_name
            user_theme.save()

    return redirect('/')  # Redireciona para a página inicial ou outra URL


def global_theme(request):
    # Obtém o tema atual
    theme = get_user_theme(request)
    if not theme:
        theme = 'kingrox'  # Tema padrão

    # Outros temas disponíveis
    temas = templates

    return {
        'current_theme': theme,
        'temas': temas,
    }


def site_config(request):
    config = SiteConfig.objects.first()
    return {'site_config': config}



def get_total_online(request):
    total_online = 0  # Valor padrão
    if request.resolver_match:  # Garante que a requisição esteja sendo processada corretamente
        try:
            conn = conexao_mssql()  # Obtém a conexão com o banco de dados
            if conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) AS TotalOnline FROM MEMB_STAT WHERE ConnectStat = 1")
                    total_online = cursor.fetchone()[0] or 0
        except Exception as e:
            print(f"Erro ao buscar total de online: {e}")  # Apenas para depuração
    return {'total_online': total_online}
