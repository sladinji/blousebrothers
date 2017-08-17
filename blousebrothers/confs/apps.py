from django.apps import AppConfig


class ConfsConfig(AppConfig):
    name = 'confs'

    def ready(self):
        import blousebrothers.checkout.signals #  noqa
