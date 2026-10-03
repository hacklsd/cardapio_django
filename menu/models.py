from django.db import models


class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    ordem = models.PositiveBigIntegerField(default=0)
    ativa = models.BooleanField(default=True)

    class Meta:
        ordering = ["ordem", "nome"]

    def __str__(self):
        return self.nome


class Produto(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='produtos')
    nome = models.CharField(max_length=150)
    descricao = models.TextField(blank=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    imagem = models.ImageField(upload_to='produtos/', null=True, blank=True)
    ativo = models.BooleanField(default=True)
    ordem = models.PositiveBigIntegerField(default=0)

    class Meta:
        ordering = ["ordem", "nome"]

    def __str__(self):
        return self.nome
