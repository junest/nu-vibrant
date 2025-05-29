import pytest
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from nu_vibrant.event.models import EventRecord
from nu_vibrant.event.services import record_event
from nu_vibrant.event.registry import event_types
from nu_vibrant.subscription.tests.factories import SubscriptionFactory, BillableMetricFactory


@pytest.mark.django_db
class TestEventServices:
    def test_record_event_with_subscription(self):
        """Test recording an event with a subscription"""
        # Register an event type
        event_types.register(
            module='test',
            event_type='test_event',
            name='Test Event',
            description='A test event'
        )
        
        # Create a user
        User = get_user_model()
        user = User.objects.create(email='test@example.com')
        
        # Create a subscription
        subscription = SubscriptionFactory(user=user)
        
        # Create a billable metric
        billable_metric = BillableMetricFactory(identifier='test_event')
        
        # Record an event
        event = record_event(
            module='test',
            event_type='test_event',
            description='Test event description',
            user=user,
            subscription=subscription,
            billable_metric=billable_metric
        )
        
        # Check that the event was created with the correct subscription and billable_metric
        assert event.subscription == subscription
        assert event.billable_metric == billable_metric
        
    def test_record_event_auto_find_billable_metric(self):
        """Test that billable_metric is automatically found if not provided"""
        # Register an event type
        event_types.register(
            module='test',
            event_type='auto_find_event',
            name='Auto Find Event',
            description='An event that should auto-find its billable metric'
        )
        
        # Create a user
        User = get_user_model()
        user = User.objects.create(email='test2@example.com')
        
        # Create a subscription
        subscription = SubscriptionFactory(user=user)
        
        # Create a billable metric with matching identifier
        billable_metric = BillableMetricFactory(identifier='auto_find_event')
        
        # Record an event without explicitly providing the billable_metric
        event = record_event(
            module='test',
            event_type='auto_find_event',
            description='Auto find test',
            user=user,
            subscription=subscription
        )
        
        # Check that the billable_metric was automatically found
        assert event.billable_metric == billable_metric