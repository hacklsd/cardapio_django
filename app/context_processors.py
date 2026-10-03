from django.conf import settings
from django.templatetags.static import static
from urllib.parse import quote_plus

from .models import ConfiguracaoRestaurante


def restaurant_info(request):
    configuracao = ConfiguracaoRestaurante.objects.filter(pk=1).first()
    whatsapp = (
        configuracao.whatsapp
        if configuracao is not None
        else settings.RESTAURANT_WHATSAPP
    )
    address = (
        configuracao.address or settings.RESTAURANT_ADDRESS
        if configuracao is not None
        else settings.RESTAURANT_ADDRESS
    )
    map_embed_url = (
        configuracao.map_embed_url or settings.RESTAURANT_MAP_EMBED_URL
        if configuracao is not None
        else settings.RESTAURANT_MAP_EMBED_URL
    )
    maps_url = (
        configuracao.maps_url or settings.RESTAURANT_MAPS_URL
        if configuracao is not None
        else settings.RESTAURANT_MAPS_URL
    )
    instagram_url = (
        configuracao.instagram_url or settings.RESTAURANT_INSTAGRAM_URL
        if configuracao is not None
        else settings.RESTAURANT_INSTAGRAM_URL
    )
    facebook_url = (
        configuracao.facebook_url or settings.RESTAURANT_FACEBOOK_URL
        if configuracao is not None
        else settings.RESTAURANT_FACEBOOK_URL
    )
    email = (
        configuracao.email or settings.RESTAURANT_EMAIL
        if configuracao is not None
        else settings.RESTAURANT_EMAIL
    )
    opening_hours = (
        configuracao.opening_hours or settings.RESTAURANT_OPENING_HOURS
        if configuracao is not None
        else settings.RESTAURANT_OPENING_HOURS
    )
    carousel_images = []
    default_carousel_images = (
        "images/ambiente-restaurante.jpg",
        "images/carne-servida.jpg",
        "images/prato-restaurante.jpg",
    )
    for field_name, default_image in zip(
        ("carousel_image_1", "carousel_image_2", "carousel_image_3"),
        default_carousel_images,
    ):
        image = getattr(configuracao, field_name, None) if configuracao else None
        carousel_images.append(image.url if image else static(default_image))

    restaurant_name = (
        configuracao.restaurant_name or settings.RESTAURANT_NAME
        if configuracao is not None
        else settings.RESTAURANT_NAME
    )
    restaurant_logo = (
        configuracao.restaurant_logo.url
        if configuracao is not None and configuracao.restaurant_logo
        else ""
    )

    if address and not map_embed_url:
        address_query = quote_plus(" ".join(address.split()))
        map_embed_url = (
            f"https://maps.google.com/maps?q={address_query}&output=embed"
        )
    return {
        "restaurant_name": restaurant_name,
        "restaurant_logo_url": restaurant_logo,
        "restaurant_whatsapp": whatsapp,
        "restaurant_instagram_url": instagram_url,
        "restaurant_facebook_url": facebook_url,
        "restaurant_email": email,
        "restaurant_opening_hours": opening_hours,
        "restaurant_address": address,
        "restaurant_map_embed_url": map_embed_url,
        "restaurant_maps_url": maps_url,
        "restaurant_carousel_images": carousel_images,
    }
