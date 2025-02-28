from django.urls import path
from .views import home, noticia_detalhe, notice_all, character_detail, ranking_view, cadastro_view, download_view, info_view, login_view, mudar_senha, mudar_id, mudar_classe, mudar_nome
from django.conf import settings
from django.conf.urls.static import static
from .context_processors import change_theme


urlpatterns = [
    path('', home, name='home'),
    path('change-theme/<str:theme_name>/', change_theme, name='change_theme'),
    path("<int:noticia_id>/", noticia_detalhe, name="noticia_detalhe"),
    path("todasNoticias/", notice_all, name="notice_all"),
    path('character/<str:character_name>/', character_detail, name='character_detail'),
    path('ranking/', ranking_view, name='ranking'),
    path("cadastro/", cadastro_view, name="cadastro"),
    path("download/", download_view, name="download"),
    path("info/", info_view, name="info"),
    path('login/', login_view, name='login'),
    path('mudar_senha/', mudar_senha, name='mudar_senha'),
    path('mudar_id/', mudar_id, name='mudar_id'),
    path('mudar_nome/', mudar_nome, name='mudar_nome'),
    path('mudar_classe/', mudar_classe, name='mudar_classe'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    