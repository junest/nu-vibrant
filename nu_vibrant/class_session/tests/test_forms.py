import pytest
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch, PropertyMock, MagicMock

from nu_vibrant.class_session.forms import ClassBookingForm
from nu_vibrant.class_session.models import ClassBooking
from nu_vibrant.class_session.tests.factories import ClassSessionFactory
from nu_vibrant.users.tests.factories import UserFactory
from nu_vibrant.subscription.tests.factories import SubscriptionFactory, PlanFactory, BillableMetricFactory, PlanChargeFactory
from nu_vibrant.subscription.models import PlanCharge, Subscription


@pytest.mark.django_db
class TestClassBookingForm:
    def test_form_valid(self):
        """Test that the form is valid with correct data"""
        # Create a user with active subscription
        user = UserFactory()
        plan = PlanFactory()
        
        # Create a billable metric for the booking event
        metric = BillableMetricFactory(identifier=ClassBooking.CONFIRMED_BOOKING_EVENT)
        
        # Create a plan charge with sufficient charge_left
        plan_charge = PlanChargeFactory(
            plan=plan,
            billable_metric=metric,
            amount=10,
            free_unit=5,
            is_rate_limiting=True
        )
        
        # Create subscription with active status
        subscription = SubscriptionFactory(
            user=user,
            plan=plan,
            status='active'
        )
        
        # Create a class session with available capacity
        class_session = ClassSessionFactory(capacity=10, status='scheduled')
        
        # Create form data
        form_data = {
            'class_session': class_session.id,
            'user': user.id,
        }
        
        # Mock the _get_plan_charge method to return our plan_charge
        with patch.object(ClassBooking, '_get_plan_charge', return_value=plan_charge):
            # Mock the charge_left property
            with patch.object(PlanCharge, 'charge_left', PropertyMock(return_value=5)):
                # Create and validate the form
                form = ClassBookingForm(data=form_data)
                form.instance.user = user
                form.instance.class_session = class_session
                
                # Check that the form is valid
                is_valid = form.is_valid()
                if not is_valid:
                    pytest.fail(f"Form should be valid but had errors: {form.errors}")
        
    def test_form_invalid_full_capacity(self):
        """Test that the form is invalid when class is at capacity"""
        # Create a user with active subscription
        user = UserFactory()
        plan = PlanFactory()
        subscription = SubscriptionFactory(user=user, plan=plan, status='active')
        
        # Create a class session with no capacity
        class_session = ClassSessionFactory(capacity=0, status='scheduled')
        
        # Create form data
        form_data = {
            'class_session': class_session.id,
            'user': user.id,
        }
        
        # Create and validate the form
        form = ClassBookingForm(data=form_data)
        form.instance.user = user
        form.instance.class_session = class_session
        
        # Check that the form is invalid
        is_valid = form.is_valid()
        assert not is_valid, "Form should be invalid due to class being at full capacity"
        
        # Run clean method to get validation errors
        try:
            form.instance.clean()
            pytest.fail("Form validation should have failed but didn't")
        except Exception as e:
            # Ensure the error is about capacity
            assert "capacity" in str(e), f"Expected capacity error but got: {str(e)}"
        
    def test_form_invalid_inactive_subscription(self):
        """Test that the form is invalid when user has inactive subscription"""
        # Create a user with inactive subscription
        user = UserFactory()
        plan = PlanFactory()
        subscription = SubscriptionFactory(user=user, plan=plan, status='inactive')
        
        # Create a class session
        class_session = ClassSessionFactory(status='scheduled')
        
        # Create form data
        form_data = {
            'class_session': class_session.id,
            'user': user.id,
        }
        
        # Create and validate the form
        form = ClassBookingForm(data=form_data)
        form.instance.user = user
        form.instance.class_session = class_session
        
        # Check that the form is invalid
        is_valid = form.is_valid()
        assert not is_valid, "Form should be invalid due to inactive subscription"
        
        # Run clean method to get validation errors
        try:
            form.instance.clean()
            pytest.fail("Form validation should have failed but didn't")
        except Exception as e:
            # Ensure the error is about subscription
            assert "subscription" in str(e), f"Expected subscription error but got: {str(e)}"
            
    def test_form_invalid_class_not_scheduled(self):
        """Test that the form is invalid when class is not in scheduled status"""
        # Create a user with active subscription
        user = UserFactory()
        plan = PlanFactory()
        subscription = SubscriptionFactory(user=user, plan=plan, status='active')
        
        # Create a completed class session
        class_session = ClassSessionFactory(status='completed')
        
        # Create form data
        form_data = {
            'class_session': class_session.id,
            'user': user.id,
        }
        
        # Create and validate the form
        form = ClassBookingForm(data=form_data)
        form.instance.user = user
        form.instance.class_session = class_session
        
        # Check that the form is invalid
        is_valid = form.is_valid()
        assert not is_valid, "Form should be invalid due to class not being scheduled"
        
        # Run clean method to get validation errors
        try:
            form.instance.clean()
            pytest.fail("Form validation should have failed but didn't")
        except Exception as e:
            # Ensure the error is about class status
            assert "scheduled" in str(e), f"Expected class status error but got: {str(e)}"