from django.db import migrations


def copiar_precos_existentes(apps, schema_editor):
    Produto = apps.get_model("produtos", "Produto")
    ProdutoPreco = apps.get_model("produtos", "ProdutoPreco")
    for produto in Produto.objects.all():
        ProdutoPreco.objects.get_or_create(
            produto=produto,
            duracao_minutos=produto.duracao_minutos,
            defaults={"preco": produto.preco, "ordem": 0},
        )


class Migration(migrations.Migration):

    dependencies = [
        ("produtos", "0002_produto_preco"),
    ]

    operations = [
        migrations.RunPython(copiar_precos_existentes, migrations.RunPython.noop),
    ]
