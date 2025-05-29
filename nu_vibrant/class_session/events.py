from nu_vibrant.event.registry import event_types
from .models import ClassBooking

# Register event types for class_session module
event_types.register(
    module='class_session',
    event_type=ClassBooking.BOOKING_EVENT,
    name='Class Booking Created',
    description='A new class booking was created'
)

event_types.register(
    module='class_session',
    event_type=ClassBooking.CONFIRMED_BOOKING_EVENT,
    name='Class Booking Confirmed',
    description='A class booking was confirmed/verified'
)