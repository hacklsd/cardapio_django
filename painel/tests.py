from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from io import BytesIO
from tempfile import TemporaryDirectory

from PIL import Image

from app.models import ConfiguracaoRestaurante
from menu.models import Categoria, Produto


class PainelAccessTests(TestCase):
    def setUp(self):
        self.dashboard_url = reverse("painel:dashboard")
        self.admin_user = get_user_model().objects.create_superuser(
            username="administrador",
            password="senha-segura",
        )
        self.regular_user = get_user_model().objects.create_user(
            username="cliente",
            password="senha-segura",
        )
        self.staff_user = get_user_model().objects.create_user(
            username="equipe",
            password="senha-segura",
            is_staff=True,
        )

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(self.dashboard_url)

        self.assertRedirects(
            response,
            f'{reverse("painel:login")}?next={self.dashboard_url}',
        )

    def test_authenticated_non_staff_user_is_forbidden(self):
        self.client.force_login(self.regular_user)

        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.status_code, 403)

    def test_staff_without_superuser_access_is_forbidden(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.status_code, 403)

    def test_non_superuser_cannot_log_in_to_panel(self):
        response = self.client.post(
            reverse("painel:login"),
            {"username": "equipe", "password": "senha-segura"},
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_superuser_can_log_in_and_open_dashboard(self):
        response = self.client.post(
            reverse("painel:login"),
            {"username": "administrador", "password": "senha-segura"},
        )

        self.assertRedirects(response, self.dashboard_url)
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Painel do cardápio")

    def test_staff_login_rejects_external_next_url(self):
        response = self.client.post(
            reverse("painel:login"),
            {
                "username": "administrador",
                "password": "senha-segura",
                "next": "https://example.com/",
            },
        )

        self.assertRedirects(response, self.dashboard_url)

    def test_logout_requires_post_and_ends_admin_session(self):
        self.client.force_login(self.admin_user)

        self.assertEqual(self.client.get(reverse("painel:logout")).status_code, 405)
        response = self.client.post(reverse("painel:logout"))

        self.assertRedirects(response, reverse("painel:login"))
        self.assertNotIn("_auth_user_id", self.client.session)


class PainelManagementTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            username="administrador",
            password="senha-segura",
        )
        self.client.force_login(self.user)
        self.categoria = Categoria.objects.create(nome="Entradas")

    def test_category_can_be_created_updated_and_deleted(self):
        response = self.client.post(
            reverse("painel:categoria_nova"),
            {"nome": "Bebidas", "ordem": 2, "ativa": "on"},
        )
        self.assertRedirects(response, reverse("painel:categorias"))
        categoria = Categoria.objects.get(nome="Bebidas")
        self.assertEqual(categoria.ordem, 2)

        response = self.client.post(
            reverse("painel:categoria_editar", args=[categoria.pk]),
            {"nome": "Drinks", "ordem": 3, "ativa": "on"},
        )
        self.assertRedirects(response, reverse("painel:categorias"))
        categoria.refresh_from_db()
        self.assertEqual(categoria.nome, "Drinks")

        response = self.client.post(
            reverse("painel:categoria_excluir", args=[categoria.pk])
        )
        self.assertRedirects(response, reverse("painel:categorias"))
        self.assertFalse(Categoria.objects.filter(pk=categoria.pk).exists())

    def test_product_can_be_created_updated_and_deleted(self):
        create_url = reverse("painel:produto_novo")
        response = self.client.post(
            create_url,
            {
                "categoria": self.categoria.pk,
                "nome": "Pão de alho",
                "descricao": "Assado na brasa",
                "preco": "12.00",
                "ordem": 1,
                "ativo": "on",
            },
        )
        self.assertRedirects(response, reverse("painel:produtos"))
        produto = Produto.objects.get(nome="Pão de alho")
        self.assertEqual(produto.categoria, self.categoria)

        response = self.client.post(
            reverse("painel:produto_editar", args=[produto.pk]),
            {
                "categoria": self.categoria.pk,
                "nome": "Pão de alho especial",
                "descricao": "",
                "preco": "15.00",
                "ordem": 2,
                "ativo": "on",
            },
        )
        self.assertRedirects(response, reverse("painel:produtos"))
        produto.refresh_from_db()
        self.assertEqual(produto.nome, "Pão de alho especial")
        self.assertEqual(str(produto.preco), "15.00")

        response = self.client.post(
            reverse("painel:produto_excluir", args=[produto.pk])
        )
        self.assertRedirects(response, reverse("painel:produtos"))
        self.assertFalse(Produto.objects.filter(pk=produto.pk).exists())

    def test_deleting_category_also_deletes_its_products(self):
        produto = Produto.objects.create(
            categoria=self.categoria,
            nome="Produto relacionado",
        )

        response = self.client.get(
            reverse("painel:categoria_excluir", args=[self.categoria.pk])
        )
        self.assertContains(response, "também serão excluídos")

        self.client.post(
            reverse("painel:categoria_excluir", args=[self.categoria.pk])
        )
        self.assertFalse(Produto.objects.filter(pk=produto.pk).exists())

    def test_panel_templates_render(self):
        produto = Produto.objects.create(
            categoria=self.categoria,
            nome="Pão de alho",
        )
        urls = (
            "painel:categorias",
            "painel:produtos",
            "painel:categoria_nova",
            "painel:produto_novo",
            ("painel:categoria_excluir", self.categoria.pk),
            ("painel:produto_excluir", produto.pk),
        )
        for route in urls:
            name, *args = route if isinstance(route, tuple) else (route,)
            with self.subTest(page=name):
                response = self.client.get(reverse(name, args=args))
                self.assertEqual(response.status_code, 200)
                if name == "painel:produto_novo":
                    self.assertContains(response, 'enctype="multipart/form-data"')

    def test_superuser_can_configure_floating_whatsapp_button(self):
        response = self.client.get(reverse("painel:whatsapp"))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            reverse("painel:whatsapp"),
            {"whatsapp": "+55 (11) 99999-8888"},
        )

        self.assertRedirects(response, reverse("painel:whatsapp"))
        config = ConfiguracaoRestaurante.objects.get(pk=1)
        self.assertEqual(config.whatsapp, "5511999998888")

    def test_whatsapp_setting_rejects_invalid_number(self):
        response = self.client.post(
            reverse("painel:whatsapp"),
            {"whatsapp": "123"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Informe um número válido")
        self.assertFalse(ConfiguracaoRestaurante.objects.exists())

    def test_whatsapp_settings_page_requires_superuser(self):
        self.client.force_login(
            get_user_model().objects.create_user(
                username="equipe-config",
                password="senha-segura",
                is_staff=True,
            )
        )

        response = self.client.get(reverse("painel:whatsapp"))

        self.assertEqual(response.status_code, 403)

    @override_settings(RESTAURANT_WHATSAPP="5511999999999")
    def test_whatsapp_form_shows_environment_default_until_saved(self):
        response = self.client.get(reverse("painel:whatsapp"))

        self.assertContains(response, 'value="5511999999999"')

    def test_superuser_can_save_location_for_public_map(self):
        response = self.client.get(reverse("painel:localizacao"))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            reverse("painel:localizacao"),
            {
                "address": "Rua do Restaurante, 10",
                "map_embed_url": "https://www.google.com/maps/embed?pb=local",
                "maps_url": "https://maps.google.com/?q=restaurante",
            },
        )

        self.assertRedirects(response, reverse("painel:localizacao"))
        config = ConfiguracaoRestaurante.objects.get(pk=1)
        self.assertEqual(config.address, "Rua do Restaurante, 10")
        self.assertEqual(
            config.map_embed_url,
            "https://www.google.com/maps/embed?pb=local",
        )

    def test_location_requires_address_and_both_https_urls(self):
        response = self.client.post(
            reverse("painel:localizacao"),
            {
                "address": "Rua do Restaurante, 10",
                "map_embed_url": "http://example.com/map",
                "maps_url": "https://maps.google.com/?q=restaurante",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "https")
        self.assertFalse(ConfiguracaoRestaurante.objects.exists())

    def test_location_can_be_saved_without_embed_url(self):
        response = self.client.post(
            reverse("painel:localizacao"),
            {
                "address": "Rua do Restaurante, 10",
                "map_embed_url": "",
                "maps_url": "https://maps.google.com/?q=restaurante",
            },
        )

        self.assertRedirects(response, reverse("painel:localizacao"))
        config = ConfiguracaoRestaurante.objects.get(pk=1)
        self.assertEqual(config.address, "Rua do Restaurante, 10")
        self.assertEqual(config.map_embed_url, "")

    def test_location_requires_address_and_maps_link_together(self):
        response = self.client.post(
            reverse("painel:localizacao"),
            {
                "address": "Rua do Restaurante, 10",
                "map_embed_url": "",
                "maps_url": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Para exibir o mapa, preencha o endereço e o link do Google Maps.",
        )
        self.assertFalse(ConfiguracaoRestaurante.objects.exists())

    def test_location_settings_require_superuser(self):
        self.client.force_login(
            get_user_model().objects.create_user(
                username="equipe-localizacao",
                password="senha-segura",
                is_staff=True,
            )
        )

        response = self.client.get(reverse("painel:localizacao"))

        self.assertEqual(response.status_code, 403)

    def test_superuser_can_edit_email_hours_and_social_links(self):
        response = self.client.get(reverse("painel:contato"))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            reverse("painel:contato"),
            {
                "email": "contato@exemplo.com",
                "opening_hours": "Segunda a sexta: 9h às 18h",
                "instagram_url": "https://www.instagram.com/restaurante/",
                "facebook_url": "https://www.facebook.com/restaurante/",
            },
        )

        self.assertRedirects(response, reverse("painel:contato"))
        config = ConfiguracaoRestaurante.objects.get(pk=1)
        self.assertEqual(config.email, "contato@exemplo.com")
        self.assertEqual(config.opening_hours, "Segunda a sexta: 9h às 18h")
        self.assertEqual(
            config.instagram_url,
            "https://www.instagram.com/restaurante/",
        )
        self.assertEqual(
            config.facebook_url,
            "https://www.facebook.com/restaurante/",
        )

    def test_contact_settings_reject_invalid_email_and_insecure_social_url(self):
        response = self.client.post(
            reverse("painel:contato"),
            {
                "email": "email-invalido",
                "opening_hours": "",
                "instagram_url": "http://www.instagram.com/restaurante/",
                "facebook_url": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Informe um endereço de email válido")
        self.assertContains(response, "https://")
        self.assertFalse(ConfiguracaoRestaurante.objects.exists())

    def test_contact_settings_require_superuser(self):
        self.client.force_login(
            get_user_model().objects.create_user(
                username="equipe-contato",
                password="senha-segura",
                is_staff=True,
            )
        )

        response = self.client.get(reverse("painel:contato"))

        self.assertEqual(response.status_code, 403)

    def test_superuser_can_replace_home_carousel_images(self):
        image_file = BytesIO()
        Image.new("RGB", (8, 8), color="green").save(image_file, format="PNG")
        image_bytes = image_file.getvalue()

        with TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                response = self.client.post(
                    reverse("painel:carrossel"),
                    {
                        "carousel_image_1": SimpleUploadedFile(
                            "sala.png", image_bytes, content_type="image/png"
                        ),
                        "carousel_image_2": SimpleUploadedFile(
                            "carne.png", image_bytes, content_type="image/png"
                        ),
                        "carousel_image_3": SimpleUploadedFile(
                            "mesa.png", image_bytes, content_type="image/png"
                        ),
                    },
                )

                self.assertRedirects(response, reverse("painel:carrossel"))
                config = ConfiguracaoRestaurante.objects.get(pk=1)
                self.assertTrue(config.carousel_image_1.name.startswith("carousel/"))
                self.assertTrue(config.carousel_image_2.name.startswith("carousel/"))
                self.assertTrue(config.carousel_image_3.name.startswith("carousel/"))

                home_response = self.client.get(reverse("home"))
                self.assertContains(home_response, config.carousel_image_1.url)
                self.assertContains(home_response, config.carousel_image_2.url)
                self.assertContains(home_response, config.carousel_image_3.url)

    def test_carousel_settings_require_superuser(self):
        self.client.force_login(
            get_user_model().objects.create_user(
                username="equipe-carrossel",
                password="senha-segura",
                is_staff=True,
            )
        )

        response = self.client.get(reverse("painel:carrossel"))

        self.assertEqual(response.status_code, 403)

    def test_superuser_can_configure_restaurant_name_and_logo(self):
        image_file = BytesIO()
        Image.new("RGB", (8, 8), color="purple").save(image_file, format="PNG")

        with TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                response = self.client.post(
                    reverse("painel:identidade"),
                    {
                        "restaurant_name": "Fuzue BBQ",
                        "restaurant_logo": SimpleUploadedFile(
                            "logo.png",
                            image_file.getvalue(),
                            content_type="image/png",
                        ),
                    },
                )

                self.assertRedirects(response, reverse("painel:identidade"))
                config = ConfiguracaoRestaurante.objects.get(pk=1)
                self.assertEqual(config.restaurant_name, "Fuzue BBQ")
                self.assertTrue(config.restaurant_logo.name.startswith("restaurant/"))

                public_response = self.client.get(reverse("home"))
                self.assertContains(public_response, "Fuzue BBQ")
                self.assertContains(public_response, config.restaurant_logo.url)

    @override_settings(RESTAURANT_NAME="Restaurante do Ambiente")
    def test_identity_form_shows_default_name_until_saved(self):
        response = self.client.get(reverse("painel:identidade"))

        self.assertContains(response, 'value="Restaurante do Ambiente"')

    def test_identity_settings_require_superuser(self):
        self.client.force_login(
            get_user_model().objects.create_user(
                username="equipe-identidade",
                password="senha-segura",
                is_staff=True,
            )
        )

        response = self.client.get(reverse("painel:identidade"))

        self.assertEqual(response.status_code, 403)
