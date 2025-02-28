from django.contrib import admin
from .models import UserTheme, Slide, DownloadList, Info,  SiteConfig, VIPType, descriptionVip, VIPAdvantage, Event, Comentario, Noticia, CastleSiege, SiteConfig
from django.db import connections
from django.core.exceptions import ValidationError
from django.db import connections
from .config import conexao_mssql


class VIPTypeInline(admin.TabularInline):
    model = VIPType
    extra = 0


class descriptionVipInline(admin.TabularInline):
    model = descriptionVip
    extra = 0

admin.site.register(DownloadList)


@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    inlines = [VIPTypeInline, descriptionVipInline]
    list_display = ['castle_siege_status', 'castle_siege_exists', 'name_server', 'version_server', 'reset_type']
    list_editable = ['castle_siege_exists', 'name_server', 'version_server', 'reset_type']

    def castle_siege_status(self, obj):
        return "Castle Siege Ativado" if obj.castle_siege_exists else "Castle Siege Desativado"
    castle_siege_status.short_description = "Configurações do Site"

    # Evita acessar o banco de dados durante a inicialização
    def has_add_permission(self, request):
        if not hasattr(self, 'initialized'):  # Apenas executa após inicialização
            self.initialized = True
            return True
        return not SiteConfig.objects.exists()

# Adiciona validação no modelo
def validate_single_instance():
    if SiteConfig.objects.count() > 1:
        raise ValidationError("Apenas uma configuração é permitida.")
    



# Verifica se a tabela CastleSiege existe no banco de dados
def table_exists(table_name):
    conn = conexao_mssql()  # Usar a conexão global
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = ?", [table_name]
        )
        return cursor.fetchone()[0] == 1



if table_exists('MuCastle_DATA'):
    @admin.register(CastleSiege)
    class CastleSiegeAdmin(admin.ModelAdmin):

        def get_queryset(self, request):
            queryset = super().get_queryset(request)
            return queryset.using('muonline')  # Garante que a consulta usa o banco 'muonline'

        def save_model(self, request, obj, form, change):
            # Forçar o uso do banco 'muonline' ao salvar o modelo
            obj.save(using='muonline')

        def has_add_permission(self, request):
            return False  # Remove o botão "Adicionar"
            
        list_display = ['MAP_SVR_GROUP', 'StartSiege', 'EndSiege', 'OWNER_GUILD']






        
@admin.register(Slide)
class UserThemeAdmin(admin.ModelAdmin):
    list_display = ('title', 'image', 'image_url')  # Defina quais campos mostrar na listagem
    list_filter = ('image', 'image_url')  # Adicione filtros por tema, se desejar


class ComentarioInline(admin.TabularInline):
    model = Comentario
    extra = 1  # Permite adicionar comentários direto no admin

class NoticiaAdmin(admin.ModelAdmin):
    list_display = ("titulo", "criado_em", "atualizado_em")
    search_fields = ("titulo",)
    inlines = [ComentarioInline]

admin.site.register(Noticia, NoticiaAdmin)
admin.site.register(Comentario)



@admin.register(Info)
class InfoAdmin(admin.ModelAdmin):
    list_display = ('command', 'description')


@admin.register(VIPAdvantage)
class VIPAdvantageAdmin(admin.ModelAdmin):
    list_display = ('vip_type', 'description', 'value')
    
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'event_day', 'formatted_time')
    fields = ['name', 'start_time', 'event_day']


# Registre o modelo no painel de administração
@admin.register(UserTheme)
class UserThemeAdmin(admin.ModelAdmin):
    list_display = ('user', 'theme')  # Defina quais campos mostrar na listagem
    list_filter = ('theme',)  # Adicione filtros por tema, se desejar




