from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from django.utils import timezone

from agendamentos.management.commands.send_appointment_reminders import Command
from agendamentos.models import Appointment
from agendamentos.notifications import (
    send_cancellation_notifications,
    send_new_booking_owner_notification,
)
from agendamentos.reminders import appointments_due_for_reminder
from core.models import StoreProfile
from produtos.models import Product


class EmailNotificationTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner",
            password="pass",
            email="owner@test.com",
        )
        StoreProfile.objects.create(user=self.owner, public_email="loja@test.com")
        self.customer = User.objects.create_user(
            username="client",
            password="pass",
            email="client@test.com",
        )
        self.product = Product.objects.create(
            owner=self.owner,
            name="Consulta",
            price=Decimal("100"),
        )
        self.starts = timezone.now() + timedelta(hours=24)
        self.appointment = Appointment.objects.create(
            product=self.product,
            customer=self.customer,
            starts_at=self.starts,
            ends_at=self.starts + timedelta(hours=1),
            guest_name="Cliente Teste",
            guest_email="guest@test.com",
            status="confirmado",
        )

    def test_owner_notification_on_new_booking(self):
        mail.outbox.clear()
        self.assertTrue(send_new_booking_owner_notification(self.appointment))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Novo agendamento", mail.outbox[0].subject)
        self.assertEqual(mail.outbox[0].to, ["owner@test.com"])

    def test_cancellation_emails_customer_and_owner(self):
        mail.outbox.clear()
        results = send_cancellation_notifications(
            self.appointment,
            actor_user=self.customer,
        )
        self.assertTrue(results["customer"])
        self.assertTrue(results["owner"])
        self.assertEqual(len(mail.outbox), 2)

    def test_cancellation_skips_owner_when_owner_cancels(self):
        mail.outbox.clear()
        results = send_cancellation_notifications(
            self.appointment,
            actor_user=self.owner,
        )
        self.assertTrue(results["customer"])
        self.assertFalse(results["owner"])
        self.assertEqual(len(mail.outbox), 1)


class ReminderCommandTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="o", password="p", email="o@t.com"
        )
        self.product = Product.objects.create(
            owner=self.owner,
            name="S",
            price=Decimal("10"),
        )

    def test_sends_24h_reminder_in_window(self):
        starts = timezone.now() + timedelta(hours=24)
        appt = Appointment.objects.create(
            product=self.product,
            starts_at=starts,
            ends_at=starts + timedelta(minutes=60),
            guest_email="r@test.com",
            guest_name="R",
            status="confirmado",
        )
        due = appointments_due_for_reminder("24h")
        self.assertIn(appt, due)
        mail.outbox.clear()
        Command().handle()
        appt.refresh_from_db()
        self.assertTrue(appt.reminder_24h_sent)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Lembrete", mail.outbox[0].subject)
