from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods, require_POST

from app.models import ConfiguracaoRestaurante
from menu.models import Categoria, Produto

from .decorators import admin_required
from .forms import (
    CategoriaForm,
    CarrosselRestauranteForm,
    IdentidadeRestauranteForm,
    InformacoesContatoForm,
    LocalizacaoRestauranteForm,
    ProdutoForm,
    WhatsappRestauranteForm,
)


@admin_required
def dashboard(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "painel/dashboard.html",
        {
            "total_categorias": Categoria.objects.count(),
            "total_produtos": Produto.objects.count(),
        },
    )


@admin_required
@require_http_methods(["GET", "POST"])
def configuracao_whatsapp(request: HttpRequest) -> HttpResponse:
    configuracao = ConfiguracaoRestaurante.objects.filter(pk=1).first()
    form = WhatsappRestauranteForm(
        request.POST if request.method == "POST" else None,
        instance=configuracao,
        initial=(
            {"whatsapp": settings.RESTAURANT_WHATSAPP}
            if configuracao is None
            else None
        ),
    )
    if request.method == "POST" and form.is_valid():
        configuracao = form.save(commit=False)
        configuracao.pk = 1
        configuracao.save()
        messages.success(request, "O WhatsApp do restaurante foi atualizado.")
        return redirect("painel:whatsapp")

    return render(
        request,
        "painel/whatsapp.html",
        {"form": form, "titulo": "Botão flutuante do WhatsApp"},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def configuracao_localizacao(request: HttpRequest) -> HttpResponse:
    configuracao = ConfiguracaoRestaurante.objects.filter(pk=1).first()
    form = LocalizacaoRestauranteForm(
        request.POST if request.method == "POST" else None,
        instance=configuracao,
        initial=(
            {
                "address": settings.RESTAURANT_ADDRESS,
                "map_embed_url": settings.RESTAURANT_MAP_EMBED_URL,
                "maps_url": settings.RESTAURANT_MAPS_URL,
            }
            if configuracao is None
            else {
                "address": configuracao.address or settings.RESTAURANT_ADDRESS,
                "map_embed_url": (
                    configuracao.map_embed_url
                    or settings.RESTAURANT_MAP_EMBED_URL
                ),
                "maps_url": configuracao.maps_url or settings.RESTAURANT_MAPS_URL,
            }
        ),
    )
    if request.method == "POST" and form.is_valid():
        configuracao = form.save(commit=False)
        configuracao.pk = 1
        configuracao.save()
        messages.success(request, "A localização do restaurante foi atualizada.")
        return redirect("painel:localizacao")

    return render(
        request,
        "painel/localizacao.html",
        {"form": form, "titulo": "Localização e mapa"},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def configuracao_contato(request: HttpRequest) -> HttpResponse:
    configuracao = ConfiguracaoRestaurante.objects.filter(pk=1).first()
    form = InformacoesContatoForm(
        request.POST if request.method == "POST" else None,
        instance=configuracao,
        initial=(
            {
                "email": settings.RESTAURANT_EMAIL,
                "opening_hours": settings.RESTAURANT_OPENING_HOURS,
                "instagram_url": settings.RESTAURANT_INSTAGRAM_URL,
                "facebook_url": settings.RESTAURANT_FACEBOOK_URL,
            }
            if configuracao is None
            else {
                "email": configuracao.email or settings.RESTAURANT_EMAIL,
                "opening_hours": (
                    configuracao.opening_hours
                    or settings.RESTAURANT_OPENING_HOURS
                ),
                "instagram_url": (
                    configuracao.instagram_url
                    or settings.RESTAURANT_INSTAGRAM_URL
                ),
                "facebook_url": (
                    configuracao.facebook_url
                    or settings.RESTAURANT_FACEBOOK_URL
                ),
            }
        ),
    )
    if request.method == "POST" and form.is_valid():
        configuracao = form.save(commit=False)
        configuracao.pk = 1
        configuracao.save()
        messages.success(request, "As informações de contato foram atualizadas.")
        return redirect("painel:contato")

    return render(
        request,
        "painel/contato.html",
        {"form": form, "titulo": "Contato, horário e redes sociais"},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def configuracao_carrossel(request: HttpRequest) -> HttpResponse:
    configuracao = ConfiguracaoRestaurante.objects.filter(pk=1).first()
    form = CarrosselRestauranteForm(
        request.POST if request.method == "POST" else None,
        request.FILES if request.method == "POST" else None,
        instance=configuracao,
    )
    if request.method == "POST" and form.is_valid():
        configuracao = form.save(commit=False)
        configuracao.pk = 1
        configuracao.save()
        messages.success(request, "As fotos do carrossel foram atualizadas.")
        return redirect("painel:carrossel")

    return render(
        request,
        "painel/carrossel.html",
        {"form": form, "titulo": "Fotos do carrossel"},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def configuracao_identidade(request: HttpRequest) -> HttpResponse:
    configuracao = ConfiguracaoRestaurante.objects.filter(pk=1).first()
    form = IdentidadeRestauranteForm(
        request.POST if request.method == "POST" else None,
        request.FILES if request.method == "POST" else None,
        instance=configuracao,
        initial=(
            {"restaurant_name": settings.RESTAURANT_NAME}
            if configuracao is None
            else {
                "restaurant_name": (
                    configuracao.restaurant_name or settings.RESTAURANT_NAME
                )
            }
        ),
    )
    if request.method == "POST" and form.is_valid():
        configuracao = form.save(commit=False)
        configuracao.pk = 1
        configuracao.save()
        messages.success(request, "A identidade do restaurante foi atualizada.")
        return redirect("painel:identidade")

    return render(
        request,
        "painel/identidade.html",
        {"form": form, "titulo": "Nome e logo do restaurante"},
    )


def login_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect("painel:dashboard")

    next_url = request.POST.get("next") or request.GET.get("next", "")
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password"),
        )

        if user is not None and user.is_superuser:
            login(request, user)
            if url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)
            return redirect("painel:dashboard")

        return render(
            request,
            "painel/login.html",
            {
                "erro": "Usuário ou senha inválidos, ou conta sem acesso de superusuário.",
                "next": next_url,
            },
            status=403 if user is not None else 200,
        )

    return render(request, "painel/login.html", {"next": next_url})


@admin_required
@require_POST
def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect("painel:login")


@admin_required
def categorias(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "painel/categorias.html",
        {"categorias": Categoria.objects.all()},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def categoria_form(request: HttpRequest, pk: int | None = None) -> HttpResponse:
    instance = get_object_or_404(Categoria, pk=pk) if pk is not None else None
    form = CategoriaForm(
        request.POST if request.method == "POST" else None,
        instance=instance,
    )
    if request.method == "POST" and form.is_valid():
        categoria = form.save()
        messages.success(request, f'Categoria "{categoria.nome}" salva.')
        return redirect("painel:categorias")

    return render(
        request,
        "painel/form.html",
        {
            "form": form,
            "titulo": "Editar categoria" if instance else "Nova categoria",
            "cancelar_url": reverse("painel:categorias"),
        },
    )


@admin_required
@require_http_methods(["GET", "POST"])
def categoria_excluir(request: HttpRequest, pk: int) -> HttpResponse:
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == "POST":
        nome = categoria.nome
        categoria.delete()
        messages.success(request, f'Categoria "{nome}" excluída.')
        return redirect("painel:categorias")

    return render(
        request,
        "painel/confirmar_exclusao.html",
        {
            "objeto": categoria,
            "titulo": "Excluir categoria",
            "aviso": "Os produtos associados a esta categoria também serão excluídos.",
            "cancelar_url": reverse("painel:categorias"),
        },
    )


@admin_required
def produtos(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "painel/produtos.html",
        {"produtos": Produto.objects.select_related("categoria")},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def produto_form(request: HttpRequest, pk: int | None = None) -> HttpResponse:
    instance = get_object_or_404(Produto, pk=pk) if pk is not None else None
    form = ProdutoForm(
        request.POST if request.method == "POST" else None,
        request.FILES if request.method == "POST" else None,
        instance=instance,
    )
    if request.method == "POST" and form.is_valid():
        produto = form.save()
        messages.success(request, f'Produto "{produto.nome}" salvo.')
        return redirect("painel:produtos")

    return render(
        request,
        "painel/form.html",
        {
            "form": form,
            "titulo": "Editar produto" if instance else "Novo produto",
            "cancelar_url": reverse("painel:produtos"),
            "multipart": True,
        },
    )


@admin_required
@require_http_methods(["GET", "POST"])
def produto_excluir(request: HttpRequest, pk: int) -> HttpResponse:
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == "POST":
        nome = produto.nome
        produto.delete()
        messages.success(request, f'Produto "{nome}" excluído.')
        return redirect("painel:produtos")

    return render(
        request,
        "painel/confirmar_exclusao.html",
        {
            "objeto": produto,
            "titulo": "Excluir produto",
            "cancelar_url": reverse("painel:produtos"),
        },
    )
