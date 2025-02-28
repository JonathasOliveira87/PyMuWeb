# mapear e controlar o uso dos bancos de dados
class MultiDBRouter:
    def db_for_read(self, model, **hints):
        """Define qual banco será usado para leitura"""
        if model._meta.app_label == 'muonline':
            return 'muonline'
        return 'default'

    def db_for_write(self, model, **hints):
        """Define qual banco será usado para escrita"""
        if model._meta.app_label == 'muonline':
            return None  # Evita que o Django tente escrever no MuOnline
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """Permite relações entre modelos do mesmo banco"""
        return None  # Evita relacionamentos entre bancos

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Define qual banco pode receber migrações"""
        if app_label == 'muonline':
            return False  # Evita migrações no MuOnline
        return True
