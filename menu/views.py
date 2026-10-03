from django.shortcuts import render
from django.db.models import Prefetch

from .models import Categoria, Produto


def cardapio(request):
    produtos_ativos = Produto.objects.filter(ativo=True)
    categorias = (
        Categoria.objects.filter(ativa=True, produtos__ativo=True)
        .prefetch_related(
            Prefetch("produtos", queryset=produtos_ativos)
        )
        .distinct()
    )
    return render(request, "menu/cardapio.html", {"categorias": categorias})
