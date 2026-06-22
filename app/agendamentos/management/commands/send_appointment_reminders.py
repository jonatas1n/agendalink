from django.core.management.base import BaseCommand

from agendamentos.models import Appointment
from agendamentos.notifications import send_appointment_reminder
from agendamentos.reminders import appointments_due_for_reminder


class Command(BaseCommand):
    help = "Envia lembretes de agendamento (24h e 1h antes). Rode via cron a cada 15–30 min."

    def handle(self, *args, **options):
        sent_24 = 0
        sent_1 = 0
        for appointment in appointments_due_for_reminder("24h"):
            if send_appointment_reminder(appointment, kind="24h"):
                appointment.reminder_24h_sent = True
                appointment.save(update_fields=["reminder_24h_sent", "updated_at"])
                sent_24 += 1
        for appointment in appointments_due_for_reminder("1h"):
            if send_appointment_reminder(appointment, kind="1h"):
                appointment.reminder_1h_sent = True
                appointment.save(update_fields=["reminder_1h_sent", "updated_at"])
                sent_1 += 1
        self.stdout.write(
            self.style.SUCCESS(f"Lembretes enviados: 24h={sent_24}, 1h={sent_1}"),
        )
