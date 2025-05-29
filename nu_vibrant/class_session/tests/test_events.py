import pytest

from nu_vibrant.class_session.models import ClassBooking
from nu_vibrant.event.registry import event_types


class TestClassSessionEvents:
    def test_event_types_registered(self):
        """Test that class_session event types are properly registered"""
        # Check that booking event is registered
        booking_event_key = f"class_session.{ClassBooking.BOOKING_EVENT}"
        booking_event = event_types.get_event_type('class_session', ClassBooking.BOOKING_EVENT)
        
        assert booking_event is not None, f"Event type {booking_event_key} should be registered"
        assert booking_event['name'] == 'Class Booking Created'
        assert 'new class booking' in booking_event['description'].lower()
        
        # Check that confirmed booking event is registered
        confirmed_event_key = f"class_session.{ClassBooking.CONFIRMED_BOOKING_EVENT}"
        confirmed_event = event_types.get_event_type('class_session', ClassBooking.CONFIRMED_BOOKING_EVENT)
        
        assert confirmed_event is not None, f"Event type {confirmed_event_key} should be registered"
        assert confirmed_event['name'] == 'Class Booking Confirmed'
        assert 'confirmed' in confirmed_event['description'].lower()