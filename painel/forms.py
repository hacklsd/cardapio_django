import re

from django import forms
from app.models import ConfiguracaoRestaurante
from menu.models import Categoria, Produto


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nome", "ordem", "ativa"]
        labels = {
            "nome": "Nome",
            "ordem": "Ordem de exibição",
            "ativa": "Categoria ativa",
        }


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = [
            "categoria",
            "nome",
            "descricao",
            "preco",
            "imagem",
            "ativo",
            "ordem",
        ]
        labels = {
            "categoria": "Categoria",
            "nome": "Nome",
            "descricao": "Descrição",
            "preco": "Preço",
            "imagem": "Imagem",
            "ativo": "Produto ativo",
            "ordem": "Ordem de exibição",
        }


class WhatsappRestauranteForm(forms.ModelForm):
    whatsapp = forms.CharField(
        required=False,
        max_length=32,
        help_text="Número internacional, com DDI e DDD.",
    )

    class Meta:
        model = ConfiguracaoRestaurante
        fields = ["whatsapp"]
        labels = {"whatsapp": "WhatsApp do restaurante"}
        widgets = {
            "whatsapp": forms.TextInput(
                attrs={
                    "inputmode": "numeric",
                    "autocomplete": "tel",
                    "placeholder": "5511999999999",
                }
            )
        }

    def clean_whatsapp(self):
        value = self.cleaned_data["whatsapp"]
        if not re.fullmatch(r"[+0-9().\-\s]*", value):
            raise forms.ValidationError(
                "Use somente números, espaços e os símbolos +, parênteses ou hífen."
            )
        digits = "".join(character for character in value if character in "0123456789")
        if digits and not 8 <= len(digits) <= 15:
            raise forms.ValidationError(
                "Informe um número válido com DDI e DDD, contendo de 8 a 15 dígitos."
            )
        return digits


class LocalizacaoRestauranteForm(forms.ModelForm):
    class Meta:
        model = ConfiguracaoRestaurante
        fields = ["address", "map_embed_url", "maps_url"]
        labels = {
            "address": "Endereço",
            "map_embed_url": "URL de incorporação do mapa",
            "maps_url": "URL para abrir no Google Maps",
        }
        help_texts = {
            "map_embed_url": (
                "Opcional. Se ficar vazio, o mapa será gerado pelo endereço."
            ),
            "maps_url": "Link HTTPS para abrir a localização no Google Maps.",
        }
        widgets = {
            "address": forms.Textarea(attrs={"rows": 3}),
            "map_embed_url": forms.URLInput(
                attrs={"placeholder": "https://www.google.com/maps/embed?..."}
            ),
            "maps_url": forms.URLInput(
                attrs={"placeholder": "https://maps.google.com/?q=..."}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        address = cleaned_data.get("address", "").strip()
        map_embed_url = cleaned_data.get("map_embed_url", "")
        maps_url = cleaned_data.get("maps_url", "")

        if any((address, map_embed_url, maps_url)) and not (address and maps_url):
            raise forms.ValidationError(
                "Para exibir o mapa, preencha o endereço e o link do Google Maps."
            )
        return cleaned_data


class InformacoesContatoForm(forms.ModelForm):
    class Meta:
        model = ConfiguracaoRestaurante
        fields = ["email", "opening_hours", "instagram_url", "facebook_url"]
        labels = {
            "email": "E-mail",
            "opening_hours": "Horário de funcionamento",
            "instagram_url": "Instagram",
            "facebook_url": "Facebook",
        }
        help_texts = {
            "opening_hours": "Uma linha por dia ou período.",
            "instagram_url": "URL HTTPS completa do perfil.",
            "facebook_url": "URL HTTPS completa da página (opcional).",
        }
        widgets = {
            "opening_hours": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": "Segunda a sexta: 11h às 22h\nSábado e domingo: 12h às 23h",
                }
            ),
            "instagram_url": forms.URLInput(
                attrs={"placeholder": "https://www.instagram.com/seu_perfil/"}
            ),
            "facebook_url": forms.URLInput(
                attrs={"placeholder": "https://www.facebook.com/sua_pagina/"}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        for field_name in ("instagram_url", "facebook_url"):
            value = cleaned_data.get(field_name)
            if value and not value.startswith("https://"):
                self.add_error(
                    field_name,
                    "Informe o endereço seguro começando com https://.",
                )
        return cleaned_data


class IdentidadeRestauranteForm(forms.ModelForm):
    class Meta:
        model = ConfiguracaoRestaurante
        fields = ["restaurant_name", "restaurant_logo"]
        labels = {
            "restaurant_name": "Nome do restaurante",
            "restaurant_logo": "Logo",
        }
        help_texts = {
            "restaurant_name": "Nome exibido no cabeçalho e no título do site.",
            "restaurant_logo": (
                "Envie uma imagem para exibir ao lado do nome. "
                "Deixe em branco para manter a logo atual."
            ),
        }
        widgets = {
            "restaurant_name": forms.TextInput(
                attrs={"placeholder": "Nome do restaurante"}
            ),
            "restaurant_logo": forms.ClearableFileInput(
                attrs={"accept": "image/*"}
            ),
        }


class CarrosselRestauranteForm(forms.ModelForm):
    class Meta:
        model = ConfiguracaoRestaurante
        fields = ["carousel_image_1", "carousel_image_2", "carousel_image_3"]
        widgets = {
            "carousel_image_1": forms.FileInput(attrs={"accept": "image/*"}),
            "carousel_image_2": forms.FileInput(attrs={"accept": "image/*"}),
            "carousel_image_3": forms.FileInput(attrs={"accept": "image/*"}),
        }
        labels = {
            "carousel_image_1": "Foto 1",
            "carousel_image_2": "Foto 2",
            "carousel_image_3": "Foto 3",
        }
        help_texts = {
            "carousel_image_1": "Sem foto enviada, a foto atual continua no carrossel.",
            "carousel_image_2": "Sem foto enviada, a foto atual continua no carrossel.",
            "carousel_image_3": "Sem foto enviada, a foto atual continua no carrossel.",
        }