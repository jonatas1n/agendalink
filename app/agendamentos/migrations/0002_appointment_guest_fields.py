from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("agendamentos", "0001_initial"),
        ("produtos", "0006_periodos_excecao"),
    ]

    operations = [
        migrations.AddField(
            model_name="agendamento",
            name="confirm_via_email",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="agendamento",
            name="confirm_via_phone",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="agendamento",
            name="guest_cpf",
            field=models.CharField(blank=True, max_length=11),
        ),
        migrations.AddField(
            model_name="agendamento",
            name="guest_email",
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name="agendamento",
            name="guest_name",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name="agendamento",
            name="guest_phone",
            field=models.CharField(blank=True, max_length=32),
        ),
        migrations.AlterField(
            model_name="agendamento",
            name="cliente",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="agendamentos",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
