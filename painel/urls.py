from django.urls import path
from . import views

app_name = "painel"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path(
        "configuracoes/whatsapp/",
        views.configuracao_whatsapp,
        name="whatsapp",
    ),
    path(
        "configuracoes/localizacao/",
        views.configuracao_localizacao,
        name="localizacao",
    ),
    path(
        "configuracoes/contato/",
        views.configuracao_contato,
        name="contato",
    ),
    path(
        "configuracoes/carrossel/",
        views.configuracao_carrossel,
        name="carrossel",
    ),
    path(
        "configuracoes/identidade/",
        views.configuracao_identidade,
        name="identidade",
    ),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("categorias/", views.categorias, name="categorias"),
    path("categorias/nova/", views.categoria_form, name="categoria_nova"),
    path(
        "categorias/<int:pk>/editar/",
        views.categoria_form,
        name="categoria_editar",
    ),
    path(
        "categorias/<int:pk>/excluir/",
        views.categoria_excluir,
        name="categoria_excluir",
    ),
    path("produtos/", views.produtos, name="produtos"),
    path("produtos/novo/", views.produto_form, name="produto_novo"),
    path(
        "produtos/<int:pk>/editar/",
        views.produto_form,
        name="produto_editar",
    ),
    path(
        "produtos/<int:pk>/excluir/",
        views.produto_excluir,
        name="produto_excluir",
    ),
]