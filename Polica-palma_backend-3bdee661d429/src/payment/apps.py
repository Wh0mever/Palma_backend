from django.apps import AppConfig

class PaymentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'src.payment'

    def ready(self):
        import src.payment.signals