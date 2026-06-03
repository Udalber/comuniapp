from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Usuario personalizado de ComuniApp.

    TODO (sesión accounts): perfil de vendedor/comprador, avatar, teléfono.
    """

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"
