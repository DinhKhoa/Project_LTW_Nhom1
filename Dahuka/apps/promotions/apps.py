from django.apps import AppConfig


class PromotionsConfig(AppConfig):
    name = 'apps.promotions'
    verbose_name = 'Khuyến mãi'

    def ready(self):
        import apps.promotions.signals
