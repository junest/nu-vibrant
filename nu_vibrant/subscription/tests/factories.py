import factory
from factory.django import DjangoModelFactory
from django.utils import timezone
from datetime import timedelta

from nu_vibrant.subscription.models import BillableMetric, Plan, PlanCharge, Subscription, Invoice
from nu_vibrant.users.tests.factories import UserFactory


class BillableMetricFactory(DjangoModelFactory):
    name = factory.Sequence(lambda n: f"Metric {n}")
    identifier = factory.Sequence(lambda n: f"metric_{n}")
    description = factory.Faker('sentence')
    aggregation_type = 'count'
    property_name = factory.Sequence(lambda n: f"property_{n}")

    class Meta:
        model = BillableMetric
        django_get_or_create = ['identifier']


class PlanFactory(DjangoModelFactory):
    name = factory.Sequence(lambda n: f"Plan {n}")
    interval = 'month'
    amount_fee = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    trial_period = 0
    validity_period = 30
    is_pay_in_advance = False
    is_active = True
    is_public = True

    class Meta:
        model = Plan


class PlanChargeFactory(DjangoModelFactory):
    display_name = factory.Sequence(lambda n: f"Plan Charge {n}")
    plan = factory.SubFactory(PlanFactory)
    billable_metric = factory.SubFactory(BillableMetricFactory)
    amount = factory.Faker('random_int', min=1, max=100)
    free_unit = factory.Faker('random_int', min=0, max=10)
    unit = 1
    is_pay_in_advance = False
    is_rate_limiting = True

    class Meta:
        model = PlanCharge


class SubscriptionFactory(DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    plan = factory.SubFactory(PlanFactory)
    status = 'active'
    subscribe_at = factory.LazyFunction(timezone.now)
    expire_at = factory.LazyAttribute(lambda o: o.subscribe_at + timedelta(days=30))

    class Meta:
        model = Subscription


class InvoiceFactory(DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    subscription = factory.SubFactory(SubscriptionFactory)
    amount = factory.SelfAttribute('subscription.plan.amount_fee')
    status = 'unpaid'
    paid_at = None

    class Meta:
        model = Invoice
        skip_postgeneration_save = True