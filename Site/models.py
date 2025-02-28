from django.db import models
from django.contrib.auth.models import User
from django.utils.html import mark_safe
from datetime import datetime, timedelta



class SiteConfig(models.Model):
    choices = [
        ('Pontuativo', 'Pontuativo'),
        ('Acumulativo', 'Acumulativo'),
        ('Dinâmico', 'Dinâmico')
    ]
    
    name_server = models.CharField(verbose_name="Nome do servidor", max_length=50, default="")
    version_server = models.CharField(verbose_name="Versão do servidor", max_length=50, default="")
    reset_type = models.CharField(verbose_name="Tipo de Resets", choices=choices, max_length=20, default="")
    castle_siege_exists = models.PositiveIntegerField(choices=[(0, 'Desativar'), (1, 'Ativar')], default=0, verbose_name="Ativar Banner do CS")
    shop = models.URLField(default="")  
    forum = models.URLField(default="")
    term = models.TextField(verbose_name="Termos e Condições",  default="", null=True, blank=True)

    class Meta:
        db_table = "Django_SiteConfig"  # Força o nome correto da tabela no banco
        verbose_name = "01 - Configuração do Site"
        verbose_name_plural = "01 - Configurações do Site"

    def __str__(self):
        return "Configurações Gerais"


class UserTheme(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Usuário")
    theme = models.CharField(max_length=50, default='kingrox', verbose_name="Tema") 

    class Meta:
        db_table = "Django_TemaUser" 
        verbose_name = "06 - Tema do Usuário"
        verbose_name_plural = "06 - Temas do Usuário"

    def __str__(self):
        return self.user.username  # Opcional: representa o objeto pelo nome de usuário


class Slide(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to='slides/', blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)

    class Meta:
        db_table = "Django_Slide"  # Força o nome correto da tabela no banco
        verbose_name = "03 - Slide"
        verbose_name_plural = "03 - Slides"

    def get_image(self):
        """Retorna a imagem correta, seja do upload ou da URL"""
        return self.image.url if self.image else self.image_url

    def __str__(self):
        return self.title if self.title else "Slide sem título"


class Noticia(models.Model):
    titulo = models.CharField(max_length=255, default="" )
    conteudo = models.TextField(default="")  # Aceita HTML
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titulo

    def mostrar_conteudo(self):
        return mark_safe(self.conteudo)  # Permite exibir HTML no template
    class Meta:
        db_table = "Django_Noticias"  # Força o nome correto da tabela no banco
        verbose_name = "10 - Noticia do Servidor"
        verbose_name_plural = "10 - Noticias do Servidor"


class Comentario(models.Model):
    noticia = models.ForeignKey(Noticia, on_delete=models.CASCADE, related_name="comentarios")
    nome = models.CharField(max_length=100, default="")
    texto = models.TextField(default="")
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comentário de {self.nome}"
    

    class Meta:
        db_table = "Django_Comentarios"
        verbose_name = "11 - Comentário"
        verbose_name_plural = "11 - Comentários"


class DownloadList(models.Model):
    title = models.CharField(max_length=100)
    link = models.URLField() 
    created = models.DateField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f'{self.title}, {self.link}'
    
    class Meta:
        db_table = "Django_DownloadList"  # Força o nome correto da tabela no banco
        verbose_name = "05 - Lista de Download"  # Nome personalizado para o painel admin
        verbose_name_plural = "05 - Listas de Downloads"  # Nome plural



class VIPType(models.Model):
    site_config = models.ForeignKey(SiteConfig, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100, verbose_name="Nome do VIP")
    class Meta:
        db_table = "Django_VipNome"  # Força o nome correto da tabela no banco
        verbose_name = "Configuração do Vip"
        verbose_name_plural = "Configurações dos Vips"

    def __str__(self):
        return self.nome
    

class descriptionVip(models.Model):
    site_config = models.ForeignKey(SiteConfig, on_delete=models.CASCADE)
    description = models.CharField(max_length=100, verbose_name="Descrição da Vantagem")
    
    class Meta:
        db_table = "Django_VipDescricao"
        verbose_name = "Cadastrar Descrição"
        verbose_name_plural = "Cadastrar Descrições"

    def __str__(self):
        return self.description


class Info(models.Model):
    command = models.CharField(max_length=50, verbose_name="Comandos")
    description = models.CharField(max_length=255, verbose_name="Descrição", default="")

    class Meta:
        db_table = "Django_Info"  # Força o nome correto da tabela no banco
        verbose_name = "07 - Comando do servidor"
        verbose_name_plural = "07 - Comandos do Servidor"

    def __str__(self):
        return self.command
    

class VIPAdvantage(models.Model):
    vip_type = models.ForeignKey(VIPType, related_name="advantages", on_delete=models.CASCADE)
    description = models.ForeignKey(descriptionVip, on_delete=models.CASCADE, default="")
    value = models.CharField(max_length=100, verbose_name="Valor da Vantagem", blank=True, null=True, default="")
    
    class Meta:
        db_table = "Django_VipVantagem"  # Força o nome correto da tabela no banco
        verbose_name = "08 - Vantagem do VIP"
        verbose_name_plural = "08 - Vantagens dos VIPs"

    def __str__(self):
        return f"{self.description}: {self.value}"
    

class Event(models.Model):
    name = models.CharField(max_length=255, help_text="Nome do evento")
    start_time = models.TimeField(help_text="Hora de início do evento")
    #duration = models.IntegerField(help_text="Duração do evento em minutos")  # Duração em minutos
    time_remaining = models.DurationField(blank=True, null=True)  # Campo para armazenar o tempo restante
    event_day = models.CharField(max_length=9, choices=[('Segunda', 'Segunda'), ('Terça', 'Terça'), ('Quarta', 'Quarta'),
                                                       ('Quinta', 'Quinta'), ('Sexta', 'Sexta'), ('Sábado', 'Sábado'), ('Domingo', 'Domingo')],
                                 help_text="Dia da semana do evento")

    def __str__(self):
        return f"{self.name} - {self.event_day} às {self.start_time}"

    def formatted_time(self):
        """Retorna a hora formatada para exibição na tela"""
        return self.start_time.strftime('%H:%M:%S')


    def time_remaining_func(self):
        """Retorna o tempo restante, o status do evento e a duração em segundos."""
        now = datetime.now()

        days_mapping = {
            'Segunda': 0,
            'Terça': 1,
            'Quarta': 2,
            'Quinta': 3,
            'Sexta': 4,
            'Sábado': 5,
            'Domingo': 6
        }

        event_day_num = days_mapping[self.event_day]
        event_datetime = datetime.combine(now.date(), self.start_time)
        days_until_event = (event_day_num - now.weekday()) % 7
        event_datetime += timedelta(days=days_until_event)

        if event_datetime < now:
            event_datetime += timedelta(weeks=1)

        remaining_time = event_datetime - now
        remaining_seconds = remaining_time.total_seconds()
        #duration_seconds = self.duration * 60  # Duração do evento em segundos

        if remaining_seconds > 0:
            status = f"{self.name} - Faltam {int(remaining_seconds)} segundos"
        elif remaining_seconds <= 0 and remaining_seconds: # > -duration_seconds:
            status = f"{self.name} - Evento iniciado!"
            remaining_seconds = 0
        else:
            status = f"{self.name} - Evento Finalizado!"
            remaining_seconds = 0

        return remaining_seconds, status, # duration_seconds


    class Meta:
        db_table = "Django_Eventos"  # Força o nome correto da tabela no banco
        verbose_name = "09 - Cadastrar Evento"
        verbose_name_plural = "09 - Cadastrar Eventos"


class Event(models.Model):
    name = models.CharField(max_length=255, help_text="Nome do evento")
    start_time = models.TimeField(help_text="Hora de início do evento")
    #duration = models.IntegerField(help_text="Duração do evento em minutos")  # Duração em minutos
    time_remaining = models.DurationField(blank=True, null=True)  # Campo para armazenar o tempo restante
    event_day = models.CharField(max_length=9, choices=[('Segunda', 'Segunda'), ('Terça', 'Terça'), ('Quarta', 'Quarta'),
                                                       ('Quinta', 'Quinta'), ('Sexta', 'Sexta'), ('Sábado', 'Sábado'), ('Domingo', 'Domingo')],
                                 help_text="Dia da semana do evento")

    def __str__(self):
        return f"{self.name} - {self.event_day} às {self.start_time}"

    def formatted_time(self):
        """Retorna a hora formatada para exibição na tela"""
        return self.start_time.strftime('%H:%M:%S')


    def time_remaining_func(self):
        """Retorna o tempo restante, o status do evento e a duração em segundos."""
        now = datetime.now()

        days_mapping = {
            'Segunda': 0,
            'Terça': 1,
            'Quarta': 2,
            'Quinta': 3,
            'Sexta': 4,
            'Sábado': 5,
            'Domingo': 6
        }

        event_day_num = days_mapping[self.event_day]
        event_datetime = datetime.combine(now.date(), self.start_time)
        days_until_event = (event_day_num - now.weekday()) % 7
        event_datetime += timedelta(days=days_until_event)

        if event_datetime < now:
            event_datetime += timedelta(weeks=1)

        remaining_time = event_datetime - now
        remaining_seconds = remaining_time.total_seconds()
        #duration_seconds = self.duration * 60  # Duração do evento em segundos

        if remaining_seconds > 0:
            status = f"{self.name} - Faltam {int(remaining_seconds)} segundos"
        elif remaining_seconds <= 0 and remaining_seconds: # > -duration_seconds:
            status = f"{self.name} - Evento iniciado!"
            remaining_seconds = 0
        else:
            status = f"{self.name} - Evento Finalizado!"
            remaining_seconds = 0

        return remaining_seconds, status, # duration_seconds


    class Meta:
        db_table = "Django_EventTime"  # Força o nome correto da tabela no banco
        verbose_name = "09 - Cadastrar Evento"
        verbose_name_plural = "09 - Cadastrar Eventos"



class CastleSiege(models.Model):
    SIEGE_OPTIONS = [
        ('0', 'Desativar'),
        ('1', 'Ativado'),
    ]
    MAP_SVR_GROUP = models.CharField(max_length=100, primary_key=True)
    StartSiege = models.DateTimeField(db_column='SIEGE_START_DATE')
    EndSiege = models.DateTimeField(db_column='SIEGE_END_DATE')
    ListaCercoGuild = models.CharField(db_column='SIEGE_GUILDLIST_SETTED', max_length=5, choices=SIEGE_OPTIONS, default='1')
    CastleOccupy = models.CharField(db_column='CASTLE_OCCUPY', max_length=5, choices=SIEGE_OPTIONS, default='1') 
    OWNER_GUILD = models.CharField(db_column='OWNER_GUILD', max_length=50, null=True)

    class Meta:
        db_table = 'MuCastle_DATA'  # Nome da tabela no banco
        verbose_name = "02 - Castle Siege"
        managed = False  # Evita que o Django tente recriar a tabela

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.StartSiege} - {self.EndSiege} - {self.OWNER_GUILD}"

