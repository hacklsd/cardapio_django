from io import BytesIO
from tempfile import TemporaryDirectory

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from PIL import Image

from .models import ConfiguracaoRestaurante


class HomePageTests(TestCase):
    def test_home_page_loads(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sabor que merece")
        self.assertNotContains(response, "DDDNUMERO")
        self.assertNotContains(response, "Copacabana Palace")
        self.assertNotContains(response, 'href="#mapa"')
        self.assertNotContains(response, 'href="#contato"')

    def test_restaurant_name_and_logo_are_displayed_in_public_header(self):
        image_file = BytesIO()
        Image.new("RGB", (8, 8), color="purple").save(image_file, format="PNG")

        with TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                configuracao = ConfiguracaoRestaurante.objects.create(
                    restaurant_name="Fuzue BBQ",
                    restaurant_logo=SimpleUploadedFile(
                        "logo.png",
                        image_file.getvalue(),
                        content_type="image/png",
                    ),
                )

                response = self.client.get(reverse("home"))

        self.assertContains(response, 'class="site-brand"')
        self.assertContains(response, 'class="site-brand-logo"')
        self.assertContains(response, configuracao.restaurant_logo.url)
        self.assertContains(response, "Fuzue BBQ")
        self.assertContains(response, "<title>Fuzue BBQ | Início</title>")

    @override_settings(RESTAURANT_NAME="Restaurante do Ambiente")
    def test_public_header_uses_default_name_when_not_configured(self):
        response = self.client.get(reverse("home"))

        self.assertContains(response, "Restaurante do Ambiente")
        self.assertContains(response, 'class="site-brand-placeholder"')

    def test_home_carousel_uses_original_restaurant_illustrations(self):
        response = self.client.get(reverse("home"))

        for image in (
            "static/images/ambiente-restaurante.jpg",
            "static/images/carne-servida.jpg",
            "static/images/prato-restaurante.jpg",
        ):
            with self.subTest(image=image):
                self.assertContains(response, image)
        self.assertNotContains(response, "images/restaurante-sala.svg")
        self.assertNotContains(response, "images/restaurante-brasa.svg")
        self.assertNotContains(response, "images/restaurante-mesa.svg")

    @override_settings(
        RESTAURANT_NAME="Fuzue BBQ",
        RESTAURANT_WHATSAPP="5511999999999",
        RESTAURANT_INSTAGRAM_URL="https://www.instagram.com/fuzuebbq/",
        RESTAURANT_ADDRESS="Rua do Restaurante, 10",
        RESTAURANT_MAP_EMBED_URL="https://maps.google.com/maps?q=restaurante&output=embed",
        RESTAURANT_MAPS_URL="https://maps.google.com/?q=restaurante",
    )
    def test_contact_details_are_configurable(self):
        response = self.client.get(reverse("home"))

        self.assertContains(response, "https://wa.me/5511999999999")
        self.assertContains(response, "https://www.instagram.com/fuzuebbq/")
        self.assertContains(response, "Rua do Restaurante, 10")
        self.assertContains(response, "https://maps.google.com/?q=restaurante")

    @override_settings(RESTAURANT_WHATSAPP="5511888888888")
    def test_saved_whatsapp_number_controls_floating_button(self):
        ConfiguracaoRestaurante.objects.create(whatsapp="5511999999999")

        response = self.client.get(reverse("home"))

        self.assertContains(
            response,
            'class="whatsapp-float"\n        href="https://wa.me/5511999999999"',
            html=False,
        )
        self.assertContains(response, 'class="whatsapp-float-icon"')
        self.assertContains(response, 'viewBox="0 0 220 220"')
        self.assertContains(response, "Fale conosco pelo WhatsApp")
        self.assertNotContains(response, "5511888888888")

    def test_floating_button_is_hidden_without_whatsapp_number(self):
        ConfiguracaoRestaurante.objects.create(whatsapp="")

        response = self.client.get(reverse("home"))

        self.assertNotContains(response, 'class="whatsapp-float"')

    def test_saved_location_is_shown_next_to_contact_card(self):
        ConfiguracaoRestaurante.objects.create(
            whatsapp="5511999999999",
            address="Rua do Restaurante, 10",
            map_embed_url="https://www.google.com/maps/embed?pb=local",
            maps_url="https://maps.google.com/?q=restaurante",
        )

        response = self.client.get(reverse("home"))

        self.assertContains(response, 'class="footer-info-grid"')
        self.assertContains(response, 'class="contact-card"')
        self.assertContains(response, 'class="location-panel"')
        self.assertContains(response, "Rua do Restaurante, 10")
        self.assertContains(
            response,
            'src="https://www.google.com/maps/embed?pb=local"',
        )
        self.assertContains(
            response,
            'href="https://maps.google.com/?q=restaurante"',
        )

    def test_location_map_is_generated_from_address_and_maps_link(self):
        ConfiguracaoRestaurante.objects.create(
            address="Rua do Restaurante, 10 - São Paulo",
            maps_url="https://maps.google.com/?q=restaurante",
        )

        response = self.client.get(reverse("home"))

        self.assertContains(response, 'class="location-panel"')
        self.assertContains(
            response,
            "https://maps.google.com/maps?q=Rua+do+Restaurante%2C+10+-+S%C3%A3o+Paulo&amp;output=embed",
            html=False,
        )
        self.assertContains(
            response,
            'href="https://maps.google.com/?q=restaurante"',
        )

    def test_contact_information_is_rendered_from_admin_settings(self):
        ConfiguracaoRestaurante.objects.create(
            email="contato@exemplo.com",
            opening_hours="Segunda a sexta: 9h às 18h\nSábado: 10h às 14h",
            instagram_url="https://www.instagram.com/restaurante/",
            facebook_url="https://www.facebook.com/restaurante/",
        )

        response = self.client.get(reverse("home"))

        self.assertContains(response, 'href="mailto:contato@exemplo.com"')
        self.assertContains(response, "Segunda a sexta: 9h às 18h")
        self.assertContains(
            response,
            'href="https://www.instagram.com/restaurante/"',
        )
        self.assertContains(response, 'class="social-icon instagram-icon"')
        self.assertContains(
            response,
            'href="https://www.facebook.com/restaurante/"',
        )
