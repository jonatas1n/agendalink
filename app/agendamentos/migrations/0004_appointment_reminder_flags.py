from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("agendamentos", "0003_confirm_via_email_default"),
    ]

    operations = [
        migrations.AddField(
            model_name="agendamento",
            name="reminder_24h_sent",
            field=models.BooleanField(default=False, db_column="lembrete_24h_enviado"),
        ),
        migrations.AddField(
            model_name="agendamento",
            name="reminder_1h_sent",
            field=models.BooleanField(default=False, db_column="lembrete_1h_enviado"),
        ),
    ]
