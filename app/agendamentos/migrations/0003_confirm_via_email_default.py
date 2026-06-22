from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("agendamentos", "0002_appointment_guest_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="agendamento",
            name="confirm_via_email",
            field=models.BooleanField(default=True),
        ),
    ]
