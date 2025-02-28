from Site.context_processors import get_user_theme

class themeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        theme = get_user_theme(request)
        if not theme:
            theme = 'kingrox'  # Tema padrão
        request.current_theme = theme
        return self.get_response(request)
