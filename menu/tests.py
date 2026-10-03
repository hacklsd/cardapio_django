from django.test import TestCase
from django.urls import reverse

from .models import Categoria, Produto


class MenuPublicoTests(TestCase):
    def test_cardapio_shows_only_active_categories_and_products(self):
        categoria_ativa = Categoria.objects.create(nome="Entradas")
        categoria_inativa = Categoria.objects.create(
            nome="Oculta",
            ativa=False,
        )
        Produto.objects.create(
            categoria=categoria_ativa,
            nome="Pão de alho",
            preco="12.00",
        )
        Produto.objects.create(
            categoria=categoria_ativa,
            nome="Produto inativo",
            ativo=False,
        )
        Produto.objects.create(
            categoria=categoria_inativa,
            nome="Produto de categoria inativa",
        )

        response = self.client.get(reverse("cardapio"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Entradas")
        self.assertContains(response, "Pão de alho")
        self.assertNotContains(response, "Oculta")
        self.assertNotContains(response, "Produto inativo")
        self.assertNotContains(response, "Produto de categoria inativa")

    def test_category_and_product_ordering_is_applied(self):
        categoria_b = Categoria.objects.create(nome="Zebra", ordem=2)
        categoria_a = Categoria.objects.create(nome="Abacaxi", ordem=1)
        Produto.objects.create(categoria=categoria_b, nome="Segundo", ordem=2)
        Produto.objects.create(categoria=categoria_b, nome="Primeiro", ordem=1)

        self.assertEqual(
            list(Categoria.objects.all()),
            [categoria_a, categoria_b],
        )
        self.assertEqual(
            list(categoria_b.produtos.all().values_list("nome", flat=True)),
            ["Primeiro", "Segundo"],
        )
        self.assertEqual(str(categoria_a), "Abacaxi")

    def test_menu_categories_follow_requested_display_order(self):
        category_names = (
            "Entradas",
            "Pratos Individuais",
            "Pratos Família",
            "Sanduíches e Hamburgueres",
            "Bebidas",
        )
        for order, name in enumerate(category_names, start=1):
            categoria = Categoria.objects.create(nome=name, ordem=order)
            Produto.objects.create(categoria=categoria, nome=f"Item {order}")

        response = self.client.get(reverse("cardapio"))
        self.assertEqual(response.status_code, 200)

        positions = [
            response.content.index(name.encode("utf-8"))
            for name in category_names
        ]
        self.assertEqual(positions, sorted(positions))
