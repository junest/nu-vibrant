import pytest
from unittest.mock import patch

from nu_vibrant.class_session.models import ClassBooking
from nu_vibrant.class_session.tests.factories import ClassBookingFactory, ClassSessionFactory
from nu_vibrant.users.tests.factories import UserFactory
from nu_vibrant.subscription.tests.factories import SubscriptionFactory, PlanFactory


@pytest.mark.django_db
class TestClassBookingSignals:
    @patch('nu_vibrant.class_session.signals.record_event')
    def test_booking_created_event(self, mock_record_event):
        """Test that an event is recorded when a booking is created"""
        # Create dependencies
        user = UserFactory()
        plan = PlanFactory()
        subscription = SubscriptionFactory(user=user, plan=plan, status='active')
        class_session = ClassSessionFactory()
        
        # Create booking
        booking = ClassBookingFactory(
            user=user,
            class_session=class_session
        )
        
        # Check that record_event was called with correct parameters
        mock_record_event.assert_called_once()
        args, kwargs = mock_record_event.call_args
        
        assert kwargs['module'] == 'class_session'
        assert kwargs['event_type'] == ClassBooking.BOOKING_EVENT
        assert kwargs['user'] == user
        assert kwargs['obj'] == booking
        assert class_session.name in kwargs['description']
    
    @patch('nu_vibrant.class_session.signals.record_event')
    def test_booking_confirmed_event(self, mock_record_event):
        """Test that an event is recorded when a booking is confirmed"""
        # Create dependencies
        user = UserFactory()
        plan = PlanFactory()
        subscription = SubscriptionFactory(user=user, plan=plan, status='active')
        class_session = ClassSessionFactory()
        
        # Create booking with unverified status
        booking = ClassBookingFactory(
            user=user,
            class_session=class_session,
            status='unverified'
        )
        
        # Reset mock to clear the creation event
        mock_record_event.reset_mock()
        
        # Update booking status to verified
        booking.status = 'verified'
        booking.save()
        
        # Check that record_event was called with correct parameters
        mock_record_event.assert_called_once()
        args, kwargs = mock_record_event.call_args
        
        assert kwargs['module'] == 'class_session'
        assert kwargs['event_type'] == ClassBooking.CONFIRMED_BOOKING_EVENT
        assert kwargs['user'] == user
        assert kwargs['obj'] == booking
        assert class_session.name in kwargs['description']