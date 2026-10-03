from django.core.validators import URLValidator
from django.db import models


https_url_validator = URLValidator(schemes=["https"])


class ConfiguracaoRestaurante(models.Model):
    id = models.PositiveSmallIntegerField(
        primary_key=True,
        default=1,
        editable=False,
    )
    restaurant_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Nome do restaurante",
    )
    restaurant_logo = models.ImageField(
        upload_to="restaurant/",
        blank=True,
        verbose_name="Logo do restaurante",
    )
    whatsapp = models.CharField(
        max_length=15,
        blank=True,
        help_text="Número internacional, com DDI e DDD, somente dígitos.",
    )
    address = models.TextField(blank=True)
    map_embed_url = models.URLField(
        blank=True,
        validators=[URLValidator(schemes=["https"])],
    )
    maps_url = models.URLField(
        blank=True,
        validators=[https_url_validator],
    )
    email = models.EmailField(blank=True)
    opening_hours = models.TextField(blank=True)
    instagram_url = models.URLField(blank=True, validators=[https_url_validator])
    facebook_url = models.URLField(blank=True, validators=[https_url_validator])
    carousel_image_1 = models.ImageField(
        upload_to="carousel/",
        blank=True,
        verbose_name="Imagem 1 do carrossel",
    )
    carousel_image_2 = models.ImageField(
        upload_to="carousel/",
        blank=True,
        verbose_name="Imagem 2 do carrossel",
    )
    carousel_image_3 = models.ImageField(
        upload_to="carousel/",
        blank=True,
        verbose_name="Imagem 3 do carrossel",
    )

    class Meta:
        verbose_name = "configuração do restaurante"
        verbose_name_plural = "configuração do restaurante"

    def __str__(self):
        return "Configuração do restaurante"
