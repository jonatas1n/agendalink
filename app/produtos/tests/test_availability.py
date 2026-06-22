from datetime import date, time
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase

from produtos.models import (
    DateAvailability,
    Product,
    UnavailablePeriod,
    WeeklyAvailability,
)
from produtos.availability import (
    available_slots_for_product,
    is_day_unavailable,
    time_windows_for_day,
)


class AvailabilityLogicTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="pro", password="x")
        self.product = Product.objects.create(
            owner=self.owner,
            name="Consulta",
            price=Decimal("100.00"),
            duration_minutes=60,
            simultaneous_capacity=1,
        )
        WeeklyAvailability.objects.create(
            product=self.product,
            weekday=0,
            start_time=time(9, 0),
            end_time=time(12, 0),
        )

    def test_weekday_returns_weekly_windows(self):
        monday = date(2025, 6, 16)
        windows = time_windows_for_day(self.product, monday)
        self.assertEqual(windows, [(time(9, 0), time(12, 0))])

    def test_unavailable_period_blocks_day(self):
        day = date(2025, 6, 16)
        UnavailablePeriod.objects.create(
            product=self.product,
            start_date=day,
            end_date=day,
            reason="Férias",
        )
        self.assertTrue(is_day_unavailable(self.product, day))
        self.assertEqual(time_windows_for_day(self.product, day), [])

    def test_unavailable_range_blocks_middle_day(self):
        UnavailablePeriod.objects.create(
            product=self.product,
            start_date=date(2025, 6, 10),
            end_date=date(2025, 6, 20),
        )
        self.assertTrue(is_day_unavailable(self.product, date(2025, 6, 15)))

    def test_date_availability_overrides_weekly(self):
        saturday = date(2025, 6, 21)
        DateAvailability.objects.create(
            product=self.product,
            date=saturday,
            start_time=time(14, 0),
            end_time=time(16, 0),
        )
        windows = time_windows_for_day(self.product, saturday)
        self.assertEqual(windows, [(time(14, 0), time(16, 0))])

    def test_available_slots_respects_duration(self):
        monday = date(2025, 6, 16)
        slots = available_slots_for_product(
            self.product,
            days=1,
            since=monday,
        )
        key = monday.isoformat()
        self.assertIn(key, slots)
        self.assertEqual(
            slots[key],
            [
                {
                    "start": "09:00",
                    "end": "10:00",
                    "disponivel": True,
                    "available": True,
                },
                {
                    "start": "10:00",
                    "end": "11:00",
                    "disponivel": True,
                    "available": True,
                },
                {
                    "start": "11:00",
                    "end": "12:00",
                    "disponivel": True,
                    "available": True,
                },
            ],
        )

    def test_unavailable_period_removes_slots(self):
        monday = date(2025, 6, 16)
        UnavailablePeriod.objects.create(
            product=self.product,
            start_date=monday,
            end_date=monday,
        )
        slots = available_slots_for_product(
            self.product,
            days=1,
            since=monday,
        )
        self.assertNotIn(monday.isoformat(), slots)
