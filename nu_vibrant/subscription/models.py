import time
import random
import string
from decimal import Decimal

from model_utils.models import TimeStampedModel
from model_utils import Choices
from django.db import models
from django.utils.translation import gettext_lazy as _


## custom queryset for subscription to filter subscription that has
# the given event on their plan_charges
class SubscriptionQuerySet(models.QuerySet):

    def active(self):
        return self.filter(status='active')

    def filter_event(self, event):
        return self.filter(
            plan__plan_charges__billable_metric__identifier=event
        ).distinct()


class BillableMetric(TimeStampedModel):
    AGGREGATION_TYPE = Choices(
        'count', 'sum', 'avg',
        'min', 'max', 'distinct_count')

    name = models.CharField(max_length=50)
    identifier = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=100, blank=True)

    aggregation_type = models.CharField(
        choices=AGGREGATION_TYPE, 
        default=AGGREGATION_TYPE.count,
        max_length=20)
    property_name = models.CharField(max_length=25)

    def __str__(self):
        return self.name 


class Plan(TimeStampedModel):
    INTERVAL = Choices(
        'day', 'week', 'month', 'year')

    name = models.CharField(max_length=50)
    interval = models.CharField(
        choices=INTERVAL,
        default=INTERVAL.month,
        max_length=10)
    amount_fee = models.DecimalField(
        max_digits=12, decimal_places=2)

    trial_period = models.IntegerField(default=0)
    validity_period = models.IntegerField(default=0)

    is_pay_in_advance = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)

    usage_charges = models.ManyToManyField(
        "BillableMetric",
        verbose_name=_("usage_charges"),
        through="PlanCharge")

    display_description = models.TextField(blank=True)


    def __str__(self):
        return self.name


class PlanCharge(TimeStampedModel):
    display_name = models.CharField(max_length=50, blank=True)

    plan = models.ForeignKey(
        "Plan",
        on_delete=models.CASCADE,
        related_name="plan_charges")
    billable_metric = models.ForeignKey(
        "BillableMetric",
        on_delete=models.CASCADE)

    amount = models.DecimalField(
        max_digits=12, decimal_places=2)
    free_unit = models.IntegerField(default=0)
    unit = models.IntegerField()

    is_pay_in_advance = models.BooleanField(default=False)
    is_rate_limiting = models.BooleanField(default=False)

    def __str__(self):
        return self.plan.name + " - " + self.billable_metric.name
    
    def _get_used_charge(self):
        # Get subscriptions using this plan charge
        subscriptions = self.plan.subscriptions.all()
        if not subscriptions.exists():
            return 0
            
        if self.billable_metric.aggregation_type == 'count':
            return self.billable_metric.events.filter(
                subscription__in=subscriptions).count()
        elif self.billable_metric.aggregation_type == 'sum':
            result = self.billable_metric.events.filter(
                subscription__in=subscriptions).aggregate(
                    models.Sum(self.billable_metric.property_name))
            return result.get(self.billable_metric.property_name + '__sum') or 0
        else:
            return 0

    @property
    def charge_left(self):
        return self._get_used_charge() - self.free_unit
        
    def calculate_extra_charge(self):
        """Calculate the extra charge for usage beyond free units"""
        extra_units = max(0, self.charge_left)
        if extra_units > 0 and not self.is_rate_limiting:
            return Decimal(str(extra_units / self.unit)) * self.amount
        return Decimal('0')


class Subscription(TimeStampedModel):
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="subscriptions")
    plan = models.ForeignKey(
        "Plan",
        on_delete=models.CASCADE,
        related_name="subscriptions")
    status = models.CharField(
        max_length=20,
        choices=Choices(
            'active', 'inactive', 'cancelled'),
        default='inactive')

    subscribe_at = models.DateTimeField(blank=True)
    expire_at = models.DateTimeField(blank=True)

    objects = SubscriptionQuerySet.as_manager()

    def __str__(self):
        return self.user.name + " - " + self.plan.name


# class Invoice to record Subscription payment
class Invoice(TimeStampedModel):

    #generated invoice_id = plan_id + user_id + timestamp
    invoice_id = models.CharField(max_length=50, unique=True)

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="invoices")
    subscription = models.ForeignKey(
        "Subscription",
        on_delete=models.CASCADE,
        related_name="invoices")
    amount = models.DecimalField(
        max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=Choices(
            'paid', 'unpaid', 'cancelled'),
        default='unpaid')
    paid_at = models.DateTimeField(null=True, blank=True)
    payment_reference = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return self.user.name + " - " + self.subscription.plan.name
    
    #function to generate invoice_id = plan_id|user_id|timestamp|4-bit randomized alphanumeric
    def generate_invoice_id(self):

        # Get current timestamp
        timestamp = int(time.time())
        
        # Generate 4-bit (characters) random alphanumeric string
        random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
        
        # Format: plan_id|user_id|timestamp|random_chars
        return f"{self.subscription.plan.id}|{self.user.id}|{timestamp}|{random_chars}"

    def save(self, *args, **kwargs):
        self.invoice_id = self.generate_invoice_id()
        super().save(*args, **kwargs)

        #trigger activate_subscription if status is paid
        if self.status == 'paid':
            self.subscription.status = 'active'
            self.subscription.save()

    # Classmethod to generate Invoice based on a Subscription
    @classmethod
    def generate_invoice(cls, subscription):
        invoice = cls(
            user=subscription.user,
            subscription=subscription,
            amount=subscription.plan.amount_fee,
            status='unpaid'
        )
        invoice.save()
        return invoice