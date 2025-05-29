import pytest

from nu_vibrant.subscription.models import Subscription
from nu_vibrant.subscription.tests.factories import (
    BillableMetricFactory, PlanFactory, PlanChargeFactory,
    SubscriptionFactory
)
from nu_vibrant.users.tests.factories import UserFactory


@pytest.mark.django_db
class TestSubscriptionQuerySet:
    def test_active_method(self):
        """Test the active() queryset method"""
        # Create subscriptions with different statuses
        active_sub = SubscriptionFactory(status='active')
        inactive_sub = SubscriptionFactory(status='inactive')
        cancelled_sub = SubscriptionFactory(status='cancelled')
        
        # Query active subscriptions
        active_subs = Subscription.objects.active()
        
        # Check that only active subscriptions are returned
        assert active_sub in active_subs
        assert inactive_sub not in active_subs
        assert cancelled_sub not in active_subs
    
    def test_filter_event_method(self):
        """Test the filter_event() queryset method"""
        # Create a billable metric with a specific identifier
        event_id = 'test_event'
        metric = BillableMetricFactory(identifier=event_id)
        
        # Create plans with and without this metric
        plan_with_event = PlanFactory()
        plan_without_event = PlanFactory()
        
        # Create plan charge linking the plan to the metric
        plan_charge = PlanChargeFactory(
            plan=plan_with_event,
            billable_metric=metric
        )
        
        # Create subscriptions for both plans
        sub_with_event = SubscriptionFactory(plan=plan_with_event)
        sub_without_event = SubscriptionFactory(plan=plan_without_event)
        
        # Query subscriptions with the event
        filtered_subs = Subscription.objects.filter_event(event_id)
        
        # Check that only subscriptions with the event are returned
        assert sub_with_event in filtered_subs
        assert sub_without_event not in filtered_subs