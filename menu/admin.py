from django.contrib import admin
from . models import Categoria, Produto


# Register your models here.
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ordem', 'ativa')
    list_editable = ('ordem', 'ativa')

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'preco', 'ativo', 'ordem')
    list_editable = ('categoria', 'preco', 'ativo', 'ordem')
    list_filter = ('categoria',)

    search_fields = ('nome', 'descricao')
    list_editable = ('preco', 'ativo', 'ordem')
