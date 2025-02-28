
# temas disponíveis
templates = ['kingrox', 'pZone']

import pyodbc


# Função para obter a conexão com o banco de dados
def conexao_mssql():
    global conn
    conn = None
    if conn is None:  # Se a conexão não existir ainda
        try:
            conn = pyodbc.connect(
                "DRIVER={SQL Server};"
                "SERVER=127.0.0.1,1433;"  # Endereço do servidor
                "DATABASE=MuOnlineS6;"  # Nome do banco de dados
                "UID=sa;"  # Usuário
                "PWD=123456;"  # Senha
                "TrustServerCertificate=yes;"  # Ignora a validação do certificado (útil para desenvolvimento)
            )
            print("Conexão bem-sucedida!")
        except pyodbc.Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            conn = None  # Se houver erro, a conexão será definida como None
    return conn



# Definindo as colunas específicas
columnsCharacter = {
    'reset': 'ResetCount',  # Nome da coluna para 'Reset'
    'master_reset': 'GrandResetCount',  # Nome da coluna para 'Master Reset'
    'pk': 'pkcount',  # Nome da coluna para 'PK'
    'hero': 'pkcount',  # Nome da coluna para 'Herói'
    'guild_score': 'G_Score',  # Nome da coluna para 'Guild Score'
}


# Definindo as colunas específicas
columnsMEMB_INFO = {
    'name': 'memb_name',  # Nome da coluna para 'memb_name'
    'nick': 'memb___id',  # Nome da coluna para 'memb___id'
    'password': 'memb__pwd',  # Nome da coluna para 'memb__pwd'
    'email': 'mail_addr',  # Nome da coluna para 'mail_addr'
    'tel': 'tel__numb',  # Nome da coluna para 'tel__numb'
    'p_id': 'sno__numb',  # Nome da coluna para 'sno__numb'
}

