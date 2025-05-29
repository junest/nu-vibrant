import pytest
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch

from nu_vibrant.subscription.models import Invoice
from nu_vibrant.subscription.tests.factories import (
    BillableMetricFactory, PlanFactory, PlanChargeFactory,
    SubscriptionFactory, InvoiceFactory
)
from nu_vibrant.users.tests.factories import UserFactory


@pytest.mark.django_db
class TestBillableMetricModel:
    def test_billable_metric_str(self):
        """Test the string representation of a BillableMetric"""
        metric = BillableMetricFactory(name="Class Bookings")
        assert str(metric) == "Class Bookings"


@pytest.mark.django_db
class TestPlanModel:
    def test_plan_str(self):
        """Test the string representation of a Plan"""
        plan = PlanFactory(name="Premium Plan")
        assert str(plan) == "Premium Plan"


@pytest.mark.django_db
class TestPlanChargeModel:
    def test_plan_charge_str(self):
        """Test the string representation of a PlanCharge"""
        plan = PlanFactory(name="Premium Plan")
        metric = BillableMetricFactory(name="Class Bookings")
        plan_charge = PlanChargeFactory(
            plan=plan,
            billable_metric=metric
        )
        assert str(plan_charge) == "Premium Plan - Class Bookings"


@pytest.mark.django_db
class TestSubscriptionModel:
    def test_subscription_str(self):
        """Test the string representation of a Subscription"""
        user = UserFactory(name="testuser")
        plan = PlanFactory(name="Premium Plan")
        subscription = SubscriptionFactory(
            user=user,
            plan=plan
        )
        assert str(subscription) == "testuser - Premium Plan"


@pytest.mark.django_db
class TestInvoiceModel:
    def test_invoice_generation(self):
        """Test that an invoice can be generated from a subscription"""
        user = UserFactory()
        plan = PlanFactory(amount_fee=150.00)
        subscription = SubscriptionFactory(
            user=user,
            plan=plan,
            status="inactive"
        )
        
        invoice = Invoice.generate_invoice(subscription)
        
        assert invoice.user == user
        assert invoice.subscription == subscription
        assert invoice.amount == plan.amount_fee
        assert invoice.status == "unpaid"
        assert invoice.invoice_id is not None

    def test_invoice_str(self):
        """Test the string representation of an Invoice"""
        user = UserFactory(name="testuser")
        plan = PlanFactory(name="Premium Plan")
        subscription = SubscriptionFactory(
            user=user,
            plan=plan
        )
        invoice = InvoiceFactory(
            user=user,
            subscription=subscription
        )
        assert str(invoice) == "testuser - Premium Plan"

    @patch('time.time')
    def test_invoice_id_generation(self, mock_time):
        """Test that invoice_id is generated correctly"""
        # Mock time.time() to return a fixed timestamp
        mock_time.return_value = 1609459200  # 2021-01-01 00:00:00
        
        user = UserFactory()
        plan = PlanFactory()
        subscription = SubscriptionFactory(
            user=user,
            plan=plan
        )
        
        # Create invoice with mocked time
        invoice = Invoice(
            user=user,
            subscription=subscription,
            amount=plan.amount_fee,
            status="unpaid"
        )
        
        # Generate invoice_id
        with patch('random.choices', return_value=['A', 'B', 'C', 'D']):
            invoice_id = invoice.generate_invoice_id()
        
        # Expected format: plan_id|user_id|timestamp|random_chars
        expected_id = f"{plan.id}|{user.id}|1609459200|ABCD"
        assert invoice_id == expected_id

    def test_subscription_activation_on_payment(self):
        """Test that subscription is activated when invoice is paid"""
        user = UserFactory()
        plan = PlanFactory()
        subscription = SubscriptionFactory(
            user=user,
            plan=plan,
            status="inactive"
        )
        
        # Create unpaid invoice
        invoice = Invoice.generate_invoice(subscription)
        assert subscription.status == "inactive"
        
        # Mark invoice as paid
        invoice.status = "paid"
        invoice.save()
        
        # Refresh subscription from database
        subscription.refresh_from_db()
        
        # Check that subscription is now active
        assert subscription.status == "active"