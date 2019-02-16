from django.apps import AppConfig


class UsersAppConfig(AppConfig):

    name = "friendcheck.users"
    verbose_name = "Users"

    def ready(self):
        try:
            import users.signals  # noqa F401
        except ImportError:
            pass
        # import the valid_ipn_received hook
        import users.paypal_signals
