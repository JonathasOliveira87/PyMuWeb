from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import password_validation
from django.db import connections


class CadastroForm(forms.Form):
    nome = forms.CharField(max_length=100, required=True, label="Nome")
    nick = forms.CharField(max_length=10, required=True, label="Nick")
    senha = forms.CharField(widget=forms.PasswordInput, required=True, label="Senha")
    repetir_senha = forms.CharField(widget=forms.PasswordInput, required=True, label="Repetir Senha")
    email = forms.EmailField(required=True, label="Email")
    repetir_email = forms.EmailField(required=True, label="Repetir Email")
    personal_id = forms.CharField(max_length=50, required=True, label="Personal ID")
    telefone = forms.CharField(max_length=20, required=True, label="Telefone")

    def clean_nick(self):
        """Valida se o nick já existe"""
        nick = self.cleaned_data.get("nick")
        if User.objects.filter(username=nick).exists():
            raise forms.ValidationError(f"O nick {nick} já está em uso!")
        return nick

    def clean_email(self):
        """Valida se o email já existe"""
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("O email já está em uso!")
        return email

    def clean(self):
        """Valida se as senhas e os emails coincidem"""
        cleaned_data = super().clean()
        senha = cleaned_data.get("senha")
        repetir_senha = cleaned_data.get("repetir_senha")
        email = cleaned_data.get("email")
        repetir_email = cleaned_data.get("repetir_email")

        if senha and repetir_senha and senha != repetir_senha:
            self.add_error("repetir_senha", "As senhas não coincidem!")

        if email and repetir_email and email != repetir_email:
            self.add_error("repetir_email", "Os e-mails não coincidem!")

        return cleaned_data


class LoginForm(forms.Form):
    memb___id = forms.CharField(label="Usuário", max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    memb__pwd = forms.CharField(label="Senha", widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class MudarSenhaForm(forms.Form):
    senha_atual = forms.CharField(widget=forms.PasswordInput, label='Senha Atual', min_length=6)
    nova_senha = forms.CharField(widget=forms.PasswordInput, label='Nova Senha', min_length=6)

    def clean_nova_senha(self):
        nova_senha = self.cleaned_data.get('nova_senha')
        
        # Validação extra de senha (opcional, pode personalizar conforme necessário)
        password_validation.validate_password(nova_senha)
        return nova_senha


class MudarIDForm(forms.Form):
    novo_id = forms.CharField(label="Novo ID", widget=forms.PasswordInput, min_length=7, max_length=7)
    senha = forms.CharField(label="Senha", widget=forms.PasswordInput, min_length=6)

    def clean_novo_id(self):
        novo_id = self.cleaned_data.get('novo_id')
        if not novo_id.isdigit():
            raise forms.ValidationError("O novo ID deve conter apenas números.")
        if len(novo_id) != 7:
            raise forms.ValidationError("O novo ID deve ter exatamente 7 dígitos.")
        return novo_id

    def clean_senha(self):
        senha = self.cleaned_data.get('senha')
        # Verifica se a senha fornecida é correta
        user = User.objects.get(username=self.initial['username'])
        if not user.check_password(senha):  # Verifica se a senha está correta
            raise forms.ValidationError("A senha está incorreta.")
        return senha


class MudarClasseForm(forms.Form):
    personagem_atual = forms.ChoiceField(label="Personagem Atual", required=True)
    nova_classe = forms.ChoiceField(
        label="Nova Classe", 
        choices=[(17, 'BK'), (48, 'MG'), (33, 'ME'), (1, 'SM')],  # Adapte conforme as classes possíveis
        required=True
    )
    senha = forms.CharField(label="Senha", widget=forms.PasswordInput, required=True)

    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop('usuario', None)  # Recebe o usuário atual
        super().__init__(*args, **kwargs)

        if usuario:
            # Pega os personagens do usuário do banco de dados
            with connections['muonline'].cursor() as cursor:
                cursor.execute("SELECT Name FROM Character WHERE AccountID = %s", [usuario.username])
                personagens = [row[0] for row in cursor.fetchall()]
            
            # Define as escolhas para o campo de personagem
            self.fields['personagem_atual'].choices = [(p, p) for p in personagens]
    
    def clean_personagem_atual(self):
        personagem_atual = self.cleaned_data.get('personagem_atual')

        # Verifica se o personagem selecionado é válido
        if not personagem_atual:
            raise forms.ValidationError("Selecione um personagem válido.")

        return personagem_atual


class AlterarNomeForm(forms.Form):
    personagem_atual = forms.ChoiceField(label="Personagem Atual", required=True)
    novo_nome = forms.CharField(max_length=10, label="Novo Nome")
    senha = forms.CharField(widget=forms.PasswordInput(), label="Senha")

    def __init__(self, *args, **kwargs):
        personagens = kwargs.pop('personagens', [])
        super().__init__(*args, **kwargs)
        self.fields['personagem_atual'].choices = [(p, p) for p in personagens]  # Preenche a lista de personagens
