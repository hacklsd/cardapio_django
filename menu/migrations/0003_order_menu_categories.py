from django.db import migrations


CATEGORY_ORDER = (
    ("Entradas", 1),
    ("Pratos Individuais", 2),
    ("Pratos Fam", 3),
    ("Sandu", 4),
    ("Bebidas", 5),
)


def set_category_order(apps, schema_editor):
    Categoria = apps.get_model("menu", "Categoria")
    database = schema_editor.connection.alias

    for name_prefix, order in CATEGORY_ORDER:
        Categoria.objects.using(database).filter(
            nome__istartswith=name_prefix
        ).update(ordem=order)


def reset_category_order(apps, schema_editor):
    Categoria = apps.get_model("menu", "Categoria")
    database = schema_editor.connection.alias

    for name_prefix, _ in CATEGORY_ORDER:
        Categoria.objects.using(database).filter(
            nome__istartswith=name_prefix
        ).update(ordem=0)


class Migration(migrations.Migration):
    dependencies = [
        ("menu", "0002_alter_categoria_options_alter_produto_options"),
    ]

    operations = [
        migrations.RunPython(set_category_order, reset_category_order),
    ]
