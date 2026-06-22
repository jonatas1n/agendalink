from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from agendamentos.models import Appointment
from core.store_profile import get_store_profile
from produtos.models import Product, WeeklyAvailability

E2E_STORE_SLUG = "e2e-loja"


E2E_USERNAME = "e2e_prof"
E2E_PASSWORD = "E2eTestPass123!"
E2E_EMAIL = "e2e.prof@example.com"
E2E_PRODUCT_NAME = "Serviço E2E"
E2E_GUEST_NAME = "Cliente E2E Seed"


class Command(BaseCommand):
    help = "Idempotent seed data for Cypress E2E tests."

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(
            username=E2E_USERNAME,
            defaults={
                "email": E2E_EMAIL,
                "first_name": "Profissional",
                "last_name": "E2E",
            },
        )
        if created:
            user.set_password(E2E_PASSWORD)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Created user {E2E_USERNAME}"))
        else:
            user.set_password(E2E_PASSWORD)
            user.email = E2E_EMAIL
            user.save(update_fields=["password", "email"])

        profile = get_store_profile(user)
        if profile.slug != E2E_STORE_SLUG:
            profile.slug = E2E_STORE_SLUG
            profile.save(update_fields=["slug", "updated_at"])

        product, p_created = Product.objects.get_or_create(
            owner=user,
            name=E2E_PRODUCT_NAME,
            defaults={
                "description": "Produto fixo para testes E2E.",
                "price": 100,
                "duration_minutes": 60,
                "simultaneous_capacity": 1,
                "active": True,
            },
        )
        if not p_created:
            product.active = True
            product.duration_minutes = 60
            product.price = 100
            product.save()

        product.weekly_availabilities.all().delete()
        for weekday in range(0, 5):
            WeeklyAvailability.objects.create(
                product=product,
                weekday=weekday,
                start_time="09:00",
                end_time="18:00",
            )

        starts_at = self._next_weekday_at(hour=10, minute=0)
        ends_at = starts_at + timedelta(minutes=product.duration_minutes)
        appointment, _ = Appointment.objects.update_or_create(
            product=product,
            guest_email="cliente.e2e@example.com",
            defaults={
                "customer": None,
                "starts_at": starts_at,
                "ends_at": ends_at,
                "status": "confirmado",
                "guest_name": E2E_GUEST_NAME,
                "guest_cpf": "52998224725",
                "guest_phone": "11999990000",
                "confirm_via_email": True,
                "confirm_via_phone": False,
            },
        )

        self.stdout.write(
            f"E2E seed OK — user={E2E_USERNAME} product_id={product.pk} "
            f"appointment_id={appointment.pk}",
        )

    def _next_weekday_at(self, hour: int, minute: int) -> datetime:
        now = timezone.localtime(timezone.now())
        candidate = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if candidate <= now:
            candidate += timedelta(days=1)
        while candidate.weekday() >= 5:
            candidate += timedelta(days=1)
        if timezone.is_naive(candidate):
            candidate = timezone.make_aware(candidate)
        return candidate
