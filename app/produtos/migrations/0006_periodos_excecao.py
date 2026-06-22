# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("produtos", "0005_duracao_livre"),
    ]

    operations = [
        migrations.CreateModel(
            name="PeriodoIndisponivel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("data_inicio", models.DateField()),
                ("data_fim", models.DateField()),
                ("motivo", models.CharField(blank=True, max_length=200)),
                (
                    "produto",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="periodos_indisponiveis",
                        to="produtos.produto",
                    ),
                ),
            ],
            options={
                "ordering": ["data_inicio", "pk"],
            },
        ),
        migrations.CreateModel(
            name="DisponibilidadeData",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("data", models.DateField()),
                ("hora_inicio", models.TimeField()),
                ("hora_fim", models.TimeField()),
                (
                    "produto",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="disponibilidades_data",
                        to="produtos.produto",
                    ),
                ),
            ],
            options={
                "ordering": ["data", "hora_inicio"],
                "unique_together": {("produto", "data", "hora_inicio")},
            },
        ),
    ]
